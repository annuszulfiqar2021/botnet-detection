# user level variables
export MC17_USER			= zulfiqaa
export MC17_SERVER			= mc17.cs.purdue.edu
export MC17_PASSWORD		= AZPCS0821

# project variables
export RAW_DATA_DIR 		= raw_dataset
export BOTNETS_DIR 			= $(RAW_DATA_DIR)/botnets
export P2P_PCAP_DIR 		= $(RAW_DATA_DIR)/p2p
export P2P_FILES_TXT		= $(P2P_PCAP_DIR)/p2p_dataset.txt
export PROC_DATA_DIR		= dataset
export P2P_DOWNLOAD_TARGET	= download_p2p_dataset.py
export DATASET_TARGET 		= process_dataset.py
export TF_DATASET_TARGET 	= gen_tf_dataset.py
export TRAIN_TARGET 		= train.py
export FLOW_STATS_TARGET 	= get_flow_statistics.py

# data variables
export STORM_PCAP_DIR 		= $(BOTNETS_DIR)/storm
# export STORM_PCAP 		= $(BOTNETS_DIR)/storm/gtisc-winobot.20071027.1193479202.pcap
# export STORM_CSV 			= $(PROC_DATA_DIR)/storm-unprocessed.csv
export STORM_PKL 			= $(PROC_DATA_DIR)/storm-processed.pkl

export WALEDAC_PCAP_DIR 	= $(BOTNETS_DIR)/waledac
# export WALEDAC_PCAP 		= $(BOTNETS_DIR)/waledac/Waledac.br0.1.anonymous.pcap
# export WALEDAC_CSV 		= $(PROC_DATA_DIR)/waledac-unprocessed.csv
export WALEDAC_PKL 			= $(PROC_DATA_DIR)/waledac-processed.pkl

export ZEUS_PCAP_DIR 		= $(BOTNETS_DIR)/zeus
# export ZEUS_PCAP 			= $(BOTNETS_DIR)/zeus/zeus1-1.pcap
# export ZEUS_CSV 			= $(PROC_DATA_DIR)/zeus-unprocessed.csv
export ZEUS_PKL 			= $(PROC_DATA_DIR)/zeus-processed.pkl

export P2P_REMOTE_DIR		= /homes/zulfiqaa/scratch/brett_dumps/
export P2P_PCAP_COUNT 		= 10

# dataset variables
export NCLASS_SAMPLES 		= 1000000000000
export TRAIN_TEST_SPLIT 	= 0.8
export TRAIN_VAL_SPLIT 		= 0.8

# model and training variables
export TRAIN_DATA_DIR		= $(PROC_DATA_DIR)/training
export EVAL_DATA_DIR		= $(PROC_DATA_DIR)/evaluation
export SPATIAL_DIR 			= spatial
export MODELS_DIR 			= models
export STORM_DNN_NAME 		= STORM_BOTNET
export WALEDAC_DNN_NAME 	= WALEDAC_BOTNET
export ZEUS_DNN_NAME 		= ZEUS_BOTNET
export BOT_DNN_NAME			= BOTNET
# export MODEL_FEATURES 	= ipv4_proto tcp_sport tcp_dport udp_sport udp_dport pkt_size inter_arrival_time isbotnet
# ipv4_ihl ipv4_tos ipv4_len ipv4_id ipv4_flags ipv4_frag ipv4_ttl ipv4_proto ipv4_chksum ipv4_src ipv4_dst ipv4_options tcp_sport tcp_dport tcp_seq tcp_ack tcp_dataofs tcp_reserved tcp_flags tcp_window tcp_chksum tcp_urgptr tcp_options udp_sport udp_dport udp_len udp_chksum pkt_size inter_arrival_time isbotnet
export MODEL_FEATURES 		= ipv4_ihl ipv4_tos ipv4_len ipv4_id ipv4_frag ipv4_ttl ipv4_proto ipv4_chksum tcp_sport tcp_dport tcp_dataofs tcp_reserved tcp_window tcp_chksum tcp_urgptr udp_sport udp_dport udp_len udp_chksum pkt_size inter_arrival_time isbotnet
export DNN_ARCHITECTURE 	= 128 256 256 256 128 64
export DNN_LAYER_PARS 		= 4 4 4 4 4 4
export INPUT_DIM 			= 19
export N_CLASSES 			= 2
export OUTPUT_DIM			= 1
export METRIC 				= f1
export BATCH_SIZE 			= 128
export EPOCHS 				= 10

# FlowLens variables
export FLOWLENS_DIR			= FlowLens
export FL_BOTNET_DIR		= $(FLOWLENS_DIR)/SecurityTasksEvaluation/BotnetAnalysis

.DEFAULT_GOAL = train-zeus-model

$(PROC_DATA_DIR):
	@echo "[LOG] Creating DATASET Directory => $(PROC_DATA_DIR)"
	mkdir $(PROC_DATA_DIR)

$(MODELS_DIR):
	@echo "[LOG] Creating MODELS Directory => $(MODELS_DIR)"
	mkdir $(MODELS_DIR)

