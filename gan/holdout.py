"""
Evaluation
"""

import numpy as np
import pandas as pd
from . import load_data
from . import holdout
from . import tools

"""
i: batch số mấy
j: sample số mấy
"""
def fill(i, j, X_test, X_test_real, pred, print_full, boundary):
    missing_pred = np.multiply(pred[j], X_test[1][j])
    missing_real = np.multiply(X_test_real[0][j], X_test[1][j])
    err = holdout.calc_error(pred[j], X_test_real[0][j], X_test[1][j])

    # Đã normalize các biến thành (0, 1), sau đó tính RMSE
    print("Errors (Normalized): {}".format(err))
    print("------------------------------------------------------------------------------------")
    print("Boundary")
    print(pd.DataFrame(boundary))
    print("------------------------------------------------------------------------------------")
    print('Dữ liệu missing được điền khuyết')
    print(pd.DataFrame(missing_pred).round(decimals=2).replace(0, '-'))
    print("------------------------------------------------------------------------------------")
    print("Dữ liệu missing thực tế")
    print(pd.DataFrame(missing_real).replace(0, '-') )
    print("------------------------------------------------------------------------------------")
    if (print_full == 1):
        print("Dữ liệu gốc")
        print(pd.DataFrame(X_test_real[0][j]))
        print("------------------------------------------------------------------------------------")
        print('Dữ liệu đã được điền')
        print(pd.DataFrame(pred[j].round(decimals = 2)))
        print("------------------------------------------------------------------------------------")
    return err


def calc_error(pred_matrix, true_matrix, mask_matrix):
    min_matrix, max_matrix, range_matrix = load_data.load_boundary_matrices()

    missing_pred = np.multiply(pred_matrix, mask_matrix)
    missing_true = np.multiply(true_matrix, mask_matrix)

    # Normalize
    norm_pred = ((missing_pred - min_matrix) / range_matrix) * mask_matrix
    norm_true = ((missing_true - min_matrix) / range_matrix) * mask_matrix

    # Tổng số giá trị thiếu
    sum_mask = len(mask_matrix[mask_matrix == True])

    error = np.sum(np.sqrt((norm_pred - norm_true) * (norm_pred - norm_true )) / sum_mask)
    
    return error

def calc_score(generator, batch_size, X_test, X_test_real, X_test_mask):
    scores = []
    for i in range(len(X_test) // batch_size):
        x_test = tools.gen_z_input(batch_size, i, X_test, X_test_mask)
        x_real = tools.gen_z_input(batch_size, i, X_test_real, X_test_mask)
        pred = generator.predict(x_test, verbose=0)
        for j in range(batch_size):
            scores.append(calc_error(pred[j], x_real[0][j], x_test[1][j]))

    error = np.mean(np.array(scores))
    
    return len(scores), error