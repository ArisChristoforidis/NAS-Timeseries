# Author: Aris Christoforidis

# EVOLUTION
LAYERS_LIST = ['CONV_1.H', 'CONV_2.H', 'CONV_3.H', 'POOL_2.A', 'POOL_3.A', 'POOL_5.A',
               'CONV_1.N', 'CONV_2.N', 'CONV_3.N', 'POOL_2.M', 'POOL_3.M', 'POOL_5.M']

# GRAPH
NODE_INTERNAL_COUNT_RANGE = range(2,3)
NODE_INPUT_TAG = 'INPUT'
NODE_OUTPUT_TAG = 'OUTPUT'
MAX_NODES = 7
MAX_EDGES = 9

# PROBABILITY

# DATA
DATASET = 'activity_recognition'

# EVALUATION
UNEVALUATED_FITNESS = -1
METRIC = 'acc'
EPOCHS = 10
