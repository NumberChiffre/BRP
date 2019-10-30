from BRP import *
from BRP.greedy.data_generator import DataGenerator
from BRP.greedy.greedy import GreedyTraversal
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.DataFrame(
        columns=['# vehicles required', 'Computational times (sec.)'],
        index=[x for x in range(1, num_test_iterations + 1)])

    for idx in range(num_test_iterations):
        obj = DataGenerator(idx=idx + 1)
        obj.data_generator()
        obj.topology_generator()

        # generate graph traversal
        gt = GreedyTraversal(obj.graph, obj.bike_data)
        start_time = time.time()
        min_traversals = gt.greedy_traversal()
        duration = time.time() - start_time
        df.index.name = 'Datasets'
        df.loc[idx + 1, '# vehicles required'] = len(min_traversals)
        df.loc[idx + 1, 'Computational times (sec.)'] = round(duration, 4)

        title = 'Figure 1: Demand Decrease and Number of Vehicles'
        plt.title(title)
        bar_width = 0.25
        plt.bar(np.arange(len(min_traversals)),
                [v[-2] for v in min_traversals.values()], bar_width,
                color='blue')
        plt.bar(np.arange(len(min_traversals)) + bar_width,
                [v[-1] for v in min_traversals.values()], bar_width,
                color='orange')
        plt.xticks(np.arange(len(min_traversals)),
                   [f'Vehicle #{x + 1}' for x in range(len(min_traversals))])
        plt.xlabel('# of Vehicles')
        leg = ['Number of visited bike stations', 'Satisfied demand']
        plt.legend(leg, framealpha=1, frameon=True)
        plt.savefig(f'{ROOT_DIR}/results/results_{idx + 1}.png')
        plt.clf()
        print(
            f'vehicles needed for simulation #{idx + 1}: {len(min_traversals)}')
    df.to_csv(f'{ROOT_DIR}/results/results.csv')
