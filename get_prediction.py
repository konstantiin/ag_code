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
        self.period = per * 6# количество измерений в день
        self.count = np.zeros((cfg["height"], cfg["width"]), dtype = int)
    def step(self, matrix):
        mat0 = matrix[:, :, 0]
        mat1 = matrix[:, :, 1]
        m0 = np.ma.masked_where(mat0 <= self.ht, mat0) 
        m0 = np.logical_and(m0, np.ma.masked_where(mat0 >= self.lt, mat0))

        m1 = np.ma.masked_where(mat1 <= self.hw , mat1)
        m1 = np.logical_and(m1, np.ma.masked_where(mat1 >= self.lw, mat1))
        mask = m0 == m1 
        mask = mask == m0
        self.count = self.count + 1
        self.count[~mask] = 0
    def get_result(self):

        return self.count

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

def get_probability():
    with open("illness_info.json", encoding="utf8") as f:
        illnesses = json.load(f)
    meters = get_meters(illnesses)

    for i in tqdm.tqdm(range(1)):# iterate over test_samples
        mat = unpack_matrix(f"days_log/test_sample-{i}.json")# потом изменим на нужное имя
        [m.step(mat) for m in meters]
    
    return [m.get_result() for m in meters]
                  


if __name__ == "__main__":
    with open("cfg.json") as f:
        cfg = json.load(f)

    ans = get_probability()
    print(ans[0])
    plt.matshow(ans[0])
    plt.show()

