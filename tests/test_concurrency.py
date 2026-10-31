#!/usr/bin/env python3
"""Prove one stuck client cannot block the registration server."""

import json
import os
import socket
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.path.join(ROOT, "server.py")
sys.path.insert(0, ROOT)

import server as regserver  # noqa: E402


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(port, path, payload=None, timeout=5, headers=None):
    url = f"http://127.0.0.1:{port}{path}"
    data = None
    req_headers = dict(headers or {})
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=req_headers, method="POST" if data is not None else "GET")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            body = response.read()
            elapsed = time.perf_counter() - started
            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                parsed = json.loads(body.decode("utf-8"))
            else:
                parsed = body
            return response.status, parsed, elapsed
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        elapsed = time.perf_counter() - started
        try:
            parsed = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            parsed = raw
        return exc.code, parsed, elapsed


def registration(national_code, name="تست"):
    return {
        "fullName": name,
        "gender": "پسر",
        "fatherName": "پدر",
        "nationalCode": national_code,
        "birthDate": "1392/01/01",
        "phone": "09120000000",
        "school": "مدرسه",
        "grade": "ششم",
        "address": "تهران",
    }


class RunningServer:
    def __init__(self, env=None, db_path=None):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.port = free_port()
        self.db = db_path or os.path.join(self.tmpdir.name, "registrations.db")
        self.env = env or {}
        self.proc = None
        self.log = os.path.join(self.tmpdir.name, "server.log")

    def start(self):
        env = os.environ.copy()
        env.update(
            {
                "HOST": "127.0.0.1",
                "PORT": str(self.port),
                "REGISTRATIONS_DB": self.db,
                "PYTHONUNBUFFERED": "1",
                "REQUEST_TIMEOUT": "8",
            }
        )
        env.update(self.env)
        log = open(self.log, "wb")
        self.proc = subprocess.Popen(
            [sys.executable, SERVER],
            cwd=ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        self._log_handle = log
        deadline = time.time() + 5
        last_error = None
        while time.time() < deadline:
            if self.proc.poll() is not None:
                break
            try:
                status, payload, _elapsed = request(self.port, "/api/health", timeout=0.5)
                if status == 200 and payload.get("status") == "ok":
                    return
            except Exception as exc:
                last_error = exc
            time.sleep(0.05)
        raise RuntimeError(
            f"server failed to start ({last_error})\n{self.logs()}"
        )

    def logs(self):
        try:
            with open(self.log, "rb") as handle:
                return handle.read().decode("utf-8", "replace")
        except OSError:
            return ""

    def stop(self):
        if self.proc is not None and self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=3)
        if getattr(self, "_log_handle", None):
            self._log_handle.close()
        self.tmpdir.cleanup()


