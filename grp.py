import telebot
import os
import json
from telebot import types
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Initialize bot
TOKEN = "7958043569:AAELYQsUYnETYM33C8kwBf-zPguWnMMkMmY"
bot = telebot.TeleBot(TOKEN, parse_mode="Markdown")


# File paths
MUTED_FILE = "muted.txt"
UNMUTED_FILE = "unmuted.txt"

# Initialize files if not exists
for f in [MUTED_FILE, UNMUTED_FILE]:
    if not os.path.exists(f):
        open(f, 'w').close()

# Function to check if user is an admin
def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

# Function to save data to a file
def save_to_file(filename: str, data: str):
    with open(filename, 'a') as f:
        f.write(f"{data}\n")

# Function to remove a user from a file
def remove_from_file(filename: str, user_id: int):
    with open(filename, 'r') as f:
        lines = f.readlines()
    with open(filename, 'w') as f:
        for line in lines:
            if str(user_id) not in line:
                f.write(line)

#₹₹₹₹₹

ADMIN_ID = "7858368373"
USER_FILE = "12.txt"

def save_user(chat_id):
    with open(USER_FILE, "a+") as file:
        file.seek(0)
        if str(chat_id) not in file.read().split():
            file.write(f"{chat_id}\n")




@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "🚫 *Access Denied!*", parse_mode='Markdown')
        return

    args = message.text.split(' ', 1)
    if len(args) < 2:
        bot.reply_to(message, "📝 *Usage:* /broadcast _<message>_", parse_mode='Markdown')
        return

    with open(USER_FILE, "r") as file:
        users = [line.strip() for line in file]

    success = 0
    failed = 0
    deleted = 0
    blocked = 0
    broadcast_msg = args[1]

    for user_id in users:
        try:
            bot.send_message(user_id, broadcast_msg)
            success += 1
        except Exception as e:
            if "Forbidden" in str(e):
                blocked += 1
            elif "chat not found" in str(e):
                deleted += 1
            else:
                failed += 1

    stats = f"""
    📢 *Broadcast Report* 📢
    
    ✅ Success: {success}
    ❌ Failed: {failed}
    🗑 Deleted: {deleted}
    🚫 Blocked: {blocked}
    """
    bot.reply_to(message, stats, parse_mode='Markdown')


