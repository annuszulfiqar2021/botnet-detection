import multiprocessing as MP
import scapy.all as scpy
from helpers import ALL_BOTNET_IPs, join_to_str, pretty_dict
import numpy as np
import statistics
import argparse
import pickle
import random
import json
import csv
import sys
import os

FIELDS = ["ipv4_src", "ipv4_dst", "num_pkts", "data_volume", "duration", "median_ipd", "isbotnet"]
P2P_CLASS = 0
BOTNET_CLASS = 1

def process_pcap_dataset(pcap_file: str, csv_file: str, metadata_file: str, samples: int, botnets_only: int, verbose: int):
    # PcapReader comes from scapy and reads packets iteratively
    # without loading the full file into memory (very efficient)
    pkts = scpy.PcapReader(pcap_file)
    # Let's iterate through every packet and maintain some numbers
    botnet_pkt_cnt, p2p_pkt_cnt = 0, 0
    botnet_conversations, p2p_conversations = {}, {}
    conversations_first_packet_arrival_time = {}
    conversations_last_packet_arrival_time = {}
    converstions_ipds = {}
    if os.path.exists(csv_file):
        print("{0} Already Exists. Not Creating Again..".format(csv_file))
        return
    for idx, pkt in enumerate(pkts, 1):
        # collect as many packets as suggested from commmand line
        if botnet_pkt_cnt+p2p_pkt_cnt > 2*samples:
            break
        # do the rest of the processing only for TCP or UDP packets
        if scpy.IP in pkt and (scpy.TCP in pkt or scpy.UDP in pkt):
            ipv4_src = pkt[scpy.IP].src
            ipv4_dst = pkt[scpy.IP].dst
            conversation_tuple = join_to_str(ipv4_src, ipv4_dst)
            # decide if it is a botnet or not using src/dst IPv4 address
            # is botnet!
            if botnets_only == 1 and (ipv4_src in ALL_BOTNET_IPs or ipv4_dst in ALL_BOTNET_IPs):
                # if sample count is exceeded, then just drop this one and move on
                if botnet_pkt_cnt > samples:
                    continue
                botnet_pkt_cnt += 1
                # initialize a new conversation only if it doesn't already exist!
                if conversation_tuple not in botnet_conversations.keys():
                    botnet_conversations[conversation_tuple] = {key:0 for key in FIELDS}
                    botnet_conversations[conversation_tuple]['ipv4_src'] = ipv4_src
                    botnet_conversations[conversation_tuple]['ipv4_dst'] = ipv4_dst
                    # update data volume
                    botnet_conversations[conversation_tuple]['data_volume'] = len(pkt)
                    # update number of pkts
                    botnet_conversations[conversation_tuple]["num_pkts"] = 1
                    # add flow start time
                    conversations_first_packet_arrival_time[conversation_tuple] = pkt.time
                    # add flow start time
                    conversations_last_packet_arrival_time[conversation_tuple] = pkt.time
                    # start this flow's empty list of IPDs
                    converstions_ipds[conversation_tuple] = [0]
                    # mark this conversation as botnet (only once!)
                    botnet_conversations[conversation_tuple]["isbotnet"] = BOTNET_CLASS
                else: # packet from a running flow, update it
                    # update data volume
                    botnet_conversations[conversation_tuple]['data_volume'] += len(pkt)
                    # increment packet count for this flow
                    botnet_conversations[conversation_tuple]["num_pkts"] += 1
                    # get inter-arrival time, and update last packet time
                    this_pkt_ipd = pkt.time - conversations_last_packet_arrival_time[conversation_tuple]
                    converstions_ipds[conversation_tuple].append(this_pkt_ipd)
                    conversations_last_packet_arrival_time[conversation_tuple] = pkt.time
            elif botnets_only == 0: # is not botnet!
                # if sample count is exceeded, then just drop this one and move on
                if p2p_pkt_cnt > samples:
                    continue
                p2p_pkt_cnt += 1
                # initialize a new conversation only if it doesn't already exist!
                if conversation_tuple not in p2p_conversations.keys():
                    p2p_conversations[conversation_tuple] = {key:0 for key in FIELDS}
                    p2p_conversations[conversation_tuple]['ipv4_src'] = ipv4_src
                    p2p_conversations[conversation_tuple]['ipv4_dst'] = ipv4_dst
                    # update data volume
                    p2p_conversations[conversation_tuple]['data_volume'] = len(pkt)
                    # update number of pkts
                    p2p_conversations[conversation_tuple]["num_pkts"] = 1
                    # add flow start time
                    conversations_first_packet_arrival_time[conversation_tuple] = pkt.time
                    # add flow start time
                    conversations_last_packet_arrival_time[conversation_tuple] = pkt.time
                    # start this flow's empty list of IPDs
                    converstions_ipds[conversation_tuple] = [0]
                    # mark this conversation as botnet (only once!)
                    p2p_conversations[conversation_tuple]["isbotnet"] = P2P_CLASS
                else: # packet from a running flow, update it
                    # update data volume
                    p2p_conversations[conversation_tuple]['data_volume'] += len(pkt)
                    # increment packet count for this flow
                    p2p_conversations[conversation_tuple]["num_pkts"] += 1
                    # get inter-arrival time, and update last packet time
                    this_pkt_ipd = pkt.time - conversations_last_packet_arrival_time[conversation_tuple]
                    converstions_ipds[conversation_tuple].append(this_pkt_ipd)
                    conversations_last_packet_arrival_time[conversation_tuple] = pkt.time
        if verbose == 1 and idx % 1000 == 0:
            sys.stdout.write("\r On Packet {0}".format(idx))
            sys.stdout.flush()
            # pkt_feature_str = ""
            # pkt_feature_str += ', IPv4 src: {0}, IPv4 dst: {1}'.format(_pkt["ipv4_src"], _pkt["ipv4_dst"])
            # pkt_feature_str += ', IPV4_PROTO = {0}, PKT size: {1}'.format(_pkt["ipv4_proto"], _pkt["pkt_size"])
            # pkt_feature_str += ', src port: {0}, dst port: {1}'.format(_pkt["tcp_sport"]+_pkt["udp_sport"], _pkt["tcp_dport"]+_pkt["udp_dport"])
            # pkt_feature_str += ', INTER-ARRIVAL-TIME = {0}'.format(_pkt["inter_arrival_time"])
            # pkt_feature_str += ', IS BOTNET? = {0}'.format(_pkt["isbotnet"])
            # pkt_feature_str += ', Packet Count (botnet/not-botnet)= {0}/{1}'.format(botnet_pkt_cnt, p2p_pkt_cnt)
            # pkt_feature_str += ', Flow Count (botnet/not-botnet)= {0}/{1}'.format(len(botnet_conversations), len(p2p_conversations))
            # print("On packet {0} => {1}".format(idx, pkt_feature_str))
    # write the conversations into csv
    with open(csv_file, 'w') as csvfile:
        csvwriter = csv.DictWriter(csvfile, fieldnames=FIELDS)
        csvwriter.writeheader()
        for bot_tup, bot_conv in botnet_conversations.items():
            # calculate median IPD
            bot_conv["median_ipd"] = statistics.median(converstions_ipds[bot_tup])
            # calculate duration
            bot_conv["duration"] = conversations_last_packet_arrival_time[bot_tup] - conversations_first_packet_arrival_time[bot_tup]
            # write new sample to csv
            csvwriter.writerow(bot_conv)
        for p2p_tup, p2p_conv in p2p_conversations.items():
            # calculate median IPD
            p2p_conv["median_ipd"] = statistics.median(converstions_ipds[p2p_tup])
            # calculate duration
            p2p_conv["duration"] = conversations_last_packet_arrival_time[p2p_tup] - conversations_first_packet_arrival_time[p2p_tup]
            # write new sample to csv
            csvwriter.writerow(p2p_conv)
    print("\nPacket Extraction Complete!")
    print("No. of Botnet Conversations: {0} (packets = {1})".format(len(botnet_conversations), botnet_pkt_cnt))
    print("No. of P2P Conversations: {0} (packets = {1})".format(len(p2p_conversations), p2p_pkt_cnt))
    print("Processed Dataset Written in {0}".format(csv_file))
    # botnet_conversations["total_packets"] = botnet_pkt_cnt
    # p2p_conversations["total_packets"] = p2p_pkt_cnt
    # metadata = {
    #     "botnets": botnet_conversations,
    #     "p2p": p2p_conversations
    # }
    # with open(metadata_file, 'w') as file_obj:
    #     json.dump(metadata, file_obj, indent=4, sort_keys=True)

