import tqdm
from utils import tools

def train(generator, discriminator, gan,
          X_train, X_mask_train, X_train_real,
          params
    ):
    
    step_per_epoch = len(X_train) // params['batch_size'] - 1
    epochs = params['epochs']
    num_epoch = params['num_epoch']

    for i in range(epochs):
        count = 0
        num_epoch += 1
        for step in tqdm.tqdm(range(step_per_epoch), desc="Epoch: " + str(num_epoch)):

            # Real data
            real_data, real_label = tools.gen_real_batch(params['batch_size'], count, X_train_real)

            # Input data
            z_input, mask_input = tools.gen_z_input(params['batch_size'], count, X_train, X_mask_train)

            # Fake data
            fake_data = generator.predict([z_input, mask_input]) 
            fake_label = tools.gen_label(params['batch_size'], is_real=False)

            # Train Discriminator
            discriminator.trainable = True
            discriminator.train_on_batch(real_data, real_label)
            discriminator.train_on_batch(fake_data, fake_label)
            discriminator.trainable = False

            # Train Generator
            gan_fake_label = tools.gen_label(params['batch_size'], is_real=True)
            gan.train_on_batch([z_input, mask_input], gan_fake_label)
            count += 1

    return generator, discriminator, gan