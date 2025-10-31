#===========modules===========
import telebot
from openai import OpenAI
import logging
from config import BOT_API_TOKEN , OPENAI_TOKEN_KEY , MAX_HISTORY , HISTORY_FILE
import json
import os


#===========Create models===========
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)
bot = telebot.TeleBot(BOT_API_TOKEN)
client = OpenAI(api_key=OPENAI_TOKEN_KEY)

#===========Chat history saving functions===========
def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {tuple(k.split("|")) if "|" in k else k: v for k, v in data.items()}
        except:
            return {}
    return {}


def save_history():
    data = {f"{k[0]}|{k[1]}" if isinstance(k, tuple) else k: v for k, v in chat_history.items()}
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

chat_history = load_history()


def get_history_key(message):
    chat_id = str(message.chat.id)
    user_id = str(message.from_user.id)

    if message.chat.type in ["supergroup", "group"]:
        return (chat_id, user_id)
    else:
        return (chat_id, user_id)


def add_to_history(key, role, content):
    if key not in chat_history:
        chat_history[key] = [{"role": "system", "content": "Answer this question"}]
    
    chat_history[key].append({"role": role, "content": content})
    
    if len(chat_history[key]) > MAX_HISTORY:
        chat_history[key] = chat_history[key][-MAX_HISTORY:]
    save_history() 


#===========AI Request===========
def request_to_openai(messages):
        response = client.chat.completions.create(model="gpt-4o-mini" , messages=messages , temperature=0.7)
        return response.choices[0].message.content.strip()


#===========Bot handling===========
@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.send_message(chat_id=message.chat.id , text="Welcome to OpenAI chat bot!\nIn groups, start your message with '/'.\nAsk your question.👌")
    key = get_history_key(message)
    if key not in chat_history:
        add_to_history(key, "system", "Answer this question")


@bot.message_handler(commands=["clear"])
def clear_history_cmd(message):
    key = get_history_key(message)
    if key in chat_history:
        del chat_history[key]
        save_history()
    bot.reply_to(message, "🗑Your chat history has been deleted.")


@bot.message_handler(func=lambda message: message.chat.type == "private" or (message.chat.type in ["group", "supergroup"] and message.text and message.text.startswith("/")))
def handle_message(message):
    user_text = message.text
    if message.chat.type in ["supergroup", "group"] and user_text.startswith("/"):
        user_text = user_text[1:].strip()
    if not user_text:
        return
    
    user_key = get_history_key(message)
    add_to_history(user_key, "user", user_text)

    bot_message = bot.reply_to(message, "💎OpenAI is Thinking about your request...")

    messages = chat_history[user_key].copy()
    ai_response = request_to_openai(messages)

    add_to_history(user_key, "assistant", ai_response)

    try:
        bot.edit_message_text(chat_id=message.chat.id , message_id=bot_message.message_id , text=ai_response , parse_mode="Markdown")
    except:
        bot.edit_message_text(chat_id=message.chat.id , message_id=bot_message.message_id , text="❌Error❌")


#===========Run===========
while True:
      bot.infinity_polling()
