import scapy.all as scpy
import pickle
import pprint
import csv

BOTNET_IPS = {
    'storm': ['66.154.80.101', '66.154.80.105', '66.154.80.111', '66.154.80.125', '66.154.83.107', '66.154.83.113', '66.154.83.138', 
                '66.154.83.80', '66.154.87.39', '66.154.87.41', '66.154.87.57', '66.154.87.58', '66.154.87.61'],
    'waledac': ['192.168.58.136', '192.168.58.137', '192.168.58.150'],
    'zeus': ['10.0.2.15']
}
ALL_BOTNET_IPs = BOTNET_IPS['storm'] + BOTNET_IPS['waledac'] + BOTNET_IPS['zeus']

# PROTO = {'TCP': 6, 'UDP': 17}
# FIELDS = ['ipv4_src', 'ipv4_dst', 'src_port', 'dst_port', 'proto', 'size', 'inter_arrival_time', 'isbotnet']

# https://scapy.readthedocs.io/en/latest/api/scapy.layers.inet.html#
FIELDS = [
    'ipv4_ihl', 'ipv4_tos', 'ipv4_len', 'ipv4_id', 'ipv4_flags', 'ipv4_frag', 'ipv4_ttl', 'ipv4_proto', 'ipv4_chksum', 'ipv4_src', 'ipv4_dst', 'ipv4_options',
    'tcp_sport', 'tcp_dport', 'tcp_seq', 'tcp_ack', 'tcp_dataofs', 'tcp_reserved', 'tcp_flags', 'tcp_window', 'tcp_chksum', 'tcp_urgptr', 'tcp_options',
    'udp_sport', 'udp_dport', 'udp_len', 'udp_chksum',
    'pkt_size', 'inter_arrival_time', 'isbotnet'
    ]

def get_all_ipv4_fields(_pkt: dict, pkt: scpy.Packet):
    _pkt['ipv4_ihl']        = pkt[scpy.IP].ihl 
    _pkt['ipv4_tos']        = pkt[scpy.IP].tos 
    _pkt['ipv4_len']        = pkt[scpy.IP].len 
    _pkt['ipv4_id']         = pkt[scpy.IP].id 
    _pkt['ipv4_flags']      = pkt[scpy.IP].flags 
    _pkt['ipv4_frag']       = pkt[scpy.IP].frag 
    _pkt['ipv4_ttl']        = pkt[scpy.IP].ttl 
    _pkt['ipv4_proto']      = pkt[scpy.IP].proto 
    _pkt['ipv4_chksum']     = pkt[scpy.IP].chksum 
    _pkt['ipv4_src']        = pkt[scpy.IP].src 
    _pkt['ipv4_dst']        = pkt[scpy.IP].dst 
    _pkt['ipv4_options']    = pkt[scpy.IP].options

def get_all_tcp_fields(_pkt: dict, pkt: scpy.Packet):
    _pkt['tcp_sport']       = pkt[scpy.TCP].sport 
    _pkt['tcp_dport']       = pkt[scpy.TCP].dport 
    _pkt['tcp_seq']         = pkt[scpy.TCP].seq 
    _pkt['tcp_ack']         = pkt[scpy.TCP].ack 
    _pkt['tcp_dataofs']     = pkt[scpy.TCP].dataofs 
    _pkt['tcp_reserved']    = pkt[scpy.TCP].reserved 
    _pkt['tcp_flags']       = pkt[scpy.TCP].flags 
    _pkt['tcp_window']      = pkt[scpy.TCP].window 
    _pkt['tcp_chksum']      = pkt[scpy.TCP].chksum 
    _pkt['tcp_urgptr']      = pkt[scpy.TCP].urgptr 
    _pkt['tcp_options']     = pkt[scpy.TCP].options

def get_all_udp_fields(_pkt: dict, pkt: scpy.Packet):
    _pkt['udp_sport']       = pkt[scpy.UDP].sport 
    _pkt['udp_dport']       = pkt[scpy.UDP].dport 
    _pkt['udp_len']         = pkt[scpy.UDP].len
    _pkt['udp_chksum']      = pkt[scpy.UDP].chksum 

def join_to_str(*args):
    ret_str = ''
    for arg in args:
        ret_str += '_{0}'.format(arg)
    return ret_str

def pretty_dict(this_dict):
    pprint.pprint(this_dict)

def load_from_csv(csv_path, skip_header=True):
    full_data, full_labels = list(), list()
    with open(csv_path, newline='\n') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',')
        for idx, row in enumerate(spamreader):
            if skip_header and idx == 0: continue
            # drop the first two fields
            # i.e., src and dst IP addresses
            row.pop(0); row.pop(0)
            # last element in a row is label
            label = row.pop(-1)
            full_data.append([float(x) for x in row])
            full_labels.append(int(label))
    return full_data, full_labels

def load_dataset_from_pickle(pklpath):
    with open(pklpath, 'rb') as handle:
        return pickle.load(handle)

def write2DCSV(filename, matrix2D):
    with open(filename, 'w+') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=",", quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for arr in matrix2D:
            row = list()
            for elem in arr:
                row.append(str(elem))
            spamwriter.writerow(row)

def makeDNNWeightFile(layer_params, lut_dir, prefix):
    weight_file = lut_dir + "/" + prefix + "_NEURON_W_LUT" + ".csv"
    weights = layer_params[0]
    weights = weights.transpose([1, 0])
    write2DCSV(weight_file, weights)
    return

def makeDNNBiasFile(layer_params, lut_dir, prefix):
    bias_file = lut_dir + "/" + prefix + "_NEURON_B_LUT" + ".csv"
    bias = layer_params[1]
    bias = bias.reshape(-1, len(bias)).transpose([1, 0])
    write2DCSV(bias_file, bias)

def makeLUTsFromModel(layers, lut_dir):
    for idx, layer_params in enumerate(layers):
        # layer_params = layer.get_weights()
        makeDNNWeightFile(layer_params, lut_dir, "L" + str(idx))
        makeDNNBiasFile(layer_params, lut_dir, "L" + str(idx))
