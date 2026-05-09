import requests
from django.conf import settings
from django.shortcuts import render, redirect
from django.urls import reverse

from .forms import WeatherForm

OWM_BASE = "https://api.openweathermap.org/data/2.5/weather"
COUNTRIES_BASE = "https://restcountries.com/v3.1/alpha"

FIELD_ICONS = {
    'temp_max':   '🌡️',
    'temp_min':   '❄️',
    'humidity':   '💧',
    'wind':       '💨',
    'pressure':   '🔵',
    'feels_like': '🧥',
    'visibility': '👁️',
    'clouds':     '☁️',
}

FIELD_LABELS = {
    'temp_max':   'Максимальна температура',
    'temp_min':   'Мінімальна температура',
    'humidity':   'Вологість',
    'wind':       'Швидкість вітру',
    'pressure':   'Тиск',
    'feels_like': 'Відчувається як',
    'visibility': 'Видимість',
    'clouds':     'Хмарність',
}


def _get_unit(key):
    units = {
        'temp_max':   ' °C',
        'temp_min':   ' °C',
        'feels_like': ' °C',
        'humidity':   ' %',
        'pressure':   ' hPa',
        'wind':       ' м/с',
        'visibility': ' км',
        'clouds':     ' %',
    }
    return units.get(key, '')


def _fetch_weather(city):
    try:
        resp = requests.get(OWM_BASE, params={
            'q':     city,
            'appid': settings.OPENWEATHER_API_KEY,
            'units': 'metric',
            'lang':  'uk',
        }, timeout=5)
    except requests.RequestException:
        return {'error': 'Помилка мережі. Спробуйте пізніше.'}

    if resp.status_code == 401:
        return {'error': 'Невірний API-ключ OpenWeatherMap.'}
    if resp.status_code == 404:
        return {'error': f'Місто "{city}" не знайдено. Перевірте назву.'}
    if resp.status_code != 200:
        return {'error': 'Помилка при отриманні даних погоди.'}

    data = resp.json()
    return {
        'city':        data['name'],
        'country':     data['sys']['country'],
        'description': data['weather'][0]['description'].capitalize(),
        'icon_url':    f"https://openweathermap.org/img/wn/{data['weather'][0]['icon']}@2x.png",
        'temp':        round(data['main']['temp']),
        'temp_max':    round(data['main']['temp_max']),
        'temp_min':    round(data['main']['temp_min']),
        'humidity':    data['main']['humidity'],
        'pressure':    data['main']['pressure'],
        'feels_like':  round(data['main']['feels_like']),
        'wind':        round(data['wind']['speed'], 1),
        'visibility':  round(data.get('visibility', 0) / 1000, 1),
        'clouds':      data['clouds']['all'],
    }


def _fetch_country(country_code):
    try:
        resp = requests.get(
            f"{COUNTRIES_BASE}/{country_code}",
            params={'fields': 'name,capital,population,region,subregion,flags'},
            timeout=5,
        )
        if resp.status_code != 200:
            return None
        data = resp.json()
        if isinstance(data, list):
            data = data[0]
        capital = data.get('capital', ['—'])[0] if data.get('capital') else '—'
        maps_url = (
            f"https://www.google.com/maps/search/?api=1&query={capital}"
            if capital != '—' else '#'
        )
        return {
            'name':       data['name']['common'],
            'capital':    capital,
            'population': f"{data.get('population', 0):,}".replace(',', '\u00a0'),
            'region':     data.get('region', '—'),
            'subregion':  data.get('subregion', '—'),
            'flag_url':   data.get('flags', {}).get('png', ''),
            'maps_url':   maps_url,
        }
    except Exception:
        return None


def index(request):
    form = WeatherForm()
    return render(request, 'weather/index.html', {'form': form})


def result(request):
    if request.method != 'POST':
        return redirect(reverse('weather:index'))

    form = WeatherForm(request.POST)
    if not form.is_valid():
        return render(request, 'weather/index.html', {'form': form})

    city            = form.cleaned_data['city'].strip()
    selected_fields = form.cleaned_data.get('fields', [])

    weather = _fetch_weather(city)
    if 'error' in weather:
        form.add_error('city', weather['error'])
        return render(request, 'weather/index.html', {'form': form})

    country_info = _fetch_country(weather['country'])

    display_fields = []
    for key in selected_fields:
        if key in weather:
            display_fields.append({
                'icon':  FIELD_ICONS.get(key, '📊'),
                'label': FIELD_LABELS.get(key, key),
                'value': f"{weather[key]}{_get_unit(key)}",
            })

    return render(request, 'weather/result.html', {
        'form':           WeatherForm(request.POST),
        'weather':        weather,
        'country':        country_info,
        'display_fields': display_fields,
    })
