import os
import dotenv
import asyncio
import logging

from telethon import TelegramClient, events
from telethon.utils import get_peer
from telethon.tl.types import PeerChannel, PeerChat

logging.basicConfig(level=logging.INFO)

dotenv.load_dotenv('./.env')

api_id = os.environ.get("API_ID")
api_hash = os.environ.get("API_HASH")

# need to keep track of sources and destinations ,
# and the protocols assocd with them
# quick poc tho lets try fwding from list a to b

b = TelegramClient('bruh', api_id, api_hash)

#           0x1
sources = [835665216]
#               0x1
destinations = [853446541]

# routing string : Source_id,Destination_id
routing_table = [
    "835665216:853446541:PHOTO",
    "835665216:813729007:TEXT"
]


# takes an event and a type to check for
# returns true if it statisfies , false if not
def validate_type(event, type):
    print(f"🧪 : Testing Type for  {type} .")
    
    def check_photo(event):
        if not (event.message.media == None):
            return True
        else:
            print(f"🧪 : Type {type} : Validation failed , Skipping.")
            return False

    def check_text(event):
        print("Check text called ")
        if event.message.media == None and event.message.message:
            return True
        else:
            print(f"🧪 : Type {type} : Validation failed , Skipping.")
            return False

    if type == "PHOTO":
        return check_photo(event)
    elif type == "TEXT":
        return check_text(event)
    else :
        print(f"🚫 : Type {type} : Unknown.")
        
# takes an event and a type to check for
# returns true if it statisfies , false if not


async def typed_send_message(event, type, dest):
    print(f"🚚 Sending {type} to destination .", dest)
    dest = PeerChat(int(dest))
    if type == "PHOTO":
        await b.send_file(dest, event.message.media)
    if type == "TEXT":
        await b.send_message(dest, event.message.message)
    print(f"🚚 Sent {type} to destination .", dest)

def find_entries(src):
    matching_entries = []
    for entry in routing_table:
        if entry.startswith(str(src)):
            matching_entries.append(entry)
    return matching_entries


@b.on(events.NewMessage(forwards=False))
async def new_messages(event):
    # print(event)
    dest = None
    # check if they are from a source chat
    src = event.message.peer_id.chat_id
    if src in sources:
        # find its destination chat
        print("🔥 Chat in Source list sent a message ", src)
        print("🕸  Matching Routing Rules : ",find_entries(src))
        for entry in find_entries(src):
            dest = entry.split(':')[1]
            type_filter = entry.split(':')[2]
            # check if the type filter matches and send correctly 
            if validate_type(event, type_filter):
                await typed_send_message(event, type_filter, dest)
    else:
        print("👀 Ignoring Chat not in sources list.", src)

b.start()
print("Bot started ...")
b.run_until_disconnected()
