import arrow
import os
import timezonefinder
import pickle
import requests
import datetime
import pytz
import io
import matplotlib.pyplot as plt
import matplotlib
import telebot
from weather_keys import api_key
from weather_settings import coord
matplotlib.use('agg')

def set_start_time():
    start = arrow.now().floor('day')
    start.to('UTC').timestamp()
    return start


def set_end_time():
    end = arrow.now().ceil('day')
    end.to('UTC').timestamp()
    return end


def check_responce_dir(name_dir: str):
    if name_dir not in os.listdir():
        os.mkdir(name_dir)


def get_date() -> str:
    return str(str(arrow.now().date().strftime('%Y-%m-%d')))


def get_zone(lat: float,lng: float) -> str:
    return str(timezonefinder.TimezoneFinder().certain_timezone_at(lat=lat, lng=lng)).replace('/', '_')


def get_from_files(date_zone: str, name_dir: str) -> tuple:
    with open(f'{name_dir}/responce_weather_{date_zone}.txt', 'rb') as file:
        responce_weather = pickle.load(file)
    with open(f'{name_dir}/responce_astronomy_{date_zone}.txt', 'rb') as file:
        responce_astronomy = pickle.load(file)
    with open(f'{name_dir}/responce_solar_{date_zone}.txt', 'rb') as file:
        responce_solar = pickle.load(file)
    return responce_weather, responce_astronomy, responce_solar


def request_weather(lat: float, lng: float, start, end, api_key: str = api_key):
    return requests.get(
        'https://api.stormglass.io/v2/weather/point',
        params={
            'lat': lat,
            'lng': lng,
            'params': ','.join(
                ['airTemperature', 'pressure', 'cloudCover', 'precipitation', 'visibility', 'humidity', 'waveHeight',
                 'waterTemperature', 'windSpeed']),
            'start': start.to('UTC').timestamp(),
            'end': end.to('UTC').timestamp()
        },
        headers={
            'Authorization': api_key
        }
    )


def request_astronomy(lat: float, lng: float, start, end, api_key: str = api_key):
    return requests.get(
            'https://api.stormglass.io/v2/astronomy/point',
            params={
                'lat': lat,
                'lng': lng,
                'params': ','.join(['sunrise', 'sunset']),
                'start': start.to('UTC').timestamp(),
                'end': end.to('UTC').timestamp()
            },
            headers={
                'Authorization': api_key
            }
        )


def request_solar(lat: float, lng: float, start, end, api_key: str = api_key):
    return requests.get(
            'https://api.stormglass.io/v2/solar/point',
            params={
                'lat' : lat,
                'lng' : lng,
                'params' : ','.join(['uvIndex']),
                'start' : start.to('UTC').timestamp(),
                'end' : end.to('UTC').timestamp()
            },
            headers={
                'Authorization': api_key
            }
        )


def save_responce_to_file(responce_weather, responce_astronomy, responce_solar, date_zone: str, name_dir: str):
    with open(f'{name_dir}/responce_weather_{date_zone}.txt','wb') as file:
        file.write(pickle.dumps(responce_weather))
    with open(f'{name_dir}/responce_astronomy_{date_zone}.txt','wb') as file:
        file.write(pickle.dumps(responce_astronomy))
    with open(f'{name_dir}/responce_solar_{date_zone}.txt','wb') as file:
        file.write(pickle.dumps(responce_solar))


def fill_parameters(parameters: list, responce_json: dict):
    for r in responce_json['meta']['params']:
        parameters.append(r)


def get_all_parameters_list(responce_weather, responce_solar) -> list:
    parameters: list = []
    fill_parameters(parameters, responce_weather.json())
    fill_parameters(parameters, responce_solar.json())
    parameters.append('sunrise')
    parameters.append('sunset')
    return parameters


