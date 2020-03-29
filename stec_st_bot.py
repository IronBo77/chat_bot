from telegram.ext import MessageHandler,Filters,Updater,CommandHandler
import apiai
import logging
import datetime
import json
from pyowm import OWM
from yandex import Translater
import os
#для статистики
from matplotlib import pyplot as plt
from covid.api import CovId19Data
import datetime as DT
import matplotlib.ticker as ticker

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
YAND_TOKEN = os.environ.get('YT_TOKEN')

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename= 'bot.log'
                    )



def c_stat():
    # для статистики
    api = CovId19Data(force=False)
    x = []
    confirmed = []
    deaths = []

    res2 = api.get_history_by_country("russia")

    for dates in res2.get('russia').get('history'):
        date = DT.datetime.strptime(dates, '%Y-%m-%d %H:%M:%S').date()
        x.append(date.strftime('%m/%d'))

    for cases in res2.get('russia').get('history').keys():
        confirmed.append(res2.get('russia').get('history').get(cases)['confirmed'])

    fig, ax = plt.subplots()
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    #  Устанавливаем интервал вспомогательных делений:
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(2))

    ax.plot(x, confirmed, color='r', linewidth=3)

    #  Добавляем линии основной сетки:
    ax.grid(which='major',
            color='k')

    #  Включаем видимость вспомогательных делений:
    ax.minorticks_on()
    #  Теперь можем отдельно задавать внешний вид
    #  вспомогательной сетки:
    ax.grid(which='minor',
            color='gray',
            linestyle=':')

    plt.xticks(rotation=60)
    ax.set_title('Подтвержденные случаи COVID-19 в России', fontsize=16)
    ax.set_xlabel('Период', fontsize=14)
    ax.set_ylabel('Количество людей', fontsize=14)

    fig.tight_layout()
    # plt.show()
    fig.savefig('c_stat')

#Отвечает за отправку ежедневных сообщений
def sender(context):
    context.bot.send_message(-1001171884119,f'Уже {datetime.date.today()}, а мы до сих пор еще ничего не сделали!')
    c_stat()
    context.bot.send_photo(-1001171884119, open('c_stat.png', 'rb'))
    api = CovId19Data(force=False)
    res = api.filter_by_country("russia")
    context.bot.send_message(-1001171884119, f'На текущий момент: {res.get("confirmed")} подтвержденных случаев,\n '
                                             f'{res.get("deaths")} умерло,\n'
                                             f'{res.get("recovered")} выздоровело.')

#Обработка команды старт
def start(update,context):
    text = 'Команды для чат бота:\n' \
           '/start - ознакомиться с возможностями бота;\n' \
           '/schedule - расписание;\n' \
           '/resp - наши проекты и ответственные за них;\n' \
           '/help - помощь;\n' \
           '/tasks - текущие задачи;\n' \
           '/covid_info - информация о COVID-19;\n' \
           '/info - о нас;\n' \
           '\n' \
           'Данный чатбот также умеет отображать погоду. Для это следует в начале сообщения указать "@bot_name" ' \
           'и далее сделать запрос погоды, например "погода в москве"'
    update.message.reply_text(text)
    print('это старт')
    logging.info(text)

def tasks(update,context):
    update.message.reply_text('Текущие задачи:')

def schedule(update,context):
    context.bot.send_photo(update.message.chat.id,open('1.jpg','rb'))

def help(update,context):
    update.message.reply_text('Тебе никто не поможет! Ты сам должен со всем разобраться!')

def covid_info(update,context):
    c_stat()
    context.bot.send_photo(update.message.chat.id, open('c_stat.png', 'rb'))
    api = CovId19Data(force=False)
    res = api.filter_by_country("russia")
    update.message.reply_text( f'На текущий момент: {res.get("confirmed")} подтвержденных случаев,\n '
                                             f'умерло - {res.get("deaths")},\n'
                                             f'выздоровело - {res.get("recovered")}.')

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
                owm = OWM(str(OWM_TOKEN))
                owm.set_language(language='ru')
                tr = Translater.Translater()
                tr.set_key(str(YAND_TOKEN))
                tr.set_text(response)
                tr.set_from_lang('ru')
                tr.set_to_lang('en')
                t_city = tr.translate()
                print(t_city)
                obs = owm.weather_at_place(t_city)
                print(owm.weather_at_place(t_city))
                w = obs.get_weather()
                t = w.get_temperature(unit='celsius')
                context.bot.send_message(chat_id=update.message.chat.id, text=response)
                context.bot.send_message(chat_id=update.message.chat.id,
                                         text=f'Сегодня ожидается: {w.get_detailed_status()}.\n'
                                              f'Диапазон температу: от {t["temp_min"]}°С до '
                                              f'{t["temp_max"]}°С. Текущая температура: '
                                              f'{t["temp"]}°С\n'
                                              )
            else:  # Если нет говорим что запрос не понятен
                context.bot.send_message(chat_id=update.message.chat.id, text='Не совсем понял Ваш запрос')



def main():
    mybot = Updater(token=str(T_TOKEN),use_context=True)
    dp = mybot.dispatcher
    #Добавляем задание в очередь
    job = mybot.job_queue
    print('Бот стартовал')
    #Время дня в которое будет выполнятся ежедневное задание
    time = datetime.time(9,30,0)
    #Добавляем задание
    job.run_daily(sender,time)
    # Обработчик команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("resp", resp))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("tasks", tasks))
    dp.add_handler(CommandHandler("schedule", schedule))
    dp.add_handler(CommandHandler("covid_info", covid_info))
    # Обработчик сообщений
    dp.add_handler(MessageHandler(Filters.text,talk_to_me))
    # Обработчик добавления новых участников
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, new_member))

    mybot.start_polling()
    mybot.idle()


main()
