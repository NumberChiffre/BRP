from collections import OrderedDict
import numpy as np
import random

import BRP
from BRP import *
from BRP.greedy.graph import Graph


class Generator:
    def __init__(self, idx=1):
        self.idx = idx
        self.bike_path = f'{ROOT_DIR}/sample_data/bike_data.txt'
        self.topology_path = f'{ROOT_DIR}/sample_data/topology.txt'
        self.bike_data = OrderedDict()

    def data_generator(self):
        """generate a list of random durations, s.t each vehicle can visit
        4 bike stations"""
        # bound deficit stations by 6, given our constraints
        num_avail_bikes = BRP.num_avail_bikes
        bike_data = {}
        random_num_bikes = []

        # generate a rand num of deficit stations along with their num of bikes
        num_deficit_stations = np.random.randint(low=min_deficit_stations,
                                                 high=7)
        num_deficit_stations_bikes = np.random.randint(
            low=min_deficit_bound, high=max_deficit_bound + 1,
            size=num_deficit_stations)

        while (num_avail_bikes - num_deficit_stations_bikes.sum()) / (
                num_bike_stations - num_deficit_stations) > 10:
            num_deficit_stations = np.random.randint(
                low=min_deficit_stations, high=7)
            num_deficit_stations_bikes = np.random.randint(
                low=min_deficit_bound, high=max_deficit_bound + 1,
                size=num_deficit_stations)
        num_avail_bikes -= num_deficit_stations_bikes.sum()

        # generate rand num of bikes for non-deficit bike stations
        while num_deficit_stations < num_bike_stations:
            n = np.random.randint(low=0, high=min(max_station_bikes + 1,
                                                  num_avail_bikes + 1))
            while (num_avail_bikes - n) >= 0 and (
                    num_avail_bikes - n) / (
                    num_bike_stations - num_deficit_stations - 1) > 10:
                n = np.random.randint(low=0,
                                      high=min(max_station_bikes + 1,
                                               num_avail_bikes + 1))
            num_avail_bikes -= n
            num_deficit_stations += 1
            random_num_bikes.append(n)

        # merge the rand num of bikes and randomly shuffle it
        random_num_bikes.extend(num_deficit_stations_bikes)
        np.random.shuffle(random_num_bikes)

        # randomly locations of the bike stations and intersections
        bike_station_indexes = np.concatenate((np.ones(num_bike_stations),
                                               np.zeros(
                                                   num_street_intersections)))
        np.random.shuffle(bike_station_indexes)

        # shuffle vertices indexes randomly
        intersection_count, bike_station_count = 1, 1
        vertices = ['at_depot']
        for val in bike_station_indexes:
            if int(val) == 1:
                vertices.append(f'b{bike_station_count}')
                bike_station_count += 1
            else:
                vertices.append(f'i{intersection_count}')
                intersection_count += 1
        bike_data['vertices'] = vertices
        bike_data['bike_data'] = list(zip([x for x in vertices if 'b' in x],
                                          [int(x) for x in random_num_bikes]))
        self.bike_data = bike_data
        self._generate_bike_data()

    def topology_generator(self):
        vertices = self.bike_data['vertices']
        self.bike_stations = [x for x in vertices if 'b' in x]
        restart = True

        while restart:
            count = 0
            edges = []
            # join two vertices at random until all edges have been filled
            while count < num_edges:
                # delta(20, 40) so far is a good fit..
                edge_weight = np.random.randint(low=lower_edge_weight,
                                                high=upper_edge_weight + 1)
                rand_pair = tuple(random.sample(vertices, 2))
                rand_pair = (rand_pair[0], rand_pair[1], edge_weight)
                if rand_pair not in edges and rand_pair[::-1] not in edges:
                    edges.append(rand_pair)
                    count += 1
            graph = Graph()
            graph.add_weighted(connections=edges)
            if graph.is_connected() and sorted(vertices) == sorted(
                    graph.graph.keys()):
                restart = False
        self.edges = edges
        self.graph = graph
        self._generate_topology_data()

    def _generate_bike_data(self):
        filename = f'{ROOT_DIR}/sample_data/bike_data_{self.idx}.txt'
        with open(filename, 'w') as f:
            f.write(f"{sum([el[-1] for el in self.bike_data['bike_data']])}\n")
            for station in self.bike_data['bike_data']:
                f.write(f'{station[0]} {station[1]}\n')

    def _generate_topology_data(self):
        filename = f'{ROOT_DIR}/sample_data/topology_{self.idx}.txt'
        with open(filename, 'w') as f:
            directed_graph = Graph(directed=True)
            directed_graph.add_weighted(connections=self.edges)
            f.write(f'{num_vertices} {num_edges}\n')
            f.write(f'{num_bike_stations}\n')
            f.write(f"{','.join(self.bike_stations).replace(',', ' ')}\n")
            f.write(f'{len(directed_graph.graph)}\n')
            for station in directed_graph.graph:
                destination_weight = []
                for destination in directed_graph.graph[station]:
                    destination_weight.append((destination,
                                               directed_graph.weights[
                                                   station, destination]))
                destination_weight = ','.join(
                    map(str, destination_weight)).replace(',', ' ')
                f.write(f'{station} {destination_weight}\n')

    def data_loader(self, type: str = 'bike_data'):
        count = 0
        data_path = self.bike_path if type == 'bike_data' else self.topology_path
        edges = []
        with open(data_path, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if type == 'bike_data':
                    if count > 0:
                        self.bike_data[f'station_{line[0]}_avail_bikes'] = line[
                            -1]
                    else:
                        self.bike_data['num_avail_bikes'] = int(line)
                elif type == 'topology':
                    if count < 4:
                        line = line.split(' ')
                        if count == 0:
                            self.bike_data['num_vertices'] = line[0]
                            self.bike_data['num_edges'] = line[-1]
                        elif count == 1:
                            self.bike_data['num_bike_stations'] = line[0]
                        elif count == 2:
                            self.bike_data['bike_stations'] = [el for el in
                                                               line]
                        elif count == 3:
                            pass
                    elif count >= 4:
                        # store into list containing [start_node, end_node, duration]
                        arr = line.split(' (')
                        edges.extend([[arr[0], arr[i].strip(')').split(' ')[0],
                                       arr[i].strip(')').split(' ')[-1]] for i
                                      in
                                      range(1, len(arr))])
                count += 1
            self.bike_data['edges'] = edges
