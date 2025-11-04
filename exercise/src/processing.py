
def stats (rows: list[dict]) -> dict:
    if not rows:
        return {"count":0, "avg_age":0,"by_city": {}}
    ages=[(r["age"]) for r in rows ] 
    avg_ages=sum(ages)/len(ages) if ages else 0
    by_city={}
    for r in rows:
        city = r["city"]
        by_city[city] = by_city.get(city, 0) + 1
    return {"count": len(rows),"avg_age": avg_ages, "by_city": by_city}

def build_report(st:dict)->str:
    lines=[]
    lines.append("Rapor")
    lines.append("")
    lines.append(f"Geçerli kayıt sayısı: {st['count']}")
    lines.append(f"ortalama yaş: {st['avg_age']:.2f}")
    lines.append("Şehir dağılımı:")
    for c,n in st["by_city"].items():
        lines.append(f"  {c}: {n}")
    return  "\n".join(lines) +"\n"

def clean_data(rows: list[dict]) -> list[dict]:
    cleaned=[]
    for r in rows:
        name=r.get("name","").strip()
        age=r.get("age","").strip()
        city=r.get("city","").strip()
        
        if not age.isdigit():
            continue
        cleaned.append({"name": name,"age": int(age),"city": city
        })
    return cleaned