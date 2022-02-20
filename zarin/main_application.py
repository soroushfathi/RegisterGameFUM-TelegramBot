# -*- coding: utf-8 -*-
#     Github.com/Rasooll
from bottle import route, template, static_file, request, redirect, get, run
import pymysql.cursors
from zeep import Client
from config import *


# تابعی برای ایجاد اتصال به دیتابیس
def MakeMySqlConncetion():
    global connection
    connection = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_NAME, charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')  # آدرس استفاده از وب گیت زرین پال
error_list = {  # لیست خطاهای زرین پال
    '100': 'عملیات با موفقیت انجام گردیده است.',
    '101': 'عملیات پرداخت موفق بوده و قبلا صحت تراکنش بررسی شده است',
    '-1': 'اطلاعات ارسال شده ناقص است',
    '-2': 'مرچنت کد و یا آی‌پی آدرس پذیرنده صحیح نیست',
    '-3': 'باتوجه به محدودیت های شاپرک امکان پرداخت با رقم درخواست شده میسر نمی‌باشد.',
    '-4': 'سطح تایید پذیرنده پایین تر از سطح نقره‌ای است',
    '-11': 'درخواست مورد نظر یافت نشد',
    '-12': 'امکان ویرایش درخواست میسر نمی‌باشد',
    '-21': 'هیچ نوع عملیات مالی برای این تراکنش یافت نشد',
    '-22': 'تراکنش ناموفق می‌باشد',
    '-33': 'رقم تراکنش با رقم پرداخت شده مطابقت ندارد',
    '-34': 'سقف تقسیم تراکنش از لحاظ تعداد یا رقم عبور نموده است',
    '-40': 'اجازه دسترسی به متد مربوطه وجود ندارد',
    '-41': 'اطلاعات ارسال شده مربوط به AdditionalData غیرمعتبر می‌باشد',
    '-42': 'مدت زمان معتبر طول عمر شناسه پرداخت باید بین 30 دقیقه تا 45 روز ‌باشد',
    '-54': 'درخواست مورد نظر آرشیو شده است'
}


@route('/<:re:[\/static$]+>/<filename>')  # این بخش برای ایجاد فایل های استاتیک است و نباید ویرایش شود
def server_static(filename):
    return static_file(filename, root='./static')


@route('https://fumgame.ir/')  # صفحه اصلی سایت
@route('/<:re:[\/$]+>')
def index():
    pm = {'index': INDEX_URL}
    return template('./tpl/main.tpl', pm)


@route('https://fumgame.ir/<:re:[\/install$]+>')  # صفحه مربوط به تنظیمات سایت
def install_func():
    try:
        MakeMySqlConncetion()
        with connection.cursor() as cursor:
            sql = '''CREATE TABLE IF NOT EXISTS info (
                name TEXT,
                email TEXT,
                price TEXT,
                description TEXT,
                authority TEXT,
                refID TEXT,
                status TEXT
                )CHARSET=utf8 COLLATE=utf8_bin;'''
            cursor.execute(sql)
        connection.commit()
    finally:  # در اینجا جداول مورد نیاز را در دیتابیس ایجاد می‌شود
        connection.close()
        pm = {'index': INDEX_URL, 'title': 'پایان فرایند تنظیمات',
              'content': 'فرآیند ایجاد جداول بانک اطلاعاتی به پایان رسید.'}
        return template('./tpl/success.tpl', pm)


