"""
Missing Values & Boundary Matrix Generation
"""

import numpy as np
import pandas as pd


def random_index_noise(x, ratio, placeholder=np.nan):
    size = round(len(x) * ratio)
    idx = np.random.randint(low=0, high=len(x), size=size)
    x[idx] = placeholder
    return x


def random_interval_noise(x, min_size, max_size, placeholder=np.nan):
    width = np.random.randint(min_size, max_size)
    where = np.random.randint(0, len(x) - width)
    x[where: where + width] = placeholder
    return x


def apply(X, params):
    '''
    * Lặp hàm `apply_ion_series()` cho tất cả các dòng numpy array 2D

    Chọn ngẫu nhiên 2 lựa chọn:
    1. Random Indices Noise: Cho một `missing value rato`
    2. Random Interval Noise: Cho một độ rộng `width` liên tiếp
    '''

    columns = X.columns

    def apply_on_series(x):
        if np.random.choice([0, 1], p = [1 - params['prob_noise'], params['prob_noise']]):
            nan_ratio = params['missing_value_ratio']
            x = random_index_noise(x, nan_ratio)
        else:
            min_size = params['missing_value_min_size']
            max_size = params['missing_value_max_size']
            x = random_interval_noise(x, min_size, max_size)
        return x

    X = X.values
    X = np.apply_along_axis(apply_on_series, 1, X)
    mask = np.isnan(X)

    # Replacing
    X = pd.DataFrame(X)
    mask = pd.DataFrame(mask)

    X.columns = columns
    mask.columns = columns

    return X, mask


def boundary_values(df, params):
    '''
    Hàm trả về các giá trị min-max của các cột
    '''
    
    return np.array(df.quantile([params['lower_quantile'], params['upper_quantile']]))


def boundary_matrix(boundary, params):
    '''
    Hàm trả về các ma trận:
        * min của từng cột
        * max của từng cột
        * range của từng cột
    '''

    min_matrix = np.array([boundary[0] for i in range(params['timesteps'])])
    max_matrix = np.array([boundary[1] for i in range(params['timesteps'])])
    range_matrix = np.array([[boundary[1][i] - boundary[0][i] for i in range(boundary.shape[1])] for j in range(params['timesteps'])])

    return min_matrix, max_matrix, range_matrix