# Author: Aris Christoforidis.
from module_manager import ModuleManager
from config import DELETE_NETWORKS_EVERY, GENERATIONS, INVALID_NETWORK_FITNESS, INVALID_NETWORK_TIME, NETWORK_REMAIN_PERCENTAGE, POPULATION_SIZE, UNEVALUATED_FITNESS
from neural_module import NeuralModule
from evaluation import Evaluator, NasBenchEvaluator
from communication import Communicator
from mpi4py import MPI

import networkx as nx
import matplotlib.pyplot as plt

def main():
    # Establish communication.
    communicator = Communicator()
    
    # Initialize evaluator.
    # Switch to this to use nasbench.
    #evaluator = NasBenchEvaluator()
    evaluator = Evaluator()

    # Initialize module manager.
    manager = ModuleManager(evaluator)

    # Make initial population.
    population = [NeuralModule(None, manager) for _ in range(POPULATION_SIZE)]

    for generation in range(GENERATIONS):
        print(f"Generation {generation+1}")
        generation_training_time = 0

        # Inform module manager for generation change.
        manager.on_generation_increase()

        # Try mutate neural modules.
        for module in population:
            module.mutate()

        # NOTE: Some modules may not be able to be evaluated, due to a pytorch issue.
        # We replace these with new modules.
        invalid_modules = []
        # Evaluate those that where mutated.
        for idx, module in enumerate(population):
            if module.fitness == UNEVALUATED_FITNESS:
                accuracy, time = evaluator.evaluate(module)
                # If the network can't be evaluated, add a new one, and mark it
                # for deletion.
                if accuracy == INVALID_NETWORK_FITNESS and time == INVALID_NETWORK_TIME:
                    print(f"Network {idx} could not be evaluated, replacing.")
                    population.append(NeuralModule(None, manager))
                    invalid_modules.append(module)
                    continue
                # If the network is ok, proceed with the algorithm.
                generation_training_time += time
                # module.show_abstract_graph()
                # module.show_full_graph()
                module.set_fitness(accuracy)
                print(f"Neural module {idx+1}: {accuracy:.3f}")

        print(f"Time elapsed: {generation_training_time:.2f} seconds")
        
        # Print best module fitness.
        best_module = max(population, key=lambda x: x.fitness)
        print(f"Best module fitness: {best_module.fitness:.2f}")

        # Remove invalid modules.
        for module in invalid_modules:
            population.remove(module)

        # Eliminate weaker modules.
        if generation % DELETE_NETWORKS_EVERY == 0:
            # Sort based on fitness.
            population.sort(key=lambda x: -x.fitness)
            # Calculate how many networks to keep and throw away the rest.
            networks_to_keep = int(NETWORK_REMAIN_PERCENTAGE * POPULATION_SIZE)
            population = population[:networks_to_keep]

            # Create new random modules.
            networks_to_create = POPULATION_SIZE - networks_to_keep
            population.extend([NeuralModule(None, manager) for _ in range(networks_to_create)])

            # Logging.
            fitness_threshold = population[networks_to_keep-1].fitness
            print(f"Replacing {networks_to_create} networks. Fitness threshold: {fitness_threshold}")

        print("="*50)
    
    # Save best network.
    manager.save_best_module()
    
    print(f"Size: {communicator._get_size()}")
    return

if __name__ == "__main__":
    main()