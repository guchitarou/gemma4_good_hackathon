"""
export TF_FORCE_GPU_ALLOW_GROWTH=true
"""

from gensim.models import Word2Vec
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Dense, Activation
from tensorflow.keras.layers import LSTM, Bidirectional
from tensorflow.keras.layers import Input, Dropout, multiply, Add, Average, Conv2D, Concatenate, LayerNormalization, Flatten, Reshape, Maximum, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.models import Model
from tensorflow.python.keras.models import load_model
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.losses import BinaryCrossentropy
from tensorflow.keras.losses import Hinge
from tensorflow.compat.v1.keras.layers import CuDNNLSTM
import tensorflow as tf
import traceback
import json
from IPython.display import clear_output
from tensorflow.keras.utils import multi_gpu_model
import matplotlib.pyplot as plt

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LeakyReLU, Reshape, UpSampling2D, Conv2DTranspose
from tensorflow.keras.layers import BatchNormalization, Input, Lambda

from IPython.display import clear_output
import time
# to use csv
import pandas as pd

import pickle as pk
import numpy as np
from tensorflow.keras.layers import Layer
import pickle as pick

import gensim
import transformers

save_pss = './experiment2/'


def torknizer_word2vec(vectors, tkmodel):
    txt = []
    for word in vectors:
        w = tkmodel.wv.most_similar(word, topn=1)[0][0]
        txt.append(w)
    return ' '.join(txt)


def Disc_ver7():
    input_img_txt_data = Input(shape=(10, 100))
    LSTM_layer_0 = Bidirectional(LSTM(units=200, activation='relu'))(input_img_txt_data)
    LSTM_layer = Dense(200, kernel_regularizer=l2(0.001), activation='relu')(LSTM_layer_0)
    out_put = Dense(1, activation='sigmoid')(LSTM_layer)
    # Define model
    modelD = Model(inputs=input_img_txt_data, outputs=[out_put])
    return modelD


def Disc_ver8():
    with tf.device("/cpu:0"):
        # Define input (shape=1)
        input_img_txt_data = Input(shape=(10, 100))
        # Define hidden layer
        layer1 = Flatten()(input_img_txt_data)
        layer2 = Dense(400, kernel_regularizer=l2(0.001), activation='relu')(layer1)
        layer3 = Dense(400, kernel_regularizer=l2(0.001), activation='relu')(layer2)
        layer4 = Concatenate(axis=-1)([layer2, layer3])
        layer5 = Dense(100, kernel_regularizer=l2(0.001), activation='relu')(layer4)
        out_put = Dense(1)(layer5)
        # Define model
        modelD = Model(inputs=input_img_txt_data, outputs=[out_put])
    return modelD


def Disc_ver9():
    # Define input (shape=1)
    input_img_txt_data = Input(shape=(10, 100))
    # Define hidden layer
    layer1 = Flatten()(input_img_txt_data)
    layer2 = Dense(200, kernel_regularizer=l2(0.001), activation='relu')(layer1)
    layer2_1 = BatchNormalization()(layer2)
    layer2_last = Concatenate(axis=-1)([layer2_1, layer2])
    layer3 = Dense(200, kernel_regularizer=l2(0.001), activation='relu')(layer2_last)
    layer3_1 = BatchNormalization()(layer2)
    layer4 = Concatenate(axis=-1)([layer3_1, layer3])
    layer5 = Dense(50, kernel_regularizer=l2(0.001), activation='relu')(layer4)
    out_put = Dense(1)(layer5)
    # Define model
    modelD = Model(inputs=input_img_txt_data, outputs=[out_put])
    return modelD


def Disc_ver10():
    input_img_txt_data = Input(shape=(10, 100))
    LSTM_layer = LSTM(units=128, activation='relu')(input_img_txt_data)
    out_put = Dense(1)(LSTM_layer)
    # Define model
    modelD = Model(inputs=input_img_txt_data, outputs=[out_put])
    return modelD


def custom_activation(x):
    return tf.tanh(x) * 9


# Custom activation function class implementation (subclassing Layer)
# (instead of tf.keras.layers.Activation())
class CustomActivation(Layer):
    def __init__(self, **kwargs):
        super(CustomActivation, self).__init__(**kwargs)

    def call(self, inputs):
        return custom_activation(inputs)


