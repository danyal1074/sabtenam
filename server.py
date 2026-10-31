#!/usr/bin/env python3
"""
سرور سامانه ثبت‌نام کانون نخبه‌پروری شهید کاظمی آشتیانی.

هر اتصال در یک نخ daemon جدا رسیدگی می‌شود تا یک کلاینت بی‌کار یا کند
بقیهٔ درخواست‌ها را پشت سر خود معطل نکند. مهلت هر اتصال محدود است،
بدنهٔ درخواست سقف دارد، و اتصال SQLite در هر حالتی بسته می‌شود.
اسکیما و داده‌های registrations.db تغییر نمی‌کند.
"""

import contextlib
import errno
import http.server
import json
import os
import socket
import socketserver
import sqlite3
import sys
import threading
import urllib.parse
import secrets
from datetime import datetime

HOST = os.environ.get("HOST", "127.0.0.1").strip() or "127.0.0.1"
PORT = int(os.environ.get("PORT", "5050"))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.environ.get(
    "REGISTRATIONS_DB", os.path.join(BASE_DIR, "registrations.db")
)

REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "30"))
MAX_CONNECTIONS = max(1, int(os.environ.get("MAX_CONNECTIONS", "128")))
MAX_BODY_BYTES = int(os.environ.get("MAX_BODY_BYTES", str(1024 * 1024)))
SQLITE_BUSY_MS = int(os.environ.get("SQLITE_BUSY_MS", "5000"))

ADMIN_USER = "mohamad"
ADMIN_PASS = "123456789"
VALID_TOKENS = set()
_tokens_lock = threading.Lock()

# Shutdown of a timed-out socket surfaces as one of these errnos in the handler.
_ABORT_ERRNOS = {
    errno.EPIPE,
    errno.ECONNRESET,
    errno.EBADF,
    errno.ENOTCONN,
    errno.ETIMEDOUT,
    errno.ECONNABORTED,
}
if hasattr(errno, "ESHUTDOWN"):
    _ABORT_ERRNOS.add(errno.ESHUTDOWN)

_BLOCKED_SUFFIXES = (
    ".db",
    ".db-wal",
    ".db-shm",
    ".sqlite",
    ".sqlite3",
    ".py",
    ".pyc",
    ".pyo",
)


def open_db():
    """Open a short-lived connection. Callers must close it."""
    parent = os.path.dirname(DB_FILE)
    if parent:
        os.makedirs(parent, exist_ok=True)
    conn = sqlite3.connect(
        DB_FILE,
        timeout=SQLITE_BUSY_MS / 1000.0,
        isolation_level=None,
        check_same_thread=True,
    )
    try:
        conn.execute(f"PRAGMA busy_timeout = {int(SQLITE_BUSY_MS)}")
        conn.execute("PRAGMA journal_mode = WAL").fetchone()
        return conn
    except Exception:
        conn.close()
        raise


@contextlib.contextmanager
def db_session():
    conn = open_db()
    try:
        yield conn
    except Exception:
        try:
            conn.rollback()
        except sqlite3.Error:
            pass
        raise
    finally:
        conn.close()


