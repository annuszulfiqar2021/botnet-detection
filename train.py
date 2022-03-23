from helpers import pretty_dict, join_to_str, makeLUTsFromModel
from gen_tf_dataset import get_tf_dataset
from spatial import generateSpatial
from model import DNN
import argparse
import os

def build_and_train_dnn(args):
    model_dir = os.path.join(args["model_dir"], args["name"]+join_to_str(*args["arch"]))
    # with open(args["cached_dataset"], 'rb') as handle:
    #     dataset = pickle.load(handle)
    # tnx, tny = dataset["tnx"], dataset["tny"]
    # tsx, tsy = dataset["tsx"], dataset["tsy"]
    training_set = get_tf_dataset(args["trainset"], args["features"], args["label"], args["batch_size"], args["is_conversation"]) # here bs = 1, we will train #epoch times on it
    eval_set = get_tf_dataset(args["evalset"], args["features"], args["label"], args["batch_size"], args["is_conversation"]) # here bs = 1, we will train #epoch times on it
    # print("TRAINING => FEATURES -> {0}, LABELS -> {1}".format(tnx.shape, tny.shape))
    # print("TEST => FEATURES -> {0}, LABELS -> {1}".format(tnx.shape, tny.shape))
    if os.path.exists(model_dir):
        # model exists already, don't overwrite
        print("MODEL DIR {0} ALREADY EXISTS. NOT OVERWRITING..".format(model_dir))
    else:
        # model doesn't exist, so create directory and train from scratch
        print("MODEL DIR {0} DOES NOT EXIST. TRAINING MODEL FROM SCRATCH..".format(model_dir))
        os.mkdir(model_dir)
        dnn = DNN(model_name=args["name"], arch=args["arch"], input_dim=args["input_dim"], output_dim=args["output_dim"], metric=args["metric"])
        print("BUILDING MODEL..")
        dnn.build()
        model = dnn.getModel()
        model.summary()
        print("TRAINING MODEL..")
        dnn.train(training_set, eval_set, args["epochs"])
        # dnn.train(tnx, tny, val_split, epochs, batch_size)
        # print("TESTING MODEL..")
        # tn_precision, tn_recall, tn_f1 = dnn.evaluate(tnx, tny)
        # ts_precision, ts_recall, ts_f1 = dnn.evaluate(tsx, tsy)
        # print("TRAINING -> Precision = {0:.2f}, Recall = {1:.2f}, F1 = {2:.2f}".format(tn_precision, tn_recall, tn_f1))
        # print("TESTING -> Precision = {0:.2f}, Recall = {1:.2f}, F1 = {2:.2f}".format(ts_precision, ts_recall, ts_f1))
        # # save the trained weights as a model
        # args["model"] = list()
        # for layer in model.layers:
        #     args["model"].append(layer.get_weights())
        # makeLUTsFromModel(layers=args["model"], lut_dir=model_dir)
        # generateSpatial(model_data=args, base_dir=args["spatial_dir"], num_pkts=2)

def main(args):
    pretty_dict(args)
    build_and_train_dnn(args)

if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--name", type=str)
    CLI.add_argument("--arch", nargs="*", type=int)
    CLI.add_argument("--pars", nargs="*", type=int)
    CLI.add_argument("--trainset", type=str)
    CLI.add_argument("--evalset", type=str)
    CLI.add_argument("--features", nargs="*", type=str)
    CLI.add_argument("--is_conversation", action='store_true')
    CLI.add_argument("--label", type=str)
    CLI.add_argument("--input_dim", type=int)
    CLI.add_argument("--output_dim", type=int)
    CLI.add_argument("--metric", type=str)
    CLI.add_argument("--batch_size", type=int)
    CLI.add_argument("--epochs", type=int)
    CLI.add_argument("--model_dir", type=str)
    CLI.add_argument("--spatial_dir", type=str)
    args = CLI.parse_args()
    main(vars(args))