import multiprocessing as MP
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

THREAD_LIMIT = 16
#create a semaphore so as not to exceed threadlimit
sem = MP.Semaphore(THREAD_LIMIT)

def process_pcap_dataset(pcap_file: str, csv_file: str, metadata_file: str, samples: int, botnets_only: int):
    sem.acquire()
    # PcapReader comes from scapy and reads packets iteratively
    # without loading the full file into memory (very efficient)
    pkts = scpy.PcapReader(pcap_file)
    # Let's iterate through every packet and maintain some metrics
    botnet_pkt_cnt, p2p_pkt_cnt = 0, 0
    botnet_flows, p2p_flows = {}, {}
    flow_last_packet_arrival_time = {}
    if os.path.exists(csv_file):
        print("{0} Already Exists. Not Creating Again..".format(csv_file))
        return
    with open(csv_file, 'w') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=FIELDS)
        csvwriter.writeheader()
        print(" Starting Packet Extraction...")
        for idx, pkt in enumerate(pkts, 1):
            # collect as many samples as suggested from commmand line
            # if len(botnet_flows) > samples and len(p2p_flows) > samples: 
            #     break
            # collect as many packets as suggested from commmand line
            if botnet_pkt_cnt+p2p_pkt_cnt > 2*samples:
                break
            # reset variables
            _pkt = {key:0 for key in FIELDS}
            # extract the 5-tuple of the packet [src.ip, dst.ip, src.port, dst.port, protocol]
            if scpy.IP in pkt:
                get_all_ipv4_fields(_pkt, pkt)
            # do the rest of the processing only for TCP or UDP packets
            if scpy.TCP in pkt or scpy.UDP in pkt:
                if scpy.TCP in pkt:
                    get_all_tcp_fields(_pkt, pkt)
                else: # if scpy.UDP in pkt
                    get_all_udp_fields(_pkt, pkt)
                _pkt["pkt_size"] = len(pkt)
                # decide if it is a botnet or not using src/dst IPv4 address
                flow_tup = join_to_str(_pkt["ipv4_src"], _pkt["ipv4_dst"], _pkt["ipv4_proto"], _pkt["tcp_sport"]+_pkt["udp_sport"], _pkt["tcp_dport"]+_pkt["udp_dport"])
                # is botnet!
                if botnets_only == 1 and (_pkt["ipv4_src"] in ALL_BOTNET_IPs or _pkt["ipv4_dst"] in ALL_BOTNET_IPs):
                    # if sample count is exceeded, then just drop this one and move on
                    if botnet_pkt_cnt > samples:
                        continue
                    _pkt["isbotnet"] = 1
                    botnet_pkt_cnt += 1
                    # check your flow dictionary
                    if flow_tup not in botnet_flows.keys():
                        # add new flow
                        botnet_flows[flow_tup] = 1
                        # add flow start time
                        flow_last_packet_arrival_time[flow_tup] = pkt.time
                        _pkt["inter_arrival_time"] = 0
                    else: # packet from a running flow, update it
                        # increment packet count for this flow
                        botnet_flows[flow_tup] += 1
                        # get inter-arrival time, and update last packet time
                        _pkt["inter_arrival_time"] = pkt.time - flow_last_packet_arrival_time[flow_tup]
                        flow_last_packet_arrival_time[flow_tup] = pkt.time
                elif botnets_only == 0: # is not botnet!
                    # if sample count is exceeded, then just drop this one and move on
                    if p2p_pkt_cnt > samples:
                        continue
                    _pkt["isbotnet"] = 0
                    p2p_pkt_cnt += 1
                    # check your flow dictionary
                    if flow_tup not in p2p_flows.keys():
                        # add new flow
                        p2p_flows[flow_tup] = 1
                        # add flow start time
                        flow_last_packet_arrival_time[flow_tup] = pkt.time
                        _pkt["inter_arrival_time"] = 0
                    else: # already seen flow, update it
                        # increment packet count for this flow
                        p2p_flows[flow_tup] += 1
                        # get inter-arrival time, and update last packet time
                        _pkt["inter_arrival_time"] = pkt.time - flow_last_packet_arrival_time[flow_tup]
                        flow_last_packet_arrival_time[flow_tup] = pkt.time
                # write new sample to csv
                csvwriter.writerow(_pkt)
                # pkt_feature_str = ""
                # pkt_feature_str += ', IPv4 src: {0}, IPv4 dst: {1}'.format(_pkt["ipv4_src"], _pkt["ipv4_dst"])
                # pkt_feature_str += ', IPV4_PROTO = {0}, PKT size: {1}'.format(_pkt["ipv4_proto"], _pkt["pkt_size"])
                # pkt_feature_str += ', src port: {0}, dst port: {1}'.format(_pkt["tcp_sport"]+_pkt["udp_sport"], _pkt["tcp_dport"]+_pkt["udp_dport"])
                # pkt_feature_str += ', INTER-ARRIVAL-TIME = {0}'.format(_pkt["inter_arrival_time"])
                # pkt_feature_str += ', IS BOTNET? = {0}'.format(_pkt["isbotnet"])
                # pkt_feature_str += ', Packet Count (botnet/not-botnet)= {0}/{1}'.format(botnet_pkt_cnt, p2p_pkt_cnt)
                # pkt_feature_str += ', Flow Count (botnet/not-botnet)= {0}/{1}'.format(len(botnet_flows), len(p2p_flows))
            if idx % 1000 == 0:
                sys.stdout.write("\r On Packet {0}".format(idx))
                sys.stdout.flush()
                # print("On packet {0}".format(idx)) # + pkt_feature_str)
    # pretty_dict(this_dict=botnet_flows)
    # pretty_dict(this_dict=p2p_flows)
    print("\nPacket Extraction Complete!")
    print("No. of Botnet Flows: {0} ({1} packets)".format(len(botnet_flows), botnet_pkt_cnt))
    print("No. of P2P Flows: {0} ({1} packets)".format(len(p2p_flows), p2p_pkt_cnt))
    print("Processed Dataset Written in {0}".format(csv_file))
    botnet_flows["total_packets"] = botnet_pkt_cnt
    p2p_flows["total_packets"] = p2p_pkt_cnt
    metadata = {
        "botnets": botnet_flows,
        "p2p": p2p_flows
    }
    with open(metadata_file, 'w') as file_obj:
        json.dump(metadata, file_obj, indent=4, sort_keys=True)
    sem.release() #!!!

