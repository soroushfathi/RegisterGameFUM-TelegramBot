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

bot_token = os.environ["FUMGAME_TOKENBOT"]
api_id = os.environ["0939***5204_apiID"]
api_hash = os.environ["0939***5204_apiHASH"]
bot = TelegramClient('bot', api_id, api_hash)

teams = []
players = []
messages = {
    'welcome': 'سلام {}، به ربات اتاق فرار فردوسی خوش اومدی',
    'create_team': 'به اتاق فرار فردوسی خوش اومدی، تیم \"{}\" با موفقیت ایجاد شد🤠\n هر یک از اعضا باید با لینک زیر'
                   'در بات استارت بزنن تا عضو گروه بشن\n{}\n'
                   '**بعد از اینکه هر یک از اعضا استارت زدن، برای شما پیامی میاد جهت تایید یا عدم تایید هم تیمی',
    # https://t.me/FUMGame_bot?start=teamecode
    'login_team': 'درخواست شما برای عضویت در تیم \"{}\" به سرگروه ارسال شد،'
                  'بعد از تایید پیام عضویت برای شما ارسال میشود',
    'request_leader': 'کاربری با نام {} درخواست عضویت در تیم را داد، در صورت تایید، عضو تیم خواهد شد',
    'accepted_player': 'عضویت شما در تیم توسط {} تایید شد',
    'ignored_player': 'متاسفانه عضویت شما در تیم تایید نشد',
}


class Team:
    def __init__(self, name: str, code: int, teamleader):
        self.name = name
        self.code = code
        self.teamleader = teamleader
        self.players = []
        self.score = 0
        self.chelp = 0

    def __str__(self):
        s = '\n'.join(map(str, self.players))
        print(s)
        return 'نام تیم: {}\nکد تیم: {}\nسرگروه: {}\nاعضا:{}'.format(self.name, self.code, self.teamleader, s)


class Player:
    def __init__(self, name: str, cid: int):
        self.name = name
        self.cid = cid
        self.currans = ''
        self.activate = False

    def __str__(self):
        return '{}, {}, {}'.format(self.name, self.cid, self.activate)


def find_team(cid):
    for t in teams:
        if t.code == cid:
            return t
        else:
            for p in t.players:
                if p.cid == cid:
                    return t
    return None


class LeaderLoginError(Exception):
    pass


class CreatedTeamError(Exception):
    pass


ans = ''


@bot.on(events.CallbackQuery)
async def handler(event):
    global ans
    print(event)
    if event.data in [b'0', b'1', b'2', b'3', b'4', b'5', b'6', b'7', b'8', b'9', b'10']:
        ans += event.data.decode("utf-8")
        await event.answer('get it')
        print(ans)
    elif event.data == b'clear':
        ans = ''
        await event.answer('answer cleared')
    elif event.data == b'check':
        await event.answer('your answer is: {}'.format(ans), alert=True)

    sender = await event.get_sender()
    if re.match(r'^accept [0-9]{3,}', event.data.decode("utf-8")):
        print(event)
        pid = int(event.data.decode("utf-8").split()[1])
        team = find_team(pid)
        for p in team.players:
            if p.cid == pid:
                p.activate = True
                players.append(p)
                break
        await bot.send_message(pid, messages['accepted_player'].format(sender.first_name))
        await bot.edit_message(sender, event.original_update.msg_id, 'عضویت {} تایید شد'.format(sender.first_name))
        await event.answer('عضویت  تایید شد')

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
                Button.text('راهنمایی🆘', resize=True, single_use=True),
                Button.text('ایجاد تیم👥', resize=True, single_use=True),
            ], [
                Button.text('مدیریت تیم🎪', resize=True, single_use=True),
                Button.request_phone('Send phone'),
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


@bot.on(events.NewMessage(pattern='راهنمایی🆘'))
async def giudness(event):
    await event.respond('این یک راهنمایی است')


@bot.on(events.NewMessage(pattern='مدیریت تیم🎪'))
async def team_managment(event):
    sender = await event.get_sender()
    team = find_team(sender.id)
    await event.respond(team.__str__())


@bot.on(events.NewMessage(pattern='ایجاد تیم👥'))
async def CreateTeam(event):
    chat = PeerChat((await event.message.get_chat())).chat_id
    sender = await event.get_sender()
    try:
        team = find_team(sender.id)
        if team is not None:
            raise CreatedTeamError
        async with bot.conversation(chat) as conv:
            await conv.send_message('نام تیم خود را وارد کنید:')
            teamname = await conv.get_response()
            sender = await event.get_sender()
            teamcode = teamname.peer_id.user_id
            teamleader = Player(sender.first_name, teamcode)
            teamleader.activate = True
            players.append(teamleader)
            team = Team(teamname.message, teamcode, teamleader)
            teams.append(team)
            await conv.send_message(messages['create_team'].format(
                teamname.message, 'https://t.me/FUMGame_bot?start=' + str(teamcode)
            ))
    except CreatedTeamError:
        await event.respond('شما در تیمی عضو هستید و نمیتونید دوباره تیم تشکیل دهید')


async def answer(event):
    buttons = [
        [
            Button.inline('1', '1'),
            Button.inline('2', '2'),
            Button.inline('3', '3'),
        ], [
            Button.inline('4', '4'),
            Button.inline('5', '5'),
            Button.inline('6', '6'),
        ], [
            Button.inline('7', '7'),
            Button.inline('8', '8'),
            Button.inline('9', '9'),
        ], [
            Button.inline('🗑', b'clear'),
            Button.inline('0', '0'),
            Button.inline('✅', b'check'),
        ]
    ]
    await event.respond(event.message, buttons=buttons)
    raise events.StopPropagation


def main():
    bot.start()
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
