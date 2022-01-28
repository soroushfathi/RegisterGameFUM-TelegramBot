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

bot_token = os.environ["FUMGAME_TOKENBOT"]
api_id = os.environ["0939***5204_apiID"]
api_hash = os.environ["0939***5204_apiHASH"]
bot = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)


teams = []
players = []


class Team:
    def __init__(self, players, name):
        self.players = players
        self.name = name
        self.score = 0
        self.level = 0
        self.chelp = 0

    def next_level(self):
        self.level += 1


class Player:
    def __init__(self, username, pid):
        self.username = username
        self.pid = pid
        self.currans = 0


class Game:
    def level1(self):
        pass

    def level2(self):
        pass

    def level3(self):
        pass

    def level4(self):
        pass

    def level5(self):
        pass

    def level6(self):
        pass

    def level7(self):
        pass


@bot.on(events.CallbackQuery)
async def handler(event):
    if event.data == b'0':
        answer += '0'
        await event.answer(answer)
        # await event.respond('me', 'right')
    elif event.data == b'1':
        answer += '1'
        await event.answer(answer)
    elif event.data == b'2':
        answer += '2'
        await event.answer(answer)
    elif event.data == b'3':
        answer += '3'
        await event.answer(answer)
    elif event.data == b'4':
        answer += '4'
        await event.answer(answer)
    elif event.data == b'5':
        answer += '6'
        await event.answer(answer)
    elif event.data == b'6':
        answer += '6'
        await event.answer(answer)
    elif event.data == b'7':
        answer += '7'
        await event.answer(answer)
    elif event.data == b'8':
        answer += '8'
        await event.answer(answer)
    elif event.data == b'9':
        answer += '9'
        await event.answer(answer)
    elif event.data == b'clear':
        answer += ''
        await event.answer('answer cleared')
    elif event.data == b'check':
        await event.answer('your answer is: {}'.format(answer), alert=True)


@bot.on(events.NewMessage(pattern='/start$'))
async def start(event):
    print(event)
    await event.respond('Welcome', buttons=[
        [
            Button.text('راهنمایی🆘', resize=True, single_use=True),
            Button.text('شرکت در مسابقه👥', resize=True, single_use=True),
        ], [
            Button.text('ایجاد مسابقه🎪', resize=True, single_use=True),
            Button.request_phone('Send phone'),
        ]])

    markup = bot.build_reply_markup(Button.inline('hi'))
    await bot.send_message('Thiisiskorvo', 'click me', buttons=markup)
    await event.respond('Hi!')
    # result = client(StartBotRequest(
    #     bot='username',
    #     peer='username',
    #     start_param='some string here'
    # ))
    # print(result.stringify())


@bot.on(events.NewMessage(pattern='راهنمایی🆘'))
async def giudness(event):
    await event.respond('این یک راهنمایی است')


@bot.on(events.NewMessage(pattern='ایجاد تیم👥'))
async def CreateTeam(event):
    chat = PeerChat((await event.message.get_chat())).chat_id
    async with bot.conversation(chat) as conv:
        await conv.send_message('نام تیم خود را وارد کنید:')
        teamname = await conv.get_response()
        print(teamname)


async def answer():
    buttons = [
        [
            Button.inline('1', b'1'),
            Button.inline('2', b'2'),
            Button.inline('3', b'3'),
        ], [
            Button.inline('4', b'4'),
            Button.inline('5', b'5'),
            Button.inline('6', b'6'),
        ], [
            Button.inline('7', b'7'),
            Button.inline('8', b'8'),
            Button.inline('9', b'9'),
        ], [
            Button.inline('🗑', b'clear'),
            Button.inline('0', b'0'),
            Button.inline('✅', b'check'),
        ]
    ]
    await event.respond(event.message, buttons=buttons)
    raise events.StopPropagation


def main():
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