@bot.message_handler(commands=['users'])
def handle_users(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.reply_to(message, "🚫 <b>Access Denied!</b>", parse_mode='html')
        return

    with open(USER_FILE, "r") as file:
        users = [line.strip() for line in file]

    user_list = []
    for user_id in users:
        try:
            chat = bot.get_chat(user_id)
            if chat.username:
                user_entry = f"👤 @{chat.username} ({user_id})"
            else:
                user_entry = f"👤 [No Username] ({user_id})"
            user_list.append(user_entry)
        except:
            user_list.append(f"❌ Invalid User ({user_id})")

    response = "📊 <b>Registered Users</b> 📊\n\n" + "\n".join(user_list)
    bot.send_message(message.chat.id, response, parse_mode='html')

# ===================== DM HANDLER =====================
@bot.message_handler(func=lambda m: m.chat.type == 'private')
def handle_dm(message: Message):
    save_user(message.chat.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("➕ κιᴅɴᴀᴘ мᴇ ʙᴀʙʏ ➕", url="https://t.me/GROUP_v01_ROBOT?startgroup=true"))
    
    bot.send_message(
        message.chat.id,
        "🛠️ Bot Control Panel 🛠️\n"
        "━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Please add me to a group to use my features!",
        parse_mode='Markdown',
        reply_markup=markup
    )

# ============== MUTE SYSTEM ============
@bot.message_handler(commands=['mute'])
def handle_mute(message: Message):
    save_user(message.chat.id)
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 You need admin privileges to use this command!")
        return

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "⚠️ Usage: /mute <user_id/reply>")
        return

    if is_admin(message.chat.id, user_id):
        bot.reply_to(message, "⛔ Cannot mute another admin!")
        return

    reason = " ".join(message.text.split()[2:]) if len(message.text.split()) > 2 else "No reason provided"

    try:
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=False)
        save_to_file(MUTED_FILE, f"{user_id}|{message.chat.id}|{reason}")

        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🔊 Unmute", callback_data=f"unmute_{user_id}"),
            InlineKeyboardButton("⛔ Kick", callback_data=f"kick_{user_id}")
        )
        markup.add(InlineKeyboardButton("🗑 Close", callback_data=f"close_{message.message_id}"))

        bot.send_message(
            message.chat.id,
            f"🔇 User Muted\n"
            f"📌 User ID: `{user_id}`\n"
            f"📝 Reason: {reason}",
            parse_mode='Markdown',
            reply_markup=markup
        )
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# ===================== UNMUTE SYSTEM =====================
@bot.message_handler(commands=['unmute'])
def handle_unmute(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 You need admin privileges to use this command!")
        return

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_id = int(message.text.split()[1])
    except:
        bot.reply_to(message, "⚠️ Usage: /unmute <user_id/reply>")
        return

    try:
        bot.restrict_chat_member(message.chat.id, user_id, can_send_messages=True)
        remove_from_file(MUTED_FILE, user_id)
        save_to_file(UNMUTED_FILE, f"{user_id}|{message.chat.id}|unmuted")

        bot.send_message(
            message.chat.id,
            f"🔊 User Unmuted\n"
            f"📌 User ID: `{user_id}`",
            parse_mode='Markdown'
        )
    except Exception as e:
        bot.reply_to(message, f"⚠️ Error: {str(e)}")

# ===================== CALLBACK HANDLER =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data.startswith('unmute_'):
        user_id = int(call.data.split('_')[1])
        chat_id = call.message.chat.id
        try:
            bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
            remove_from_file(MUTED_FILE, user_id)
            save_to_file(UNMUTED_FILE, f"{user_id}|{chat_id}|unmuted")
            bot.edit_message_text("🔊 User has been unmuted!", chat_id, call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, f"⚠️ Error: {str(e)}")

    elif call.data.startswith('kick_'):
        user_id = int(call.data.split('_')[1])
        chat_id = call.message.chat.id
        try:
            bot.kick_chat_member(chat_id, user_id)
            bot.edit_message_text("⛔ User has been kicked!", chat_id, call.message.message_id)
        except Exception as e:
            bot.answer_callback_query(call.id, f"⚠️ Error: {str(e)}")

    elif call.data.startswith('close_'):
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except:
            pass

import telebot
import random



# 🚀 Ultra-Cool VC Messages
VC_START_MSGS = [
    "🎤 Aᴄᴛɪᴠᴀᴛɪɴɢ Vᴏɪᴄᴇ Sʏsᴛᴇᴍ...\n🔊 Fʀᴇǫᴜᴇɴᴄʏ Lɪɴᴋ Eɴᴀʙʟᴇᴅ!",
    "⚡ Iɴɪᴛɪᴀᴛɪɴɢ Sᴏᴜɴᴅ Mᴏᴅᴜʟᴇ...\n🎧 Aᴜᴅɪᴏ Cᴏɴɴᴇᴄᴛɪᴏɴ Sᴛᴀʙʟᴇ!",
    "🔮 Dᴇᴘʟᴏʏɪɴɢ Vᴏᴄᴀʟ Nᴇᴛᴡᴏʀᴋ...\n🛸 Eᴍᴘᴏᴡᴇʀɪɴɢ Sᴏᴜɴᴅ Gᴇɴᴇʀᴀᴛɪᴏɴ!",
]

VC_END_MSGS = [
    "❌ Vᴏɪᴄᴇ Cᴏᴍᴍᴜɴɪᴄᴀᴛɪᴏɴ Tᴇʀᴍɪɴᴀᴛᴇᴅ!\n🔕 Rᴇsᴏɴᴀɴᴄᴇ Fʀᴇᴇᴢᴇ Aᴄᴛɪᴠᴀᴛᴇᴅ...",
    "🛑 Aᴜᴅɪᴏ Fʟᴏᴡ Hᴀʟᴛᴇᴅ!\n🎶 Nᴏ Mᴏʀᴇ Rᴇᴠᴇʀʙs...",
    "🔇 Sɪʟᴇɴᴄᴇ Pʀᴏᴄᴇss Iɴɪᴛɪᴀᴛᴇᴅ...\n💀 Sᴏᴜɴᴅ Wᴀᴠᴇs Dɪsᴄᴏɴɴᴇᴄᴛᴇᴅ!",
]

@bot.message_handler(content_types=['video_chat_started'])
def handle_video_chat_started(message):
    chat_id = message.chat.id
    fancy_text = random.choice(VC_START_MSGS)
    
    bot.send_message(
        chat_id,  
        f"╭━━━━━━━━━━━━━━━⊷\n"
        f"┣ ⏺ Vᴏɪᴄᴇ Cʜᴀᴛ Aᴄᴛɪᴠᴇ!\n\n"
        f"┣ ⚡ {fancy_text}\n\n"
        f"┣ 🔥 Eɴᴛᴇʀ ᴛʜᴇ ᴀᴜᴅɪᴏ ᴅɪᴍᴇɴsɪᴏɴ!\n"
        f"╰━━━━━━━━━━━━━━━⊷"
    )

@bot.message_handler(content_types=['video_chat_ended'])
def handle_video_chat_ended(message):
    chat_id = message.chat.id
    fancy_text = random.choice(VC_END_MSGS)

    bot.send_message(
        chat_id,  
        f"╭━━━━━━━━━━━━━━━⊷\n"
        f"┣ ❌ Vᴏɪᴄᴇ Cʜᴀᴛ Eɴᴅᴇᴅ!\n\n"
        f"┣ 🔕 {fancy_text}\n\n"
        f"┣ 🎵 Bᴀᴄᴋ ᴛᴏ ᴛʜᴇ ᴍᴜsɪᴄ ᴡᴏʀʟᴅ...\n"
        f"╰━━━━━━━━━━━━━━━⊷"
    )




    
from telebot import types




from telebot import TeleBot, types


user_messages = {}  # Initialize dictionary to store user messages

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)
    chat_id = message.chat.id
    
    # Inline buttons
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("●『 ᴊᴏɪɴ 』 🌹", url="https://t.me/armanteamvip"),
        types.InlineKeyboardButton("●『 ᴊᴏɪɴ 』 🌹", url="https://t.me/clickmekarna")
    )
    keyboard.add(types.InlineKeyboardButton("🥀『 ᴊᴏɪɴᴇᴅ 』 🥀", callback_data="joined"))
    
    # Send message with photo
    sent_message = bot.send_photo(
        chat_id, 
        photo="https://graph.org/file/e0280f7e13b27eead48e7-d83d423d80796076de.jpg",
        caption="нιι ᴅᴀʀʟιɴԍ 💕\n\nᴘʟᴇᴀsᴇ נoιɴ ouʀ ԍʀouᴘ ᴀɴᴅ cнᴀɴɴᴇʟ ғoʀ ʙoт uᴘᴅᴀтᴇs ᴀɴᴅ мoʀᴇ 😀\n\nтнᴀɲкs ʙᴀʙ", 
        reply_markup=keyboard
    )
    
    # Store message ID
    user_messages[chat_id] = sent_message.message_id

