from telegram.ext import Updater
from telegram.ext import MessageHandler
from telegram.ext import Filters
from telegram.ext import Updater
from telegram.ext import CommandHandler
import logging
import os


REQUEST_KWARGS={
    'proxy_url':'socks5://179.43.157.119:1080',
    # Optional, if you need authentication:
    'urllib3_proxy_kwargs': {
        'assert_hostname': 'False',
        'cert_reqs': 'CERT_NONE'
        # 'username': 'user',
        # 'password': 'password'
    }
    }

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename= 'bot.log'
                    )

def greet_user(update,context):
    text = 'Vizvan start'
    update.message.reply_text(text)
    logging.info(text)

def talk_to_me(update,context):
    if update.message.text=='тест':
        user_text = f'Привет {update.message.from_user.first_name} ({update.message.from_user.username})! ' \
                f'Ты написал "{update.message.text}".'
        update.message.reply_text(user_text)
    else:
        user_text = update.message.text
        print(user_text)
        print(update.message)
        update.message.reply_text(user_text)



def main():
    TOKEN = os.environ.get('MY_TOKEN')
    mybot = Updater(token=str(TOKEN),use_context=True)
    dp = mybot.dispatcher

    print('Бот стартовал')
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(MessageHandler(Filters.text,talk_to_me))
    mybot.start_polling()
    mybot.idle()


main()
