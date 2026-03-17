import time
import os
import cv2
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from nudenet import NudeDetector

TOKEN = "8755311088:AAE4nP_Sm6grF20OJcDpBmlSNZIheR6mYXM"

detector = NudeDetector()

bad_words = [
"sex","porn","xxx","chut","chudai","nude","18+","adult",
"hentai","nsfw","onlyfans","sex","porn",
"xxx","nude","18+","gandu","lund","bhosdkie",
"maa ke lode","maa ki chut","madarchod","chutiya",
"randi","bhenchod","bhen ke lode","gay","lesbian",
"laoda","lauda chusega","yek laoda fhaik krr marunga sara khandaan chud jayega",
"adult","jhaat ke baal","burchodi","laude","chusega",
"fuck","bitch","asshole","motherfucker"
]

user_messages = {}

async def moderate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message
    user = msg.from_user
    chat_id = msg.chat_id

    text = msg.text.lower() if msg.text else ""
    caption = msg.caption.lower() if msg.caption else ""

    member = await context.bot.get_chat_member(chat_id, user.id)
    is_admin = member.status in ["administrator","creator"]

    # 🔞 text detection
    for word in bad_words:
        if word in text or word in caption:

            await msg.delete()

            if not is_admin:
                await context.bot.ban_chat_member(chat_id, user.id)
                await context.bot.send_message(chat_id,    " Chal Nikal Laude ")

            return

    # 🎞 GIF / animation detection
    if msg.animation:

        file = await context.bot.get_file(msg.animation.file_id)
        path = "gif.mp4"
        await file.download_to_drive(path)

        cap = cv2.VideoCapture(path)
        frame_count = 0
        nsfw_found = False

        while cap.isOpened():
            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            if frame_count % 10 == 0:

                img = "frame.jpg"
                cv2.imwrite(img, frame)

                result = detector.detect(img)

                if len(result) > 0:
                    nsfw_found = True
                    break

        cap.release()

        if nsfw_found:

            await msg.delete()

            if not is_admin:
                await context.bot.ban_chat_member(chat_id, user.id)
                await context.bot.send_message(chat_id,"Porn GIF bhej raha tha — Nikal Bsdk")

        os.remove(path)

    # ⚡ spam detection
    now = time.time()

    if user.id not in user_messages:
        user_messages[user.id] = []

    user_messages[user.id].append(now)

    user_messages[user.id] = [t for t in user_messages[user.id] if now - t < 5]

    if len(user_messages[user.id]) > 5:

        if not is_admin:
            await context.bot.ban_chat_member(chat_id, user.id)
            await context.bot.send_message(chat_id,"Spam mat kar bsdk")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.ALL, moderate))

app.run_polling()