from telethon import Button
from bot_oop import Player, Team


async def player_register(conv, team, players):
    await conv.send_message('👤 نام و نام خانوادگی خود را وارد کنید:')
    name = await conv.get_response()
    await conv.send_message('🆔 شماره دانشجویی خود را وارد کنید :')
    studentid = await conv.get_response()
    studentid = studentid.message
    while not studentid.isnumeric():
        await conv.send_message("شماره دانشجویی معتبر نیست، دوباره وارد کنید")
        studentid = await conv.get_response()
        studentid = studentid.message
    but = [[Button.request_phone('Send phone')]]
    await conv.send_message('☎️برای ارتباط و دسترسی بهتر، شماره تلفن خود را از دکمه پایین برای ارسال'
                            'انتخاب کنید.', buttons=but)
    phonenumber = await conv.get_response()

    player = Player(sender.id, studentid, phonenumber.media.phone_number, sender.username, name.message)
    player.activate = True
    player.leader = True
    team.members.append(player)
    players.append(player)
