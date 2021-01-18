# Author: Aris Christoforidis

# EVOLUTION
POPULATION_SIZE = 1
GENERATIONS = 1000
MAX_NOTABLE_MODULES = 15
TEMP_MODULE_TTL = 10
MIN_PROPERTIES_OBS_COUNT = 3
DELETE_NETWORKS_EVERY = 10
NETWORK_REMAIN_PERCENTAGE = 0.8
LAYERS_LIST = ['CONV_1.H', 'CONV_2.H', 'CONV_3.H', 'POOL_2.A', 'POOL_3.A', 'POOL_5.A', #'DROPOUT_20.N', 'DROPOUT_40.N', 'DROPOUT_60.N',
               'CONV_1.N', 'CONV_2.N', 'CONV_3.N', 'POOL_2.M', 'POOL_3.M', 'POOL_5.M']#, 'RELU_1.N']

# GRAPH
NODE_INTERNAL_COUNT_RANGE = range(2,3)
NODE_INPUT_TAG = 'INPUT'
NODE_OUTPUT_TAG = 'OUTPUT'
LAYER_INPUT_PREFIX = 'IN'
LAYER_OUTPUT_SUFFIX = 'OUT'

# PROBABILITY
ADD_NODE_PROBABILITY = 0.25
ADD_EDGE_PROBABILITY = 0.7
DROPOUT_PROBABILITY = 0.1

# DATA
DATASET = 'activity_recognition'
BEST_NETWORK_SCORE_LABEL = 'score'
BEST_NETWORK_PROPERTIES_LABEL = 'properties'

# LAYERS
CHANNEL_COUNT = 32
STRIDE_COUNT = 1

# EVALUATION
UNEVALUATED_FITNESS = -1
METRIC = 'acc'
EPOCHS = 20

# ERROR HANDLING
INVALID_NETWORK_FITNESS = -2
INVALID_NETWORK_TIME = -2

# SAVING
BEST_NETWORK_DATA_SAVE_BASE_PATH = "best_network_data"