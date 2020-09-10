from telegram.ext import MessageHandler,Filters,Updater,CommandHandler
import apiai
import logging
import datetime
from PIL import Image as Img, ImageDraw as ImgDr
import json
import os
from pyowm import OWM
from yandex import Translater
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
           '/resp - наши проекты и ответственные за них;\n' \
           '/help - помощь;\n' \
           '/path - построить маршрут до необходимой аудитории. Для этого введите /path <start_room> <target_room>;\n' \
           '/tasks - текущие задачи;\n' \
           '/info - о нас;\n' \
           '/covid_info - информация о COVID-19;\n' \
           '\n' \
           'Данный чатбот также умеет отображать погоду. Для это следует в начале сообщения указать "@stec_st_bot" ' \
           'и далее сделать запрос погоды, например "погода в москве"'
    update.message.reply_text(text)
    logging.info(text)
    update.message.text


def tasks(update,context):
    update.message.reply_text('Текущие задачи: ' )

def schedule(update,context):
    context.bot.send_photo(update.message.chat.id,open('1.jpg','rb'))

def help(update,context):
    update.message.reply_text('Тебе никто не поможет! Ты сам должен со всем разобраться!')

def info(update,context):
    update.message.reply_text('О нас:')
    context.bot.send_photo(update.message.chat.id,open('4.png','rb'))

def path(update,context):
    def get_path_picture(floor, building):
        path = os.path.abspath(building)
        pictures = os.listdir(path)
        for picture_name in pictures:
            if floor in picture_name:
                path_picture = os.path.join(path, picture_name)
                break
        return path_picture

    def get_floor(begin_place, finish_place):
        path = os.getcwd()
        # new building
        if len(finish_place) >= 4 and finish_place[0] == '0':
            floor = finish_place[1]
            path_picture = get_path_picture(floor, 'New')
            return floor
        # old building
        elif len(finish_place) < 4:
            floor = finish_place[0]
            path_picture = get_path_picture(floor, 'Old')
            return floor
        else:
            return 'ERROR: room is not defined'

    def get_floor_by_room(begin_place, finish_place):
        path = os.getcwd()
        # new building
        if len(finish_place) >= 4 and finish_place[0] == '0':
            floor = finish_place[1]
            path_picture = get_path_picture(floor, 'New')
            return path_picture
        # old building
        elif len(finish_place) < 4:
            floor = finish_place[0]
            path_picture = get_path_picture(floor, 'Old')
            return path_picture
        else:
            return 'ERROR: room is not defined'

    points = {}
    for line in open('points.txt'):
        line = line.split('\n')
        line = line[0]
        line = line.split(' ')
        line[1] = int(line[1])
        line[2] = int(line[2])
        points[line[0]] = line[1:]

    graphs = {}
    for line in open('graphs.txt'):
        line = line.split('\n')
        line = line[0]
        line = line.split(' ')
        graphs[line[0]] = line[1:]
    #############################

    # from tkinter import *
    # window = Tk()
    # canv = Canvas(window ,width=1000 ,height=600 ,bg="white")
    # ent1 = Entry(window ,width=2)
    # ent2 = Entry(window ,width=2)
    # but = Button(window ,text="Paths")

    ent1 = "enter"
    ent2 = context.args[1]

    def write_way_to_image(points, file_path):
        new_points = []
        for point in points:
            x, y = point
            new_points.append((x, y))

        with Img.open(file_path) as im:
            if new_points:
                radius = 10
                begin_ellipse = [(new_points[0][0] - radius, new_points[0][1] - radius)
                    , (new_points[0][0] + radius, new_points[0][1] + radius)]
                finish_ellipse = [(new_points[-1][0] - radius, new_points[-1][1] - radius)
                    , (new_points[-1][0] + radius, new_points[-1][1] + radius)]
            draw = ImgDr.Draw(im)
            draw.ellipse(begin_ellipse, fill=(239, 48, 56), width=6)
            draw.line(new_points, width=6, fill=(239, 48, 56))
            draw.ellipse(finish_ellipse, fill=(167, 252, 0), width=6)

            # write to stdout
            im.save("image_with_way_" + get_floor(context.args[0], context.args[1]) + ".png")

    def func_points():  # прорисовка точек
        for i in points:
            coords = points[i]
            x = coords[0]
            y = coords[1]
            # canv.create_rectangle(x ,y , x +5 , y +5 ,fill="black")
            # canv.create_text( x -5 , y -5 ,text=i)

    def check_graph(graph, first_p, second_p, col, indent):  # обработка каждого графа-маршрута
        colors = ["green", "red", "blue"]
        qty = 0  # Количество точек между заданными пользователем точками
        if first_p in graph:
            if second_p in graph:
                f = 0  # Где находится первая
                while first_p != graph[f]:  # определяем
                    f += 1
                s = 0  # Где находится вторая точка
                while second_p != graph[s]:
                    s += 1
                if f < s:  # Если первая точка встречается раньше, чем вторая:
                    qty = s - f  # количество точек от первой до второй
                    ramir_points = []
                    while f < s:  # прорисовка отрезков
                        coords = points[graph[f]]
                        x1 = coords[0]
                        y1 = coords[1]
                        ramir_points.append([x1, y1])
                        coords = points[graph[f + 1]]
                        x2 = coords[0]
                        y2 = coords[1]
                        ramir_points.append([x2, y2])

                        #
                        # canv.create_line(x1 +indent ,y1 +indent, \
                        #                  x2 +indent ,y2 +indent ,fill="green")

                        f += 1
                        write_way_to_image(ramir_points,
                                           get_floor_by_room(context.args[0], context.args[
                                               1]))  # points -- его данные с точками прям поинтс и оставь, path -- путь полученный из моей функции вчерашней, картинка со схемой на которой нужно нарисовать маршрут
                # сохранит там же где и скрипт в файл "image_with_way.png"
                else:
                    qty = f - s
                    ramir_points = []
                    while s < f:
                        coords = points[graph[f]]
                        x1 = coords[0]
                        y1 = coords[1]
                        ramir_points.append([x1, y1])
                        coords = points[graph[f - 1]]
                        x2 = coords[0]
                        y2 = coords[1]
                        ramir_points.append([x2, y2])

                        # canv.create_line(x1 +indent ,y1 +indent, \
                        #                  x2 +indent ,y2 +indent ,fill=colors[col])

                        f -= 1
                    write_way_to_image(ramir_points,
                                       get_floor_by_room(context.args[0], context.args[
                                           1]))  # points -- его данные с точками прям поинтс и оставь, path -- путь полученный из моей функции вчерашней, картинка со схемой на которой нужно нарисовать маршрут
        # сохранит там же где и скрипт в файл "image_with_way.png"
        col += 1
        indent += 2
        return qty, col, indent

    def func_paths():
        print('In func Path')
        # canv.delete('all')
        func_points()
        col = 0  # счетчик для цвета
        indent = 0  # отступ
        first_p = ent1
        second_p = ent2
        qty_points = 100
        min_graph = ' '
        for i in graphs:
            q, col, indent = check_graph \
                (graphs[i], first_p, second_p, col, indent)
            if q != 0 and q < qty_points:
                qty_points = q
                min_graph = i
        print('The shortest path:', min_graph)

    if (get_floor(context.args[0], context.args[1]) == '2'):
        func_paths()
        context.bot.send_photo(update.message.chat.id,
                               open("image_with_way_" + get_floor(context.args[0], context.args[1]) + ".png", 'rb'))
    else:
        context.bot.send_photo(update.message.chat.id,
                               open(get_floor_by_room(context.args[0], context.args[1]), 'rb'))


