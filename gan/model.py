"""
Creating model
"""

import tensorflow as tf
from keras.models import Sequential, Model
from keras.layers import (
    Dense, Flatten, Dropout, LSTM, GRU, RNN, LeakyReLU, Bidirectional,
    Input, Lambda, Multiply, Add
)
from keras.layers.convolutional import (
    Conv1D, MaxPooling1D
)
from keras.optimizers import Adam

from gan.load_data import load_boundary_matrices


def adam_optimizer(alpha):
    return Adam(lr=alpha)


# Generator
def create_generator(optimizer, params):

    min_matrix, max_matrix, range_matrix = load_boundary_matrices()

    input = Input((params['timesteps'], params['num_features'],)) # Input 1 là 1 ma trận bị missing values
    mask = Input((params['timesteps'], params['num_features'],))  # Input 2 là 1 ma trận mask 0/1

    ### GRU hoặc LSTM
    gru = Bidirectional(GRU(units=params['num_features'], return_sequences=True))(input)
    # gru = LSTM(units=params['num_features'], return_sequences=True)(input)

    # GRU nối với input để tạo ra ma trận mới, qua sigmoid nên sẽ nằm trong (0, 1)
    gru1 = GRU(units=params['num_features'], return_sequences=True)(gru)
    gru2 = GRU(units=params['num_features'], return_sequences=True, activation="sigmoid")(gru1)
    # Scale (0, 1) thành giá trị trong đoạn (min, max)
    lambda_output = Lambda(lambda x: (x * range_matrix) + min_matrix)(gru2)
    # Nhân ma trận đã điền khuyết với ma trận mask để chỉ lấy các giá trị điền
    imputed = Multiply()([lambda_output, mask])
    # Cuối cùng, cộng ma trận filled với ma trận missing ban đầu
    final = Add()([input, imputed])

    # Model
    model = Model(inputs=[input, mask], outputs=final)

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer=optimizer)
    
    return model


# Discriminator
def create_discriminator(optimizer, params):

    input = Input((params['timesteps'], params['num_features'],)) # Input 1 là 1 ma trận đã điền khuyết

    ### GRU hoặc Conv1D
    gru = Bidirectional(GRU(units=params['num_features'], return_sequences=True))(input)
    # conv1d = Conv1D(filter=20, kernel_size=1)(input)

    leaky = LeakyReLU(alpha=0.2)(gru)
    # leaky = LeakyReLU(alpha=0.2)(conv1d)

    dropout = Dropout(0.5)(leaky)
    flatten = Flatten()(dropout)
    dense = Dense(1, activation='sigmoid')(flatten)

    # Model
    model = Model(inputs=input, outputs=dense)

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer=optimizer, metrics=['accuracy'])

    return model


# GAN
def create_gan(discriminator, generator, optimizer):

    discriminator.trainable = False

    gen = generator

    output = discriminator(gen.output)

    # Model
    gan= Model(inputs=gen.input, outputs=output)

    # Compile model
    gan.compile(loss='binary_crossentropy', optimizer=optimizer)

    return gan