from keras import backend as K
from sklearn import metrics
import numpy as np

class Metric:
    @classmethod
    def get(cls, name):
        if name == "precision":
            return Precision
        elif name == "recall":
            return Recall
        elif name == "f1":
            return F1
        else:
            # bad input
            return None

def Recall(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def Precision(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def F1(y_true, y_pred):
    precision = Precision(y_true, y_pred)
    recall = Recall(y_true, y_pred)
    return 2*((precision*recall)/(precision+recall+K.epsilon()))

# def Accuracy(true_labels, predicted_labels):
#     return 100*metrics.accuracy_score(true_labels, predicted_labels)

# def Precision(true_labels, predicted_labels):
#     return 100*metrics.precision_score(true_labels, predicted_labels)

# def Recall(true_labels, predicted_labels):
#     return 100*metrics.recall_score(true_labels, predicted_labels)

# def F1(true_labels, predicted_labels):
#     return 100*metrics.f1_score(true_labels, predicted_labels, average="weighted", labels=np.unique(predicted_labels))