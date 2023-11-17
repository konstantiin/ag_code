'''
Хуйня которая парсит данные и сохраняет их в виде жсончиков в days_log_raw в формате [время, id станции, имя станции, широта, 
долгота, высота, {метеорологический_параметр: значение}]
'''
import json
import wget
import pandas as pd

def parse_csv(file):
    df = pd.read_csv(file, sep = ';', comment = '#')

    res = df.transpose().to_dict()
    return res



def parse_weather(start, finish):#dd.mm.yyyy
    '''

    функция сохраняет файлы в папку days_log_raw c именем id-day вида [время, имя_станции, широта, долгота, высота, [{параметр_погоды: значение}]],


    Разумеется эта херня не работает нормально, потому что у них сайт генерирует ссылку на скачивание только при взаимодействии с интерфейсом.
    API у них то ли нет то ли я его не нашёл, если кто-то это пофиксит будет збс. Пока что я просто скачаю данные за месяц.
    '''
    with open("stations.json", encoding="utf-8") as f:
        stations = json.loads(f.read())
    
    for id in stations.keys():
        path = f"https://ru1.rp5.ru/download/files.synop/{id[:2]}/{id}.{start}.{finish}.1.0.0.ru.utf8.00000000.csv.gz"
        destination = f"{id}-{start}-{finish}.csv.gz"
        while (True):
            try:
                wget.download(path, destination)    
                print("good: " + path)
                break
            except:
                print("wrong: " + path)
                if (path[10] == '9'):
                    break
                path = path[:10] + str(int(path[10])+1) + path[11:]
                
        data = parse_csv(destination)
        for key in data.keys():
            dt = [key, id] + stations[id] + [data[key]]


            with open(f"days_log_raw/{id}--{key.replace('.', '-').replace(':', '-').replace(' ', '_')}.json", "w+", encoding='utf-8') as f:
                json.dump(dt, f, ensure_ascii=False)

if  __name__ == "__main__":
    parse_weather("01.04.2021", "01.05.2021")


