from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
from pytgcalls.exceptions import GroupCallNotFound
import asyncio

# Bot Client (Your Bot)
bot = Client(
    "GEMINI_PRO_v1_ROBOT",
    api_id="27152769",
    api_hash="b98dff566803b43b3c3120eec537fc1d",
    bot_token="7690937386:AAG5BY6X4nzbz0jmtAWxVYWsFSFxW7tV6IE"
)

# User Client (Assistant Account)
user = Client(
    "assistant_off_OG",
    api_id="27152769",  # Use assistant's API ID
    api_hash="b98dff566803b43b3c3120eec537fc1d"  # Use assistant's API hash
)

# Initialize PyTgCalls with the user client
pytgcalls = PyTgCalls(user)

async def get_active_call(chat_id: int):
    try:
        return await pytgcalls.get_active_call(chat_id)
    except GroupCallNotFound:
        return None

@bot.on_message(filters.command("join") & filters.group)
async def join_vc(_, m: Message):
    chat_id = m.chat.id
    
    try:
        # Create call if not exists
        if not await get_active_call(chat_id):
            await user.send(
                functions.phone.CreateGroupCall(
                    peer=await user.resolve_peer(chat_id),
                    random_id=user.rnd_id() // 9000000000
                )
            )
            await m.reply("✅ **Automatically started voice chat!**")

        # Join the call with silent audio
        await pytgcalls.join_group_call(
            chat_id,
            AudioPiped("http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"),
            stream_type="silent"  # Remove this if you have audio
        )
        await m.reply("🤖 **Assistant joined the voice chat!**")

    except ChatAdminRequired:
        await m.reply("❗ **Assistant needs admin rights to manage VC!**")
    except Exception as e:
        await m.reply(f"❌ Error: {str(e)}")

@bot.on_message(filters.command("leave") & filters.group)
async def leave_vc(_, m: Message):
    chat_id = m.chat.id
    try:
        await pytgcalls.leave_group_call(chat_id)
        await m.reply("👋 **Assistant left the voice chat!**")
    except Exception as e:
        await m.reply(f"❌ Error: {str(e)}")

async def main():
    await user.start()
    await bot.start()
    await pytgcalls.start()
    print("Bot & Assistant Ready!")
    await idle()

if __name__ == "__main__":
    asyncio.run(main())