def fill_dict_param_value(all_dict_param_value: dict,responce_json: dict):
    if 'hours' in responce_json.keys():
        for hour in responce_json['hours']:
            for key in all_dict_param_value.keys():
                if key in hour.keys():
                    all_dict_param_value[key].append(hour[key]['sg'])
    else:
        for key in all_dict_param_value.keys():
            if key in responce_json['data'][0]:
                all_dict_param_value[key] = responce_json['data'][0][key]


def get_all_dict_param_value(responce_weather, responce_solar, responce_astronomy) -> dict:
    all_dict_param_value: dict = dict()
    all_parameters_list = get_all_parameters_list(responce_weather=responce_weather, responce_solar=responce_solar)
    for p in all_parameters_list:
        all_dict_param_value[p] = []
    fill_dict_param_value(all_dict_param_value,responce_weather.json())
    fill_dict_param_value(all_dict_param_value,responce_solar.json())
    fill_dict_param_value(all_dict_param_value,responce_astronomy.json())
    return all_dict_param_value


def set_correct_time_zone(lat: float, lng: float, all_dict_param_value: dict) -> tuple:
    mess_date = datetime.datetime.strptime(all_dict_param_value['sunrise'], '%Y-%m-%dT%H:%M:%S+00:00')
    tz = pytz.timezone(get_zone(lat=lat, lng=lng).replace('_', '/'))
    mess_date_new_zone = tz.normalize(mess_date.astimezone(tz))
    try:
        delta = int(mess_date_new_zone.tzname())
    except ValueError:
        delta = int(str(mess_date_new_zone.tzinfo.tzname).split(str(mess_date_new_zone.tzname()))[-1].split(':')[0])
    sunrise = datetime.datetime.strptime(all_dict_param_value['sunrise'], '%Y-%m-%dT%H:%M:%S+00:00') + datetime.timedelta(
        hours=delta)
    sunset = datetime.datetime.strptime(all_dict_param_value['sunset'], '%Y-%m-%dT%H:%M:%S+00:00') + datetime.timedelta(
        hours=delta)
    sunrise_time = sunrise.strftime('%H:%M:%S')
    sunset_time = sunset.strftime('%H:%M:%S')
    return sunrise_time, sunset_time


def get_message_to_tg(sunrise_time, sunset_time, coord: tuple = coord) -> str:
    lat, lng = coord
    return str(coord).strip('(').strip(')') + '\n' \
        + get_zone(lat=lat, lng=lng).replace('_', '/') + '\n' \
        + str(arrow.now().date().strftime('%d.%m.%Y %A')) + '\n' \
        + f'sunrise: {sunrise_time}' + '\n' \
        + f'sunset: {sunset_time}'


def draw_graphs(all_parameters_list: list, all_dict_param_value: dict, all_dict_param_measure: dict, message: str) \
        -> list:
    graphs: list = []
    for p in all_parameters_list:  # Не больше 10 параметров типа list в all_parameters_list!!
        for key, value in all_dict_param_value.items():
            if type(value) == list and p == key:

                fig = plt.figure()
                if all_dict_param_value[p] != []:

                    plt.plot(all_dict_param_value[p])

                    plt.axis([0, 23, min(all_dict_param_value[p]) - 0.5, max(all_dict_param_value[p]) + 0.5])
                    plt.locator_params(axis='x', nbins=24)
                    plt.locator_params(axis='y', nbins=len(all_dict_param_value[p]))

                    plt.title(p)
                    plt.xlabel('Hours')
                    plt.ylabel(all_dict_param_measure[p])
                    plt.grid()

                    if graphs == []:
                        with io.BytesIO() as buf:
                            plt.savefig(buf)
                            buf.seek(0)
                            # форматируем картинки для телебота и запихиваем в массив
                            graphs.append(telebot.types.InputMediaPhoto(media=buf.read(), caption=message))
                    else:
                        with io.BytesIO() as buf:
                            plt.savefig(buf)
                            buf.seek(0)
                            # форматируем картинки для телебота и запихиваем в массив
                            graphs.append(telebot.types.InputMediaPhoto(media=buf.read()))
                    plt.close(fig=fig)
    return graphs
