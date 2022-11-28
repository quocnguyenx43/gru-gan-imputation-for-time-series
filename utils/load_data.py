import numpy as np
import pandas as pd
import yaml

from . import deterioration as de

# Load params
def load_params():
    params = yaml.load(open('gan/config.yaml'), yaml.Loader)
    return params

# Load dataset
def load_dataset():
    params = load_params()
    data = pd.read_csv(params['data_path'])
    cols = ["Temperature", "Relative_Humidity", "Specific_Humidity", "Precipitation", "Pressure", "Wind_Speed", "Wind_Direction"]
    real_df = data[cols]
    # Create missing values
    missing_df, mask_df = de.apply(real_df.copy(), params)

    return real_df, missing_df, mask_df

# Load boundary
def load_boundary():
    params = load_params()
    _, missing_df, _ = load_dataset()
    return de.boundary_values(missing_df, params)

# Load min-max & range matrix
def load_boundary_matrices():
    min_matrix, max_matrix, range_matrix = de.boundary_matrix(load_boundary(), load_params())
    return min_matrix, max_matrix, range_matrix