#!/usr/bin/python3
import json
import logging
import subprocess
import sys
import textwrap
import webbrowser

from telethon.errors import TakeoutInitDelayError, ChannelPrivateError
from telethon.sync import TelegramClient
from telethon.tl import functions
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.types import Channel, Photo

logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s', level=logging.ERROR)

# Modify both of these with your own values obtained from https://my.telegram.org/apps
API_ID = 0
API_HASH = ''


def chat_full_info_or_none(left_chat, client: TelegramClient):
    try:
        return client(GetFullChannelRequest(left_chat))
    except ChannelPrivateError:
        return None


def dump_chat(left_chat, full_info, client: TelegramClient):
    if full_info is None:
        print(' > You cannot access full information about this chat. It may be private, or you were removed by an admin.\n'
              ' > Dumping only information you can access.')
        print(textwrap.indent(json.dumps(left_chat.to_dict(), indent=4, default=lambda x: x.__repr__()), prefix=' >  '))
    else:
        print(textwrap.indent(json.dumps(full_info.to_dict(), indent=4, default=lambda x: x.__repr__()), prefix=' >  '))

        if isinstance(full_info.full_chat.chat_photo, Photo):
            if sys.platform == 'linux':
                resp = input(' > View the current chat photo? [y/N]: ')
                if resp == 'y':
                    path = client.download_profile_photo(entity=full_info.full_chat, file='/tmp/chat-photo.png')
                    if isinstance(path, str):
                        subprocess.check_output(['xdg-open', path], stderr=subprocess.DEVNULL)
            else:
                print(' > Viewing chat photos is currently only supported on Linux desktop.')
        else:
            print(' > This chat has no profile picture.')


def open_chat(left_chat):
    if left_chat.username is None:
        print(' > This chat has no username - unable to open it.')
    else:
        print(' > Attempting to open chat.')
        webbrowser.open(f'tg://resolve?domain={left_chat.username}')


def process_left_chat(left_chat, client: TelegramClient):
    full_info = chat_full_info_or_none(left_chat, client)
    additional = ' (may not be possible for this chat)' if full_info is None else ''
    resp = input(f'Attempt to rejoin "{left_chat.title}"{additional}? [y/N/o/d/exit]: ').lower()

    if resp == 'y':
        try:
            client(functions.channels.JoinChannelRequest(left_chat))
            print(f' > Successfully rejoined "{left_chat.title}!"')
        except Exception as e:
            print(f' > Unable to rejoin "{left_chat.title}": "{e.__class__.__name__}: {str(e)}".')
    elif resp == 'd':
        dump_chat(left_chat, full_info, client)
        process_left_chat(left_chat, client)
    elif resp == 'o':
        open_chat(left_chat)
        process_left_chat(left_chat, client)
    elif resp == 'exit':
        raise StopIteration
    elif resp not in ['n', '']:
        print(f' > Unsupported option "{resp}"')
        process_left_chat(left_chat, client)


def main():
    with TelegramClient('telethon-session', API_ID, API_HASH) as client:
        with client.takeout(channels=True) as takeout_session:
            result = takeout_session(functions.channels.GetLeftChannelsRequest(0))
            print('\nEach left chat will be shown in the order that you originally joined.\n'
                  'Type one of the following options for each chat, followed by pressing enter:\n'
                  ' •    y: attempt to re-join this chat\n'
                  ' •    N: skip this chat (default)\n'
                  ' •    d: dump all known information about this chat\n'
                  ' •    o: open the chat in Telegram without joining (chat must be public with a username)\n'
                  ' • exit: skip all remaining chats and quit the script\n\n')
            for left_chat in result.chats:
                try:
                    process_left_chat(left_chat, client)
                except StopIteration:
                    break

            if len(result.chats) == 0:
                print('No left chats were found. Either they have since been deleted, or you have not left any groups or channels.')
            print(f'\n\n{"=" * 50}\nAll done. You may want to remove this session from another device if you do not wish to run the script again:')
            print('Settings -> Privacy and Security -> Show all Sessions')


if __name__ == '__main__':
    try:
        if API_ID == 0 or API_HASH == '':
            print('Error, please set configuration variables API_ID and API_HASH.')
            print('These may be found here: https://my.telegram.org/apps.')
            exit(1)
        main()
    except TakeoutInitDelayError:
        input('Approve takeout from another session, and then press ENTER')
        main()
