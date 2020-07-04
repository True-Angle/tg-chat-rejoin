
# tg-chat-rejoin

When you leave a supergroup or channel in Telegram it is possible to see these chats in a data export taken through Telegram Desktop. This script uses the chat export function to find groups that you were once a member of and allows you to choose to rejoin them, if possible. This is useful if you have forgotten the username of a group.

It is not possible to rejoin private groups and channels unless you were once an admin, and it is not possible to rejoin any group or channel in which you were removed by an admin and still exist in the "Removed Users" list.

## Usage

 1. Clone the repository and `cd` into the repository
 2. Create and copy your application access key and hash from [here](https://my.telegram.org/apps)
 3. Modify the `API_ID` and `API_HASH` variables in `tg_chat_rejoin/__main__.py`
 4. Install the [Telethon](https://github.com/LonamiWebs/Telethon) library, ideally via a virtual environment:
 	- `python3 -m venv ./venv && source ./venv/bin/activate`
	- `pip3 install -r requirements.txt`
 5. Run the script `python3 tg_chat_rejoin`
 6. Follow the prompts

When finished, remove the session from another device unless you wish to re-run the script later.