def minn():
    with tf.device("/cpu:0"):
        in_data = Input(shape=(10, 100))
        in_data2 = Input(shape=(10, 200))

        shared_lstm1 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(in_data)
        shared_lstm2 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(in_data)
        shared_lstm3 = Bidirectional(CuDNNLSTM(100, kernel_regularizer=l2(0.001), return_sequences=True))(in_data)

        shared_lstm1 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm1)
        shared_lstm2 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm2)
        shared_lstm3 = Bidirectional(CuDNNLSTM(100, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm3)

        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm2 = BatchNormalization()(shared_lstm2)
        shared_lstm3 = BatchNormalization()(shared_lstm3)

        shared_lstm1 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm1)
        shared_lstm2 = Bidirectional(CuDNNLSTM(256, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm2)
        shared_lstm3 = Bidirectional(CuDNNLSTM(100, kernel_regularizer=l2(0.001), return_sequences=True))(shared_lstm3)

        shared_dense1 = Dense(200, activation='relu', kernel_regularizer=l2(0.001))(shared_lstm1)
        shared_dense1_soft = Dense(200, activation='softmax', kernel_regularizer=l2(0.001))(shared_lstm1)
        shared_dense1_00 = multiply([shared_dense1, shared_dense1_soft])
        shared_dense1_00 = BatchNormalization()(shared_dense1_00)
        shared_dense2 = Dense(200, activation='relu', kernel_regularizer=l2(0.001))(shared_lstm2)
        shared_dense2_soft = Dense(200, activation='softmax', kernel_regularizer=l2(0.001))(shared_dense2)
        shared_dense2_00 = multiply([shared_dense2, shared_dense2_soft])
        shared_dense2_add = Add()([shared_dense2_00, shared_dense2])
        shared_dense2_add = BatchNormalization()(shared_dense2_add)

        LSTM_layer1 = Dropout(0.25)(shared_dense1_00)
        LSTM_layer2 = Dropout(0.5)(shared_dense2_add)

        conca = Concatenate(axis=-1)([LSTM_layer2, in_data2])
        shared_dense3 = Dense(200, activation='tanh', kernel_regularizer=l2(0.001))(conca)
        shared_dense4 = Average()([LSTM_layer1, shared_dense3, shared_lstm3])
        shared_dense4 = BatchNormalization()(shared_dense4)
        shared_dense2 = Dense(100, kernel_regularizer=l2(0.001), activation=CustomActivation())(shared_dense4)
    return Model(inputs=[in_data, in_data2], outputs=[shared_dense2])


class GPTLayer_ver2_g(Layer):
    def call(self, encoded_input):
        encoded_input = tf.convert_to_tensor(encoded_input)
        greedy_output = model(encoded_input)
        result = tf.reshape(greedy_output.hidden_states, [-1, 149760])
        return result


def Genere_ver11():
    with tf.device("/cpu:0"):
        # Define input (shape=1)
        input_sentence = Input(shape=(15,), dtype=tf.int32)
        input_image = Input(shape=(4096,))

        # Define hidden layer
        layer1 = Dense(100, activation='relu')(input_sentence)
        layer1 = Flatten()(layer1)
        layer1 = Dense(100, activation='relu')(layer1)

        # Define hidden layer
        layer2 = Dense(200, activation='relu')(input_image)
        layer2 = Dense(100, activation='relu')(layer2)
        input_s = Concatenate(axis=-1)([layer1, layer2])
        input_s = Dense(100, activation='relu')(input_s)
        i_layer = RepeatVector(10)(input_s)

        shared_lstm1 = Bidirectional(LSTM(500, kernel_regularizer=l2(0.01), return_sequences=True))(i_layer)
        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm1 = LeakyReLU()(shared_lstm1)
        shared_lstm1 = Bidirectional(LSTM(500, kernel_regularizer=l2(0.01), return_sequences=True))(shared_lstm1)
        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm1 = LeakyReLU()(shared_lstm1)

        shared_lstm2 = Bidirectional(LSTM(500, kernel_regularizer=l2(0.01), return_sequences=True))(i_layer)
        shared_lstm2 = BatchNormalization()(shared_lstm2)
        shared_lstm2 = LeakyReLU()(shared_lstm2)
        shared_lstm2 = Bidirectional(LSTM(500, kernel_regularizer=l2(0.01), return_sequences=True))(shared_lstm2)
        shared_lstm2 = BatchNormalization()(shared_lstm2)
        shared_lstm2 = LeakyReLU()(shared_lstm2)

        shared_dense_1 = Average()([shared_lstm1, shared_lstm2])

        shared_lstm1 = Bidirectional(LSTM(500, kernel_regularizer=l2(0.01), return_sequences=True))(shared_dense_1)
        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm1 = LeakyReLU()(shared_lstm1)
        shared_lstm1 = Bidirectional(LSTM(256, kernel_regularizer=l2(0.01), return_sequences=True))(shared_lstm1)
        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm1 = LeakyReLU()(shared_lstm1)
        shared_lstm1 = Bidirectional(LSTM(100, kernel_regularizer=l2(0.01), return_sequences=True))(shared_lstm1)
        shared_lstm1 = BatchNormalization()(shared_lstm1)
        shared_lstm1 = LeakyReLU()(shared_lstm1)
        last_layer = Dense(100, activation='tanh', kernel_regularizer=l2(0.01))(shared_lstm1)
        out_put = CustomActivation()(last_layer)

        modelG = Model(inputs=[input_sentence, input_image], outputs=[out_put])
    return modelG


gpulist = tf.config.experimental.list_physical_devices('GPU')

cross_entropy = BinaryCrossentropy()


def data_generator_ver2(Sentence_image2):
    # Loop forever over images
    y_mislabled = np.ones((1, 1))
    for x in Sentence_image2:
        yield x, y_mislabled


def generator_loss(fake_output):
    fake_loss = -tf.reduce_mean(fake_output)
    return fake_loss


def discriminator_loss(real_output, fake_output):
    real_loss = tf.reduce_mean(tf.nn.relu(1.0 - real_output))
    fake_loss = tf.reduce_mean(tf.nn.relu(1.0 + fake_output))
    return fake_loss + real_loss


def train_step_test(_txt, _image, disc_input, stopdisc_tain, n):
    disc_input1 = tf.convert_to_tensor(disc_input)
    with tf.GradientTape() as gen_tape, tf.GradientTape() as disc_tape:
        fake_input_2 = generator([_txt, _image], training=True)
        real_output = modelD(disc_input1, training=True)
        fake_output = modelD(fake_input_2, training=True)

        gen_loss = generator_loss(fake_output)
        disc_loss = discriminator_loss(real_output, fake_output)

        gradients_of_generator = gen_tape.gradient(gen_loss, generator.trainable_variables)
        generator_optimizer.apply_gradients(zip(gradients_of_generator, generator.trainable_variables))
        gradients_of_discriminator = disc_tape.gradient(disc_loss, modelD.trainable_variables)
        discriminator_optimizer.apply_gradients(zip(gradients_of_discriminator, modelD.trainable_variables))

    return gen_loss, disc_loss


def change_data(Sentence_image):
    text = []
    image = []
    for data in Sentence_image:
        text.append(data[0][0])
        image.append(data[1][0])
    return np.array(text), np.array(image)


def get_data(number, json_load):
    input_data_txt = []
    input_data_img = []
    random_index = np.random.randint(0, 214354, number)
    for n in random_index:
        img_id = json_load['questions'][n]['image_id']
        q_id = json_load['questions'][n]['question_id']
        get_featur_img = np.load('./NewImage_and_anser/val2014_npy/' + str(img_id) + '.npy')
        get_featur_txt = np.load('./NewImage_and_anser/val2014_text_npy_GPT_torken/' + str(q_id) + '.npy')
        input_data_txt.append(get_featur_txt[0])
        input_data_img.append(get_featur_img[0])
    return np.array(input_data_txt), np.array(input_data_img)


def get_data2(number, batch, json_load, gpt_input_sentence):
    input_data_txt = []
    input_data_img = []
    random_index = np.array(range(number, number + batch))
    for n in random_index:
        img_id = json_load['questions'][n]['image_id']
        q_id = json_load['questions'][n]['question_id']
        get_featur_img = np.load('./NewImage_and_anser/val2014_npy/' + str(img_id) + '.npy')
        get_featur_txt = gpt_input_sentence[q_id]
        input_data_txt.append(get_featur_txt[0])
        input_data_img.append(get_featur_img[0])
    return np.array(input_data_txt), np.array(input_data_img)


def train_ver3(X_train_Sentence, gpt_input_sentence, json_load, epochs=10, batch=64, wait_g_train=0):
    save_interval = 3
    Dont_trainG = 0
    G_s_loss = []
    D_s_loss = []
    gen_acc_list = []
    disc_acc_list = []
    lang = []
    law_testnoise = tf.random.normal([1, 100])
    n = 0
    img_id = json_load['questions'][n]['image_id']
    q_id = json_load['questions'][n]['question_id']
    seedget_featur_img = np.load('./NewImage_and_anser/val2014_npy/' + str(img_id) + '.npy')
    seedget_featur_txt = gpt_input_sentence[q_id]
    print("start")
    save_num = epochs / 10
    for iteration in range(epochs):
        gen_loss_list = []
        disc_loss_list = []
        for ii in range(0, 1000, int(batch / 2)):
            _txt, _image = get_data2(ii, batch, json_load, gpt_input_sentence)
            Sentence_T = np.array(X_train_Sentence[ii: ii + np.int64(batch / 2)])
            gen_loss, disc_loss = train_step_test(_txt, _image, Sentence_T, wait_g_train, iteration)
            print(str(iteration) + "==>" + str(ii))

        fake_input_2 = generator([_txt, _image], training=False)
        real_output = modelD(X_train_Sentence[ii: ii + np.int64(batch / 2)], training=False)
        fake_output = modelD(fake_input_2, training=False)
        fake_r = fake_output.numpy().mean()
        real_r = real_output.numpy().mean()
        gen_acc_list.append(fake_r)
        disc_acc_list.append(real_r)

        if iteration % save_num == 0:
            generator.save(save_pss + 'my_model' + str(iteration) + str(".h5"))
        print('epoch: %d, [Discriminator :: d_loss: %f], [ Generator :: loss: %f],\n [ fake :: output: %f],[ real :: output: %f]' % (
            iteration, np.array(disc_loss).mean(), np.array(gen_loss).mean(), fake_r, real_r))
        print("test generate")

        G_s_loss.append(gen_loss)
        D_s_loss.append(disc_loss)

        test_d = generator.predict([seedget_featur_txt, seedget_featur_img])
        test_d = torknizer_word2vec(test_d[0], model_Word2Vec)
        lang.append(test_d)
        print(test_d)
        print("-" * 15)
    return G_s_loss, D_s_loss, lang, gen_acc_list, disc_acc_list


# Load models and data
model_Word2Vec = Word2Vec.load("./GPT2_lang_model/Ver1_word2vec.model")
json_open = open('./NewImage_and_anser/v2_OpenEnded_mscoco_val2014_questions.json', 'r')
json_load = json.load(json_open)
X_train_Sentence = pd.read_pickle("./GPT2_lang_model/text_data_word2vec.pkl")
gpt_input_sentence = pd.read_pickle("./NewImage_and_anser/GPT2_VAQ_questions.pkl")

epochs = 2000
batch = 500
wait_g_train = 5

generator_optimizer = tf.keras.optimizers.Adam(0.0001, 0.5)
discriminator_optimizer = tf.keras.optimizers.Adam(0.0001, 0.5)

modelD = Disc_ver8()
generator = Genere_ver11()
generator.summary()
modelD.summary()

G_s_loss, D_s_loss, lang, gen_acc_list, disc_acc_list = train_ver3(
    X_train_Sentence, gpt_input_sentence, json_load, epochs, batch, wait_g_train
)

f = open(save_pss + 'lang_result.txt', 'wb')
list_row = lang
pk.dump(list_row, f)

# Plot generator and discriminator loss
fig = plt.figure()
plt.plot(range(1, len(np.array(G_s_loss)) + 1), np.array(G_s_loss), 'b', label='g_loss')
plt.plot(range(1, len(np.array(D_s_loss)) + 1), np.array(D_s_loss), 'r', label='D_loss')
plt.title('Training GAN G Loss')
plt.legend()
plt.grid()
fig.savefig(save_pss + 'lossgoodtest.png')

# Plot generator and discriminator accuracy
fig = plt.figure()
plt.plot(range(1, len(np.array(gen_acc_list)) + 1), np.array(gen_acc_list), 'b', label='g_acc')
plt.plot(range(1, len(np.array(disc_acc_list)) + 1), np.array(disc_acc_list), 'r', label='D_acc')
plt.title('Training GAN Accuracy')
plt.legend()
plt.grid()
fig.savefig(save_pss + 'acctest.png')

# Save models
generator.save(save_pss + 'GANlastGmodel.h5')
modelD.save(save_pss + 'GANlastDmodel.h5')

# Generate sample outputs
random_index = np.random.randint(0, 214354, 50)
for n in random_index:
    img_id = json_load['questions'][n]['image_id']
    q_id = json_load['questions'][n]['question_id']
    get_featur_img = np.load('./NewImage_and_anser/val2014_npy/' + str(img_id) + '.npy')
    get_featur_txt = gpt_input_sentence[q_id]
    test_d = generator.predict([get_featur_txt, get_featur_img])
    test_d = torknizer_word2vec(test_d[0], model_Word2Vec)
    print(test_d)
    print("-" * 10)