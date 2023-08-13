import os
import weather_lib
from weather_settings import coord, all_dict_param_measure, name_dir

def weather_painter() -> list:

    # устанавливается время
    start = weather_lib.set_start_time()
    end = weather_lib.set_end_time()

    # устанавливаем координаты
    lat, lng = coord

    # создаём папку responces
    weather_lib.check_responce_dir(name_dir=name_dir)

    # определяем текущую дату и зону по координатам
    date_zone = weather_lib.get_date()+'_'+weather_lib.get_zone(lat=lat, lng=lng)

    # провеяем, есть ли сегодняшние файлы
    file_list = [_ for _ in os.listdir(name_dir) if date_zone in _ ]
    # если есть, открывем их, если нет - тянем запросом и сохраняем в файлы
    if file_list != []:
        responce_weather, responce_astronomy, responce_solar = weather_lib.get_from_files(date_zone=date_zone, \
                                                                                          name_dir=name_dir)
    else:
        # запросы
        responce_weather = weather_lib.request_weather(lat=lat, lng=lng, start=start, end=end)
        responce_astronomy = weather_lib.request_astronomy(lat=lat, lng=lng, start=start, end=end)
        responce_solar = weather_lib.request_solar(lat=lat, lng=lng, start=start, end=end)
        # save responces to files
        weather_lib.save_responce_to_file(responce_weather=responce_weather, responce_astronomy=responce_astronomy, \
                                          responce_solar=responce_solar, date_zone=date_zone, name_dir=name_dir)

    # заполняем список параметров
    all_parameters_list = weather_lib.get_all_parameters_list(responce_weather=responce_weather, \
                                                              responce_solar=responce_solar)

    #формируем словарь параметр-значение по часам
    all_dict_param_value = weather_lib.get_all_dict_param_value(responce_weather=responce_weather, \
                                                                responce_solar=responce_solar, \
                                                                responce_astronomy=responce_astronomy)
    # перевод давления в мм рт.ст.
    all_dict_param_measure['pressure'] = 'mmHg'
    all_dict_param_value['pressure'] = [round(i * 0.75006375541921,2) for i in all_dict_param_value['pressure']]


    # колдунство с часовыми поясами
    sunrise_time, sunset_time = weather_lib.set_correct_time_zone(lat=lat, lng=lng, \
                                                                  all_dict_param_value=all_dict_param_value)

    # формируем сообщение для отправки в тг
    message: str = weather_lib.get_message_to_tg(sunrise_time=sunrise_time, \
                                                 sunset_time=sunset_time)

    # проверка на 10 параметров
    if len([type(i) for i in all_dict_param_value.values() if type(i) == list]) <= 10:
        # рисуем графики
        graphs = weather_lib.draw_graphs(all_parameters_list=all_parameters_list, \
                                         all_dict_param_value=all_dict_param_value, \
                                         all_dict_param_measure=all_dict_param_measure, \
                                         message=message)
        return graphs
    else:
        return []