def main(args):
    pretty_dict(args)
    all_pcaps = os.listdir(args["pcapdir"])
    arguments = []
    # preprocess the dataset
    for idx, pcap_file in enumerate(all_pcaps, 1):
        split_name = pcap_file.split('.')
        if split_name[-1] != "pcap":
            print("\n==> Skipping {0}..\n".format(pcap_file))
            continue
        pcap_name = '.'.join(x for x in split_name[:-1])
        pcap_path = os.path.join(args["pcapdir"], pcap_file)
        csv_path = os.path.join(args["csvdir"], "conversations_"+pcap_name+'.csv')
        metadata_file = os.path.join(args["csvdir"], "conversations_"+pcap_name+".txt")
        print("\n ({0}/{1}) Starting to Process File {2}".format(idx, len(all_pcaps), pcap_file))
        arguments.append((pcap_path, csv_path, metadata_file, args["samples"], args["botnets_only"], args["verbose"]))
    # spawn a pool of processes
    print(f"Starting computation on {MP.cpu_count()} cores")
    # https://zetcode.com/python/multiprocessing/
    with MP.Pool() as pool:
        pool.starmap(process_pcap_dataset, arguments)


if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--pcapdir", type=str)
    CLI.add_argument("--samples", type=int)
    CLI.add_argument("--botnets_only", type=int)
    CLI.add_argument("--csvdir", type=str)
    CLI.add_argument("--verbose", type=int, default=0)
    args = vars(CLI.parse_args())
    main(args)