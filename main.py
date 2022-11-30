import pandas as pd
import numpy as np

# Importing
from gan import deterioration as de
from gan import tools
from gan import processing
from gan import load_data
from gan import holdout

from gan.model import adam_optimizer, create_generator, create_discriminator, create_gan
from gan.train import train

def main():

    # Load params, dataset (real, missing, mask)
    print('==========================================')
    print('Loading dataset & params')
    params = load_data.load_params()
    real_df, missing_df, mask_df = load_data.load_dataset()
    print('==========================================')

    # Create boundary
    print('==========================================')
    print('Loading boundary')
    boundary = load_data.load_boundary()
    print('==========================================')

    # Convert to numpy array
    print('==========================================')
    print('Creating missing value dataset & mask dataset')
    real = np.array(real_df)
    missing = np.array(missing_df.replace(np.nan, 0))
    mask = np.array(mask_df.replace([False, True],  [0, 1]))
    print('==========================================')

    # Create boundary matrix
    min_matrix, max_matrix, range_matrix = load_data.load_boundary_matrices()

    # Processing input data
    print('==========================================')
    print('Input transforming')
    X, X_mask, X_real = processing.input_transform(missing, mask, real, params)
    print('==========================================')

    # Train, test spliting
    print('==========================================')
    print('Train & test spliting')
    X_train, X_train_real, X_train_mask, X_test, X_test_real, X_test_mask = processing.train_test_split(X, X_mask, X_real, params)
    print('==========================================')

    # Modeling
    print('==========================================')
    print('Creating model')
    optimizer = adam_optimizer(params['learning_rate'])
    generator = create_generator(optimizer, params)
    discriminator = create_discriminator(optimizer, params)
    gan = create_gan(discriminator, generator, optimizer)
    print('==========================================')

    # Training
    print('==========================================')
    print('Training')
    generator, _, _ = train(
        generator, discriminator, gan,
        X_train, X_train_mask, X_train_real,
        params
    )
    print('==========================================')

    # Predicting
    i = 0 # (0, len(X_test) // batch_size = 45)
    j = 0 # (0, batch_size - 1)
    x_test = tools.gen_z_input(params['batch_size'], i, X_test, X_test_mask)
    x_real = tools.gen_z_input(params['batch_size'], i, X_test_real, X_test_mask)
    pred = generator.predict(x_test)
    holdout.fill(i, j, x_test, x_real, pred, 0, boundary)

    print('==========================================')
    print('Calc score error')
    num_test_size, score = holdout.calc_score(generator, params['batch_size'], X_test, X_test_real, X_test_mask)
    print('Number test size: ', num_test_size)
    print('Score: ', score)
    print('==========================================')

if __name__ == '__main__':
    main()