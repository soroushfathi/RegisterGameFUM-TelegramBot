from telethon import Button
import re
from asyncio.exceptions import TimeoutError


class Team:
    def __init__(self, name: str, code: int):
        self.name = name
        self.code = code
        self.members = []
        self.memberscount = len(self.members)
        self.statuspay = False
        self.score = 0

    def __str__(self):
        s = '\n'.join(map(str, self.members))
        le = None
        for p in self.members:
            if p.leader:
                le = p
                break
        return '🎛نام تیم: {}\n🀄️کد تیم: {}\n👤سرگروه:\n {}\n👥اعضا:\n{}\n' \
               '🎫وضعیت پرداخت: {}'.format(self.name, self.code, le, s, self.statuspay)


class Player:
    def __init__(self, tc, ci, si, sf, phn, un, n):
        self.teamcode = tc
        self.chatid = ci
        self.studentid = si
        self.studyfield = sf
        self.phonenumber = phn
        self.username = un
        self.name = n
        self.leader = False
        self.activate = False

    def __str__(self):
        return '➖نام: {}، آیدی: {}، رشته تحصیلی: {}، عضویت: {}'.format(self.name, self.username, self.studyfield, self.activate)


salescode20 = ['metal', 'mech', 'esa', 'fumrs', 'nano', 'aerospace', 'IECF', 'omran', 'chemicaleng', 'EESC', 'Fum_or',
               'ssces', 'adyan', 'mahad', 'Quran_hadith', 'feghh', 'tarikh', 'FUPAC', 'ZAMIN', 'Biology', 'physics',
               'CPAFUM', 'FumSaab', 'jobsway', 'esaof', 'management', 'law', 'political', 'accounting', 'Afgh_Studies',
               'vetmedssc', 'vls', 'HHSA', 'CPA', 'biotechVssa', 'saohsofu', 'csllf', 'Arabicliteratures', 'russiandep',
               'AEA_FUM', 'geography', 'sociology_in_ferdowsi', 'stat', 'cs_fum', 'mohitezist', 'shilat', 'Lis',
               'tabiat', 'lis_fum', 'psychology', 'educational_', 'cognitive_science', 'Aupa', 'sport', 'BsE', 'AEA',
               'AAPB', 'Agri_Research', 'horticultural', 'landscape', 'soil_science', 'Moj', 'FST', 'Royan',
               'Samandari', 'AzManBepors', 'Engarium360', 'Mafakher', 'Fumnews', 'fararestan']
salescode25 = ['Game25']
salescode30 = ['Game30']
salescode35 = ['Game35']
messages = {
    'welcome': 'سلام {}👋🏻، به ربات اتاق فرار فردوسی خوش اومدی👽،\n❗️ پیشنهاد میشه قبل از ایجاد تیم راهنمایی مسابقه رو بخونی'
               ' تا در مورد شیوه ثبت نام و برگزاری مسابقه آشنا بشی',
    'sos': '⁉️ راهنمایی:\n💠 شیوه برگزاری مسابقه در کانال اطلاع رسانی میشه\n'
           '\n🔖 آموزش کامل نحوه ثبت نام در هایلایت های <a href="https://www.instagram.com/fumgame/">پیج اینستاگرام انجمن</a> \n'
           '\n🔖اگر با اتاق فرار آشنا نیستین، تو کانالمون مفصل توضیح دادیم\n'
           '\n💬هر گونه سوال و ابهامی داشتین میتونین از ما بپرسین @Fum_Game_PR \n'
           '\n🔴 لطفا حتما حتما توجه کنید که این مسابقه مخصوص دانشجویان دانشگاه فردوسی است و اطلاعات ارسالی شما بررسی میشود'
           ' اگر دانشجوی این دانشگاه نیستید علاوه بر اینکه قادر به شرکت در بازی نبوده، ثبت‌نام شما لغو خواهد شد.',
    'payment': '💰صورت حساب - شما به عنوان نماینده گروه پرداخت رو انجام میدین\nهزینه ثبت نام: {}\nکسر هزینه از کد تخفیف: {}\n-'
               '---------------------------------------------------------------\n'
               'قابل پرداخت: {}\nدرگاه: <a href="{}">لینک پرداخت</a>'
               '\n❗️❗️موقع پرداخت حتما فیلترشکن خاموش باشه',
    'create_team': 'به اتاق فرار فردوسی خوش اومدی👻، تیم \"{}\" با موفقیت ایجاد شد🤠\n این پیامو برای هم تیمی هات بفرست'
                   ' که با لینک، داخل بات استارت بزنن تا عضو گروه بشن\n{}\n'
                   '❕❕بعد از اینکه هریک از هم تیمی هات استارت زدن، پیامی برای تایید یا عدم تایید هم تیمی برات میاد📬\n',
    # https://t.me/FUMGame_bot?start=teamecode
    'login_team': '⚠️درخواست شما برای عضویت در تیم \"{}\" به سرگروه ارسال شد،'
                  'بعد از تایید پیام عضویت برای شما ارسال میشود',
    'request_leader': 'کاربری با نام \'{}\' و آیدی \' {}@ \' درخواست عضویت در تیم را داد',
    'accepted_player': 'عضویتت در تیم توسط سرگروه({}) تایید شد🤠 آرزوی موفقیت برای تیمتون✌🏻\n📌در ضمن داخل کیبورد'
                       ' هم دکمه \'مدیریت تیم\' باز شده',
    'ignored_player': '‼️متاسفانه سرگروه({}) عضویت شما رو تایید نکرد❌',
    'info_accepter_leader': '📂خب اطلاعاتت دریافت شد\n🔶نام: {} 🔶 شماره دانشجویی: {} 🔶 شماره تلفن: {}'
                            ' 🔶 کد تخفیف(حساس ب حروف کوچک و بزرگ): {}\nکل مبلغ: 60000 تومن با کد تخفیف 👈🏻 {} تومن\n'
                            ' اگر اطلاعاتت رو درست وارد کردی و مورد تاییدت هست عبارت \"`تایید میکنم`\"،'
                            'در غیر اینصورت \"`دریافت مجدد`\" رو تایپ کن.(روی عبارت مورد نظر بزن و داخل متنت paste کن)',
    'info_accepter': '📂خب اطلاعاتت دریافت شد\n🔶نام: {} 🔶 شماره دانشجویی: {} 🔶 شماره تلفن: {}\n'
                     'اگر اطلاعاتت رو درست وارد کردی و مورد تاییدت هست عبارت \"`تایید میکنم`\"،'
                     'در غیر اینصورت \"`دریافت مجدد`\" رو تایپ کن.(روی عبارت مورد نظر بزن و داخل متنت paste کن)',
}


