from flask import Flask, render_template, jsonify
import datetime, random, requests, _random, json
import requests

_weather_cache = {
    "time": None,
    "temp": None,
    "humidity": None,
    "code": None
}

def get_weather(lat=60.39, lon=25.09):
    global _weather_cache

    now = datetime.datetime.now()

    if _weather_cache["time"] and (now - _weather_cache["time"]).seconds < 900:
        return (
            _weather_cache["temp"],
            _weather_cache["humidity"],
            _weather_cache["code"]
        )
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,weather_code"
        )

        r = requests.get(url)
        cur = r.json()["current"]

        temperature = cur["temperature_2m"]
        humidity = cur["relative_humidity_2m"]
        code = cur["weather_code"]

        _weather_cache["time"] = now
        _weather_cache["temp"] = temperature
        _weather_cache["humidity"] = humidity
        _weather_cache["code"] = code

        return temperature, humidity, code

    except Exception:
        if _weather_cache["temp"] is not None:
            return (
                _weather_cache["temp"],
                _weather_cache["humidity"],
                _weather_cache["code"]
            )

        return 0, 0, 0



months_list = ["January", "February", "March", "April", "May", "June", "Jule", "August", "September", "October", "November", "December"]
day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

NIGHT_THEME = False


app = Flask(__name__)
DB_FILE = "events.json"
var_buf = None

def getTheme(code, current_hour):
    global NIGHT_THEME

    if 4 <= current_hour <= 11:
        NIGHT_THEME = False
        theme_name = "bg-img/morning.png"
        if 0 <= code < 3:
            theme_name = "bg-img/morning.png"
        elif 3 <= code < 55:
            theme_name = "bg-img/day_cloudy.png"
        elif 61 <= code < 65 or 80 <= code < 82 or 95 < code < 99:
            theme_name = "bg-img/day_rainy.png"
        else: theme_name = "bg-img/day_snowy.png"
    elif 11 <= current_hour <= 16:
        NIGHT_THEME = False
        theme_name = "bg-img/day.png"
        if 0 <= code < 3:
            theme_name = "bg-img/morning.png"
        elif 3 <= code < 55:
            theme_name = "bg-img/day_cloudy.png"
        elif 61 <= code < 65 or 80 <= code < 82 or 95 < code < 99:
            theme_name = "bg-img/day_rainy.png"
        else: theme_name = "bg-img/day_snowy.png"
    elif 17 <= current_hour <= 21:
        NIGHT_THEME = False
        theme_name = "bg-img/evening.png"
        if 0 <= code < 3:
            theme_name = "bg-img/morning.png"
        elif 3 <= code < 55:
            theme_name = "bg-img/day_cloudy.png"
        elif 61 <= code < 65 or 80 <= code < 82 or 95 < code < 99:
            theme_name = "bg-img/day_rainy.png"
        else: theme_name = "bg-img/day_snowy.png"
    else:
        theme_name = "bg-img/night.png"
        NIGHT_THEME = True
        if 0 <= code < 3:
            theme_name = "bg-img/night.png"
        elif 3 <= code < 55:
            theme_name = "bg-img/night-cloudy.png"
        elif 61 <= code < 65 or 80 <= code < 82 or 95 < code < 99:
            theme_name = "bg-img/night-rainy.png"
        else: theme_name = "bg-img/night-snowy.png"
    return theme_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    now = datetime.datetime.now()
    today = now.day
    month = months_list[now.month - 1]
    week_day_num = day_list[now.weekday()]
    current_hour = now.hour
    temp, humi, code = get_weather()
    theme_name = getTheme(code, current_hour)
    global var_buf

    day_number = today
    month_name = month
    weekDay = week_day_num
    outdoor_temp = temp
    var_buf = outdoor_temp
    humidity_ouside = humi
    NTValue = None
    if NIGHT_THEME:
        NTValue = "rgb(230, 180, 17)"
    else: NTValue = "black"

    return jsonify({
        "day_number": day_number,
        "month_name": month_name,
        "weekDay": weekDay,
        "outdoor_temp": outdoor_temp,
        "humidity_outside": humidity_ouside,
        "theme": theme_name,
        "ntv": NTValue
    })

@app.route('/events')
def events():

    DB_LOADED = load_db()["events"]
    json_event_list = []
    for event in DB_LOADED:
        if event["day"] == day_number and event["month"] == month_name:
            if event["type"] == "birthday":
                json_event_list.append({
                    "icon": "---",
                    "text": f"---"
                })
            elif event["type"] == "---":
                json_event_list.append({
                    "icon": "---",
                    "text": f"---"
                })
    if len(json_event_list) > 0:
        return jsonify(json_event_list)
    else:
        json_event_list.append({
            "icon": "✔️",
            "text": f"No Events..."
        })
        return jsonify(json_event_list)

def load_db():
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

