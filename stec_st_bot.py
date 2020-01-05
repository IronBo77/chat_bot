from telegram.ext import MessageHandler,Filters,Updater,CommandHandler
import apiai
import logging
import datetime
import json
from pyowm import OWM
import goslate
import os


'''
#При использовании прокси
#PROXY = {'proxy_url':'socks5://179.43.157.119:1080'}
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
    
'''

T_TOKEN = os.environ.get('TEL_TOKEN')
DF_TOKEN = os.environ.get('DL_FL_TOKEN')
OWM_TOKEN = os.environ.get('Op_We_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename= 'bot.log'
                    )

#Отвечает за отправку ежедневных сообщений
def sender(context):
    context.bot.send_message(-1001171884119,f'Уже {datetime.date.today()}, а мы до сих пор еще ничего не сделали!')

#Обработка команды старт
def start(update,context):
    text = 'Команды для чат бота:\n' \
           '/start - ознакомиться с возможностями бота;\n' \
           '/resp - наши проекты и ответственные за них;\n' \
           '/help - помощь;\n' \
           '/tasks - текущие задачи;\n' \
           '/info - о нас;\n' \
           '\n' \
           'Данный чатбот также умеет отображать погоду. Для это следует в начале сообщения указать "@bot_name" ' \
           'и далее сделать запрос погоды, например "погода в москве"'
    update.message.reply_text(text)
    print('это старт')
    logging.info(text)

def tasks(update,context):
    update.message.reply_text('Текущие задачи:')

def help(update,context):
    update.message.reply_text('Тебе никто не поможет! Ты сам должен со всем разобраться!')

def info(update,context):
    update.message.reply_text('О нас:')
    print('это инфо')

def resp(update,context):
    update.message.reply_text('Основные направления\n'
                              )


#Отвечает за приветствие новых участников
def new_member(update,context):
    for members in update.message.new_chat_members:
        print(update.message)
        context.bot.send_message(update.message.chat.id, f'Здравствуйте, {members.first_name} (@{members.username})!\n'
                                                 f'Рады приветствовать вас в группе "{update.message.chat.title}".\n'
                                                  'Чтобы ознакомиться с возможностями чат бота введите "/start".\n')




#Обработка сообщений
def talk_to_me(update,context):
    user_text = f'Привет {update.message.from_user.first_name} (@{update.message.from_user.username})! ' \
                f'Ты написал "{update.message.text}".'
    comm_text ='Добавьте "/" перед названием команды'

    dict_words = {
        'Тест': [update.message.reply_text,user_text],
        'тест': [update.message.reply_text,user_text],
        'start': [update.message.reply_text,comm_text],
        'help': [update.message.reply_text, comm_text],
        'resp': [update.message.reply_text, comm_text]
    }
    if update.message.text in dict_words:
        dict_words.get(update.message.text)[0](dict_words.get(update.message.text)[1])
    else:
        request = apiai.ApiAI(str(DF_TOKEN)).text_request()  # Токен для авторизации в Dialogflow
        request.lang = 'ru'  # Указвыаем язык запроса
        request.session_id = 'BotNameST'  # Id сессии диалога
        text = update.message.text
        if context.bot.name in text:
            request.query = text
            responseJson = json.loads(request.getresponse().read().decode('utf-8'))
            print( responseJson)
            response = responseJson.get('result').get('parameters').get('address').get('city')
            print(response)

            if response:  # Если есть ответ выводим
                context.bot.send_message(chat_id=update.message.chat.id, text=response)
                owm = OWM(str(OWM_TOKEN))
                owm.set_language(language='ru')
                t_city = goslate.Goslate().translate(response, 'en')
                print(t_city)
                obs = owm.weather_at_place(t_city)
                print(owm.weather_at_place(t_city))
                w = obs.get_weather().get_temperature(unit='celsius')
                context.bot.send_message(chat_id=update.message.chat.id, text = w['temp'])

            else:  # Если нет говорим что запрос не понятен
                context.bot.send_message(chat_id=update.message.chat.id, text='Не совсем понял Ваш запрос')



def main():
    mybot = Updater(token=str(T_TOKEN),use_context=True)
    dp = mybot.dispatcher
    #Добавляем задание в очередь
    job = mybot.job_queue
    print('Бот стартовал')
    #Время дня в которое будет выполнятся ежедневное задание
    time = datetime.time(12,30,0)
    #Добавляем задание
    job.run_daily(sender,time)
    # Обработчик команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("resp", resp))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("tasks", tasks))
    # Обработчик сообщений
    dp.add_handler(MessageHandler(Filters.text,talk_to_me))
    # Обработчик добавления новых участников
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    mybot.start_polling()
    mybot.idle()


main()