@bot.callback_query_handler(func=lambda call: call.data == "joined")
def joined(call):
    chat_id = call.message.chat.id

    # Delete old message
    if chat_id in user_messages:
        try:
            bot.delete_message(chat_id, user_messages[chat_id])
        except Exception:
            pass  # Avoid crashing if the message is already deleted
    
    # Inline buttons for new message
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("➕ ᴀᴅᴅ тo ԍʀouᴘ ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"),
        types.InlineKeyboardButton(": ‌‌➛ ᴅᴇvᴇʟoᴘᴇʀ ⚚", url="https://t.me/MR_INDIAN_OWNER_1")
    )
    
    # Send new message
    bot.send_photo(
        chat_id, 
        photo="https://graph.org/file/e0280f7e13b27eead48e7-d83d423d80796076de.jpg",
        caption="wᴇʟcoмᴇ ʙᴀʙ 😄\n\nнow ᴀʀᴇ ʏou тoᴅᴀʏ 😊\n\nwнᴀт cᴀɴ ᴅo тнιs ʙoт ?\n\nтʏᴘᴇ /нᴇʟᴘ то sᴇᴇ\n\nтнᴀɲкs ʙᴀʙʏ ғoʀ Ноιɴιɴԍ us 💕", 
        reply_markup=keyboard
    )



    
@bot.message_handler(commands=['help'])
def send_help(message):
    save_user(message.chat.id)
    user_id = message.chat.id
    
    keyboard = InlineKeyboardMarkup()
    keyboard.row_width = 2
    keyboard.add(
        InlineKeyboardButton("➕ ᴀᴅᴅ тo ԍʀouᴘ ➕", url=f"https://t.me/{bot.get_me().username}?startgroup=true"),
        InlineKeyboardButton("➕ ᴀᴅᴅ тo cнᴀɴɴᴇʟ ➕", url=f"https://t.me/{bot.get_me().username}?startchannel=true"),
        InlineKeyboardButton("➛ ᴅᴇvᴇʟoᴘᴇʀ ⚚", url="https://t.me/MR_INDIAN_OWNER_1")
    )
    
    help_message = "1️⃣ ᴀᴅᴅ тнιs ʙoт ιɴ ʏouʀ ԍʀouᴘ\n2️⃣ נusт мᴀκᴇ тнᴇ ʙoт ᴀᴅмιɴ\n3️⃣ ᴅoɴᴇ 👍\n\n🥀 тнᴀɴκs ʙᴀʙʏ ғoʀ usιɴԍ мᴇ 🥹\n\nWE NOT DETAILED HOW TO USE..."
    bot.send_message(message.chat.id, help_message, reply_markup=keyboard)



