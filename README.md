# سامانه ثبت‌نام پذیرفته‌شدگان کانون نخبه‌پروری شهید کاظمی آشتیانی

فرم آنلاین و سامانه مدیریت ثبت‌نام داوطلبان برتر آزمون ورودی کانون نخبه‌پروری دانشمند شهید کاظمی آشتیانی.

## 🚀 ویژگی‌ها:
- طراحی واکنش‌گرا (Responsive) و راست‌چین (RTL) با لوگوی اختصاصی کانون
- اعتبارسنجی دقیق کد ملی ۱۰ رقمی (با الگوریتم رقم کنترلی) و شماره تلفن همراه
- ذخیره اطلاعات در پایگاه داده SQLite روی سرور
- صدور خودکار کد رهگیری یکتا برای هر داوطلب
- جلوگیری از ثبت‌نام تکراری بر اساس کد ملی
- قابلیت خروجی اکسل (CSV) با کدگذاری UTF-8
- حالت چاپ رسمی برگه فرم با فرمت استاندارد A4 و محل امضا/اثر انگشت

## 🛠️ نحوه راه‌اندازی روی سرور مجازی (Linux VPS):

### اجرای مستقیم با پایتون:
```bash
python3 server.py
```
سپس فرم روی پورت `8080` در دسترس خواهد بود: `http://SERVER_IP:8080`

### راه‌اندازی دائمی در پس‌زمینه با systemd (اختیاری):
```bash
sudo nano /etc/systemd/system/kazemi-form.service
```
محتوای زیر را قرار دهید:
```ini
[Unit]
Description=Kazemi Ashtiani Registration Service
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/registration-form
ExecStart=/usr/bin/python3 server.py
Restart=always
Environment=PORT=80

[Install]
WantedBy=multi-user.target
```
سپس سرویس را فعال کنید:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now kazemi-form
```
