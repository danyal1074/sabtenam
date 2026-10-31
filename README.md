# سامانه ثبت‌نام پذیرفته‌شدگان کانون نخبه‌پروری شهید کاظمی آشتیانی

فرم آنلاین و سامانه مدیریت ثبت‌نام داوطلبان برتر آزمون ورودی کانون نخبه‌پروری دانشمند شهید کاظمی آشتیانی.

## ویژگی‌ها
- طراحی واکنش‌گرا (Responsive) و راست‌چین (RTL) با لوگوی اختصاصی کانون
- اعتبارسنجی دقیق کد ملی ۱۰ رقمی (با الگوریتم رقم کنترلی) و شماره تلفن همراه
- ذخیره اطلاعات در پایگاه داده SQLite روی سرور
- صدور خودکار کد رهگیری یکتا برای هر داوطلب
- جلوگیری از ثبت‌نام تکراری بر اساس کد ملی
- قابلیت خروجی اکسل (CSV) با کدگذاری UTF-8
- حالت چاپ رسمی برگه فرم با فرمت استاندارد A4 و محل امضا/اثر انگشت
- پاسخ همزمان به چند درخواست، حتی اگر یک اتصال بی‌کار یا کند باز بماند
- مسیر سلامت `GET /api/health` برای بررسی زنده بودن سرویس

## چرا قبلاً 504 می‌داد
نسخهٔ قبلی فقط با `socketserver.TCPServer` کار می‌کرد: در هر لحظه یک درخواست، و بدون مهلت زمانی روی سوکت. کافی بود یک کلاینت اتصال TCP را باز کند و چیزی نفرستد. پروسه همان اتصال را قبول می‌کرد و روی خواندن خط اول درخواست می‌ماند. nginx اتصال را برقرار می‌دید ولی پاسخی نمی‌گرفت و بعد از حدود ۶۰ ثانیه **504 Gateway Time-out** برمی‌گرداند (502 نیست، چون پروسه زنده است). بقیهٔ سایت و `/api/health` اصلی جدا از این فرم هستند و به همین خاطر سالم می‌ماندند.

این رفتار قبل از اصلاح روی همین کد آزمایش شد: تا وقتی آن سوکت بی‌کار بسته نشده بود، درخواست بعدی اصلاً جواب نمی‌گرفت.

الان هر اتصال در یک نخ daemon جدا رسیدگی می‌شود، برای هر اتصال یک مهلت مطلق (پیش‌فرض ۳۰ ثانیه) هست، حجم بدنه سقف دارد، و اتصال SQLite حتی اگر خطا پیش بیاید بسته می‌شود. حالت WAL و `busy_timeout` هم اضافه شده تا قفل کوتاه پایگاه، بقیهٔ درخواست‌ها را نکشد. اسکیما و داده‌های `registrations.db` عوض نمی‌شود.

## اجرا روی سرور (پشت nginx)
سرویس فقط روی `127.0.0.1` گوش می‌دهد و با کاربر غیر root (معمولاً `www-data`) اجرا می‌شود. nginx همان ماشین درخواست‌های `https://roshd.digiral.ir/sabtenam/` را به این پورت پروکسی می‌کند. پورت پیش‌فرض `5050` است. اگر nginx به پورت دیگری پروکسی می‌کند، همان را در واحد systemd بگذارید تا لازم نباشد تنظیم nginx را عوض کنید.

فایل `registrations.db` (و در کنارش `registrations.db-wal` و `registrations.db-shm`) را حذف نکنید. ثبت‌نام‌های قبلی همان‌جا می‌مانند.

### استقرار و راه‌اندازی مجدد

اگر مسیر پروژه روی سرور چیز دیگری است، در دستورها و در `deploy/kazemi-form.service` همان مسیر را بگذارید. پورت را با خروجی nginx یکی کنید:

```bash
sudo nginx -T 2>/dev/null | grep -n -E 'sabtenam|proxy_pass'
ss -ltnp | grep -E 'python|server.py'
```

سپس:

```bash
cd /var/www/registration-form
git fetch origin cursor/fix-registration-server-hang-a0fb
# تا ادغام این اصلاح در main، همین شاخه را بگیرید. بعد از ادغام:
#   git checkout main && git pull origin main
git checkout -B cursor/fix-registration-server-hang-a0fb origin/cursor/fix-registration-server-hang-a0fb

sudo cp deploy/kazemi-form.service /etc/systemd/system/kazemi-form.service
sudo chown -R www-data:www-data /var/www/registration-form
sudo systemctl daemon-reload
sudo systemctl enable kazemi-form
sudo systemctl restart kazemi-form
sudo systemctl status kazemi-form --no-pager

curl -fsS -m 5 http://127.0.0.1:5050/api/health
curl -fsS -m 15 -o /dev/null -w "public %{http_code}\n" https://roshd.digiral.ir/sabtenam/
```

اگر پروسهٔ قدیمی هنوز پورت را گرفته (برای مثال `python3 server.py` که قبلاً دستی اجرا شده):

```bash
ss -ltnp | grep python
sudo systemctl stop kazemi-form
sudo fuser -k 5050/tcp
sudo systemctl start kazemi-form
```

`fuser -k` را فقط وقتی بزنید که مطمئن هستید روی همان پورت، پروسهٔ قبلی همین فرم است.

لاگ سرویس:

```bash
sudo journalctl -u kazemi-form -n 80 --no-pager
```

اگر `proxy_pass` به‌جای `127.0.0.1` به یک آدرس غیر loopback اشاره می‌کند، یا آن را به `http://127.0.0.1:5050` تغییر دهید، یا موقتاً در واحد systemd مقدار `HOST=0.0.0.0` بگذارید. حالت درست این است که فرم فقط از طریق nginx و روی loopback در دسترس باشد.

نمونهٔ محل nginx (فقط اگر هنوز پروکسی ندارید؛ اگر دارید همان را نگه دارید):

```nginx
location /sabtenam/ {
    proxy_pass http://127.0.0.1:5050/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_connect_timeout 5s;
    proxy_read_timeout 60s;
    proxy_send_timeout 60s;
}
```

### اجرای محلی

```bash
HOST=127.0.0.1 PORT=5050 python3 server.py
```

فرم روی `http://127.0.0.1:5050/` باز می‌شود. آزمایش اینکه یک اتصال بی‌کار بقیه را مسدود نمی‌کند:

```bash
python3 tests/test_concurrency.py
```

متغیرهای محیطی اختیاری: `HOST`، `PORT`، `REQUEST_TIMEOUT` (ثانیه)، `MAX_CONNECTIONS`، `MAX_BODY_BYTES`، `SQLITE_BUSY_MS`، `REGISTRATIONS_DB`.
