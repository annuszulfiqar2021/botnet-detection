import matplotlib.pyplot as plt
import scapy.all as scpy
from helpers import *
import pandas as pd
import numpy as np
import argparse
import pickle
import random
import json
import csv
import sys
import os


def process_flow_dictionary_file(filename):
    with open(filename) as infile:
        data = json.load(infile)
    return data

def main(args):
    pretty_dict(args)
    flow_dict_files = [os.path.join(args["traindir"], _file) for _file in os.listdir(args["traindir"]) if _file.endswith(".txt")]
    flow_dict_files += [os.path.join(args["evaldir"], _file) for _file in os.listdir(args["evaldir"]) if _file.endswith(".txt")]
    count = 0
    bot_flows, p2p_flows = {}, {}
    bot_pkt_cnt, p2p_pkt_cnt = 0, 0
    for flow_dict_file in flow_dict_files:
        # get flows dictionary from file
        these_flows = process_flow_dictionary_file(flow_dict_file)
        # get botnet flows count and delete that key
        this_botnet_dict = these_flows["botnets"]
        bot_pkt_cnt += this_botnet_dict["total_packets"]
        this_botnet_dict.pop("total_packets", None)
        # add this flow dictionary to our running botnet flows
        bot_flows.update(this_botnet_dict)
        # get p2p flows count and delete that key
        this_p2p_dict = these_flows["p2p"]
        p2p_pkt_cnt += this_p2p_dict["total_packets"]
        this_p2p_dict.pop("total_packets", None)
        # add this flow dictionary to our running p2p flows
        p2p_flows.update(this_p2p_dict)
        count += 1
        print(f"{count}-{flow_dict_file}_________________________________________________________________________________________")
    print(f"Bot flows = {len(bot_flows)}, Bot packets = {bot_pkt_cnt}, Max Packets per Flow = {max(bot_flows.values())}")
    print(f"P2P flows = {len(p2p_flows)}, P2P packets = {p2p_pkt_cnt}, Max Packets per Flow = {max(p2p_flows.values())}")
    # print(bot_flows.values())
    bot_flow_dist = pd.DataFrame(dict(botnets=list(bot_flows.values())))
    p2p_flow_dist = pd.DataFrame(dict(p2ps=list(p2p_flows.values())))
    fig, axes = plt.subplots(1, 2)
    bot_flow_dist.hist('botnets', bins=10000, ax=axes[0], log=True)
    p2p_flow_dist.hist('p2ps', bins=10000, ax=axes[1], log=True)
    plt.show()

if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--traindir", type=str)
    CLI.add_argument("--evaldir", type=str)
    args = vars(CLI.parse_args())
    main(args)