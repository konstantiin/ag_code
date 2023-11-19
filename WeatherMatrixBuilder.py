import json
import numpy as np
from scipy.interpolate import LinearNDInterpolator


class WeatherMatrixBuilder:
    def __init__(self, file="stations.json") -> None:
        with open(file) as f:
            s = json.load(f)
            self.indexes = []
            self.latitudes = []
            self.longitudes = []
            self.heights = []
            for i in s.keys():
                self.indexes.append(i)
                self.latitudes.append(s[i][1])
                self.longitudes.append(s[i][2])
                self.heights.append(s[i][3])
            self.gr1 = np.linspace(min(self.latitudes) - 0.3, max(self.latitudes) + 0.3, num=4096)
            self.gr2 = np.linspace(min(self.longitudes) - 0.3, max(self.longitudes) + 0.3, num=4096)
            self.x1, self.y1 = np.meshgrid(self.gr1, self.gr2)

    def produce(self, time, data="new_data"):
        t = []
        u = []
        for i in self.indexes:
            with open(f"{data}/{i}--{time}.json") as f:
                j = json.load(f)
            t.append(j[6]["T"])
            u.append(j[6]["U"])
        t_interpolator = LinearNDInterpolator(list(zip(self.latitudes, self.longitudes)), t)
        u_interpolator = LinearNDInterpolator(list(zip(self.latitudes, self.longitudes)), u)

        z_t = t_interpolator(self.x1, self.y1)
        z_u = u_interpolator(self.x1, self.y1)
        z_t = np.nan_to_num(z_t, nan=-300)
        z_u = np.nan_to_num(z_u, nan=-300)
        np.save(f"days_log/{time}.npy", np.array([z_t, z_u]))
