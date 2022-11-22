import functools
from typing import Callable
from datetime import datetime

def timeworker(func : Callable) -> Callable:
    @functools.wraps(func)
    def check_worker_performance(*args,**kwargs):
        then = datetime.now()
        result = func(*args,**kwargs)
        print(f"Worker 🔨 finished within {(datetime.now()-then).total_seconds():.2f}")
        return result
    return check_worker_performance
