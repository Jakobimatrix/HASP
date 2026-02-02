import time
from typing import NamedTuple
from datetime import datetime
from config.template_config import TIME_FORMAT

class Timestamp(NamedTuple):
    seconds: int
    nanoseconds: int

def get_timestamp() -> Timestamp:
    unix_time_ns = time.time_ns()
    unix_time_s = unix_time_ns // 1_000_000_000
    unix_time_subsec = unix_time_ns % 1_000_000_000
    return Timestamp(unix_time_s, unix_time_subsec)

def format_timestamp_seconds(seconds: int) -> str:
    return datetime.utcfromtimestamp(seconds).strftime(TIME_FORMAT)