class ConcurrencyTests(unittest.TestCase):
    def test_idle_connection_does_not_block_others(self):
        server = RunningServer()
        server.start()
        idle = socket.create_connection(("127.0.0.1", server.port), timeout=2)
        try:
            time.sleep(0.3)
            with ThreadPoolExecutor(max_workers=16) as pool:
                futures = [
                    pool.submit(request, server.port, "/api/health", None, 2)
                    for _ in range(16)
                ]
                results = [future.result(timeout=3) for future in futures]
            for status, payload, elapsed in results:
                self.assertEqual(status, 200, server.logs())
                self.assertEqual(payload["status"], "ok")
                self.assertLess(elapsed, 1.0, "request waited on the idle client")
            status, body, elapsed = request(server.port, "/", timeout=2)
            self.assertEqual(status, 200)
            self.assertLess(elapsed, 1.0)
            self.assertIn(b"<html", body.lower() if isinstance(body, bytes) else b"")
        finally:
            idle.close()
            server.stop()

    def test_slow_drip_is_cut_off_and_health_stays_fast(self):
        server = RunningServer({"REQUEST_TIMEOUT": "2"})
        server.start()
        drip = socket.create_connection(("127.0.0.1", server.port), timeout=2)
        try:
            drip.settimeout(5)
            drip.sendall(
                b"POST /api/register HTTP/1.0\r\n"
                b"Content-Length: 100000\r\n"
                b"Content-Type: application/json\r\n\r\n"
            )
            started = time.perf_counter()
            died = False
            while time.perf_counter() - started < 5:
                status, payload, elapsed = request(server.port, "/api/health", timeout=1)
                self.assertEqual(status, 200, server.logs())
                self.assertLess(elapsed, 0.8)
                try:
                    drip.sendall(b"x")
                except OSError:
                    died = True
                    break
                time.sleep(0.15)
            self.assertTrue(died, "slow client was not disconnected")
            self.assertLess(time.perf_counter() - started, 4.5)
        finally:
            drip.close()
            server.stop()

    def test_concurrent_registrations_and_duplicate_national_code(self):
        server = RunningServer()
        server.start()
        try:
            with ThreadPoolExecutor(max_workers=12) as pool:
                unique = [
                    pool.submit(
                        request,
                        server.port,
                        "/api/register",
                        registration(f"100000{i:04d}", f"نام{i}"),
                        5,
                    )
                    for i in range(10)
                ]
                dupes = [
                    pool.submit(
                        request,
                        server.port,
                        "/api/register",
                        registration("5555555555", "تکراری"),
                        5,
                    )
                    for _ in range(8)
                ]
                unique_results = [future.result(timeout=8) for future in unique]
                dupe_results = [future.result(timeout=8) for future in dupes]

            self.assertTrue(all(item[0] == 200 for item in unique_results), unique_results)
            codes = {item[1]["trackingCode"] for item in unique_results}
            self.assertEqual(len(codes), 10)

            statuses = sorted(item[0] for item in dupe_results)
            self.assertEqual(statuses.count(200), 1, dupe_results)
            self.assertEqual(statuses.count(409), 7, dupe_results)

            conn = sqlite3.connect(server.db)
            try:
                count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
                dup = conn.execute(
                    "SELECT COUNT(*) FROM students WHERE national_code = ?",
                    ("5555555555",),
                ).fetchone()[0]
                mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
            finally:
                conn.close()
            self.assertEqual(count, 11)
            self.assertEqual(dup, 1)
            self.assertEqual(mode, "wal")
        finally:
            server.stop()

    def test_oversized_body_rejected_without_blocking_health(self):
        server = RunningServer()
        server.start()
        try:
            started = time.perf_counter()
            sock = socket.create_connection(("127.0.0.1", server.port), timeout=2)
            sock.settimeout(2)
            sock.sendall(
                b"POST /api/register HTTP/1.0\r\nContent-Length: 99999999\r\n\r\n"
            )
            data = b""
            while b"\r\n\r\n" not in data:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            sock.close()
            elapsed = time.perf_counter() - started
            self.assertIn(b"413", data.split(b"\r\n", 1)[0])
            self.assertLess(elapsed, 1.0)
            status, _payload, health_elapsed = request(server.port, "/api/health", timeout=2)
            self.assertEqual(status, 200)
            self.assertLess(health_elapsed, 1.0)
        finally:
            server.stop()

    def test_failed_insert_closes_sqlite_connection(self):
        opened = []
        real_open = regserver.open_db
        previous_db = regserver.DB_FILE

        def wrapped():
            conn = real_open()
            opened.append(conn)
            return conn

        tmp = tempfile.TemporaryDirectory()
        regserver.open_db = wrapped
        regserver.DB_FILE = os.path.join(tmp.name, "registrations.db")
        try:
            regserver.init_db()
            opened.clear()
            status, payload = regserver.save_registration(
                {
                    "fullName": "الف",
                    "fatherName": "ب",
                    "nationalCode": "123",
                    "phone": "09120000000",
                    "trackingCode": "KA-000001",
                },
                "127.0.0.1",
            )
            self.assertEqual(status, 200, payload)
            status, payload = regserver.save_registration(
                {
                    "fullName": "ج",
                    "fatherName": "د",
                    "nationalCode": "456",
                    "phone": "09120000001",
                    "trackingCode": "KA-000001",
                },
                "127.0.0.1",
            )
            self.assertEqual(status, 500, payload)
            self.assertGreaterEqual(len(opened), 2)
            for conn in opened:
                with self.assertRaises(sqlite3.ProgrammingError):
                    conn.execute("SELECT 1")
        finally:
            regserver.open_db = real_open
            regserver.DB_FILE = previous_db
            tmp.cleanup()

    def test_existing_database_without_gender_keeps_rows(self):
        tmp = tempfile.TemporaryDirectory()
        db_path = os.path.join(tmp.name, "registrations.db")
        conn = sqlite3.connect(db_path)
        conn.execute(
            """
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_code TEXT UNIQUE,
                full_name TEXT,
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
        conn.execute(
            """
            INSERT INTO students (
                tracking_code, full_name, father_name, national_code, phone, created_at
            ) VALUES ('KA-000001', 'قدیمی', 'پدر', '9999999999', '09121111111',
                      '2020-01-01 00:00:00')
            """
        )
        conn.commit()
        conn.close()

        server = RunningServer(db_path=db_path)
        server.db = db_path
        server.start()
        try:
            status, payload, _elapsed = request(
                server.port,
                "/api/register",
                registration("8888888888", "جدید"),
                5,
            )
            self.assertEqual(status, 200, payload)
            conn = sqlite3.connect(db_path)
            try:
                columns = [row[1] for row in conn.execute("PRAGMA table_info(students)")]
                rows = conn.execute(
                    "SELECT tracking_code, full_name, gender, national_code FROM students ORDER BY id"
                ).fetchall()
            finally:
                conn.close()
            self.assertIn("gender", columns)
            self.assertEqual(rows[0][0], "KA-000001")
            self.assertEqual(rows[0][1], "قدیمی")
            self.assertEqual(rows[0][2], "نامشخص")
            self.assertEqual(len(rows), 2)
        finally:
            server.stop()
            tmp.cleanup()

    def test_write_lock_does_not_block_health(self):
        server = RunningServer()
        server.start()
        holder = sqlite3.connect(server.db, timeout=5, isolation_level=None)
        try:
            holder.execute("PRAGMA busy_timeout = 5000")
            holder.execute("BEGIN IMMEDIATE")
            status, payload, elapsed = request(server.port, "/api/health", timeout=2)
            self.assertEqual(status, 200, server.logs())
            self.assertEqual(payload["status"], "ok")
            self.assertLess(elapsed, 1.0)

            result = {}

            def submit():
                result["value"] = request(
                    server.port,
                    "/api/register",
                    registration("7777777777", "قفل"),
                    5,
                )

            worker = threading.Thread(target=submit)
            worker.start()
            time.sleep(0.3)
            status, _payload, elapsed = request(server.port, "/api/health", timeout=2)
            self.assertEqual(status, 200)
            self.assertLess(elapsed, 1.0)
            self.assertTrue(worker.is_alive())
            holder.rollback()
            worker.join(timeout=5)
            self.assertFalse(worker.is_alive())
            self.assertEqual(result["value"][0], 200, result)
        finally:
            try:
                holder.close()
            except sqlite3.Error:
                pass
            server.stop()

    def test_static_form_served_and_secrets_are_not(self):
        server = RunningServer()
        server.start()
        try:
            status, body, _elapsed = request(server.port, "/index.html", timeout=2)
            self.assertEqual(status, 200)
            self.assertIn("ثبت‌نام".encode("utf-8"), body)
            status, body, _elapsed = request(server.port, "/fonts/BTitrBd.ttf", timeout=2)
            self.assertEqual(status, 200)
            self.assertGreater(len(body), 1000)
            for path in ("/server.py", "/registrations.db", "/registrations.db-wal", "/.gitignore"):
                code, _body, elapsed = request(server.port, path, timeout=2)
                self.assertEqual(code, 404, path)
                self.assertLess(elapsed, 1.0)
            code, payload, _elapsed = request(
                server.port,
                "/api/admin/login",
                {"username": "nope", "password": "nope"},
                2,
            )
            self.assertEqual(code, 401)
            self.assertFalse(payload["success"])
            code, payload, _elapsed = request(
                server.port,
                "/api/admin/login",
                {"username": regserver.ADMIN_USER, "password": regserver.ADMIN_PASS},
                2,
            )
            self.assertEqual(code, 200, payload)
            token = payload["token"]
            code, payload, _elapsed = request(
                server.port,
                "/api/admin/stats",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2,
            )
            self.assertEqual(code, 200, payload)
            self.assertEqual(payload["total"], 0)
            code, body, _elapsed = request(server.port, "/admin.html", timeout=2)
            self.assertEqual(code, 200)
            self.assertIn("پنل".encode("utf-8"), body)

            code, payload, _elapsed = request(
                server.port,
                "/api/register",
                registration("1010101010", "مدیریتی"),
                5,
            )
            self.assertEqual(code, 200, payload)
            code, payload, _elapsed = request(
                server.port,
                "/api/admin/submissions",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2,
            )
            self.assertEqual(code, 200, payload)
            self.assertEqual(payload["records"][0]["national_code"], "1010101010")
            self.assertEqual(payload["records"][0]["full_name"], "مدیریتی")
            student_id = payload["records"][0]["id"]
            code, csv_body, _elapsed = request(
                server.port,
                "/api/admin/export-csv",
                headers={"Authorization": f"Bearer {token}"},
                timeout=2,
            )
            self.assertEqual(code, 200)
            self.assertIn("کد پیگیری".encode("utf-8"), csv_body)
            self.assertIn("1010101010".encode("utf-8"), csv_body)
            code, payload, _elapsed = request(
                server.port,
                "/api/admin/delete",
                {"id": student_id},
                2,
                headers={"Authorization": f"Bearer {token}"},
            )
            self.assertEqual(code, 200, payload)
            self.assertTrue(payload["success"])
        finally:
            server.stop()

    def test_connection_cap_rejects_quickly_and_releases(self):
        server = RunningServer({"MAX_CONNECTIONS": "2", "REQUEST_TIMEOUT": "5"})
        server.start()
        held = []
        try:
            for _ in range(2):
                sock = socket.create_connection(("127.0.0.1", server.port), timeout=2)
                held.append(sock)
            time.sleep(0.3)
            started = time.perf_counter()
            code, payload, elapsed = request(server.port, "/api/health", timeout=2)
            self.assertEqual(code, 503, server.logs())
            self.assertFalse(payload["success"])
            self.assertLess(elapsed, 1.0)
            self.assertLess(time.perf_counter() - started, 1.5)
            held.pop().close()
            deadline = time.time() + 2
            recovered = None
            while time.time() < deadline:
                recovered = request(server.port, "/api/health", timeout=1)
                if recovered[0] == 200:
                    break
                time.sleep(0.05)
            self.assertIsNotNone(recovered)
            self.assertEqual(recovered[0], 200, server.logs())
        finally:
            for sock in held:
                sock.close()
            server.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
