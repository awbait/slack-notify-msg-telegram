from telethon import TelegramClient, sync, events
from telethon.tl.types import PeerUser
import threading, asyncio, datetime, slack

# Telegram - https://my.telegram.org/
api_id = 12345
api_hash = ''
phone = ''
session_name = str(api_id)

# Slack - https://api.slack.com/apps (Bot User OAuth Access Token)
slack_token = 'xoxb-'
slack_channel = '#general'

client = TelegramClient(session_name, api_id, api_hash)
slack_client = slack.WebClient(token=slack_token, run_async=True)
dialogs = {}

async def main():
  while True:
    for dialog in dialogs:
      time = dialogs.get(dialog, 'none')
      if time < 10:
        dialogs[dialog] = time + 1
      elif time == 10:
        user_id = int(dialog)
        chats = await client.get_dialogs()
        chat = [x for x in chats if x.id == user_id][0]
        if chat.unread_count > 0:
          user = await client.get_entity(PeerUser(user_id))
          first_name = user.to_dict()['first_name']
          last_name = user.to_dict()['last_name']
          username = first_name + ' ' + last_name
          notify = f'There are {chat.unread_count} unread messages from: {username}'
          dialogs[dialog] = time + 1
          slack_client.chat_postMessage(channel=slack_channel, text=notify, username='Telegram')
    now = datetime.datetime.now()
    after = now.second + now.microsecond / 1_000_000
    if after:
      await asyncio.sleep(60 - after)
      
loop = asyncio.get_event_loop()
loop.create_task(main())

@client.on(events.NewMessage)
async def normal_handler(event):
  user_id = event.message.to_dict()['from_id']
  me = await client.get_me()
  if me.id != user_id:
    dialogs[user_id] = 0

client.connect()
if not client.is_user_authorized():
  client.send_code_request(phone)
  client.sign_in(phone, input('Enter code: '))
client.run_until_disconnected()
loop.run_forever()