LOCKED_GROUPS_FILE = "locked_groups.txt"

# Ensure file exists
if not os.path.exists(LOCKED_GROUPS_FILE):
    open(LOCKED_GROUPS_FILE, 'w').close()

def is_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def is_anonymous_admin(chat_id: int, user_id: int) -> bool:
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status == 'administrator' and member.can_restrict_members
    except:
        return False

def is_bot_admin(chat_id: int) -> bool:
    try:
        bot_info = bot.get_me()
        bot_member = bot.get_chat_member(chat_id, bot_info.id)
        return bot_member.status in ['administrator', 'creator']
    except:
        return False

def is_group_locked(chat_id: int) -> bool:
    with open(LOCKED_GROUPS_FILE, 'r') as f:
        return str(chat_id) in f.read()

def lock_group(chat_id: int):
    with open(LOCKED_GROUPS_FILE, 'a') as f:
        f.write(f"{chat_id}\n")

def unlock_group(chat_id: int):
    with open(LOCKED_GROUPS_FILE, 'r') as f:
        lines = f.readlines()
    with open(LOCKED_GROUPS_FILE, 'w') as f:
        for line in lines:
            if str(chat_id) not in line:
                f.write(line)

# ===================== GROUP LOCK SYSTEM =====================
@bot.message_handler(commands=['lock'])
def handle_lock(message: types.Message):
    save_user(message.chat.id)
    if not message.text.strip().endswith(" all"):
        bot.reply_to(message, "⚠️ ɪɴᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ!\nᴜsᴇ: `/lock all`", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_bot_admin(chat_id):
        bot.reply_to(message, "❌ ɪ ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ\n📌 ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ғɪʀsᴛ!", parse_mode="Markdown")
        return

    if not (is_admin(chat_id, user_id) or is_anonymous_admin(chat_id, user_id)):
        bot.answer_callback_query(callback_query_id=message.message_id, text="🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!", show_alert=True)
        return

    if is_group_locked(chat_id):
        bot.reply_to(message, "🔒 ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ʟᴏᴄᴋᴇᴅ!")
        return

    try:
        bot.delete_message(chat_id, message.message_id)  # Delete command message
        bot.set_chat_permissions(chat_id, types.ChatPermissions(can_send_messages=False))
        lock_group(chat_id)

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("🗑 Close", callback_data="close_msg"))

        bot.send_message(
            chat_id,
            "🚨 ɢʀᴏᴜᴘ ʟᴏᴄᴋᴇᴅ 🚨\n"
            "🔒 ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɴᴏᴡ!\n\n"
            "🔇 ᴍᴇᴍʙᴇʀs ᴄᴀɴɴᴏᴛ ᴄʜᴀᴛ ᴜɴᴛɪʟ ᴜɴʟᴏᴄᴋᴇᴅ",
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(chat_id, f"❌ **ᴇʀʀᴏʀ:** {str(e)}")

# ===================== GROUP UNLOCK SYSTEM =====================
@bot.message_handler(commands=['unlock'])
def handle_unlock(message: types.Message):
    if not message.text.strip().endswith(" all"):
        bot.reply_to(message, "⚠️ ɪɴᴄᴏʀʀᴇᴄᴛ ғᴏʀᴍᴀᴛ!\nᴜsᴇ: `/unlock all`", parse_mode="Markdown")
        return

    user_id = message.from_user.id
    chat_id = message.chat.id

    if not is_bot_admin(chat_id):
        bot.reply_to(message, "❌ ɪ ᴀᴍ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ\n📌 ᴘʟᴇᴀsᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀɴ ᴀᴅᴍɪɴ ғɪʀsᴛ!", parse_mode="Markdown")
        return

    if not (is_admin(chat_id, user_id) or is_anonymous_admin(chat_id, user_id)):
        bot.answer_callback_query(callback_query_id=message.message_id, text="🚫 ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!", show_alert=True)
        return

    if not is_group_locked(chat_id):
        bot.reply_to(message, "🔓 ᴄʜᴀᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴜɴʟᴏᴄᴋᴇᴅ!")
        return

    try:
        bot.delete_message(chat_id, message.message_id)  # Delete command message
        bot.set_chat_permissions(chat_id, types.ChatPermissions(can_send_messages=True))
        unlock_group(chat_id)

        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton("🗑 Close", callback_data="close_msg"))

        bot.send_message(
            chat_id,
            "✅ ɢʀᴏᴜᴘ ᴜɴʟᴏᴄᴋᴇᴅ\n"
            "💬 ᴍᴇᴍʙᴇʀs ᴄᴀɴ ɴᴏᴡ ᴄʜᴀᴛ ᴀɢᴀɪɴ 🎉",
            reply_markup=markup
        )
    except Exception as e:
        bot.send_message(chat_id, f"❌ **ᴇʀʀᴏʀ:** {str(e)}")

