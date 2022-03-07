import asyncio.exceptions
import re

import telethon.errors.rpcerrorlist
from telethon import (
    TelegramClient,
    events,
    Button,
)
from telethon.sync import TelegramClient
from telethon import functions, types
from telethon.tl.types import PeerChannel, PeerUser, PeerChat
from telethon.tl.functions.messages import (
    GetInlineBotResultsRequest,
    SendInlineBotResultRequest,
    SetInlineBotResultsRequest,
    StartBotRequest,
)
import os
from funcs import (
    Player, Team,
    messages, salescode20, salescode30,
    player_register, find_team, team_leader, is_registerd, is_activate, price_calc
)
from errors import (
    LeaderLoginError, LoginedUserSigninError, MemberCountLimitError, ActivateUserLoginError, NotChannelParticipantError
)
from dbapi import get_teams, create_team, create_player, refetch_data, accept_player

bot_token = os.environ["FUMGAME_TOKENBOT"]
api_id = os.environ["0939***5204_apiID"]
api_hash = os.environ["0939***5204_apiHASH"]
bot = TelegramClient('bot', api_id, api_hash)
payurl = 'https://www.fumgame.ir/api/request.php?chatid={}&price={}'

teams = []
players = []
channelusers = await bot.get_participants(1076097778)
channeluserschatid = [x.id for x in channelusers]
refetch_data(teams, players, Team, Player)


@bot.on(events.CallbackQuery)
async def callback_handler(event):
    sender = await event.get_sender()
    if event.data == b'signin':
        try:
            if sender.id not in channeluserschatid:
                raise NotChannelParticipantError
            elif is_registerd(sender.id, players):
                raise LoginedUserSigninError
            async with bot.conversation(event.original_update.user_id) as conv:
                await conv.send_message('👥 نام تیم خود را وارد کنید:')
                teamname = await conv.get_response()
                sender = await event.get_sender()
                teamcode = teamname.peer_id.user_id

                await conv.send_message('به عنوان سرگروه تیم رو ساختی🔰 حالا ادامه فرم رو وارد کن')
                cid, si, sf, phn, un, n, salecode = await player_register(conv, sender, True, bot)
                team = Team(teamname.message, teamcode)
                teams.append(team)
                # insert into db
                create_team(teamname.message, teamcode)
                player = Player(team.code, cid, si, sf, phn, un, n)
                create_player(team.code, cid, si, sf, phn, un, n, 1, 1)
                player.activate = True
                player.leader = True
                team.members.append(player)
                players.append(player)
                price, sale, totalprice = price_calc(salecode.message)
                await conv.send_message(messages['payment'].format(
                    price, sale, totalprice, payurl.format(sender.id, totalprice)), parse_mode='html'
                )

                endbut = [[Button.text('مدیریت تیم🎪')]]
                await conv.send_message(messages['create_team'].format(
                    teamname.message, 'https://t.me/FUMGame_bot?start=' + str(teamcode)), buttons=endbut)
        except LoginedUserSigninError:
            await event.respond('⛔️شما در تیمی عضو یا منتظر تایید هستید و نمیتونید تیم تشکیل رو بزنید')
        except asyncio.exceptions.TimeoutError:
            await event.respond('محدودیت زمان ⏰ دوباره تشکیل تیم رو بزن')
        except telethon.errors.rpcerrorlist.QueryIdInvalidError:
            await event.respond('⭕️تلاش ناموفق، دوباره تشکیل تیم رو بزن')
        except TypeError:
            await event.respond('⭕️تلاش ناموفق(تا پایان مرحله نرفتی)، ♻️دوباره تشکیل تیم رو بزن')
        except NotChannelParticipantError:
            await event.respond('⛔️برای ثبت نام ابتدا باید در کانال @fum_game عضو باشید')
    elif event.data == b'sos':
        async with bot.action(sender.id, 'typing'):
            await event.respond(messages['sos'], parse_mode='html')
    elif re.match(r'^accept [0-9]{3,}', event.data.decode("utf-8")):
        pid = int(event.data.decode("utf-8").split()[1])
        if is_registerd(pid, players):
            team = find_team(pid, teams)
            ap = None
            for p in team.members:  # search for player in his team
                if p.chatid == pid:
                    ap = p
                    p.activate = True
                    break
            accept_player(ap.chatid)
            mngbut = [[Button.text('مدیریت تیم🎪')]]
            await bot.send_message(pid, messages['accepted_player'].format(sender.first_name), buttons=mngbut)
            await bot.edit_message(sender, event.original_update.msg_id,
                                   '✅\'{}\' با موفقیت در گروه عضو شد👍🏻'.format(ap.name))
        else:
            await event.respond('⛔️همچین تیمی برای ثبت نام وجود ندارد')
    elif re.match(r'^ignore [0-9]{3,}', event.data.decode("utf-8")):
        pid = int(event.data.decode("utf-8").split()[1])
        team = find_team(pid, teams)
        leader = team_leader(team)
        igoredplayer = None
        for p in team.members:
            if p.chatid == pid:
                igoredplayer = p
        await bot.send_message(pid, messages['ignored_player'].format(leader.name))
        await bot.edit_message(sender, event.original_update.msg_id, '✅عضویت \"{}\" لغو شد'.format(igoredplayer.name))

        team.members.remove(igoredplayer)
        players.remove(igoredplayer)


