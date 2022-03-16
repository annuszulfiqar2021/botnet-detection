import scapy.all as scpy
from helpers import *
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
        these_flows = process_flow_dictionary_file(flow_dict_file)
        bot_flows.update(these_flows["botnets"])
        bot_pkt_cnt += these_flows["botnets"]["total_packets"]
        p2p_flows.update(these_flows["p2p"])
        p2p_pkt_cnt += these_flows["p2p"]["total_packets"]
        count += 1
        print(f"{count}-{flow_dict_file}_________________________________________________________________________________________")
    print(f"Bot flows = {len(bot_flows)}, Bot packets = {bot_pkt_cnt}")
    print(f"P2P flows = {len(p2p_flows)}, P2P packets = {p2p_pkt_cnt}")

if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--traindir", type=str)
    CLI.add_argument("--evaldir", type=str)
    args = vars(CLI.parse_args())
    main(args)