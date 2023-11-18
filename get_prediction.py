'''
Эта функция возвращает матрицу, где каждой координате соответствует вероятность возникновения заболевания в этом месте.
По сути матрицу вероятностей размером width * height * (количество заболеваний), где параметры width и height определены в cfg.json. 
'''
import sys
import json
import numpy as np
import matplotlib.pyplot as plt
import tqdm
cfg = {}
eps = 3
samples_per_day = 8
days = 3
with open("illness_info.json", encoding="utf8") as f:
    illnesses = json.load(f)

grad_coord_x = {}
grad_coord_y = {}








def unpack_matrix(file):#жсон
    with open(file) as f:
        data = np.asarray(json.load(f))
    return data
class IllnessMeter:
    def __init__(self, lowest_temp, highest_temp, 
                 lowest_wetness, highest_wetness, per) -> None:
        self.lt = lowest_temp
        self.ht = highest_temp
        self.lw = lowest_wetness
        self.hw = highest_wetness
        self.period = per * 8# количество измерений в день
        self.count = np.zeros((cfg["height"], cfg["width"]), dtype = int)
    def step(self, matrix):
        mat0 = matrix[:, :, 0]
        mat1 = matrix[:, :, 1]
        m0 = np.where(mat0 <= self.ht + eps, True, False)
        m0 = np.logical_and(m0, np.where(mat0 >= self.lt - eps, True, False))

        m1 = np.where(mat1 <= self.ht + eps, True, False)
        m1 = np.logical_and(m1, np.where(mat1 >= self.lt - eps, True, False))
        mask = m0 == m1 
        mask = mask == m0
        self.count[mask] += 1
    def get_result(self):
        return np.where(self.count >= self.period - eps, 1, 0)

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
    for path in tqdm.tqdm(mat_paths):# iterate over test_samples
        mat = unpack_matrix(path)
        [m.step(mat) for m in meters]
    
    
    return [m.get_result() for m in meters]






def construct_dic(x, y, name):
    return {"x": grad_coord_x[x], "y": grad_coord_y[y], "name": name}

def save_to_json(name, ans):
    
    json_res = []
    for ill, mat in map(illnesses.keys(), ans):
        json_res += np.apply_along_axis(lambda x, y: {"x": grad_coord_x[x], "y": grad_coord_y[y], "name": ill},  1,  np.asarray(mat.nonzero()).T).tolist()

    with open(name, "w+") as f:
        json.dump(json_res)

    


#data format: dd.mm.yyyy_tt:tt
def get_matrix_paths(date_time):
     return []




if __name__ == "__main__":

    grad_coord_x = get_grad_coord_x()
    grad_coord_y = get_grad_coord_y()


    with open("cfg.json") as f:
        cfg = json.load(f)
    predict_time = sys.argv[1]
    paths = get_matrix_paths(predict_time)
    ans = get_probability(paths) 
    save_path = f"zalupa_{predict_time}.json"
    save_to_json(save_path, ans)
    exit(0)
    

