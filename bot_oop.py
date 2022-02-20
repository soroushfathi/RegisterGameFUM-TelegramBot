import asyncio.exceptions
import re
from uuid import uuid4
from telethon import (
    TelegramClient,
    events,
    Button,
)
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import (
    PeerChannel,
    PeerUser,
    PeerChat,
)
from telethon.tl.functions.messages import (
    GetInlineBotResultsRequest,
    SendInlineBotResultRequest,
    SetInlineBotResultsRequest,
    StartBotRequest,
)
import os
from uuid import uuid4
from functions import player_register

bot_token = os.environ["FUMGAME_TOKENBOT"]
api_id = os.environ["0939***5204_apiID"]
api_hash = os.environ["0939***5204_apiHASH"]
bot = TelegramClient('bot', api_id, api_hash)
payurl = 'https://www.fumgame.ir/p/request.php?chatid={}&price={}'

teams = []
players = []
salescode = ''
with open('salescode.txt') as f:
    salescode = [line.rstrip('\n') for line in f]
f.close()

messages = {
    'welcome': 'سلام {}، به ربات اتاق فرار فردوسی خوش اومدی،\n❗️ پیشنهاد میشه قبل از ایجاد تیم راهنمایی مسابقه رو بخونی'
               'تا در مورد شیوه ثبت نام و برگزاری مسابقه آشنا بشی',
    'sos': 'راهنمایی مسابقه',
    'payment': '💰صورت حساب\nهزینه ثبت نام: {}\nکسر هزینه از کد تخفیف: {}\n----------------------------------------\n'
               'قابل پرداخت: {}\nدرگاه: {}',
    'create_team': 'به اتاق فرار فردوسی خوش اومدی👻، تیم \"{}\" با موفقیت ایجاد شد🤠\n هر یک از اعضا باید با لینک زیر'
                   'در بات استارت بزنن تا عضو گروه بشن\n{}\n'
                   '**بعد از اینکه هریک از هم تیمی هات استارت زدن، پیامی برای تایید یا عدم تایید هم تیمی برات میاد\n',
    # https://t.me/FUMGame_bot?start=teamecode
    'login_team': 'درخواست شما برای عضویت در تیم \"{}\" به سرگروه ارسال شد،'
                  'بعد از تایید پیام عضویت برای شما ارسال میشود',
    'request_leader': 'کاربری با نام {} درخواست عضویت در تیم را داد، در صورت تایید، عضو تیم خواهد شد',
    'accepted_player': 'عضویت شما در تیم توسط {} تایید شد',
    'ignored_player': 'متاسفانه عضویت شما در تیم تایید نشد',
}


class Team:
    def __init__(self, name: str, code: int):
        self.name = name
        self.code = code
        self.members = []
        self.statuspay = False
        self.score = 0

    def __str__(self):
        s = '\n'.join(map(str, self.members))
        le = None
        for p in self.members:
            if p.leader:
                le = p
                break
        return 'نام تیم: {}\nکد تیم: {}\nسرگروه: {}\nاعضا:{}'.format(self.name, self.code, le, s)


class Player:
    def __init__(self, ci, si, phn, un, n):
        self.chatid = ci
        self.studentid = si
        self.phonenumber = phn
        self.username = un
        self.name = n
        self.leader = False
        self.activate = False

    def __str__(self):
        return 'نام: {}، آیدی: {}، عضویت: {}'.format(self.name, self.un, self.activate)


def find_team(cid):
    for t in teams:
        for p in t.members:
            if p.chatid == cid:
                return t
    return None


class LeaderLoginError(Exception):
    pass


class CreatedTeamError(Exception):
    pass


