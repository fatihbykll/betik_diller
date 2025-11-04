from functools import wraps
import time

def timer(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        t0= time.perf_counter() # 0.andaki time
        result=func(*args,**kwargs)
        total_time=time.perf_counter()-t0
        print("total_time: ", total_time)
        return result
    return wrapper


def required_column(requireds: set[str]):
    def deco(func):
        @wraps(func)
        def wrapper(rows, *args,**kwargs):
            if not rows:
                raise ValueError("Boş veri seti")
            keys= set(rows[0].keys())
            missing=requireds-keys
            if missing:
                raise ValueError("Eksik kolon")
            return func(rows,*args,**kwargs)
        return wrapper
    return deco
        
                


