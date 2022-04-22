# from __future__ import division, print_function, absolute_import
from sklearn.model_selection import train_test_split
from itertools import accumulate
import numpy as np
import csv

PL_HIST_LENGTH  = 46
IPT_HIST_LENGTH = 56
labels_to_class = {
    "benign":       [1, 0],
    "malicious":    [0, 1]
}

def load_from_file(dataset, shift):
    with open(dataset) as dataset_file:
        print("Loading Dataset: {0} ...".format(dataset))
        attributes, labels = [], []
        csv_reader = csv.reader(dataset_file)
        for n, row in enumerate(csv_reader):
            if(n == 0):
                continue
            else:
                try:
                    label_class = labels_to_class[row[-1]]
                except:
                    print("UNKNOWN LABEL FOUND IN THIS ROW = {0}".format(row))
                    continue
                # attributes.append(row[:-1])
                # only pick the PL + IPT bin attributes, not the high-level flow attributes
                attributes.append(list(map(int, row[shift:-1])))
                labels.append(label_class)
        
        print("Dataset size: Attributes = {0}, Labels = {1}".format(np.asarray(attributes).shape, np.asarray(labels).shape))
        print(type(attributes), type(attributes[0]))
        print(type(labels), type(labels[0]))
        return attributes, labels