def init_db():
    with db_session() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_code TEXT UNIQUE,
                full_name TEXT,
                gender TEXT DEFAULT 'نامشخص',
                father_name TEXT,
                national_code TEXT,
                birth_date TEXT,
                phone TEXT,
                school TEXT,
                grade TEXT,
                address TEXT,
                ip_address TEXT,
                created_at TEXT
            )
            """
        )
        columns = [row[1] for row in conn.execute("PRAGMA table_info(students)")]
        if "gender" not in columns:
            conn.execute(
                "ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'نامشخص'"
            )


def default_tracking_code():
    return f"KA-{int(datetime.now().timestamp()) % 1000000:06d}"


def random_tracking_code():
    return f"KA-{secrets.randbelow(1_000_000):06d}"


def save_registration(data, client_ip):
    """Insert one registration. Returns (http_status, json_body)."""
    full_name = data.get("fullName", "").strip()
    gender = data.get("gender", "نامشخص").strip()
    father_name = data.get("fatherName", "").strip()
    national_code = data.get("nationalCode", "").strip()
    birth_date = data.get("birthDate", "").strip()
    phone = data.get("phone", "").strip()
    school = data.get("school", "").strip()
    grade = data.get("grade", "").strip()
    address = data.get("address", "").strip()
    supplied = data.get("trackingCode") or None
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if not (full_name and father_name and national_code and phone):
        return 400, {"success": False, "message": "اطلاعات ضروری ناقص است."}

    first_code = supplied or default_tracking_code()
    attempts = 1 if supplied else 6
    last_error = None

    with db_session() as conn:
        for attempt in range(attempts):
            code = first_code if attempt == 0 else random_tracking_code()
            try:
                conn.execute("BEGIN IMMEDIATE")
                existing = conn.execute(
                    "SELECT tracking_code FROM students WHERE national_code = ?",
                    (national_code,),
                ).fetchone()
                if existing:
                    conn.rollback()
                    return 409, {
                        "success": False,
                        "message": (
                            f"این کد ملی قبلاً با کد پیگیری {existing[0]} ثبت‌نام شده است."
                        ),
                        "trackingCode": existing[0],
                    }
                conn.execute(
                    """
                    INSERT INTO students (
                        tracking_code, full_name, gender, father_name, national_code,
                        birth_date, phone, school, grade, address, ip_address, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        code,
                        full_name,
                        gender,
                        father_name,
                        national_code,
                        birth_date,
                        phone,
                        school,
                        grade,
                        address,
                        client_ip,
                        created_at,
                    ),
                )
                conn.commit()
                return 200, {
                    "success": True,
                    "message": "اطلاعات با موفقیت ثبت شد.",
                    "trackingCode": code,
                }
            except sqlite3.IntegrityError as exc:
                conn.rollback()
                last_error = exc
        return 500, {"success": False, "message": str(last_error)}


def health_payload():
    """Lightweight liveness check. A locked writer must not stall this for long."""
    try:
        conn = sqlite3.connect(
            DB_FILE,
            timeout=1.0,
            isolation_level=None,
            check_same_thread=True,
        )
        try:
            conn.execute("PRAGMA busy_timeout = 1000")
            conn.execute("SELECT 1").fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return 503, {"status": "error"}
    return 200, {"status": "ok"}


def remember_token(token):
    with _tokens_lock:
        VALID_TOKENS.add(token)


def token_is_valid(token):
    if not token:
        return False
    with _tokens_lock:
        return token in VALID_TOKENS


def is_blocked_static(url_path):
    """Refuse to serve the database, its WAL files, or the Python source."""
    path = urllib.parse.unquote(url_path.split("?", 1)[0])
    parts = [part for part in path.split("/") if part not in ("", ".")]
    if any(part.startswith(".") for part in parts):
        return True
    if not parts:
        return False
    name = parts[-1].lower()
    return name.endswith(_BLOCKED_SUFFIXES)


class ThreadedServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Accept on the main thread; handle each connection on a daemon thread."""

    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 128

    def __init__(self, server_address, handler):
        super().__init__(server_address, handler)
        self._slots = threading.BoundedSemaphore(MAX_CONNECTIONS)

    def process_request(self, request, client_address):
        if not self._slots.acquire(blocking=False):
            threading.Thread(
                target=self._reject_busy, args=(request,), daemon=True
            ).start()
            return
        try:
            super().process_request(request, client_address)
        except Exception:
            self._slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self._slots.release()

    def _reject_busy(self, request):
        body = json.dumps(
            {
                "success": False,
                "message": "سرور مشغول است. لطفاً چند لحظه بعد دوباره تلاش کنید.",
            },
            ensure_ascii=False,
        ).encode("utf-8")
        raw = (
            b"HTTP/1.0 503 Service Unavailable\r\n"
            b"Content-Type: application/json; charset=utf-8\r\n"
            b"Connection: close\r\n"
            b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n\r\n" + body
        )
        try:
            request.settimeout(0.5)
            request.sendall(raw)
        except OSError:
            pass
        finally:
            try:
                self.shutdown_request(request)
            except OSError:
                try:
                    request.close()
                except OSError:
                    pass


class RegistrationHandler(http.server.SimpleHTTPRequestHandler):
    timeout = REQUEST_TIMEOUT if REQUEST_TIMEOUT > 0 else None
    protocol_version = "HTTP/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def setup(self):
        super().setup()
        self._deadline_timer = None
        if self.timeout and self.timeout > 0:
            timer = threading.Timer(float(self.timeout), self._abort_connection)
            timer.daemon = True
            timer.start()
            self._deadline_timer = timer

    def finish(self):
        timer = getattr(self, "_deadline_timer", None)
        if timer is not None:
            timer.cancel()
        try:
            super().finish()
        except OSError:
            pass

    def _abort_connection(self):
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def handle(self):
        try:
            super().handle()
        except (TimeoutError, ConnectionError, socket.timeout):
            self.close_connection = True
        except OSError as exc:
            if exc.errno not in _ABORT_ERRNOS:
                self.log_error("OSError handling request: %s", exc)
            self.close_connection = True

    def list_directory(self, path):
        self.send_error(404, "Not found")
        return None

    def is_authenticated(self):
        auth_header = self.headers.get("Authorization", "")
        token = auth_header.replace("Bearer ", "").strip()
        if not token:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            token = qs.get("token", [""])[0].strip()
        if not token:
            cookie_header = self.headers.get("Cookie", "")
            for cookie in cookie_header.split(";"):
                if "admin_token=" in cookie:
                    token = cookie.split("admin_token=")[-1].strip()
        return token_is_valid(token)

    def read_body(self):
        raw_length = self.headers.get("Content-Length", "0")
        try:
            length = int(raw_length)
        except (TypeError, ValueError):
            self.send_json_response(
                400, {"success": False, "message": "Content-Length نامعتبر است."}
            )
            return None
        if length < 0 or length > MAX_BODY_BYTES:
            self.send_json_response(
                413,
                {"success": False, "message": "حجم درخواست بیش از حد مجاز است."},
            )
            return None
        if length == 0:
            return b"{}"
        return self.rfile.read(length)

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        body = self.read_body()
        if body is None:
            return

        if parsed.path.endswith("/api/register"):
            try:
                data = json.loads(body.decode("utf-8"))
                client_ip = self.headers.get("X-Real-IP") or self.client_address[0]
                status, payload = save_registration(data, client_ip)
                self.send_json_response(status, payload)
            except Exception as exc:
                self.send_json_response(
                    500, {"success": False, "message": str(exc)}
                )
            return

        if parsed.path.endswith("/api/admin/login"):
            try:
                data = json.loads(body.decode("utf-8"))
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                if username == ADMIN_USER and password == ADMIN_PASS:
                    token = secrets.token_hex(24)
                    remember_token(token)
                    self.send_json_response(
                        200, {"success": True, "token": token, "user": ADMIN_USER}
                    )
                else:
                    self.send_json_response(
                        401,
                        {
                            "success": False,
                            "message": "نام کاربری یا رمز عبور اشتباه است.",
                        },
                    )
            except Exception as exc:
                self.send_json_response(
                    500, {"success": False, "message": str(exc)}
                )
            return

        if parsed.path.endswith("/api/admin/delete"):
            if not self.is_authenticated():
                self.send_json_response(
                    403, {"success": False, "message": "دسترسی غیرمجاز"}
                )
                return
            try:
                data = json.loads(body.decode("utf-8"))
                student_id = data.get("id")
                with db_session() as conn:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
                    conn.commit()
                self.send_json_response(
                    200, {"success": True, "message": "رکورد حذف شد."}
                )
            except Exception as exc:
                self.send_json_response(
                    500, {"success": False, "message": str(exc)}
                )
            return

        self.send_json_response(404, {"error": "مسیر نامعتبر است"})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path.endswith("/api/health"):
            status, payload = health_payload()
            self.send_json_response(status, payload)
            return

        if parsed.path.endswith("/api/admin/submissions"):
            if not self.is_authenticated():
                self.send_json_response(
                    403,
                    {
                        "success": False,
                        "message": "ابتدا وارد پنل مدیریت شوید.",
                    },
                )
                return
            try:
                with db_session() as conn:
                    conn.row_factory = sqlite3.Row
                    rows = [
                        dict(row)
                        for row in conn.execute(
                            "SELECT id, tracking_code, full_name, gender, father_name, "
                            "national_code, birth_date, phone, school, grade, address, "
                            "created_at FROM students ORDER BY id DESC"
                        )
                    ]
                self.send_json_response(200, {"success": True, "records": rows})
            except Exception as exc:
                self.send_json_response(500, {"error": str(exc)})
            return

        if parsed.path.endswith("/api/admin/stats"):
            if not self.is_authenticated():
                self.send_json_response(
                    403, {"success": False, "message": "دسترسی غیرمجاز"}
                )
                return
            try:
                with db_session() as conn:
                    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    today_count = conn.execute(
                        "SELECT COUNT(*) FROM students WHERE created_at LIKE ?",
                        (f"{today_str}%",),
                    ).fetchone()[0]
                    gender_stats = dict(
                        conn.execute(
                            "SELECT gender, COUNT(*) FROM students GROUP BY gender"
                        ).fetchall()
                    )
                    grade_stats = dict(
                        conn.execute(
                            "SELECT grade, COUNT(*) FROM students GROUP BY grade"
                        ).fetchall()
                    )
                    schools_count = conn.execute(
                        "SELECT COUNT(DISTINCT school) FROM students"
                    ).fetchone()[0]
                    top_schools = [
                        {"school": row[0], "count": row[1]}
                        for row in conn.execute(
                            "SELECT school, COUNT(*) as cnt FROM students "
                            "WHERE school != '' GROUP BY school ORDER BY cnt DESC LIMIT 5"
                        )
                    ]
                self.send_json_response(
                    200,
                    {
                        "success": True,
                        "total": total,
                        "today": today_count,
                        "schools": schools_count,
                        "gender": gender_stats,
                        "grades": grade_stats,
                        "top_schools": top_schools,
                    },
                )
            except Exception as exc:
                self.send_json_response(500, {"error": str(exc)})
            return

        if parsed.path.endswith("/api/admin/export-csv"):
            if not self.is_authenticated():
                self.send_json_response(
                    403, {"success": False, "message": "دسترسی غیرمجاز"}
                )
                return
            try:
                with db_session() as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute(
                        "SELECT tracking_code, full_name, gender, father_name, "
                        "national_code, birth_date, phone, school, grade, address, "
                        "created_at FROM students ORDER BY id ASC"
                    ).fetchall()
                csv_lines = [
                    "\ufeffکد پیگیری,نام و نام خانوادگی,جنسیت,نام پدر,کد ملی,تاریخ تولد,شماره تماس,مدرسه,پایه تحصیلی,آدرس,تاریخ و زمان ثبت\n"
                ]
                for record in rows:
                    addr = (
                        (record["address"] or "")
                        .replace("\n", " ")
                        .replace(",", "،")
                        .replace('"', '""')
                    )
                    csv_lines.append(
                        f'"{record["tracking_code"]}","{record["full_name"]}",'
                        f'"{record["gender"] or "نامشخص"}","{record["father_name"]}",'
                        f'"{record["national_code"]}","{record["birth_date"]}",'
                        f'"{record["phone"]}","{record["school"]}","{record["grade"]}",'
                        f'"{addr}","{record["created_at"]}"\n'
                    )
                csv_data = "".join(csv_lines).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header(
                    "Content-Disposition",
                    'attachment; filename="ashtiani_all_students.csv"',
                )
                self.send_header("Content-Length", str(len(csv_data)))
                self.end_headers()
                self.wfile.write(csv_data)
            except Exception as exc:
                self.send_json_response(500, {"error": str(exc)})
            return

        if parsed.path.endswith("/api/admin/export-json"):
            if not self.is_authenticated():
                self.send_json_response(
                    403, {"success": False, "message": "دسترسی غیرمجاز"}
                )
                return
            try:
                with db_session() as conn:
                    conn.row_factory = sqlite3.Row
                    rows = [
                        dict(row)
                        for row in conn.execute(
                            "SELECT tracking_code, full_name, gender, father_name, "
                            "national_code, birth_date, phone, school, grade, address, "
                            "created_at FROM students ORDER BY id ASC"
                        )
                    ]
                json_data = json.dumps(rows, ensure_ascii=False, indent=2).encode(
                    "utf-8"
                )
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header(
                    "Content-Disposition",
                    'attachment; filename="ashtiani_backup.json"',
                )
                self.send_header("Content-Length", str(len(json_data)))
                self.end_headers()
                self.wfile.write(json_data)
            except Exception as exc:
                self.send_json_response(500, {"error": str(exc)})
            return

        if is_blocked_static(parsed.path):
            self.send_error(404, "Not found")
            return
        super().do_GET()

    def send_json_response(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(body)


def main():
    if hasattr(os, "geteuid") and os.geteuid() == 0:
        print(
            "هشدار: سرور با کاربر root اجرا شده است. پشت nginx با کاربر غیرممتاز اجرا کنید.",
            file=sys.stderr,
        )
    init_db()
    print("سرور ثبت‌نام کانون کاظمی آشتیانی فعال شد.")
    print(f"نشانی: http://{HOST}:{PORT}")
    httpd = ThreadedServer((HOST, PORT), RegistrationHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nسرور متوقف شد.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
