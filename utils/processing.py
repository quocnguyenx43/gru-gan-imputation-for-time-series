import numpy as np
import pandas as pd

def input_transform(missing, mask, real, params):
    """ 
    Chuyển đổi missing thành các sample, mỗi sample là 5 dòng (timesteps=5)
    """
    X = []
    X_mask = []
    for i in range(len(missing) - params['timesteps']):
        missing_sample = missing[i:i + params['timesteps']]
        mask_sample = mask[i:i + params['timesteps']]
        X.append(missing_sample)
        X_mask.append(mask_sample)
    X = np.stack(X)
    X_mask = np.stack(X_mask)

    X_real = []
    for i in range(len(real) - params['timesteps']):
        real_sample = real[i:i + params['timesteps']]
        X_real.append(real_sample)
    X_real = np.stack(X_real)

    return X, X_mask, X_real


def train_test_split(X, X_mask, X_real, params):
    """ 
    Chia tập train và test theo tỉ lệ
    """

    train_ratio = params['train_ratio']

    X_train = X[0: int(len(X) * train_ratio)]
    X_train_real = X_real[0: int(len(X_real) * train_ratio)]
    X_train_mask = X_mask[0: int(len(X_mask) * train_ratio)]
    
    X_test = X[int(len(X) * train_ratio): len(X)]
    X_test_real = X_real[int(len(X_real) * train_ratio): len(X_real)]
    X_test_mask = X_mask[int(len(X_mask) * train_ratio): len(X_mask)]

    return X_train, X_train_real, X_train_mask, X_test, X_test_real, X_test_mask