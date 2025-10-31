import telebot
from openai import OpenAI
from config import BOT_API_TOKEN , OPENAI_TOKEN_KEY
import logging



bot = telebot.TeleBot(BOT_API_TOKEN)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

client = OpenAI(api_key=OPENAI_TOKEN_KEY)



def request_to_OpenAI(request):
    messages = [
          {
            "role" : "system" ,
            "content" : "Answer this question"
          },
          {
            "role" : "user" ,
            "content" : request
          },
    ]
    a_response = client.chat.completions.create(model="gpt-4o-mini" , messages=messages)
    response = a_response.choices[0].message.content.strip()
    return response



@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.send_message(chat_id=message.chat.id , text="Welcome to OpenAI chat bot!\nIn groups, start your message with '/'.\nAsk your question.👌")


@bot.message_handler(func=lambda message : message.chat.type in ["supergroup" , "group"] and message.text.startswith("/"))
def handle_message_in_group(message):
        try:
          response_message = bot.reply_to(message=message , text="💎OpenAI is Thinking about your request...")
          AI_response = request_to_OpenAI(message.text[1:])
          bot.edit_message_text(text=AI_response , chat_id=message.chat.id , message_id=response_message.message_id , parse_mode="MarkDown")
        except:
             bot.edit_message_text(text="❌Error❌" , chat_id=message.chat.id , message_id=response_message.message_id)


@bot.message_handler(func=lambda message : message.chat.type in ["private"])
def handle_message_in_private(message):
        try:
          response_message = bot.reply_to(message=message , text="💎OpenAI is Thinking about your request...")
          AI_response = request_to_OpenAI(message.text)
          bot.edit_message_text(text=AI_response , chat_id=message.chat.id , message_id=response_message.message_id , parse_mode="MarkDown")
        except:
             bot.edit_message_text(text="❌Error❌" , chat_id=message.chat.id , message_id=response_message.message_id)


while True:
    bot.infinity_polling()
