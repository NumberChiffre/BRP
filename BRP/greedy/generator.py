from collections import OrderedDict
from BRP import *


class Generator:
    def __init__(self, idx=1):
        self.idx = idx
        self.bike_path = f'{ROOT_DIR}/sample_data/bike_data.txt'
        self.topology_path = f'{ROOT_DIR}/sample_data/topology.txt'
        self.bike_data = OrderedDict()

    def data_generator(self):
        raise NotImplementedError()

    def topology_generator(self):
        raise NotImplementedError()
