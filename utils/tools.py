"""
Useful things
"""

import numpy as np
import pandas as pd

def gen_label(size, is_real=True, noise_ratio=0.1):
    if is_real:
        label = np.ones(size,) * 1
    else:
        label = np.ones(size,) * 0
    return np.squeeze(label)


def gen_z_input(batch_size, step, dset, dset_mask):
    return [dset[step * batch_size: (step + 1) * batch_size], dset_mask[step * batch_size: (step + 1) * batch_size]]


def gen_fake_batch(generator, batch_size, step, dset, dset_mask):
    z = gen_z_input(batch_size, step, dset, dset_mask)
    fake_dset = generator.predict(z)
    fake_label = gen_label(batch_size, is_real=False)
    return fake_dset, fake_label


def gen_real_batch(batch_size, step, dset):
    real_dset = dset[step * batch_size: (step + 1) * batch_size]
    real_label = gen_label(batch_size, is_real=True)
    return real_dset, real_label
    