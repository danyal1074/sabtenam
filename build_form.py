import os
import base64

dir_path = r"C:\Users\danyal\.gemini\antigravity\scratch\registration-form"
logo_path = os.path.join(dir_path, "logo.jpg")

with open(logo_path, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode("utf-8")

html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>فرم ثبت‌نام پذیرفته‌شدگان - کانون نخبه‌پروری شهید کاظمی آشتیانی</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary: #0d7377;
            --primary-dark: #074b4e;
            --primary-light: #14a098;
            --secondary: #109153;
            --accent-red: #d9383a;
            --bg-color: #f3f6f9;
            --card-bg: #ffffff;
            --text-main: #1f2937;
            --text-muted: #6b7280;
            --border-color: #d1d5db;
            --focus-ring: rgba(13, 115, 119, 0.25);
            --radius-md: 10px;
            --radius-lg: 16px;
            --shadow-sm: 0 2px 4px rgba(0,0,0,0.04);
            --shadow-md: 0 10px 25px -5px rgba(13, 115, 119, 0.08), 0 8px 10px -6px rgba(0,0,0,0.04);
            --shadow-lg: 0 20px 35px -10px rgba(13, 115, 119, 0.15);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            background-color: var(--bg-color);
            background-image: radial-gradient(#d1e4e5 1px, transparent 1px), radial-gradient(#d1e4e5 1px, #f3f6f9 1px);
            background-size: 40px 40px;
            background-position: 0 0, 20px 20px;
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px 14px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}

        .container {{
            width: 100%;
            max-width: 780px;
            margin: 0 auto;
        }}

        /* Action Toolbar */
        .top-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            gap: 12px;
            flex-wrap: wrap;
        }}

        .badge-info {{
            background: rgba(13, 115, 119, 0.1);
            color: var(--primary-dark);
            font-size: 13px;
            font-weight: 700;
            padding: 7px 16px;
            border-radius: 20px;
            border: 1px solid rgba(13, 115, 119, 0.25);
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .btn-group {{
            display: flex;
            gap: 10px;
        }}

        .btn-tool {{
            padding: 8px 16px;
            font-size: 13.5px;
            border-radius: 8px;
            cursor: pointer;
            border: 1px solid #cbd5e1;
            background: #ffffff;
            color: #334155;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
            font-weight: 600;
            box-shadow: var(--shadow-sm);
        }}

        .btn-tool:hover {{
            background: #f8fafc;
            border-color: var(--primary);
            color: var(--primary);
            transform: translateY(-1px);
        }}

        /* Main Form Card */
        .card {{
            background: var(--card-bg);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            border: 1px solid rgba(226, 232, 240, 0.9);
            overflow: hidden;
            position: relative;
        }}

        .card::before {{
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            left: 0;
            height: 6px;
            background: linear-gradient(90deg, #109153 0%, #109153 33%, #ffffff 33%, #ffffff 66%, #d9383a 66%, #d9383a 100%);
        }}

        /* Header Section */
        .form-header {{
            padding: 32px 28px 24px;
            text-align: center;
            border-bottom: 1px solid #edf2f7;
            position: relative;
        }}

        .logo-wrapper {{
            width: 140px;
            height: 140px;
            margin: 0 auto 16px;
            position: relative;
            background: #ffffff;
            border-radius: 50%;
            padding: 8px;
            box-shadow: 0 4px 18px rgba(13, 115, 119, 0.12);
            border: 2px dashed rgba(13, 115, 119, 0.35);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .logo-wrapper img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}

        .form-title {{
            font-size: 23px;
            font-weight: 800;
            color: #074b4e;
            margin-bottom: 8px;
            line-height: 1.4;
        }}

        .form-subtext {{
            color: var(--text-muted);
            font-size: 15px;
            max-width: 580px;
            margin: 0 auto;
            line-height: 1.7;
            font-weight: 500;
        }}

        .guide-alert {{
            margin: 20px 28px 0;
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            color: #065f46;
            padding: 12px 18px;
            border-radius: 10px;
            font-size: 13.5px;
            display: flex;
            align-items: center;
            gap: 10px;
            line-height: 1.6;
        }}

        /* Form Body */
        .form-body {{
            padding: 28px;
        }}

        .form-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px 24px;
        }}

        .form-group {{
            display: flex;
            flex-direction: column;
            gap: 7px;
        }}

        .form-group.col-span-2 {{
            grid-column: span 2;
        }}

        .form-label {{
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 5px;
        }}

        .form-label .num {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 22px;
            height: 22px;
            background: #f1f5f9;
            color: var(--primary);
            border-radius: 6px;
            font-size: 12px;
            font-weight: 700;
            margin-left: 2px;
        }}

        .form-label .required {{
            color: var(--accent-red);
            font-size: 16px;
        }}

        .form-label .label-badge {{
            font-size: 11px;
            background: #f3f4f6;
            color: #64748b;
            padding: 2px 7px;
            border-radius: 6px;
            margin-right: auto;
            font-weight: normal;
        }}

        .input-wrapper {{
            position: relative;
            display: flex;
            align-items: center;
        }}

        .input-control {{
            width: 100%;
            height: 48px;
            padding: 0 16px;
            border: 1.5px solid var(--border-color);
            border-radius: var(--radius-md);
            font-size: 14.5px;
            color: var(--text-main);
            background: #fbfcfe;
            transition: all 0.2s ease;
            outline: none;
        }}

        .input-control:hover {{
            border-color: #94a3b8;
            background: #ffffff;
        }}

        .input-control:focus {{
            border-color: var(--primary);
            background: #ffffff;
            box-shadow: 0 0 0 4px var(--focus-ring);
        }}

        .input-control.is-invalid {{
            border-color: var(--accent-red);
            background: #fff8f8;
        }}

        .input-control.is-invalid:focus {{
            box-shadow: 0 0 0 4px rgba(217, 56, 58, 0.15);
        }}

        textarea.input-control {{
            height: auto;
            min-height: 85px;
            padding: 12px 16px;
            resize: vertical;
            line-height: 1.6;
        }}

        .date-row {{
            display: grid;
            grid-template-columns: 1fr 1.3fr 1.2fr;
            gap: 8px;
        }}

        .error-message {{
            color: var(--accent-red);
            font-size: 12px;
            margin-top: 3px;
            display: none;
            font-weight: 500;
        }}

        .is-invalid ~ .error-message,
        .input-control.is-invalid + .error-message {{
            display: block;
        }}

        /* Form Actions */
        .form-actions {{
            margin-top: 30px;
            padding-top: 22px;
            border-top: 1px solid #f1f5f9;
            display: flex;
            justify-content: flex-end;
            gap: 12px;
        }}

        .btn-submit {{
            background: linear-gradient(135deg, #0d7377 0%, #074b4e 100%);
            color: #ffffff;
            border: none;
            padding: 13px 36px;
            font-size: 16px;
            font-weight: 700;
            border-radius: var(--radius-md);
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(13, 115, 119, 0.35);
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 10px;
        }}

        .btn-submit:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(13, 115, 119, 0.45);
        }}

        .btn-submit:active {{
            transform: translateY(0);
        }}

        .btn-reset {{
            background: #f8fafc;
            color: #475569;
            border: 1px solid #cbd5e1;
            padding: 13px 24px;
            font-size: 15px;
            font-weight: 600;
            border-radius: var(--radius-md);
            cursor: pointer;
            transition: all 0.2s;
        }}

        .btn-reset:hover {{
            background: #f1f5f9;
            color: #1e293b;
        }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(4px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
        }}

        .modal-overlay.active {{
            display: flex;
        }}

        .modal-card {{
            background: #ffffff;
            border-radius: 20px;
            max-width: 480px;
            width: 100%;
            padding: 32px 26px;
            text-align: center;
            box-shadow: var(--shadow-lg);
            animation: modalIn 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }}

        @keyframes modalIn {{
            from {{ opacity: 0; transform: scale(0.92) translateY(10px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        .modal-icon {{
            width: 66px;
            height: 66px;
            background: #dcfce7;
            color: #16a34a;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 32px;
            margin: 0 auto 16px;
        }}

        .modal-title {{
            font-size: 20px;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 8px;
        }}

        .modal-desc {{
            font-size: 14px;
            color: #64748b;
            line-height: 1.7;
            margin-bottom: 20px;
        }}

        .tracking-box {{
            background: #f8fafc;
            border: 1px dashed #cbd5e1;
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 22px;
        }}

        .tracking-code {{
            font-family: monospace;
            font-size: 22px;
            font-weight: 800;
            color: var(--primary);
            letter-spacing: 2px;
        }}

        /* Admin Records Table */
        .records-section {{
            margin-top: 28px;
            background: #ffffff;
            border-radius: var(--radius-lg);
            padding: 22px;
            box-shadow: var(--shadow-sm);
            border: 1px solid #e2e8f0;
        }}

        .records-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }}

        .records-title {{
            font-size: 15.5px;
            font-weight: 700;
            color: #1e293b;
        }}

        .table-responsive {{
            overflow-x: auto;
        }}

        table.records-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: right;
        }}

        table.records-table th {{
            background: #f8fafc;
            padding: 10px 12px;
            color: #475569;
            font-weight: 600;
            border-bottom: 1.5px solid #e2e8f0;
            white-space: nowrap;
        }}

        table.records-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #f1f5f9;
            color: #334155;
            white-space: nowrap;
        }}

        /* PRINT STYLES FOR A4 FORM */
        .print-only {{
            display: none;
        }}

        @media print {{
            @page {{
                size: A4 portrait;
                margin: 12mm 15mm;
            }}

            body {{
                background: none !important;
                padding: 0 !important;
                margin: 0 !important;
                color: #000 !important;
                -webkit-print-color-adjust: exact;
                print-color-adjust: exact;
            }}

            .top-bar, .form-actions, .records-section, .btn-group, .guide-alert, .modal-overlay {{
                display: none !important;
            }}

            .container {{
                max-width: 100% !important;
                width: 100% !important;
            }}

            .card {{
                box-shadow: none !important;
                border: 2px solid #222 !important;
                border-radius: 8px !important;
            }}

            .card::before {{
                display: none !important;
            }}

            .form-header {{
                padding: 12px 18px 10px !important;
                border-bottom: 2px solid #222 !important;
                display: flex !important;
                align-items: center !important;
                justify-content: space-between !important;
                text-align: right !important;
            }}

            .header-info {{
                flex: 1;
            }}

            .logo-wrapper {{
                width: 85px !important;
                height: 85px !important;
                margin: 0 15px !important;
                border: none !important;
                box-shadow: none !important;
                padding: 0 !important;
            }}

            .form-title {{
                font-size: 17px !important;
                color: #000 !important;
                margin-bottom: 3px !important;
            }}

            .form-subtext {{
                font-size: 12px !important;
                color: #333 !important;
            }}

            .print-meta {{
                display: block !important;
                font-size: 11px !important;
                text-align: left !important;
                line-height: 1.8 !important;
                min-width: 160px !important;
            }}

            .form-body {{
                padding: 16px 20px !important;
            }}

            .form-grid {{
                gap: 14px 18px !important;
            }}

            .form-label {{
                font-size: 13px !important;
                color: #000 !important;
                margin-bottom: 2px !important;
            }}

            .form-label .label-badge {{
                display: none !important;
            }}

            .input-control {{
                border: 1px solid #555 !important;
                background: #fff !important;
                height: 38px !important;
                border-radius: 4px !important;
                color: #000 !important;
                font-size: 13px !important;
                padding: 0 10px !important;
            }}

            textarea.input-control {{
                min-height: 55px !important;
            }}

            .print-signatures {{
                display: flex !important;
                justify-content: space-between !important;
                margin-top: 30px !important;
                padding-top: 15px !important;
                border-top: 1px dashed #666 !important;
            }}

            .sig-box {{
                width: 46%;
                text-align: center;
                font-size: 12px;
                line-height: 2.3;
                border: 1px solid #ddd;
                padding: 10px;
                border-radius: 6px;
            }}
        }}

        @media (max-width: 640px) {{
            .form-grid {{
                grid-template-columns: 1fr;
                gap: 16px;
            }}
            .form-group.col-span-2 {{
                grid-column: span 1;
            }}
            .form-header {{
                padding: 24px 16px 16px;
            }}
            .form-body {{
                padding: 20px 16px;
            }}
            .top-bar {{
                flex-direction: column;
                align-items: stretch;
            }}
            .btn-group {{
                justify-content: space-between;
            }}
        }}
    </style>
