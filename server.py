#!/usr/bin/env python3
"""
سرور اختصاصی ثبت‌نام کانون نخبه‌پروری دانشمند شهید کاظمی آشتیانی
نوشته شده با کتابخانه‌های استاندارد پایتون (بدون نیاز به نصب پکیج اضافه)
قابل اجرا روی انواع سرورهای لینوکس (اوبونتو، دبیان و...) و ویندوز
"""

import http.server
import socketserver
import json
import sqlite3
import os
import sys
import urllib.parse
from datetime import datetime

PORT = int(os.environ.get("PORT", 8080))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "registrations.db")

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
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
    ''')
    conn.commit()
    conn.close()

class RegistrationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def do_POST(self):
        if self.path == '/api/register':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            try:
                data = json.loads(body.decode('utf-8'))
                full_name = data.get('fullName', '').strip()
                father_name = data.get('fatherName', '').strip()
                national_code = data.get('nationalCode', '').strip()
                birth_date = data.get('birthDate', '').strip()
                phone = data.get('phone', '').strip()
                school = data.get('school', '').strip()
                grade = data.get('grade', '').strip()
                address = data.get('address', '').strip()
                tracking_code = data.get('trackingCode') or f"KA-{int(datetime.now().timestamp()) % 1000000:06d}"
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                client_ip = self.client_address[0]

                if not (full_name and father_name and national_code and phone):
                    self.send_json_response(400, {'success': False, 'message': 'اطلاعات ضروری ناقص است.'})
                    return

                conn = sqlite3.connect(DB_FILE)
                c = conn.cursor()
                
                # Check for duplicate national code
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
                    INSERT INTO students (tracking_code, full_name, father_name, national_code, birth_date, phone, school, grade, address, ip_address, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (tracking_code, full_name, father_name, national_code, birth_date, phone, school, grade, address, client_ip, created_at))
                conn.commit()
                conn.close()

                self.send_json_response(200, {
                    'success': True,
                    'message': 'ثبت‌نام با موفقیت ذخیره شد.',
                    'trackingCode': tracking_code
                })
            except Exception as e:
                self.send_json_response(500, {'success': False, 'message': str(e)})
        else:
            self.send_json_response(404, {'error': 'مسیر مورد نظر یافت نشد'})

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/submissions':
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT id, tracking_code, full_name, father_name, national_code, birth_date, phone, school, grade, address, created_at FROM students ORDER BY id DESC')
                rows = [dict(row) for row in c.fetchall()]
                conn.close()
                self.send_json_response(200, {'success': True, 'records': rows})
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})
        elif parsed.path == '/api/export-csv':
            try:
                conn = sqlite3.connect(DB_FILE)
                conn.row_factory = sqlite3.Row
                c = conn.cursor()
                c.execute('SELECT tracking_code, full_name, father_name, national_code, birth_date, phone, school, grade, address, created_at FROM students ORDER BY id ASC')
                rows = c.fetchall()
                conn.close()

                csv_lines = ["\ufeffکد پیگیری,نام و نام خانوادگی,نام پدر,کد ملی,تاریخ تولد,شماره تماس,مدرسه,پایه تحصیلی,آدرس,تاریخ و زمان ثبت\n"]
                for r in rows:
                    addr = (r['address'] or '').replace('\n', ' ').replace(',', '،')
                    csv_lines.append(f'"{r["tracking_code"]}","{r["full_name"]}","{r["father_name"]}","{r["national_code"]}","{r["birth_date"]}","{r["phone"]}","{r["school"]}","{r["grade"]}","{addr}","{r["created_at"]}"\n')

                csv_data = "".join(csv_lines).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type', 'text/csv; charset=utf-8')
                self.send_header('Content-Disposition', 'attachment; filename="kazemi_ashtiani_students.csv"')
                self.send_header('Content-Length', str(len(csv_data)))
                self.end_headers()
                self.wfile.write(csv_data)
            except Exception as e:
                self.send_json_response(500, {'error': str(e)})
        else:
            # Serve index.html and static files
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
    print(f"🌐 آدرس محلی: http://localhost:{PORT}")
    print(f"💾 پایگاه داده: {DB_FILE}")
    with socketserver.TCPServer(("", PORT), RegistrationHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nسرور متوقف شد.")