async def player_register(conv, sender, leader, bot):
    flg = True
    while flg:
        try:
            await conv.send_message('👤 نام و نام خانوادگی خودت رو وارد کن:')
            name = await conv.get_response()
            await conv.send_message('🆔 شماره دانشجویی خودتون رو(به انگلیسی) وارد کنین :')
            studentid = await conv.get_response()
            studentid = studentid.message
            while (not studentid.isnumeric()) or len(studentid) > 10 or len(studentid) < 6:
                await conv.send_message("🚫شماره دانشجویی معتبر نیست، دوباره وارد کنید")
                studentid = await conv.get_response()
                studentid = studentid.message
            await conv.send_message('🧑🏻‍🎓رشته تحصیلیت رو وارد کن:')
            studyfield = await conv.get_response()
            studyfield = studyfield.message
            but = [[Button.request_phone('Send phone')]]
            await conv.send_message('☎️برای ارتباط و دسترسی بهتر، شماره تلفن رو از دکمه پایین برای ارسال '
                                    'انتخاب کن. یا میتونی به صورت دستی وارد کنی'
                                    '.(لازم به ذکره تمامی اطلاعات محفوظ است)', buttons=but)
            try:
                phonenumber = await conv.get_response()
                phonenumber = phonenumber.media.phone_number
            except AttributeError:
                phonenumber = phonenumber.message
                while not re.match(r"^\s*(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})(?: *x(\d+))?\s*$", phonenumber):
                    await conv.send_message("🚫شماره تلفن معتبر نیست، دوباره وارد کنید")
                    phonenumber = await conv.get_response()
                    phonenumber = phonenumber.message
            salecode = None
            if leader:
                await conv.send_message('🔰کد تخفیف را وارد کنید:\n(اگر کد تخفیف نداری \'ندارم\' رو تایپ کن):',
                                        buttons=Button.clear())
                salecode = await conv.get_response()
                price, sale, totalprice = price_calc(salecode.message)
                await conv.send_message(messages['info_accepter_leader'].format(
                    name.message, studentid, phonenumber, salecode.message, totalprice), buttons=Button.clear())
            else:
                await conv.send_message(messages['info_accepter'].format(name.message, studentid, phonenumber), buttons=Button.clear())
            accepter = await conv.get_response()
            if accepter.message == "تایید میکنم":
                async with bot.action(sender.id, 'typing'):
                    await conv.send_message('✅اطلاعات تایید شد')
                return [sender.id, studentid, studyfield, phonenumber, sender.username, name.message, salecode]
            else:
                await conv.send_message('❌اطلاعات تایید نشد، دوباره اطلاعات رو پر کن')
                flg = True
        except TimeoutError:
            flg = False
            await bot.send_message(sender.id, 'محدودیت زمان یک دقیقه⏰')


def find_team(cid, teams):
    for t in teams:
        for p in t.members:
            if p.chatid == cid:
                return t
    return None


def team_leader(team):
    for p in team.members:
        if p.leader:
            return p
    return None


def is_registerd(cid, players) -> bool:
    all_chatid = [x.chatid for x in players]
    if cid in all_chatid:
        return True
    return False


def is_activate(cid, players) -> bool:
    for p in players:
        if p.chatid == cid and p.activate:
            return True
    return False


def price_calc(salecode):
    price = 60000
    sale = 0
    if salecode in salescode20:
        sale = (price * 2) // 10
    elif salecode in salescode25:
        sale = (price * 25) // 100
    elif salecode in salescode30:
        sale = (price * 3) // 10
    elif salecode in salescode35:
        sale = (price * 35) // 100
    elif salecode == 'sofa' or salecode == 'HDoosti':
        sale = (price * 50) // 100
    elif salecode == 'sfhd':
        sale = (price * 96) // 100
    return [price, sale, price - sale]