</head>
<body>

    <div class="container">
        <!-- Top Toolbar -->
        <div class="top-bar">
            <span class="badge-info">
                <span>🌟</span>
                <span>فرم اختصاصی پذیرفته‌شدگان کانون شهید کاظمی آشتیانی</span>
            </span>
            <div class="btn-group">
                <button type="button" class="btn-tool" onclick="printBlankForm()">
                    <span>🖨️</span>
                    <span>چاپ فرم خام (A4 کاغذی)</span>
                </button>
                <button type="button" class="btn-tool" onclick="exportToCSV()">
                    <span>📥</span>
                    <span>خروجی اکسل (CSV)</span>
                </button>
            </div>
        </div>

        <!-- Main Registration Form Card -->
        <div class="card" id="printableCard">
            <!-- Header -->
            <div class="form-header">
                <div class="header-info">
                    <h1 class="form-title">فرم ثبت‌نام پذیرفته‌شدگان آزمون ورودی</h1>
                    <p class="form-subtext">کانون نخبه‌پروری دانشمند شهید کاظمی آشتیانی</p>
                </div>
                
                <div class="logo-wrapper">
                    <img src="data:image/jpeg;base64,{logo_b64}" alt="لوگوی کانون نخبه‌پروری دانشمند شهید کاظمی آشتیانی">
                </div>

                <div class="print-meta print-only">
                    <div><strong>شماره پرونده:</strong> ....................</div>
                    <div><strong>تاریخ پذیرش:</strong> ..... / ..... / ۱۴۰...</div>
                    <div><strong>محل الصاق عکس ۴×۳</strong></div>
                </div>
            </div>

            <div class="guide-alert">
                <span style="font-size: 18px;">ℹ️</span>
                <span>داوطلب نخبه گرامی؛ خواهشمند است مشخصات هویتی و تحصیلی خود را با دقت تمام و دقیقاً مطابق با اسناد سجلی (شناسنامه) تکمیل فرمایید.</span>
            </div>

            <!-- Form -->
            <form id="registrationForm" class="form-body" onsubmit="handleFormSubmit(event)" novalidate>
                <div class="form-grid">
                    
                    <!-- 1. نام و نام خانوادگی -->
                    <div class="form-group">
                        <label class="form-label" for="fullName">
                            <span class="num">۱</span>
                            <span>نام و نام خانوادگی</span>
                            <span class="required">*</span>
                            <span class="label-badge">مطابق شناسنامه</span>
                        </label>
                        <div class="input-wrapper">
                            <input type="text" id="fullName" name="fullName" class="input-control" placeholder="مثال: علی رضایی" required>
                        </div>
                        <span class="error-message">لطفاً نام و نام خانوادگی را وارد فرمایید.</span>
                    </div>

                    <!-- 2. نام پدر -->
                    <div class="form-group">
                        <label class="form-label" for="fatherName">
                            <span class="num">۲</span>
                            <span>نام پدر</span>
                            <span class="required">*</span>
                        </label>
                        <div class="input-wrapper">
                            <input type="text" id="fatherName" name="fatherName" class="input-control" placeholder="مثال: محمد" required>
                        </div>
                        <span class="error-message">لطفاً نام پدر را وارد فرمایید.</span>
                    </div>

                    <!-- 3. کد ملی -->
                    <div class="form-group">
                        <label class="form-label" for="nationalCode">
                            <span class="num">۳</span>
                            <span>کد ملی</span>
                            <span class="required">*</span>
                            <span class="label-badge">۱۰ رقمی بدون خط تیره</span>
                        </label>
                        <div class="input-wrapper">
                            <input type="tel" id="nationalCode" name="nationalCode" class="input-control" placeholder="مثال: 0012345678" maxlength="10" required>
                        </div>
                        <span class="error-message" id="nationalCodeError">کد ملی باید یک عدد ۱۰ رقمی معتبر باشد.</span>
                    </div>

                    <!-- 4. تاریخ تولد -->
                    <div class="form-group">
                        <label class="form-label">
                            <span class="num">۴</span>
                            <span>تاریخ تولد (هجری شمسی)</span>
                            <span class="required">*</span>
                        </label>
                        <div class="date-row">
                            <select id="birthDay" name="birthDay" class="input-control" required>
                                <option value="" disabled selected>روز</option>
                            </select>
                            <select id="birthMonth" name="birthMonth" class="input-control" required>
                                <option value="" disabled selected>ماه</option>
                                <option value="فروردین">فروردین</option>
                                <option value="اردیبهشت">اردیبهشت</option>
                                <option value="خرداد">خرداد</option>
                                <option value="تیر">تیر</option>
                                <option value="مرداد">مرداد</option>
                                <option value="شهریور">شهریور</option>
                                <option value="مهر">مهر</option>
                                <option value="آبان">آبان</option>
                                <option value="آذر">آذر</option>
                                <option value="دی">دی</option>
                                <option value="بهمن">بهمن</option>
                                <option value="اسفند">اسفند</option>
                            </select>
                            <select id="birthYear" name="birthYear" class="input-control" required>
                                <option value="" disabled selected>سال</option>
                            </select>
                        </div>
                        <span class="error-message" id="birthDateError">لطفاً روز، ماه و سال تولد را کامل انتخاب کنید.</span>
                    </div>

                    <!-- 5. شماره تماس -->
                    <div class="form-group">
                        <label class="form-label" for="phone">
                            <span class="num">۵</span>
                            <span>شماره تماس (تلفن همراه)</span>
                            <span class="required">*</span>
                            <span class="label-badge">جهت اطلاع‌رسانی پیامکی</span>
                        </label>
                        <div class="input-wrapper">
                            <input type="tel" id="phone" name="phone" class="input-control" placeholder="مثال: 09123456789" maxlength="11" required>
                        </div>
                        <span class="error-message" id="phoneError">شماره موبایل ۱۱ رقمی معتبر (شروع با ۰۹) وارد کنید.</span>
                    </div>

                    <!-- 6. نام مدرسه -->
                    <div class="form-group">
                        <label class="form-label" for="school">
                            <span class="num">۶</span>
                            <span>نام مدرسه کنونی</span>
                            <span class="required">*</span>
                        </label>
                        <div class="input-wrapper">
                            <input type="text" id="school" name="school" class="input-control" placeholder="مثال: دبیرستان استعدادهای درخشان شهید بهشتی" required>
                        </div>
                        <span class="error-message">لطفاً نام مدرسه فعلی خود را قید فرمایید.</span>
                    </div>

                    <!-- 7. پایه تحصیلی -->
                    <div class="form-group col-span-2">
                        <label class="form-label" for="grade">
                            <span class="num">۷</span>
                            <span>پایه تحصیلی پذیرفته‌شده</span>
                            <span class="required">*</span>
                            <span class="label-badge">برای سال تحصیلی جدید</span>
                        </label>
                        <select id="grade" name="grade" class="input-control" required>
                            <option value="" disabled selected>پایه تحصیلی را انتخاب نمایید...</option>
                            <option value="پایه ششم ابتدایی">پایه ششم ابتدایی</option>
                            <option value="پایه هفتم (دوره اول متوسطه)">پایه هفتم (دوره اول متوسطه)</option>
                            <option value="پایه هشتم (دوره اول متوسطه)">پایه هشتم (دوره اول متوسطه)</option>
                            <option value="پایه نهم (دوره اول متوسطه)">پایه نهم (دوره اول متوسطه)</option>
                            <option value="پایه دهم (دوره دوم متوسطه)">پایه دهم (دوره دوم متوسطه)</option>
                            <option value="پایه یازدهم (دوره دوم متوسطه)">پایه یازدهم (دوره دوم متوسطه)</option>
                            <option value="پایه دوازدهم (دوره دوم متوسطه)">پایه دوازدهم (دوره دوم متوسطه)</option>
                        </select>
                        <span class="error-message">لطفاً پایه تحصیلی را انتخاب فرمایید.</span>
                    </div>

                    <!-- 8. آدرس -->
                    <div class="form-group col-span-2">
                        <label class="form-label" for="address">
                            <span class="num">۸</span>
                            <span>نشانی کامل محل سکونت</span>
                            <span class="required">*</span>
                            <span class="label-badge">همراه با کد پستی (اختیاری)</span>
                        </label>
                        <textarea id="address" name="address" class="input-control" placeholder="استان، شهر، خیابان اصلی، خیابان فرعی، کوچه، پلاک، طبقه و واحد..." required></textarea>
                        <span class="error-message">لطفاً نشانی کامل محل سکونت را یادداشت فرمایید.</span>
                    </div>

                </div>

                <!-- Print Signature Section (Only shows in A4 paper print) -->
                <div class="print-signatures print-only">
                    <div class="sig-box">
                        <strong>امضاء و اثر انگشت پذیرفته‌شده / ولی دانش‌آموز:</strong>
                        <p>اینجانب صحت تمامی اطلاعات قیدشده در این فرم را تایید می‌نمایم.</p>
                        <br>
                        <div>تاریخ و امضاء: .......................................</div>
                    </div>
                    <div class="sig-box">
                        <strong>مهر و امضاء کارشناس ثبت‌نام کانون:</strong>
                        <p>پرونده داوطلب بررسی و قبولی در آزمون ورودی محرز گردید.</p>
                        <br>
                        <div>نام مسئول و امضاء: ..................................</div>
                    </div>
                </div>

                <!-- Form Action Buttons -->
                <div class="form-actions">
                    <button type="button" class="btn-reset" onclick="resetForm()">پاک کردن فرم</button>
                    <button type="submit" class="btn-submit">
                        <span>ثبت نهایی اطلاعات</span>
                        <span>✓</span>
                    </button>
                </div>
            </form>
        </div>

        <!-- Registered Submissions Table (Local storage admin view) -->
        <div class="records-section" id="recordsBox" style="display: none;">
            <div class="records-header">
                <h3 class="records-title">📋 اسامی ثبت‌نام شده در این دستگاه (<span id="recordCount">0</span> نفر)</h3>
                <button type="button" class="btn-tool" onclick="clearAllRecords()" style="color: #dc2626; border-color: #fecaca;">
                    🗑️ پاک کردن حافظه موقت
                </button>
            </div>
            <div class="table-responsive">
                <table class="records-table">
                    <thead>
                        <tr>
                            <th>ردیف</th>
                            <th>نام و نام خانوادگی</th>
                            <th>نام پدر</th>
                            <th>کد ملی</th>
                            <th>پایه تحصیلی</th>
                            <th>تلفن تماس</th>
                            <th>کد رهگیری</th>
                        </tr>
                    </thead>
                    <tbody id="recordsTableBody">
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- Confirmation Modal -->
    <div class="modal-overlay" id="successModal">
        <div class="modal-card">
            <div class="modal-icon">✓</div>
            <h2 class="modal-title">ثبت‌نام با موفقیت انجام شد</h2>
            <p class="modal-desc">
                اطلاعات داوطلب در سیستم ثبت گردید. لطفاً کد رهگیری زیر را جهت پیگیری‌های بعدی یادداشت یا رسید چاپی را دریافت فرمایید.
            </p>
            <div class="tracking-box">
                <div style="font-size: 13px; color: #64748b; margin-bottom: 4px;">کد رهگیری پذیرفته‌شده:</div>
                <div class="tracking-code" id="modalTrackingCode">KA-140401</div>
            </div>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button type="button" class="btn-tool" style="background: var(--primary); color: #fff; padding: 10px 20px; border: none;" onclick="printRegisteredReceipt()">
                    🖨️ چاپ رسید پرونده
                </button>
                <button type="button" class="btn-tool" style="padding: 10px 20px;" onclick="closeModal()">
                    بستن پنجره
                </button>
            </div>
        </div>
    </div>

    <script>
        // Populate Persian date selectors
        const daySelect = document.getElementById('birthDay');
        for (let i = 1; i <= 31; i++) {{
            const opt = document.createElement('option');
            opt.value = i;
            opt.textContent = i;
            daySelect.appendChild(opt);
        }}

        const yearSelect = document.getElementById('birthYear');
        const currentShamsiYear = 1404;
        for (let y = currentShamsiYear - 8; y >= currentShamsiYear - 20; y--) {{
            const opt = document.createElement('option');
            opt.value = y;
            opt.textContent = y;
            yearSelect.appendChild(opt);
        }}

        // Convert Persian/Arabic digits to English digits
        function toEnglishDigits(str) {{
            if (!str) return '';
            return str.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d))
                      .replace(/[٠-٩]/g, d => '٠١٢٣٤٥٦٧٨٩'.indexOf(d));
        }}

        // Iranian National Code Validator (Modulus 11 algorithm)
        function isValidIranianNationalCode(input) {{
            const code = toEnglishDigits(input).trim();
            if (!/^\d{{10}}$/.test(code)) return false;
            if (/^(\d)\\1{{9}}$/.test(code)) return false; // like 0000000000 or 1111111111

            const check = parseInt(code[9]);
            let sum = 0;
            for (let i = 0; i < 9; i++) {{
                sum += parseInt(code[i]) * (10 - i);
            }}
            const remainder = sum % 11;
            return (remainder < 2 && check === remainder) || (remainder >= 2 && check === (11 - remainder));
        }}

        // Iranian Mobile Validator
        function isValidIranianMobile(input) {{
            const phone = toEnglishDigits(input).trim();
            return /^09\\d{{9}}$/.test(phone);
        }}

        // Load records from localStorage
        function loadRecords() {{
            const records = JSON.parse(localStorage.getItem('kazemi_ashtiani_records') || '[]');
            const tbody = document.getElementById('recordsTableBody');
            const box = document.getElementById('recordsBox');
            const countSpan = document.getElementById('recordCount');

            countSpan.textContent = records.length;
            if (records.length === 0) {{
                box.style.display = 'none';
                return;
            }}

            box.style.display = 'block';
            tbody.innerHTML = '';
            records.forEach((rec, idx) => {{
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${{idx + 1}}</td>
                    <td><strong>${{rec.fullName}}</strong></td>
                    <td>${{rec.fatherName}}</td>
                    <td dir="ltr" style="text-align: right;">${{rec.nationalCode}}</td>
                    <td>${{rec.grade}}</td>
                    <td dir="ltr" style="text-align: right;">${{rec.phone}}</td>
                    <td><span style="font-family: monospace; background: #e0f2fe; color: #0369a1; padding: 3px 8px; border-radius: 4px; font-weight: 700;">${{rec.trackingCode}}</span></td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Form Submit Handler
        async function handleFormSubmit(event) {{
            event.preventDefault();

            const fullName = document.getElementById('fullName').value.trim();
            const fatherName = document.getElementById('fatherName').value.trim();
            const nationalCode = toEnglishDigits(document.getElementById('nationalCode').value).trim();
            const birthDay = document.getElementById('birthDay').value;
            const birthMonth = document.getElementById('birthMonth').value;
            const birthYear = document.getElementById('birthYear').value;
            const phone = toEnglishDigits(document.getElementById('phone').value).trim();
            const school = document.getElementById('school').value.trim();
            const grade = document.getElementById('grade').value;
            const address = document.getElementById('address').value.trim();

            let hasError = false;

            // Reset error highlights
            document.querySelectorAll('.input-control').forEach(el => el.classList.remove('is-invalid'));

            if (!fullName) {{
                document.getElementById('fullName').classList.add('is-invalid');
                hasError = true;
            }}
            if (!fatherName) {{
                document.getElementById('fatherName').classList.add('is-invalid');
                hasError = true;
            }}
            if (!isValidIranianNationalCode(nationalCode)) {{
                document.getElementById('nationalCode').classList.add('is-invalid');
                hasError = true;
            }}
            if (!birthDay || !birthMonth || !birthYear) {{
                document.getElementById('birthDay').classList.add('is-invalid');
                document.getElementById('birthMonth').classList.add('is-invalid');
                document.getElementById('birthYear').classList.add('is-invalid');
                hasError = true;
            }}
            if (!isValidIranianMobile(phone)) {{
                document.getElementById('phone').classList.add('is-invalid');
                hasError = true;
            }}
            if (!school) {{
                document.getElementById('school').classList.add('is-invalid');
                hasError = true;
            }}
            if (!grade) {{
                document.getElementById('grade').classList.add('is-invalid');
                hasError = true;
            }}
            if (!address) {{
                document.getElementById('address').classList.add('is-invalid');
                hasError = true;
            }}

            if (hasError) {{
                const firstInvalid = document.querySelector('.is-invalid');
                if (firstInvalid) firstInvalid.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                return;
            }}

            // Generate unique tracking code
            let trackingCode = 'KA-' + Math.floor(100000 + Math.random() * 900000);
            const record = {{
                id: Date.now(),
                trackingCode,
                fullName,
                fatherName,
                nationalCode,
                birthDate: `${{birthYear}}/${{birthMonth}}/${{birthDay}}`,
                phone,
                school,
                grade,
                address,
                submittedAt: new Date().toLocaleDateString('fa-IR')
            }};

            // Try sending to server if hosted
            try {{
                const resp = await fetch('api/register', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify(record)
                }});
                const result = await resp.json();
                if (resp.status === 409) {{
                    alert(result.message);
                    return;
                }}
                if (result.trackingCode) {{
                    trackingCode = result.trackingCode;
                    record.trackingCode = trackingCode;
                }}
            }} catch (e) {{
                // Fallback for static file / local offline preview
                console.log('Running in local/offline mode, stored in browser.');
            }}

            const records = JSON.parse(localStorage.getItem('kazemi_ashtiani_records') || '[]');
            records.unshift(record);
            localStorage.setItem('kazemi_ashtiani_records', JSON.stringify(records));

            // Show confirmation modal
            document.getElementById('modalTrackingCode').textContent = trackingCode;
            document.getElementById('successModal').classList.add('active');
            loadRecords();
        }}

        function closeModal() {{
            document.getElementById('successModal').classList.remove('active');
            resetForm();
        }}

        function resetForm() {{
            document.getElementById('registrationForm').reset();
            document.querySelectorAll('.input-control').forEach(el => el.classList.remove('is-invalid'));
        }}

        function clearAllRecords() {{
            if (confirm('آیا از حذف کلیه ثبت‌نام‌های ذخیره‌شده در این دستگاه اطمینان دارید؟')) {{
                localStorage.removeItem('kazemi_ashtiani_records');
                loadRecords();
            }}
        }}

        // Export to Excel / CSV with UTF-8 BOM
        function exportToCSV() {{
            const records = JSON.parse(localStorage.getItem('kazemi_ashtiani_records') || '[]');
            if (records.length === 0) {{
                alert('هنوز هیچ رکوردی ثبت نشده است.');
                return;
            }}

            let csvContent = "\\uFEFF"; // UTF-8 BOM
            csvContent += "کد رهگیری,نام و نام خانوادگی,نام پدر,کد ملی,تاریخ تولد,شماره تماس,نام مدرسه,پایه تحصیلی,آدرس,تاریخ ثبت\\n";

            records.forEach(r => {{
                const cleanAddress = r.address.replace(/[\\r\\n]+/g, ' ');
                const row = [
                    `"${{r.trackingCode}}"`,
                    `"${{r.fullName}}"`,
                    `"${{r.fatherName}}"`,
                    `"${{r.nationalCode}}"`,
                    `"${{r.birthDate}}"`,
                    `"${{r.phone}}"`,
                    `"${{r.school}}"`,
                    `"${{r.grade}}"`,
                    `"${{cleanAddress}}"`,
                    `"${{r.submittedAt}}"`
                ];
                csvContent += row.join(",") + "\\n";
            }});

            const blob = new Blob([csvContent], {{ type: 'text/csv;charset=utf-8;' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.setAttribute("href", url);
            link.setAttribute("download", `ثبت_نام_کانون_کاظمی_آشتیانی_${{Date.now()}}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }}

        // Print Blank Form for Paper Filling
        function printBlankForm() {{
            const currentVals = {{
                fullName: document.getElementById('fullName').value,
                fatherName: document.getElementById('fatherName').value,
                nationalCode: document.getElementById('nationalCode').value,
                phone: document.getElementById('phone').value,
                school: document.getElementById('school').value,
                address: document.getElementById('address').value
            }};

            resetForm();
            window.print();

            document.getElementById('fullName').value = currentVals.fullName;
            document.getElementById('fatherName').value = currentVals.fatherName;
            document.getElementById('nationalCode').value = currentVals.nationalCode;
            document.getElementById('phone').value = currentVals.phone;
            document.getElementById('school').value = currentVals.school;
            document.getElementById('address').value = currentVals.address;
        }}

        function printRegisteredReceipt() {{
            closeModal();
            window.print();
        }}

        window.addEventListener('DOMContentLoaded', loadRecords);
    </script>
</body>
</html>
"""

output_path = os.path.join(dir_path, "index.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated successfully at", output_path)