# ===================== CALLBACK HANDLER =====================
@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "close_msg":
        bot.delete_message(call.message.chat.id, call.message.message_id)




import telebot
import json
import os



DELETE_GROUPS_FILE = "delete_groups.json"

# Load active delete groups safely
def load_delete_groups():
    if not os.path.exists(DELETE_GROUPS_FILE) or os.stat(DELETE_GROUPS_FILE).st_size == 0:
        return {}  # Return an empty dictionary if file doesn't exist or is empty
    try:
        with open(DELETE_GROUPS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}  # If corrupted, return empty dict

# Save active delete groups
def save_delete_groups(groups):
    with open(DELETE_GROUPS_FILE, "w") as f:
        json.dump(groups, f, indent=4)

# Load delete status
delete_groups = load_delete_groups()

# Check if a user is an admin
def is_admin(chat_id, user_id):
    try:
        chat_admins = bot.get_chat_administrators(chat_id)
        return user_id in [admin.user.id for admin in chat_admins]
    except:
        return False

# /delete all command
@bot.message_handler(commands=['delete'])
def delete_all(message):
    if message.chat.type == "private":
        return

    args = message.text.split()
    
    if len(args) != 2 or args[1] != "all":
        bot.reply_to(message, "USAGE: `/delete all`", parse_mode="Markdown")
        return

    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 ʏou ᴀʀᴇ ɴoт ᴀɴ ᴀᴅмιɴ oғ тнιs ԍʀouᴘ !", parse_mode="Markdown")
        return

    delete_groups[str(message.chat.id)] = True
    save_delete_groups(delete_groups)
    
    bot.send_message(message.chat.id, "✅ ᴀuтo-ᴅᴇʟᴇтᴇ :- 𝐄𝐍𝐀𝐁𝐋𝐄𝐃\n\nᴀʟʟ ɴᴇw мᴇssᴀԍᴇs wιʟʟ ʙᴇ ᴅᴇʟᴇтᴇᴅ ιɴsтᴀɴтʟʏ !", parse_mode="Markdown")

# /undelete all command
@bot.message_handler(commands=['undelete'])
def undelete_all(message):
    if message.chat.type == "private":
        return

    args = message.text.split()
    
    if len(args) != 2 or args[1] != "all":
        bot.reply_to(message, "USAGE: `/undelete all`", parse_mode="Markdown")
        return

    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 ʏou ᴀʀᴇ ɴoт ᴀɴ ᴀᴅмιɴ oғ тнιs ԍʀouᴘ !", parse_mode="Markdown")
        return

    if str(message.chat.id) in delete_groups:
        del delete_groups[str(message.chat.id)]
        save_delete_groups(delete_groups)
        bot.send_message(message.chat.id, "❌ ᴀuтo-ᴅᴇʟᴇтᴇ :- 𝐃𝐈𝐒𝐀𝐁𝐋𝐄𝐃\n\nɴᴇw мᴇssᴀԍᴇs wιʟʟ ɴoт ʙᴇ ᴅᴇʟᴇтᴇᴅ.", parse_mode="Markdown")
    else:
        bot.reply_to(message, "⚠️ ᴀuтo-ᴅᴇʟᴇтᴇ ιs ᴀʟʀᴇᴀᴅʏ ᴅιsᴀʙʟᴇᴅ.", parse_mode="Markdown")




import re
from telebot.types import Message, ChatPermissions


# File to store deleted messages
DELETED_FILE = "dl.json"

# Regex to detect links (only HTTPS)
LINK_REGEX = re.compile(r"https?://\S+")

# Load deleted messages history
try:
    with open(DELETED_FILE, "r") as f:
        deleted_messages = json.load(f)
except:
    deleted_messages = {}

def save_deleted_messages():
    with open(DELETED_FILE, "w") as f:
        json.dump(deleted_messages, f, indent=2)

