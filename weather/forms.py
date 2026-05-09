from django import forms

FIELD_CHOICES = [
    ('temp_max',    'Максимальна температура'),
    ('temp_min',    'Мінімальна температура'),
    ('humidity',    'Вологість'),
    ('wind',        'Швидкість вітру'),
    ('pressure',    'Тиск'),
    ('feels_like',  'Відчувається як'),
    ('visibility',  'Видимість'),
    ('clouds',      'Хмарність'),
]


class WeatherForm(forms.Form):
    city = forms.CharField(
        label='Місто',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Наприклад: Kyiv, London, New York',
            'autofocus': True,
        }),
    )
    fields = forms.MultipleChoiceField(
        label='Показати дані',
        choices=FIELD_CHOICES,
        widget=forms.CheckboxSelectMultiple(),
        initial=['temp_max', 'temp_min', 'humidity', 'wind'],
        required=False,
    )
