from itertools import accumulate
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tqdm.keras import TqdmCallback
from metrics import *
import tensorflow as tf

class DNN:
    def __init__(self, model_name, arch, input_dim, output_dim, metric):
        self.model_name = model_name + "_DNN"
        self.model = None
        self.arch = arch
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.metric = metric

    def getModel(self):
        return self.model

    def build(self):
        # model = tf.keras.Sequential([
        #     tf.keras.layers.Dense(5, activation='relu'),
        #     tf.keras.layers.Dense(5, activation='relu'),
        #     tf.keras.layers.Dense(10, activation='relu'),
        #     tf.keras.layers.Dense(10, activation='relu'),
        #     tf.keras.layers.Dense(10, activation='relu'),
        #     tf.keras.layers.Dense(10, activation='relu'),
        #     tf.keras.layers.Dense(5, activation='relu'),
        #     tf.keras.layers.Dense(5, activation='relu'),
        #     tf.keras.layers.Dense(1, activation='sigmoid'),
        # ])
        model = Sequential()
        for layer_idx, num_hidden_units in enumerate(self.arch):
            if layer_idx == 0:
                model.add(Dense(num_hidden_units, name="input_layer", input_dim=self.input_dim, activation='relu'))
            else:
                model.add(Dense(num_hidden_units, name="intermediate_layer_" + str(layer_idx), activation='relu'))
        model.add(Dense(self.output_dim, name="final_layer_", activation='sigmoid'))
        model.compile(loss='binary_crossentropy', optimizer='adam', metrics=[Metric.get(self.metric)])
        self.model = model

    def train(self, train_ds, eval_ds, epochs):
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="./logs", update_freq='batch')
        self.model.fit(train_ds, validation_data=eval_ds, epochs=epochs, callbacks=[tensorboard_callback])

    def evaluate(self, testX, testY):
        predY = self.model.predict(testX)
        predY = tf.cast(predY, tf.float32)
        testY = tf.cast(testY, tf.float32)
        return Precision(testY, predY), Recall(testY, predY), F1(testY, predY)

    @staticmethod
    def csOptimize(inputs):

        parameters = inputs[0]
        state = inputs[1]

        batch_size = int(parameters["batch_size"])
        # epochs = int(parameters["epochs"])
        epochs = 50
        layers = []
        pars = []

        for key, val in parameters.items():
            if key.startswith("neurons_layers_"):
                layers.append(int(val))
            elif key.startswith("pars_layers_"):
                pars.append(int(val))

        pars.append(2)

        for idx, val in enumerate(layers):
            if val == 0:
                del layers[idx]
                del pars[idx]

        tnx = state["dataset"]["data"]["train"]
        tny = state["dataset"]["labels"]["train"]
        tsx = state["dataset"]["data"]["test"]
        tsy = state["dataset"]["labels"]["test"]
        dnn = DNN(state["name"], layers, state["input_dim"],
                  state["output_dim"], state["metrics"])
        dnn.build()
        dnn.train(tnx, tny, epochs, batch_size)
        metric_value = dnn.evaluate(tsx, tsy)

        metric_value = -1.0 * metric_value
        arch = []
        model = dnn.getModel()
        layers = []
        print(model.layers)
        for layer in model.layers:
            arch.append(len(layer.get_weights()[0][0]))
            layers.append(layer.get_weights())

        return metric_value, arch, layers, pars
