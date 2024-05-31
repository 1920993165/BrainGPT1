import json, requests
from Functions.weather.utils import *
from Utils.tools import log

def weather_search_city(city):
	key = get_config()['weather']['weather_key']
	url = f"https://geoapi.qweather.com/v2/city/lookup?location={city}&key={key}"
	response = requests.get(url)
	response = json.loads(response.text)
	city_id = response['location'][0]['id']
	return int(city_id)

def weather_get(id):
	key = get_config()['weather']['weather_key']
	url = f"https://devapi.qweather.com/v7/weather/now?location={id}&key={key}"
	response = requests.get(url)
	response = json.loads(response.text)
	return response

def weather_get_tmr(id):
	key = get_config()['weather']['weather_key']
	url = f"https://devapi.qweather.com/v7/weather/3d?location={id}&key={key}"
	response = requests.get(url)
	response = json.loads(response.text)
	return response['daily'][1]

def weather_search_local(city):
	import numpy as np
	data = np.loadtxt("Functions/weather/Weather_Location_Name.csv", delimiter=",", dtype=str, encoding='utf-8')
	for cities in data:
		if cities in city:
			return cities
	else:
		return get_config()['weather']['preferred_location']

def wea_run(city : str, question_time:str):
    prompt=city
    if question_time=="明天":
        log("Retrieving tomorrow's weather", "EVENT")
        city = weather_search_local(prompt)
        id = weather_search_city(city)
        print(id)
        info = json.dumps(weather_get_tmr(id), ensure_ascii=False)
        info = json.loads(info)
        temp_max = info['tempMax']
        temp_min = info['tempMin']
        text_day = info['textDay']
        text_night = info['textNight']
        wind_dir_day = info['windDirDay']
        wind_scale_day = info['windScaleDay']
        wind_dir_night = info['windDirNight']
        wind_scale_night = info['windScaleNight']
        return f"已知明天{city}最高温度为{temp_max}摄氏度，最低温度为{temp_min}摄氏度，白天天气为{text_day}，吹{wind_scale_day}级{wind_dir_day}；晚上天气为{text_night}，吹{wind_scale_night}级{wind_dir_night}，"
        # return {"add": f"已知明天{city}最高温度为{temp_max}摄氏度，最低温度为{temp_min}摄氏度，白天天气为{text_day}，吹{wind_scale_day}级{wind_dir_day}；晚上天气为{text_night}，吹{wind_scale_night}级{wind_dir_night}，", "prefix": "", "suffix": ""}
    else:
        log("Retrieving today's weather", "EVENT")
        city = weather_search_local(prompt)
        id = weather_search_city(city)
        info = json.dumps(weather_get(id), ensure_ascii=False)
        info = json.loads(info)
        # print(info)
        temp = info['now']['temp']
        text = info['now']['text']
        wind_dir = info['now']['windDir']
        wind_scale = info['now']['windScale']
        return f"已知现在{city}天气为{text}，温度为{temp}摄氏度，吹{wind_scale}级{wind_dir}，"
        # return {"add": f"已知现在{city}天气为{text}，温度为{temp}摄氏度，吹{wind_scale}级{wind_dir}，", "prefix": "", "suffix": ""}


if __name__=="__main__":
    print(wea_run("上海","明天"))