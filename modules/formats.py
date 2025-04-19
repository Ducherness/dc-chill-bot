import zlib
import string
from datetime import datetime
from random import sample
from typing import Optional, List, Union

def error_text(command: str, incorrect_value: str) -> str:
    words = command.split()
    position = words.index(incorrect_value)
    clear = sum(len(word) + 1 for word in words[:position])
    underline = '‾' * len(incorrect_value)
    return f"```{command}\n{' ' * clear}{underline}```"

def code_text(text: str) -> bytes:
    return zlib.compress(text.encode())

def decode_text(text: bytes) -> str:
    return zlib.decompress(text).decode()

def form_date(date: Optional[str] = None) -> Optional[str]:
    if date is None:
        datetime_date = datetime.now()
        return datetime_date.strftime('%d.%m.%Y')
    
    try:
        day, month, year = map(int, date.split('.'))
        if not (1 <= day <= 31 and 1 <= month <= 12 and year == datetime.now().year):
            return None
        if month == 2 and day > 29:
            return None
        return f"{day:02d}.{month:02d}.{year}"
    except (ValueError, IndexError):
        return None

def form_time_to_text(time_in_integer: int, words: List[str] = ['день', 'дня', 'дней']) -> str:
    if time_in_integer % 10 == 1 and time_in_integer % 100 != 11:
        return words[0]
    elif 2 <= time_in_integer % 10 <= 4 and (time_in_integer % 100 < 10 or time_in_integer % 100 >= 20):
        return words[1]
    return words[2]

def convert_time_to_seconds(time: str) -> Optional[int]:
    time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        return int(time[:-1]) * time_convert[time[-1]]
    except (KeyError, ValueError):
        return None

def generate_random_string(length: int) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(sample(chars, length))

class DateFormat:
    def __init__(self, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds

    def __str__(self) -> str:
        """Возвращает время в формате 'dd:hh:mm:ss' или 'hh:mm:ss'."""
        if self.days == 0:
            return f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
        return f"{self.days:02d}:{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"

def format_millis_to_time(millis: int) -> DateFormat:
    days, millis = divmod(millis, 86400000)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    seconds = millis // 1000
    return DateFormat(days, hours, minutes, seconds)

def format_time_to_millis(d: int = 0, h: int = 0, m: int = 0, s: int = 0) -> int:
    return d * 86400000 + h * 3600000 + m * 60000 + s * 1000
