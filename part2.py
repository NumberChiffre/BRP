from BRP import *
from BRP.greedy.grid_generator import GridGenerator
from BRP.greedy.greedy_second import GreedyTraversalSecond
import pandas as pd
import numpy as np
import time
import matplotlib.pyplot as plt

if __name__ == '__main__':
    df = pd.DataFrame(
        columns=['# vehicles required', 'Computational times (sec.)'],
        index=[x for x in range(1, num_test_iterations + 1)])

    for idx in range(num_test_iterations):
        obj = GridGenerator(idx=idx + 1)
        obj.data_generator()
        obj.topology_generator()

        # generate graph traversal
        gt = GreedyTraversalSecond(obj.graph, obj.bike_data)
        start_time = time.time()
        min_traversals = gt.greedy_traversal()
        duration = time.time() - start_time
        df.index.name = 'Datasets'
        df.loc[idx + 1, '# vehicles required'] = len(min_traversals)
        df.loc[idx + 1, 'Computational times (sec.)'] = round(duration, 4)