# Check if user is admin
def is_admin(chat_id, user_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        return any(admin.user.id == user_id for admin in admins)
    except:
        return False

# Auto-delete link messages
@bot.message_handler(func=lambda message: bool(LINK_REGEX.search(message.text or "")))
def delete_link_messages(message: Message):
    if is_admin(message.chat.id, message.from_user.id):
        return  # Ignore admins

    bot.delete_message(message.chat.id, message.message_id)

    user = message.from_user
    alert_message = f"[{user.first_name}](tg://user?id={user.id}) USER IS SENDING LINK\n\nWITHOUT ADMIN PERMISSION"
    sent_alert = bot.send_message(message.chat.id, alert_message)

    # Log deleted messages
    if str(message.chat.id) not in deleted_messages:
        deleted_messages[str(message.chat.id)] = []
    deleted_messages[str(message.chat.id)].append(
        {"username": user.username or "No Username", "message": message.text}
    )
    save_deleted_messages()

# Auto-delete photos with links
@bot.message_handler(content_types=["photo"])
def delete_photo_with_links(message: Message):
    if message.caption and LINK_REGEX.search(message.caption):
        if is_admin(message.chat.id, message.from_user.id):
            return  # Ignore admins

        bot.delete_message(message.chat.id, message.message_id)

        user = message.from_user
        alert_message = f"[{user.first_name}](tg://user?id={user.id}) USER IS SENDING LINK IN PHOTO\n\nWITHOUT ADMIN PERMISSION"
        sent_alert = bot.send_message(message.chat.id, alert_message)

        # Log deleted messages
        if str(message.chat.id) not in deleted_messages:
            deleted_messages[str(message.chat.id)] = []
        deleted_messages[str(message.chat.id)].append(
            {"username": user.username or "No Username", "message": "Photo with Link"}
        )
        save_deleted_messages()

# Command: /see (Admins only)
@bot.message_handler(commands=["see"])
def see_deleted_messages(message: Message):
    if not is_admin(message.chat.id, message.from_user.id):
        return

    chat_id = str(message.chat.id)
    if chat_id not in deleted_messages or not deleted_messages[chat_id]:
        bot.send_message(message.chat.id, "No deleted messages in this group.")
        return

    report = f"**THIS GROUP INFO**\nDELETED MESSAGES: `{len(deleted_messages[chat_id])}`\n\n"
    for i, entry in enumerate(deleted_messages[chat_id], 1):
        report += f"{i}. `{entry['username']}` - `{entry['message']}`\n"

    bot.send_message(message.chat.id, report)

import telebot
from telebot.types import ChatMemberAdministrator, ChatPermissions



# 🚀 Stylish Ban Messages
BAN_MSGS = [
    "🔥 {first_name} нᴀs ʙᴇᴇɴ ᴇʀᴀsᴇᴅ ғʀoм ᴇxιsтᴇɴcᴇ\n🚫 ɴo sᴇcoɴᴅ cнᴀɴcᴇs !",
    "⚠️ {first_name} נusт ԍoт ᴇנᴇcтᴇᴅ ιɴтo тнᴇ voιᴅ !\n💀 ʀιᴘ, ʟιттʟᴇ ʙuᴅᴅʏ",
    "❌ {first_name} нᴀs ʙᴇᴇɴ ᴇʟιмιɴᴀтᴇᴅ\n🔨 нᴀммᴇʀ oғ נusтιcᴇ sтʀικᴇs",
    "🔫 {first_name} נusт ԍoт sɴιᴘᴇᴅ\n🧨 ԍᴀмᴇ ovᴇʀ, тʀʏ ᴀԍᴀιɴ ɴᴇvᴇʀ",
    "👋 {first_name} wᴀs ᴀ мιsтᴀκᴇ... ᴀɴᴅ ɴow тнᴇʏ'ʀᴇ ԍoɴᴇ\n💣 ԍooᴅ ʀιᴅᴅᴀɴcᴇ"
]

@bot.message_handler(commands=['ban'])
def ban_user(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Get bot and user admin status
    bot_member = bot.get_chat_member(chat_id, bot.get_me().id)
    user_member = bot.get_chat_member(chat_id, user_id)

    if not bot_member.can_restrict_members:
        bot.reply_to(message, "❌ ι ɴᴇᴇᴅ ᴀᴅмιɴ ʀιԍнтs тo ʙᴀɴ usᴇʀs !")
        return

    if user_member.status not in ["administrator", "creator"]:
        bot.reply_to(message, "🚫 uɴᴀuтнoʀιzᴇᴅ ᴀccᴇss !\n⚠️ oɴʟʏ ԍʀouᴘ ᴀᴅмιɴs cᴀɴ usᴇ тнιs coммᴀɴᴅ !", parse_mode="Markdown")
        return

    if message.reply_to_message:
        banned_user = message.reply_to_message.from_user
    else:
        args = message.text.split()
        if len(args) < 2:
            bot.reply_to(message, "❌ Usage: `/ban <user_id>` or reply to a user.", parse_mode="Markdown")
            return
        try:
            banned_user = bot.get_chat_member(chat_id, int(args[1])).user
        except:
            bot.reply_to(message, "⚠️ ιɴvᴀʟιᴅ usᴇʀ ιᴅ !", parse_mode="Markdown")
            return

    # Delete the admin's command message
    bot.delete_message(chat_id, message.message_id)

    # Ban the user
    bot.ban_chat_member(chat_id, banned_user.id)

    # Send stylish ban message
    ban_message = random.choice(BAN_MSGS).format(first_name=f"[{banned_user.first_name}](tg://user?id={banned_user.id})")
    bot.send_message(chat_id, f"╭━━━━━━━━━━━━━━━⊷\n"
                              f"┣ 🚨 𝙐𝙨𝙚𝙧 𝘽𝙖𝙣𝙣𝙚𝙙 !\n\n"
                              f"┣ 🛑 {ban_message}\n\n"
                              f"┣ ⚡ Jusтιcᴇ нᴀs ʙᴇᴇɴ sᴇʀvᴇᴅ!\n"
                              f"╰━━━━━━━━━━━━━━━⊷", parse_mode="Markdown")


import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton



# Function to delete user join/leave messages
def delete_message(chat_id, message_id):
    try:
        bot.delete_message(chat_id, message_id)
    except:
        pass  # Ignore errors if unable to delete

# Inline button to delete the bot's message
def close_button():
    markup = InlineKeyboardMarkup()
    close_btn = InlineKeyboardButton("❌ Close", callback_data="delete_this")
    markup.add(close_btn)
    return markup

def get_group_owner(chat_id):
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.status == 'creator':
                return admin.user
        return None
    except Exception as e:
        print(f"Error fetching group owner: {e}")
        return None

# Welcome message when a user joins
@bot.message_handler(content_types=["new_chat_members"])
def welcome_message(message):
    for new_member in message.new_chat_members:
        delete_message(message.chat.id, message.message_id)  # Delete user join message

        group_name = message.chat.title
        group_link_part = f"[{group_name}](https://t.me/{message.chat.username})" if message.chat.username else group_name
        first_name = new_member.first_name
        user_link = f"[{first_name}](tg://user?id={new_member.id})"

        # Get group owner
        owner = get_group_owner(message.chat.id)
        owner_link = f"[{owner.first_name}](tg://user?id={owner.id})" if owner else "None"

        welcome_text = f"""
├── 🔹 {group_link_part}  
│   │  
│   ├ 👋 wᴇʟcoмᴇ ᴅᴇᴀʀ. →  {user_link} 🔥
│   ├ 👑 ԍʀᴘ owɴᴇʀ → {owner_link} 😎
│   ⋅ ────── ✪ ────── ⋅
├ 💬 wᴇʟcoмᴇ тo тнᴇ ԍʀouᴘ! ᴇɴנoʏ ʏouʀ sтᴀʏ.  
        """

        bot.send_message(message.chat.id, welcome_text, 
                       reply_markup=close_button(),
                       parse_mode="Markdown")

# Goodbye message when a user leaves
@bot.message_handler(content_types=["left_chat_member"])
def goodbye_message(message):
    delete_message(message.chat.id, message.message_id)  # Delete user leave message

    left_member = message.left_chat_member
    group_name = message.chat.title
    group_link_part = f"[{group_name}](https://t.me/{message.chat.username})" if message.chat.username else group_name
    first_name = left_member.first_name
    user_link = f"[{first_name}](tg://user?id={left_member.id})"

    # Get group owner
    owner = get_group_owner(message.chat.id)
    owner_link = f"[{owner.first_name}](tg://user?id={owner.id})" if owner else "None"

    goodbye_text = f"""
├── 🔹 {group_link_part}  
│   │  
│   ├ 👋 ԍooᴅ ʙʏᴇ → {user_link} 🌚
│   ├ 👑 ԍʀᴘ owɴᴇʀ → {owner_link} ✨
│   ⋅ ────── ✪ ────── ⋅
├ 💬 ԍooᴅ ʙʏᴇ, ɴᴇvᴇʀ coмᴇ ᴀԍᴀιɴ 🤗
    """

    bot.send_message(message.chat.id, goodbye_text, 
                   reply_markup=close_button(),
                   parse_mode="Markdown")

# Handle close button clicks
@bot.callback_query_handler(func=lambda call: call.data == "delete_this")
def delete_welcome_or_goodbye(call):
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass  # Ignore errors if unable to delete


# Function to format user info message in HTML
def get_user_info(user, chat_id):
    first_name = user.first_name or "Unknown"
    user_id = user.id
    username = f"@{user.username}" if user.username else "N/A"

    return f"""
<b>╭─── ⋅ ⋅ ── ✪ 𝙐𝙎𝙀𝙍 𝙄𝙉𝙁𝙊 ✪ ── ⋅ ⋅ ───╮</b>
│   ├─ 🪪 <b>ɴᴀмᴇ →</b> {first_name}
│   │
│   ├─ 🆔 <b>ιᴅ →`</b> <code>{user_id}</code>`
│   │
│   ├─ 📛 <b>usᴇʀɴᴀмᴇ →</b> {username}
│   │
│   ├─ 💬 <b>cнᴀт ιᴅ → `</b> <code>{chat_id}</code>`
<b>╰─── ⋅ ⋅ ────── ✪ ────── ⋅ ⋅ ───╯</b>
"""

# Command handler for /me, /id, /info
@bot.message_handler(commands=["me", "id", "info"])
def user_info(message):
    chat_type = message.chat.type  # Check if it's a group or private chat
    chat_id = message.chat.id  # Get chat ID

    # If in a group and the user is replying, fetch replied user's info
    if chat_type in ["group", "supergroup"] and message.reply_to_message:
        if message.reply_to_message.from_user:
            target_user = message.reply_to_message.from_user
            bot.send_message(chat_id, get_user_info(target_user, chat_id), parse_mode="HTML")
        else:
            bot.send_message(chat_id, "🚫 <b>User not found!</b>", parse_mode="HTML")
    
    # If not a group OR the user isn't replying, show the command sender's info
    else:
        bot.send_message(chat_id, get_user_info(message.from_user, chat_id), parse_mode="HTML")


from telebot import types



FILTER_FILE = "fl.txt"

# Create filter file if not exists
if not os.path.exists(FILTER_FILE):
    open(FILTER_FILE, 'w').close()

def is_admin(chat_id, user_id):
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def save_filter(chat_id, trigger, response):
    with open(FILTER_FILE, 'a') as f:
        f.write(f"{chat_id}|{trigger}|{response}\n")

def get_filters(chat_id):
    filters = {}
    with open(FILTER_FILE, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split('|')
            if len(parts) == 3 and parts[0] == str(chat_id):
                filters[parts[1]] = parts[2]
    return filters

def remove_filter(chat_id, trigger):
    lines = []
    removed = False
    with open(FILTER_FILE, 'r') as f:
        for line in f.readlines():
            parts = line.strip().split('|')
            if len(parts) == 3 and parts[0] == str(chat_id) and parts[1] == trigger:
                removed = True
            else:
                lines.append(line)
    
    if removed:
        with open(FILTER_FILE, 'w') as f:
            f.writelines(lines)
    return removed

# ===================== COMMAND HANDLERS =====================
@bot.message_handler(commands=['filter'])
def add_filter(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 Admin only command!")
        return

    try:
        _, trigger, response = message.text.split("'", 2)
        trigger = trigger.strip()
        response = response.strip()
        
        save_filter(message.chat.id, trigger, response)
        bot.reply_to(message, f"✅ Filter added!\nTrigger: '{trigger}'\nResponse: {response}")
        
    except Exception as e:
        bot.reply_to(message, "⚠️ Invalid format! Use:\n/filter 'trigger' response")

@bot.message_handler(commands=['filters'])
def list_filters(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 Admin only command!")
        return

    filters = get_filters(message.chat.id)
    if not filters:
        bot.reply_to(message, "❌ No filters set for this group!")
        return

    response = "📜 Active Filters:\n" + "\n".join(
        [f"⚡ '{trigger}' → {response}" for trigger, response in filters.items()]
    )
    bot.reply_to(message, response)

@bot.message_handler(commands=['stop'])
def remove_filter_cmd(message):
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "🚫 Admin only command!")
        return

    try:
        trigger = message.text.split()[1].strip("'")
        if remove_filter(message.chat.id, trigger):
            bot.reply_to(message, f"❌ Filter removed: '{trigger}'")
        else:
            bot.reply_to(message, "⚠️ Filter not found!")
    except:
        bot.reply_to(message, "⚠️ Use: /stop trigger_word")

# ===================== MESSAGE FILTERING =====================
@bot.message_handler(func=lambda m: True, content_types=['text'])
def handle_message(message):
    if message.chat.type in ['group', 'supergroup']:
        filters = get_filters(message.chat.id)
        trigger = message.text.strip().lower()
        
        if trigger in filters:
            bot.reply_to(message, filters[trigger])

# Auto-delete new messages when enabled
@bot.message_handler(content_types=[
    "text", "photo", "video", "audio", "voice", 
    "document", "sticker", "video_note", "animation"])
def delete_all_media(message):
    if str(message.chat.id) in delete_groups:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass




print("𝗕𝗢𝗧 𝗜𝗦 𝗥𝗨𝗡𝗡𝗜𝗡𝗚 🚀")
bot.infinity_polling()