$(SPATIAL_DIR):
	@echo "[LOG] Creating SPATIAL Directory => $(SPATIAL_DIR)"
	mkdir $(SPATIAL_DIR)

download-p2p:
	python $(P2P_DOWNLOAD_TARGET) --user $(MC17_USER) --server $(MC17_SERVER) --password $(MC17_PASSWORD) --remotedir $(P2P_REMOTE_DIR) \
				--files $(P2P_FILES_TXT) --downloaddir $(P2P_PCAP_DIR) -n $(P2P_PCAP_COUNT)

waledac-dataset: | $(PROC_DATA_DIR)
	python $(DATASET_TARGET) --name waledac --pcapdir $(WALEDAC_PCAP_DIR) --nclasses $(N_CLASSES) --samples $(NCLASS_SAMPLES) --botnets_only 1 \
				--split $(TRAIN_TEST_SPLIT) --csvdir $(PROC_DATA_DIR) --pkldir $(PROC_DATA_DIR)

storm-dataset: | $(PROC_DATA_DIR)
	python $(DATASET_TARGET) --name storm --pcapdir $(STORM_PCAP_DIR) --nclasses $(N_CLASSES) --samples $(NCLASS_SAMPLES) --botnets_only 1 \
				--split $(TRAIN_TEST_SPLIT) --csvdir $(PROC_DATA_DIR) --pkldir $(PROC_DATA_DIR) 

zeus-dataset: | $(PROC_DATA_DIR)
	python $(DATASET_TARGET) --name zeus --pcapdir $(ZEUS_PCAP_DIR) --nclasses $(N_CLASSES) --samples $(NCLASS_SAMPLES) --botnets_only 1 \
				--split $(TRAIN_TEST_SPLIT) --csvdir $(PROC_DATA_DIR) --pkldir $(PROC_DATA_DIR) 

p2p-dataset: | $(PROC_DATA_DIR)
	python $(DATASET_TARGET) --name p2p --pcapdir $(P2P_PCAP_DIR) --nclasses $(N_CLASSES) --samples $(NCLASS_SAMPLES) --botnets_only 0 \
				--split $(TRAIN_TEST_SPLIT) --csvdir $(PROC_DATA_DIR) --pkldir $(PROC_DATA_DIR) 

training: | $(MODELS_DIR) $(SPATIAL_DIR)
	python $(TRAIN_TARGET) --name $(BOT_DNN_NAME) --arch $(DNN_ARCHITECTURE) --pars $(DNN_LAYER_PARS) --trainset $(TRAIN_DATA_DIR) --evalset $(EVAL_DATA_DIR) \
			--features $(MODEL_FEATURES) --label isbotnet --input_dim $(INPUT_DIM) --output_dim $(OUTPUT_DIM) --metric $(METRIC) --batch_size $(BATCH_SIZE) \
			--epochs $(EPOCHS) --model_dir $(MODELS_DIR) --spatial_dir $(SPATIAL_DIR)

gen-tf-dataset: | $(PROC_DATA_DIR)
	python $(TF_DATASET_TARGET) --csvdir $(PROC_DATA_DIR)

waledac-experiment: waledac-dataset train-waledac-model

storm-experiment: storm-dataset train-storm-model

zeus-experiment: zeus-dataset train-zeus-model

get-flow-statistics:
	python $(FLOW_STATS_TARGET) --traindir $(TRAIN_DATA_DIR) --evaldir $(EVAL_DATA_DIR)

# FlowLens targets
flowlens-parse-pcaps:
	python $(FL_BOTNET_DIR)/peershark/FilterPackets.py



clean-flowlens-run:
	-rm -rf $(FL_BOTNET_DIR)/classificationResults $(FL_BOTNET_DIR)/FeatureSets $(FL_BOTNET_DIR)/FlowData $(FL_BOTNET_DIR)/SuperFlowData $(FL_BOTNET_DIR)/TrainingData

# clean-csv:
# 	-rm -rf $(PROC_DATA_DIR)/*

# clean-pkl:
# 	-rm -rf $(PROC_DATA_DIR)/*

# clean-dataset: clean-csv clean-pkl

# clean-waledac-model:
# 	-rm -rf $(shell find ./$(MODELS_DIR) -name "WALEDAC*")

# clean-storm-model:
# 	-rm -rf $(shell find ./$(MODELS_DIR) -name "STORM*")

# clean-zeus-model:
# 	-rm -rf $(shell find ./$(MODELS_DIR) -name "ZEUS*")

clean-model:
	-rm -rf $(shell find ./$(MODELS_DIR) -name "BOTNET*")

clean-waledac-spatial:
	-rm -rf $(shell find ./$(SPATIAL_DIR) -name "WALEDAC*")

clean-storm-spatial:
	-rm -rf $(shell find ./$(SPATIAL_DIR) -name "STORM*")

clean-zeus-spatial:
	-rm -rf $(shell find ./$(SPATIAL_DIR) -name "ZEUS*")

clean-models: clean-model # clean-waledac-model clean-storm-model clean-zeus-model

clean-spatial: clean-waledac-spatial clean-storm-spatial

clean-logs:
	-rm -rf logs/

clean: clean-models clean-spatial clean-logs #  clean-dataset