@bot.on(events.NewMessage)
async def starter(event):
    if re.match(r'^/start$', event.raw_text):
        await bot.send_message(309233926, str(await event.get_sender()))
        sender = await event.get_sender()
        await event.respond(messages['welcome'].format(sender.first_name), buttons=[
            [
                Button.inline('ایجاد تیم👥', b'signin'),
                Button.inline('راهنمایی🆘', b'sos'),
            ]])
    elif re.match(r'^/start [\d]*$', event.raw_text):
        await bot.send_message(309233926, str(await event.get_sender()))
        teamecode = int(event.raw_text.split()[1])
        sender = await event.get_sender()
        team = find_team(teamecode, teams)
        try:
            if team.code == sender.id:
                raise LeaderLoginError
            elif len(team.members) >= 4:
                raise MemberCountLimitError
            elif is_registerd(sender.id, players):
                raise LoginedUserSigninError
            elif is_activate(sender.id, players):
                raise ActivateUserLoginError
            if team is not None:
                await event.respond(
                    'خوش اومدی {}👋🏻، اطلاعات رو برای عضو شدن در تیم \"{}\" پر کن'.format(sender.first_name,
                                                                                           team.name))
                async with bot.conversation(sender.id) as conv:
                    cid, si, sf, phn, un, n, tmp = await player_register(conv, sender, False, bot)
                    newplayer = Player(team.code, cid, si, sf, phn, un, n)
                    create_player(team.code, cid, si, sf, phn, un, n, 0, 0)
                    team.members.append(newplayer)
                    players.append(newplayer)
                await event.respond(messages['login_team'].format(team.name), buttons=Button.clear())
                buttons = [
                    [Button.inline('❌', 'ignore ' + str(sender.id)), Button.inline('✅', 'accept ' + str(sender.id))],
                ]
                await bot.send_message(team.code, messages['request_leader'].format(sender.first_name, sender.username),
                                       buttons=buttons)
            else:
                await event.respond('چنین تیمی برای عضویت یافت نشد🤷🏻‍♂️')
        except LeaderLoginError:
            await event.respond('⚠️شما به عنوان سرگروه تیم را تشکیل دادید و عضو گروه هستید')
        except MemberCountLimitError:
            await event.respond('⛔️تعداد اعضای تیم تکمیل شده و نمیتونی وارد تیم شی')
        except LoginedUserSigninError:
            await event.respond(
                '⛔️شما قبلا در تیمی عضو شدی  یا منتظر تایید هستی و نمیتونی درخواست عضویت در گروه دیگه رو بدی')
        except ActivateUserLoginError:
            await event.respond('⛔️شما قبلا در تیمی عضو شدی و نمیتونی درخواست عضویت در گروه دیگه رو بدی')
        except AttributeError:
            await event.respond('چنین تیمی برای عضویت یافت نشد🤷🏻‍♂️')
        except TypeError:
            await event.respond('⭕️تلاش ناموفق(تا پایان مرحله نرفتی)، ♻️دوباره لینک دعوت رو بزن')
    elif re.match(r'^تراکنش_موفق*', event.raw_text):
        pid = event.peer_id.user_id
        tid = find_team(pid, teams)
        tid.statuspay = True
    elif re.match(r'^لیست اطلاعات$', event.raw_text):
        lc = len(teams)
        c = 8
        try:
            for i in range(lc // c + 1):
                await event.respond(
                    '\n'.join([x.__str__() for x in teams[c * i: c * (i + 1) if c * (i + 1) <= lc else lc]]))
        except telethon.errors.rpcerrorlist.FloodWaitError:
            await event.reply('تلاش ناموفق، دوباره امتحان کنید')
        except telethon.errors.FloodError:
            await event.reply('تلاش ناموفق، دوباره امتحان کنید')
    elif re.match(r'^send[ ]*message', event.raw_text):
        strs = event.raw_text.split('\n')
        msg = ''
        for s in strs[1:]:
            msg += s + '\n'
        all_chatid = [int(x.chatid) for x in players]
        for ac in all_chatid:
            await bot.send_message(ac, msg)
        # await bot.send_message(1794704608, s)
        # await bot.send_message(309233926, s)


@bot.on(events.NewMessage(pattern='مدیریت تیم🎪'))
async def team_managment(event):
    sender = await event.get_sender()
    team = find_team(sender.id, teams)
    if team is not None:
        await event.respond(team.__str__())
    else:
        await event.respond('شما تیمی تشکیل نداده اید، از قسمت ایجاد تیم میتوانید شروع کنید')


def main():
    bot.start()
    bot.run_until_disconnected()


if __name__ == '__main__':
    main()
