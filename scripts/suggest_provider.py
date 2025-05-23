import requests, random, time, pathlib

SEEDS = (pathlib.Path("config/seeds.txt")
         .read_text(encoding="utf-8").splitlines())

def api(part: str) -> list[str]:
    url = ("https://suggest.yandex.net/suggest-ya.cgi"
           f"?v=4&uil=ru&part={part}")
    return requests.get(url, timeout=5).json()[1]

def get_daily(max_items=30) -> list[str]:
    random.shuffle(SEEDS)
    out = []
    for seed in SEEDS:
        for s in api(seed):
            if s not in out:
                out.append(s)
            if len(out) >= max_items:
                return out
        time.sleep(0.4)          # не бомбим API
    return out
