import os
import sys
import json
sys.path.append(os.environ["HOMUNCULUS_HOME"])
import homunculus
from homunculus.alchemy import DataLoader, Model, platforms
import bd_loader


@DataLoader
def wrapper_func():
    # tnx, tsx, tny, tsy = bd_loader.load_from_file("../app_data/flowlens_flowmarkers/Dataset_32_64.csv")
    tnx, tny = bd_loader.load_from_file("../app_data/flowlens_flowmarkers/Dataset_64_512.csv", shift=4)
    tsx, tsy = bd_loader.load_from_file("../app_data/flowlens_flowmarkers/PerPktHist_Subset10k_64_512.csv", shift=0)
    return {
            "data": {
                "train": tnx,
                "test": tsx
            },
            "labels": {
                "train": tny,
                "test": tsy
            }
    }


def load_config(config_file):
    with open(config_file, 'r') as cf:
        return json.load(cf)


botnet_detector = Model({
    "algorithm": ["dnn"],
    "name": "test_botnet_detection",
    "data_loader": wrapper_func,
    "config": {"dnn": load_config("config.json")}
})

testbed = platforms.Testbed()
testbed.schedule(botnet_detector)
homunculus.generate(testbed)