@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    if event.data == b'signin':
        try:
            team = find_team(sender.id)
            if team is not None:
                raise CreatedTeamError
            async with bot.conversation(event.original_update.user_id) as conv:
                await conv.send_message('👥 نام تیم خود را وارد کنید:')
                teamname = await conv.get_response()
                print(teamname)
                sender = await event.get_sender()
                teamcode = teamname.peer_id.user_id
                team = Team(teamname.message, teamcode)
                teams.append(team)

                await conv.send_message('تو به عنوان سرگروه تیم رو ساختی، حالا ادامه فرم رو وارد کن')
                await player_register(conv, team, players)

                price = 60000
                sale = 0
                await conv.send_message('🔰کد تخفیف را وارد کنید:\n(اگر کد تخفیف نداری \'ندارم\' رو تایپ کن):',
                                        buttons=Button.clear())
                salecode = await conv.get_response()
                if str(salecode.message) in salescode:
                    sale = (price * 2) // 10
                totalprice = price - sale
                await conv.send_message(messages['payment'].format(price, sale, totalprice
                                                                   , payurl.format(sender.id, totalprice)))

                endbut = [[Button.text('مدیریت تیم🎪')]]
                await conv.send_message(messages['create_team'].format(
                    teamname.message, 'https://t.me/FUMGame_bot?start=' + str(teamcode)), buttons=endbut)
        except CreatedTeamError:
            await event.respond('شما در تیمی عضو هستید و نمیتونید دوباره تیم تشکیل دهید')
        except asyncio.exceptions.TimeoutError:
            await event.respond('محدودیت زمان - دوباره امتحان کنید')

    elif event.data == b'sos':
        await bot.send_message(sender, messages['sos'])

    if re.match(r'^accept [0-9]{3,}', event.data.decode("utf-8")):
        print(event)
        pid = int(event.data.decode("utf-8").split()[1])
        team = find_team(pid)
        for p in team.members:
            if p.cid == pid:
                p.activate = True
                players.append(p)
                break
        await bot.send_message(pid, messages['accepted_player'].format(sender.first_name))
        await bot.edit_message(sender, event.original_update.msg_id, 'عضویت {} تایید شد'.format(sender.first_name))
        await event.answer('عضویتت در تیم توسط سرگروه تایید شد')
    elif re.match(r'^ignore [0-9]{3,}', event.data.decode("utf-8")):
        await bot.send_message(pid, messages['ignored_player'])
        await bot.edit_message(sender, event.original_update.msg_id, 'عضویت {} لغو شد'.format(sender.first_name))
        await event.answer('عدم تایید')
        team = find_team(pid)
        for p in team.players:
            if p.cid == pid:
                team.players.remove(p)
                break


@bot.on(events.NewMessage)
async def starter(event):
    if re.match(r'^/start$', event.raw_text):
        sender = await event.get_sender()
        await event.respond(messages['welcome'].format(sender.first_name), buttons=[
            [
                Button.inline('ایجاد تیم👥', b'signin'),
                Button.inline('راهنمایی🆘', b'sos'),
            ]])
    elif re.match(r'^/start [\d]*$', event.raw_text):
        teamecode = int(event.raw_text.split()[1])
        sender = await event.get_sender()
        team = find_team(teamecode)
        try:
            if team.code == sender.id:
                raise LeaderLoginError
            if team is not None:
                newplayer = Player(sender.first_name, sender.id)
                team.players.append(newplayer)
                await event.respond(messages['login_team'].format(team.name))
                buttons = [
                    [Button.inline('❌', 'ignore ' + str(sender.id)), Button.inline('✅', 'accept ' + str(sender.id))],
                ]
                await bot.send_message(team.code, messages['request_leader'].format(sender.first_name), buttons=buttons)
            else:
                await event.respond('چنین تیمی برای عضویت وجود ندارد')
        except LeaderLoginError:
            await event.respond('شما به عنوان سرگروه تیم را تشکیل دادید و قبلا عضو گروه هستید')
    elif re.match(r'^/start .*', event.raw_text):
        await event.respond('بازی هنوز شروع نشده، لطفا در زمان تعیین شده استارت بزنید')


@bot.on(events.NewMessage(pattern='مدیریت تیم🎪'))
async def team_managment(event):
    sender = await event.get_sender()
    team = find_team(sender.id)
    if team is not None:
        await event.respond(team.__str__())
    else:
        await event.respond('شما تیمی تشکیل نداده اید، از قسمت ایجاد تیم میتوانید شروع کنید')


def main():
    bot.start()
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