def covid_info(update,context):
    c_stat()
    context.bot.send_photo(update.message.chat.id, open('c_stat.png', 'rb'))
    api = CovId19Data(force=False)
    res = api.filter_by_country("russia")
    update.message.reply_text( f'На текущий момент: {res.get("confirmed")} подтвержденных случаев,\n '
                                             f'умерло - {res.get("deaths")},\n'
                                             f'выздоровело - {res.get("recovered")}.')



def resp(update,context):
    pass
    # update.message.reply_text('Утарбаев Рамазан (AR/VR) - виртуальное производство.\n'
    #                           'Островский Богдан (программирование) - SCADA.\n'
    #                           'Меликов Павел (программирование, электроника) - 3d принтер.\n'
    #                           'Абдулов Рамир (программирование) - SCADA.\n'
    #                           'Паленов Иван - прототипирование.\n')


#Отвечает за добавление новых участников
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
            data_time = responseJson.get('result').get('parameters').get('date-time')
            print(response)
            print(data_time)



            if response:  # Если есть ответ выводим
                owm = OWM(str(OWM_TOKEN))
                owm.set_language(language='ru')
                tr = Translater.Translater()
                tr.set_key(str(YAND_TOKEN))
                tr.set_text(response)
                tr.set_from_lang('ru')
                tr.set_to_lang('en')
                t_city = tr.translate()
                fc = owm.three_hours_forecast(t_city)
                print(fc)




                print(t_city)
                obs = owm.weather_at_place(t_city)
                print(owm.weather_at_place(t_city))
                w = obs.get_weather()
                t = w.get_temperature(unit='celsius')
                context.bot.send_message(chat_id=update.message.chat.id, text=response)
                context.bot.send_message(chat_id=update.message.chat.id, text =f'Сегодня ожидается: {w.get_detailed_status()}.\n' 
                                                                         f'Диапазон температу: от {t["temp_min"]}°С до ' 
                                                                         f'{t["temp_max"]}°С. Текущая температура: '
                                                                                f'{t["temp_max"]}°С\n'
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
    time = datetime.time(18,34,0)
    #Добавляем задание
    job.run_daily(sender,time)
    # Обработчик команд
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("resp", resp))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("path", path, pass_args=True))
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