def build_and_cache_dataset(args):
    # if cached dataset already exists, don't recreate. Just show what's inside
    if os.path.exists(args["pklpath"]):
        print("{0} Already Exists. Not Creating Again..".format(args["pklpath"]))
        with open(args["pklpath"], 'rb') as handle:
            dataset = pickle.load(handle)
            for key, val in dataset.items():
                print("{0} -> {1}".format(key, val.shape))
    else:
        features, labels = load_from_csv(csv_path=args["csvpath"])
        # convert train/test labels to one-hot
        labels = np.eye(args["nclasses"])[labels]
        arr_features, arr_labels = np.array(features), np.array(labels)
        # create ordered indices and shuffle them
        _indices = [*range(len(features))]
        random.shuffle(_indices)
        # split by given ratio
        split = int(args["split"]*len(features))
        tn_idx, ts_idx = _indices[:split], _indices[split:]
        tn_features, tn_labels = arr_features[tn_idx], arr_labels[tn_idx]
        ts_features, ts_labels = arr_features[ts_idx], arr_labels[ts_idx]
        dataset = {
            "tnx": tn_features, "tny": tn_labels,
            "tsx": ts_features, "tsy": ts_labels
        }
        with open(args["pklpath"], 'wb') as handle:
            pickle.dump(dataset, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("CACHED NUMPY DATASET AS {0}".format(args["pklpath"]))
        for key, val in dataset.items():
            print("{0} -> {1}".format(key, val.shape))

def main(args):
    pretty_dict(args)
    all_pcaps = os.listdir(args["pcapdir"])
    processes = []
    # preprocess the dataset
    for idx, pcap_file in enumerate(all_pcaps, 1):
        split_name = pcap_file.split('.')
        if split_name[-1] != "pcap":
            print("\n==> Skipping {0}..\n".format(pcap_file))
            continue
        pcap_name = '.'.join(x for x in split_name[:-1])
        pcap_path = os.path.join(args["pcapdir"], pcap_file)
        csv_path = os.path.join(args["csvdir"], pcap_name+'.csv')
        metadata_file = os.path.join(args["csvdir"], pcap_name+".txt")
        print("\n ({0}/{1}) Starting to Process File {2}".format(idx, len(all_pcaps), pcap_file))
        # process_pcap_dataset(pcap_path, csv_path, metadata_file, args["samples"], args["botnets_only"])
        # spawn a new process
        # https://zetcode.com/python/multiprocessing/
        pcap_process = MP.Process(target=process_pcap_dataset, args=(pcap_path, csv_path, metadata_file, args["samples"], args["botnets_only"]))
        pcap_process.daemon = True # stop the process once the main thread dies
        pcap_process.start()
        processes.append(pcap_process)
    # wait for all processes to be finished
    for process in processes:
        while process.is_alive():
            pass
    build_and_cache_dataset(args)


if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--name", type=str)
    CLI.add_argument("--pcapdir", type=str)
    CLI.add_argument("--nclasses", type=int)
    CLI.add_argument("--samples", type=int)
    CLI.add_argument("--botnets_only", type=int)
    CLI.add_argument("--split", type=float)
    CLI.add_argument("--csvdir", type=str)
    CLI.add_argument("--pkldir", type=str)
    args = vars(CLI.parse_args())
    main(args)