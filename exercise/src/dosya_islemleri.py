from pathlib import Path
from .dekorator import timer,required_column
import csv,json

@timer
def read_csv(path):
    with Path(path).open("r", encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f)) # her satırı bir listeye atar

@timer
def write_json(path, obj):
    with Path(path).open("w",encoding="utf-8") as f:
        json.dump(obj,f)

@timer
def write_text(path,text):
    Path(path).write_text(text,encoding="utf-8")