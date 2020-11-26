
import traceback
from copy import deepcopy

import dgl
import networkx as nx
import numpy as np
import torch
from sklearn.preprocessing import OneHotEncoder

from nord.design.metaheuristics.evolutionary.graph_rem import (Innovation,
                                                               NASGenome)
from nord.design.metaheuristics.evolutionary.graph_rem.rem_config import (
    INPUT, OUTPUT)
from nord.neural_nets import BenchmarkEvaluator

from .graph_dataset import GraphDataset

DEBUG = False


def descriptor_to_feature_tensor(descriptor, one_hot=True):
    """
    Create a feature tensor according to ReNAS, utilizing a
    NeuralDescriptor.
    """
    max_nodes = 7

    labels = ['input',
              'conv1x1-bn-relu',
              'conv3x3-bn-relu',
              'maxpool3x3',
              'output']

    encoding = {labels[i]: i for i in range(5)}

    matrix, ops = BenchmarkEvaluator.descriptor_to_matrix(descriptor)
    ops_encoded = [encoding[key] for key in ops]
    nodes = len(ops)

    needed_nodes = max_nodes-nodes

    matrix = np.insert(matrix, [-1 for _ in range(needed_nodes)], 0, axis=1)
    matrix = np.insert(matrix, [-1 for _ in range(needed_nodes)], 0, axis=-0)

    feature_matrix = np.zeros((1, max_nodes, max_nodes))
    ops_encoded = ops_encoded[:-1]
    ops_encoded.extend(['' for _ in range(needed_nodes)])
    ops_encoded.append(4)

    if one_hot:
        feature_matrix = np.zeros((5, max_nodes, max_nodes))
        inds = np.where(matrix == 1)
        for i, j in zip(*inds):
            feature_matrix[ops_encoded[j], i, j] = 1

    else:
        inds = np.where(matrix == 1)
        for i, j in zip(*inds):
            feature_matrix[0, i, j] = ops_encoded[j]

    return feature_matrix


def get_nasbench_dataset(initial_population_size: int, evolutions: int,
                         classes: int = 3,
                         seed: int = 1337, val_perc: float = 0.1,
                         test_perc: float = 0.3,
                         all_vs_all: [bool, bool] = [True, True],
                         as_dgl: bool = True, one_hot: bool = True):

    evaluator = BenchmarkEvaluator(verbose=False)

    np.random.seed(seed)
    torch.random.manual_seed(seed)

    # parents_perc = 0.25
    identity_prob = 0.05
    add_node_prob = 0.25
    initial_add_node_prob = 1.0

    innv = Innovation()
    innv.new_generation()

    population = []

    def evaluate(g):

        fitness = 0
        total_time = 0
        fits = []
        times = []
        try:
            d = g.to_descriptor()
            # fitness = len(d.layers) + len(d.connections)

            for _ in range(30):
                fitness, total_time = evaluator.descriptor_evaluate(
                    d, acc='test_accuracy')
                fits.append(fitness)
                times.append(total_time)
        except Exception as e:
            if DEBUG:
                print('INVALID')
                print(offspring)
                print(e)
                traceback.print_exc()

        if len(fits) == 0:
            return 0, 0
        fitness = np.average(fits)
        total_time = np.average(times)
        return fitness, total_time

    def in_dataset(g):
        try:
            d = g.to_descriptor()
        except Exception as e:
            if DEBUG:
                print('INVALID')
                print(offspring)
                print(e)
                traceback.print_exc()
            return False

        return evaluator.has_been_evaluated(d)

    for i in range(initial_population_size):
        g = NASGenome(identity_prob, add_node_prob, innovation=innv)
        g.mutate(add_node_rate=initial_add_node_prob)
        population.append(g)

    generation = 0
    fitnesses = []

    for i in range(initial_population_size):
        g = population[i]
        fitness, total_time = evaluate(g)
        fitnesses.append(fitness)

    while generation < evolutions:

        innv.new_generation()
        generation += 1

        sample_sz = 1  # random search
        sample = np.random.choice(population, size=sample_sz)
        parent = np.argmax([x.fitness for x in sample])
        parent = sample[parent]
        offspring = deepcopy(parent)
        offspring.mutate()
        fitness, total_time = 0, 0

        if in_dataset(offspring):
            generation -= 1
            continue
            print('In Dataset')
        try:
            fitness, total_time = evaluate(offspring)

        except Exception as e:
            if DEBUG:
                print('INVALID')
                print(offspring)
                print(e)
                traceback.print_exc()
        if fitness < 0.01:
            generation -= 1
            continue

        offspring.fitness = fitness
        population.append(offspring)
        fitnesses.append(fitness)
    onehot_encoder = OneHotEncoder(sparse=False)
    onehot_encoder.fit(np.array(
        [x for x in range(-2, 3)]).reshape(-1, 1))

    trainset, valset, testset = None, None, None

    graphs = []
    fits = []
    graph_no = 0
    for g, f in zip(population, fitnesses):
        if f < 0.01:
            continue
        if as_dgl:
            gg = g.to_networkx()
            labels = list(gg.nodes)

            gg = nx.relabel.convert_node_labels_to_integers(gg)
            new_labels = list(gg.nodes)
            g_dgl = dgl.DGLGraph(gg)

            for i in range(len(new_labels)):
                data = g.nodes.genes[labels[i]].value
                if labels[i] == INPUT:
                    data = -2
                elif labels[i] == OUTPUT:
                    data = -1

                onehot_encoded = onehot_encoder.transform(
                    np.array(data).reshape(-1, 1))
                g_dgl.nodes[new_labels[i]].data['x'] = torch.tensor(
                    onehot_encoded)
            graphs.append(g_dgl)
            fits.append(f)

        else:
            d = g.to_descriptor()
            ft = descriptor_to_feature_tensor(d, one_hot)
            graphs.append(ft)
            fits.append(f)

    graph_no = len(graphs)

    if as_dgl:

        array_holder = np.empty(len(graphs), dtype=np.object)
        for i in range(len(graphs)):
            array_holder[i] = graphs[i]
        graphs = array_holder

    graphs = np.array(graphs)
    fits = np.array(fits)
    indices = np.random.permutation(graph_no)

    train_no = int(graph_no*(1-val_perc-test_perc))
    val_no = int(graph_no*val_perc)

    trainset = GraphDataset(graphs[indices[:train_no]],
                            fits[indices[:train_no]],
                            classes, all_vs_all=all_vs_all[0])
    valset = None
    if (val_no > 0):
        valset = GraphDataset(graphs[indices[train_no:train_no+val_no]],
                              fits[indices[train_no:train_no+val_no]],
                              classes, all_vs_all=all_vs_all[1])

    testset = GraphDataset(graphs[indices[train_no+val_no:]],
                           fits[indices[train_no+val_no:]],
                           classes, all_vs_all=all_vs_all[1])

    return trainset, valset, testset
