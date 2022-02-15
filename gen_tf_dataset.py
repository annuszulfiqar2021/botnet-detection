from cProfile import label
import tensorflow as tf
from helpers import *
import argparse
import pathlib

"""
FIELDS = [
    'ipv4_ihl', 'ipv4_tos', 'ipv4_len', 'ipv4_id', 'ipv4_flags', 'ipv4_frag', 'ipv4_ttl', 'ipv4_proto', 'ipv4_chksum', 'ipv4_src', 'ipv4_dst', 'ipv4_options',
    'tcp_sport', 'tcp_dport', 'tcp_seq', 'tcp_ack', 'tcp_dataofs', 'tcp_reserved', 'tcp_flags', 'tcp_window', 'tcp_chksum', 'tcp_urgptr', 'tcp_options',
    'udp_sport', 'udp_dport', 'udp_len', 'udp_chksum',
    'pkt_size', 'inter_arrival_time', 'isbotnet'
    ]
"""

def show_batch(dataset):
  for batch, label in dataset.take(1):
    for key, value in batch.items():
      print("{:20s}: {}".format(key,value.numpy()))

def batch_processor(features, labels):
    """ https://www.tensorflow.org/tutorials/load_data/csv
    """
    # combine 4 ports into 2
    features['sport'] = features['tcp_sport'] + features['udp_sport']
    features['dport'] = features['tcp_dport'] + features['udp_dport']
    features.pop('tcp_sport', None)
    features.pop('udp_sport', None)
    features.pop('tcp_dport', None)
    features.pop('udp_dport', None)
    # cast all values
    # for key, value in features.items():
    #     features[key] = float(value)
    # print(type(features))
    # workaround https://stackoverflow.com/questions/65241790/how-to-efficiently-use-a-tf-data-dataset-made-of-ordereddict
    return (tf.stack([tf.cast(x, tf.float32) for x in features.values()], axis=1), labels)

def get_tf_dataset(csvpath: str, fields, label_name, batch_size):
    """ https://www.tensorflow.org/api_docs/python/tf/data/experimental/make_csv_dataset
        https://www.tensorflow.org/guide/data
        https://colab.research.google.com/github/adammichaelwood/tf-docs/blob/csv-feature-columns/site/en/r2/tutorials/load_data/csv.ipynb#scrollTo=Q_nm28IzNDTO
    """
    packet_ds = tf.data.experimental.make_csv_dataset(file_pattern = "{0}/*.csv".format(csvpath),
                                                        select_columns=fields,
                                                        label_name=label_name, 
                                                        batch_size=batch_size, 
                                                        num_epochs=1,
                                                        num_parallel_reads=20,
                                                        shuffle_buffer_size=10000)
    # preprocess the entire batch
    processed_packet_ds = packet_ds.map(batch_processor)
    return processed_packet_ds

def main(args):
    pretty_dict(args)
    processed_packet_ds = get_tf_dataset(args["csvdir"], 
                                        ['ipv4_proto', 
                                        'tcp_sport', 'tcp_dport', 
                                        'udp_sport', 'udp_dport', 
                                        'pkt_size', 'inter_arrival_time', 'isbotnet'],
                                        'isbotnet')
    

    examples, labels = next(iter(processed_packet_ds)) # Just the first batch.
    print("EXAMPLES: \n", examples, "\n")
    print("LABELS: \n", labels)
    # show_batch(processed_packet_ds)
    # for samples in processed_packet_ds.take(1):
    #     pkts, labels = samples
    #     for i, (name, value) in enumerate(pkts.items()):
    #         print(type(samples), type(pkts), type(labels))
    #         print(f"{name:20s}: {value}")
    #     print(labels)
    # print('...')
    # print(f"[total: {len(samples)} features]")


if __name__ == "__main__":
    CLI = argparse.ArgumentParser()
    CLI.add_argument("--csvdir", type=str)
    args = vars(CLI.parse_args())
    main(args)