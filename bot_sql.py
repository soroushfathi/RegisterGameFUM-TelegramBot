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
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="$F#1268@sofa",
    database="fumgame_escaperoom_telebot",
)
dbcur = db.cursor()

bot_token = os.environ["FUMGAME_TOKENBOT"]
api_id = os.environ["0939***5204_apiID"]
api_hash = os.environ["0939***5204_apiHASH"]
bot = TelegramClient('bot', api_id, api_hash)


messages = {
    'welcome': 'سلام {}، به ربات اتاق فرار فردوسی خوش اومدی',
    'create_team': 'به اتاق فرار فردوسی خوش اومدی، تیم \"{}\" با موفقیت ایجاد شد🤠\n هر یک از اعضا باید با لینک زیر'
                   'در بات استارت بزنن تا عضو گروه بشن\n{}\n'
                   '**بعد از اینکه هر یک از اعضا استارت زدن، برای شما پیامی میاد جهت تایید یا عدم تایید هم تیمی\n'
                   'این هم لینک شروع بازیه، در ساعت تعیین شده همه ی اعضا باید با این لینک وارد بات بشن و '
                   'بازی رو شروع کنن:\n{}',
    # https://t.me/FUMGame_bot?start=teamecode
    # https://t.me/FUMGame_bot?start=teamname
    'login_team': 'درخواست شما برای عضویت در تیم \"{}\" به سرگروه ارسال شد،'
                  'بعد از تایید پیام عضویت برای شما ارسال میشود',
    'request_leader': 'کاربری با نام {} درخواست عضویت در تیم را داد، در صورت تایید، عضو تیم خواهد شد',
    'accepted_player': 'عضویت شما در تیم توسط {} تایید شد',
    'ignored_player': 'متاسفانه عضویت شما در تیم تایید نشد',
}


@bot.on(events.NewMessage)
async def starter(event):
    if re.match(r'^/start$', event.raw_text):
        sender = await event.get_sender()
        buttons = [
            [
                Button.inline('ایجاد تیم👥', b'signin'),
                Button.inline('ورود به تیم👥', b'login'),
            ], [
                Button.inline('راهنمایی🆘', b'help'),
            ],
        ]
        await event.respond(messages['welcome'].format(sender.first_name), buttons=buttons)


def main():
    bot.start()
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
