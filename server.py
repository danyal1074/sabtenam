#!/usr/bin/env python3
"""
سرور پیشرفته سامانه ثبت‌نام کانون نخبه‌پروری شهید کاظمی آشتیانی
پشتیبانی از تفکیک جنسیت، آمار تحلیلی چندگانه، فیلترها و خروجی‌های گوناگون
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import urllib.parse
import secrets
from datetime import datetime

PORT = int(os.environ.get("PORT", 5050))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "registrations.db")

ADMIN_USER = "mohamad"
ADMIN_PASS = "123456789"
VALID_TOKENS = set()

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
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
    ''')
    # Auto-migrate table if gender column doesn't exist
    c.execute("PRAGMA table_info(students)")
    columns = [row[1] for row in c.fetchall()]
    if 'gender' not in columns:
        c.execute("ALTER TABLE students ADD COLUMN gender TEXT DEFAULT 'نامشخص'")
    
    conn.commit()
    conn.close()

class RegistrationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def is_authenticated(self):
        auth_header = self.headers.get('Authorization', '')
        token = auth_header.replace('Bearer ', '').strip()
        if not token:
            parsed = urllib.parse.urlparse(self.path)
            qs = urllib.parse.parse_qs(parsed.query)
            token = qs.get('token', [''])[0].strip()
        if not token:
            cookie_header = self.headers.get('Cookie', '')
            for cookie in cookie_header.split(';'):
                if 'admin_token=' in cookie:
                    token = cookie.split('admin_token=')[-1].strip()
        return token in VALID_TOKENS

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else b'{}'
        
        # 1. Public Student Registration
        if parsed.path.endswith('/api/register'):
            try:
                data = json.loads(body.decode('utf-8'))
                full_name = data.get('fullName', '').strip()
                gender = data.get('gender', 'نامشخص').strip()
                father_name = data.get('fatherName', '').strip()
                national_code = data.get('nationalCode', '').strip()
                birth_date = data.get('birthDate', '').strip()
                phone = data.get('phone', '').strip()
                school = data.get('school', '').strip()
                grade = data.get('grade', '').strip()
                address = data.get('address', '').strip()
                tracking_code = data.get('trackingCode') or f"KA-{int(datetime.now().timestamp()) % 1000000:06d}"
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                client_ip = self.headers.get('X-Real-IP') or self.client_address[0]

                if not (full_name and father_name and national_code and phone):
                    self.send_json_response(400, {'success': False, 'message': 'اطلاعات ضروری ناقص است.'})
                    return

                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                # Check duplicate national code
                c.execute('SELECT tracking_code FROM students WHERE national_code = ?', (national_code,))
                existing = c.fetchone()
                if existing:
                    conn.close()
                    self.send_json_response(409, {
                        'success': False,
                        'message': f'این کد ملی قبلاً با کد پیگیری {existing[0]} ثبت‌نام شده است.',
                        'trackingCode': existing[0]
                    })
                    return

                c.execute('''
                    INSERT INTO students (tracking_code, full_name, gender, father_name, national_code, birth_date, phone, school, grade, address, ip_address, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tracking_code, full_name, gender, father_name, national_code, birth_date, phone, school, grade, address, client_ip, created_at))
                conn.commit()
                conn.close()

                self.send_json_response(200, {
                    'success': True,
                    'message': 'اطلاعات با موفقیت ثبت شد.',
                    'trackingCode': tracking_code
                })
            except Exception as e:
                self.send_json_response(500, {'success': False, 'message': str(e)})

        # 2. Admin Login
        elif parsed.path.endswith('/api/admin/login'):
            try:
                data = json.loads(body.decode('utf-8'))
                username = data.get('username', '').strip()
                password = data.get('password', '').strip()

                if username == ADMIN_USER and password == ADMIN_PASS:
                    token = secrets.token_hex(24)
                    VALID_TOKENS.add(token)
                    self.send_json_response(200, {
                        'success': True,
                        'token': token,
                        'user': ADMIN_USER
                    })
                else:
                    self.send_json_response(401, {
                        'success': False,
                        'message': 'نام کاربری یا رمز عبور اشتباه است.'
                    })
            except Exception as e:
                self.send_json_response(500, {'success': False, 'message': str(e)})

        # 3. Admin Delete Record
        elif parsed.path.endswith('/api/admin/delete'):
            if not self.is_authenticated():
                self.send_json_response(403, {'success': False, 'message': 'دسترسی غیرمجاز'})
                return
            try:
                data = json.loads(body.decode('utf-8'))
                student_id = data.get('id')
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                c.execute('DELETE FROM students WHERE id = ?', (student_id,))
                conn.commit()
                conn.close()
                self.send_json_response(200, {'success': True, 'message': 'رکورد حذف شد.'})
            except Exception as e:
                self.send_json_response(500, {'success': False, 'message': str(e)})
        else:
            self.send_json_response(404, {'error': 'مسیر نامعتبر است'})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        
        # 1. Admin Submissions List
        if parsed.path.endswith('/api/admin/submissions'):
            if not self.is_authenticated():
                self.send_json_response(403, {'success': False, 'message': 'ابتدا وارد پنل مدیریت شوید.'})
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT id, tracking_code, full_name, gender, father_name, national_code, birth_date, phone, school, grade, address, created_at FROM students ORDER BY id DESC')
                rows = [dict(row) for row in c.fetchall()]
                conn.close()
                self.send_json_response(200, {'success': True, 'records': rows})
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})

        # 2. Admin Statistics with Gender, Grades, and Schools
        elif parsed.path.endswith('/api/admin/stats'):
            if not self.is_authenticated():
                self.send_json_response(403, {'success': False, 'message': 'دسترسی غیرمجاز'})
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                # Total
                c.execute('SELECT COUNT(*) FROM students')
                total = c.fetchone()[0]

                # Today
                today_str = datetime.now().strftime("%Y-%m-%d")
                c.execute('SELECT COUNT(*) FROM students WHERE created_at LIKE ?', (f'{today_str}%',))
                today_count = c.fetchone()[0]

                # Gender Breakdown
                c.execute('SELECT gender, COUNT(*) FROM students GROUP BY gender')
                gender_stats = dict(c.fetchall())

                # Grade Breakdown
                c.execute('SELECT grade, COUNT(*) FROM students GROUP BY grade')
                grade_stats = dict(c.fetchall())

                # Distinct Schools
                c.execute('SELECT COUNT(DISTINCT school) FROM students')
                schools_count = c.fetchone()[0]

                # Top Schools
                c.execute('SELECT school, COUNT(*) as cnt FROM students WHERE school != "" GROUP BY school ORDER BY cnt DESC LIMIT 5')
                top_schools = [{"school": row[0], "count": row[1]} for row in c.fetchall()]

                conn.close()
                self.send_json_response(200, {
                    'success': True,
                    'total': total,
                    'today': today_count,
                    'schools': schools_count,
                    'gender': gender_stats,
                    'grades': grade_stats,
                    'top_schools': top_schools
                })
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})

        # 3. Admin CSV Export
        elif parsed.path.endswith('/api/admin/export-csv'):
            if not self.is_authenticated():
                self.send_json_response(403, {'success': False, 'message': 'دسترسی غیرمجاز'})
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT tracking_code, full_name, gender, father_name, national_code, birth_date, phone, school, grade, address, created_at FROM students ORDER BY id ASC')
                rows = c.fetchall()
                conn.close()

                csv_lines = ["\ufeffکد پیگیری,نام و نام خانوادگی,جنسیت,نام پدر,کد ملی,تاریخ تولد,شماره تماس,مدرسه,پایه تحصیلی,آدرس,تاریخ و زمان ثبت\n"]
                for r in rows:
                    addr = (r['address'] or '').replace('\n', ' ').replace(',', '،').replace('"', '""')
                    csv_lines.append(f'"{r["tracking_code"]}","{r["full_name"]}","{r["gender"] or "نامشخص"}","{r["father_name"]}","{r["national_code"]}","{r["birth_date"]}","{r["phone"]}","{r["school"]}","{r["grade"]}","{addr}","{r["created_at"]}"\n')

                csv_data = "".join(csv_lines).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="ashtiani_all_students.csv"')
                self.send_header('Content-Length', str(len(csv_data)))
                self.end_headers()
                self.wfile.write(csv_data)
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})

        # 4. Admin JSON Export (Full Backup)
        elif parsed.path.endswith('/api/admin/export-json'):
            if not self.is_authenticated():
                self.send_json_response(403, {'success': False, 'message': 'دسترسی غیرمجاز'})
                return
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT tracking_code, full_name, gender, father_name, national_code, birth_date, phone, school, grade, address, created_at FROM students ORDER BY id ASC')
                rows = [dict(r) for r in c.fetchall()]
                conn.close()

                json_data = json.dumps(rows, ensure_ascii=False, indent=2).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="ashtiani_backup.json"')
                self.send_header('Content-Length', str(len(json_data)))
                self.end_headers()
                self.wfile.write(json_data)
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})
        else:
            # Serve index.html, admin.html, etc.
            super().do_GET()

    def send_json_response(self, code, data):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == '__main__':
    init_db()
    print(f"🚀 سرور ثبت‌نام کانون کاظمی آشتیانی فعال شد.")
    print(f"🌐 پورت: {PORT}")
    with socketserver.TCPServer(("", PORT), RegistrationHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nسرور متوقف شد.")
