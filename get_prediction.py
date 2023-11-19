'''
Эта функция возвращает матрицу, где каждой координате соответствует вероятность возникновения заболевания в этом месте.
По сути матрицу вероятностей размером width * height * (количество заболеваний), где параметры width и height определены в cfg.json. 
'''
import sys
import os
import json
import numpy as np
import matplotlib.pyplot as plt
import tqdm
import datetime
import WeatherMatrixBuilder

cfg = {}
eps_t = 0
eps_u = 0
samples_per_day = 8
with open("illness_info.json", encoding="utf8") as f:
    illnesses = json.load(f)

grad_coord_x = {}
grad_coord_y = {}
timestamp = 0




def parse_date_to_timestamp(time_str):
    global timestamp
    time_str = time_str.replace(' ', '_').replace('.', '_').replace(':', '_')
    tm = list( time_str.split('_'))
    dt = datetime.datetime.fromisoformat(f"{tm[2]}{tm[1]}{tm[0]}T{tm[3]}0000")
    timestamp = int(dt.timestamp())

def unpack_matrix(file):#жсон

    data = np.load(file)
    return data
class IllnessMeter:
    def __init__(self, lowest_temp, highest_temp, 
                 lowest_wetness, highest_wetness, per) -> None:
        self.lt = lowest_temp
        self.ht = highest_temp
        self.lw = lowest_wetness
        self.hw = highest_wetness
        self.period = per * samples_per_day# количество измерений в день
        self.count = np.zeros((cfg["height"], cfg["width"]), dtype = int)
        self.cm = 0
    def step(self, matrix):
        self.cm+=1
        
        matrix = np.moveaxis(matrix, 0, -1)
        mat0 = matrix[:, :, 0]
        mat1 = matrix[:, :, 1]
        #print(mat0[1023][1700: 1710])
        m0 = mat0 <= (self.ht + eps_t)
        #print(m0[1023][1700: 1710])
        #print(self.lt-eps)
        m0 = np.logical_and(m0, mat0 >= (self.lt-eps_t))
        #tmp = mat0 >= (self.lt-eps)

        
        m1 = mat1 <= (self.hw + eps_u)
        m1 = np.logical_and(m1, mat1 >= (self.lw-eps_u))
        
        mask = np.logical_and(m1, m0)
        
        #print(mask[1023][1700: 1710])
        self.count[mask] += 1
        #print(np.max(self.count))
        #exit(0)
    def get_result(self):
        #print(np.max(self.count), self.period - eps)
        #print(self.cm)
        return self.count >= (self.period)

def get_meters(illness_info):
    res = []
    for name in illness_info.keys():
        res.append(
            IllnessMeter(lowest_temp=illness_info[name]["temperature_lb"], 
                         highest_temp=illness_info[name]["temperature_ub"],
                         lowest_wetness=illness_info[name]["wetness_lb"],
                         highest_wetness=illness_info[name]["wetness_ub"],
                         per = illness_info[name]["period"])
        )
    return res

def get_probability(mat_paths):
    
    meters = get_meters(illnesses)
    cnt = 0
    c =0 
    for path in tqdm.tqdm(mat_paths):# iterate over test_samples
        if not os.path.exists(path):
            cnt += 1
            continue
        mat = unpack_matrix(path)
        c+=1
        for m in meters:
            m.step(mat)
        
    return [m.get_result() for m in meters]






def construct_dic(x, y, name):
    return {"x": grad_coord_x[x], "y": grad_coord_y[y], "name": name}


def save_to_json(name, ans):
    
    json_res = {
        "timestamp": timestamp,
        "illness" : [
            "Милдью или ложная мучнистая роса",
            "Оидиум",
            "Антракноз",
            "Серая гниль",
            "Чёрная пятнистость",
            "Чёрная гниль",
            "Белая гниль",
            "Вертициллезное увядание",
            "Альтернариоз",
            "Фузариоз",
            "Краснуха",
            "Бактериальный рак"
        ],
        "data": []
    }
    for ill, mat in zip(range(len(illnesses)), ans):
        bad = np.asarray(mat.nonzero()).T
        if (bad.shape[0] == 0):
            continue
        print(len(bad))
        #print(np.apply_along_axis(lambda x: print(x[0]),  1,  bad[:10]))
        for x in tqdm.tqdm(bad):
            json_res["data"].append({"x": grad_coord_x[x[0]], "y": grad_coord_y[x[1]], "name": ill})
        #json_res += np.apply_along_axis(lambda x: {"x": grad_coord_x[x[0]], "y": grad_coord_y[x[1]], "name": ill},  1,  bad).tolist()
    
    with open(name, "w+", encoding="utf8") as f:
        json.dump(json_res, f, ensure_ascii=False)

    


#data format: dd.mm.yyyy_tt:tt
def get_matrix_ts(date_time):
    step = 10800
    parse_date_to_timestamp(date_time)
    cur = timestamp
    print(cur)
    mats = []
    for t in range(cur, 0,-10800):
        mats.append(f"{t}")
        if (len(mats) == 26):
            break
    return mats
     




if __name__ == "__main__":
    builder = WeatherMatrixBuilder.WeatherMatrixBuilder()
    grad_coord_x = builder.gr1
    grad_coord_y = builder.gr2


    with open("cfg.json") as f:
        cfg = json.load(f)
    eps_t = cfg['eps_t']
    eps_u = cfg['eps_u']
    predict_time = sys.argv[1]
    ts = get_matrix_ts(predict_time)
    paths = []
    for t in tqdm.tqdm(ts):
        paths.append(f"days_log/{t}.npy")
        if (os.path.exists(f"days_log/{t}.npy")):
            continue
        try:
            builder.produce(t, data="days_log_raw")
        except: pass
    ans = get_probability(paths) 
    save_path = f"zalupa_{predict_time}.json"
    save_to_json(save_path, ans)
    exit(0)
    