# این بخش برای پردازش درخواست واریز وجه است
@get('https://fumgame.ir/<:re:[\/request$]+>')
def makerequest():
    # گرفتن اطلاعات از طریق متد GET
    name = request.query.name
    email = request.GET.get("email")
    price = request.GET.get("price")
    description = request.query.description  # تفاوت به دلیل پشتیبانی از یونیکد و زبان فارسی است.
    if email and price:
        # ارسال اطلاعات به زرین پال برای دریافت شماره تراکنش جهت پرداخت
        result = client.service.PaymentRequest(MERCHANT, price, description, email, '', CallbackURL)
        if result.Status == 100:
            authority = str(result.Authority)
            try:
                MakeMySqlConncetion()
                with connection.cursor() as cursor:
                    # ثبت اطلاعات پرداخت کننده در دیتابیس
                    sql = "INSERT INTO info (name, email, price, description, authority) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(sql, (name, email, price, description, authority))
                connection.commit()
            finally:
                connection.close()  # قطع اتصال با دیتابیس
                # منتقل کردن کاربر به صفحه پرداخت
                redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
        else:  # نمایش خطا در صورت وجود
            errtext = {'index': INDEX_URL, 'errorText': error_list[str(result.Status)]}
            return template('./tpl/error.tpl', errtext)
    else:
        # نمایش خطا در صورت ارسال درخواست خالی و بدون اطلاعات
        # توحه: مقدار بازگشتی ۲۰۰ است و نمیتوان از طریق ای‌پی‌آی استفاده کرد.
        errtext = {'index': INDEX_URL, 'errorText': 'هیچ اطلاعاتی ارسال نشده است'}
        return template('./tpl/error.tpl', errtext)


# بازگشت کاربر و بررسی وضعیت پرداخت
@get('/<:re:[\/verify$]+>')
def verify_func():
    if request.GET.get('Status') == 'OK':
        authority = str(request.GET['Authority'])
        MakeMySqlConncetion()
        with connection.cursor() as cursor:
            sql = "SELECT price,authority FROM info WHERE authority=%s"
            cursor.execute(sql, (authority,))  # دریافت اطلاعات از دیتابیس
            sqldata = cursor.fetchone()
            price = int(sqldata['price'])  # دریافت مبلغ تراکنش
        # ارسال درخواست به زرین پال برای بررسی وضعیت تراکنش
        result = client.service.PaymentVerification(MERCHANT, authority, price)
        if result.Status == 100:  # درصورت موفقیت آمیز بودن تراکنش
            with connection.cursor() as cursor:
                sql2 = "UPDATE info SET status='OK',refID=%s WHERE authority=%s"
                # ثیت وضعیت پرداخت شده در دیتابیس
                cursor.execute(sql2, (str(result.RefID), authority,))
            connection.commit()  # ارسال اطلاعات جدید به دیتابیس
            connection.close()
            pm = {'index': INDEX_URL, 'refID': str(result.RefID)}
            # نمایش صفحه پرداخت موفقیت آمیز به کاربر
            return template('./tpl/payment-ok.tpl', pm)
        elif result.Status == 101:  # نمایش وضعیت تراکنشی که قبلا تایید شده است
            pm = {'index': INDEX_URL, 'title': 'نتیجه بررسی وضعیت پرداخت', 'content': 'پرداخت شما قبلا تایید شده است'}
            return template('./tpl/info.tpl', pm)
        else:  # نمایش خطا به کاربر
            pm = {'index': INDEX_URL, 'errorText': error_list[result.Status]}
            return template('./tpl/error.tpl', pm)
    elif request.GET.get('Status') == 'NOK':  # نمایش خطا در صورت ناموفق بودن تراکنش
        pm = {'index': INDEX_URL, 'errorText': 'تراکنش ناموفق بوده و یا توسط کاربر لغو گردیده است'}
        return template('./tpl/error.tpl', pm)
    else:  # درصورتی که این صفحه مستقیما بدون هیچ درخواستی باز شود این بخش لود می شود.
        pm = {'index': INDEX_URL, 'errorText': 'هیچ تراکنشی انجام نشده است'}
        return template('./tpl/error.tpl', pm)


@route('/<:re:[\/admin$]+>')  # مربوط به صفحه ادمین ، احتمالا در آینده تکمیل می شود
def admin_func():
    pm = {'index': INDEX_URL, 'title': 'در دست طراحی',
          'content': 'بخش مدیریت در نسخه‌های آینده‌ی این اسکریپت اضافه خواهد شد.'}
    return template('./tpl/info.tpl', pm)


'''
 این بخش مربوط به اجرای این برنامه است
 با این دستور برنامه فقط در شبکه داخلی شما در دسترس است
 اگر میخواهید در اینترنت هم از این برنامه بدون نیاز به وب سرور استفاده کنید از دستور زیر استفاده کنید
 run(host='0.0.0.0', port=8080)
'''
run(host='localhost', port=8080)
