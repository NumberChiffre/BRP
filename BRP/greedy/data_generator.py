from collections import defaultdict, OrderedDict
from typing import Dict, List
import numpy as np
import random

from BRP import ROOT_DIR
from BRP.greedy.graph import Graph


class Generator:
    def __init__(self):
        self.bike_path = f'{ROOT_DIR}/sample_data/bike_data.txt'
        self.topology_path = f'{ROOT_DIR}/sample_data/topology.txt'
        self.bike_data = OrderedDict()

        # params given for part I
        self.num_avail_bikes = 60
        self.num_bike_stations = 10
        self.min_deficit_stations = 3
        self.min_deficit_bound = 0
        self.max_deficit_bound = 4
        self.num_street_intersections = 20
        self.num_edges = 70
        self.num_vehicles = 100
        self.max_station_bikes = 10
        self.min_station_bikes = 5
        self.min_station_visits = 4
        self.vehicle_shift = 8 * 60  # in minutes

        # bikes + intersections + at_depot, where deposit is the 0th index
        self.num_vertices = self.num_bike_stations + self.num_street_intersections

    def data_generator(self):
        """generate a list of random durations, s.t each vehicle can visit 4 bike stations"""

        # bound deficit stations by 6, given our constraints
        bike_data = {}
        random_num_bikes = []

        # generate a rand num of deficit stations along with their num of bikes
        num_deficit_stations = np.random.randint(low=self.min_deficit_stations,
                                                 high=7)
        num_deficit_stations_bikes = np.random.randint(
            low=self.min_deficit_bound, high=self.max_deficit_bound + 1,
            size=num_deficit_stations)
        while (self.num_avail_bikes - num_deficit_stations_bikes.sum()) / (
                self.num_bike_stations - num_deficit_stations) > 10:
            num_deficit_stations = np.random.randint(
                low=self.min_deficit_stations, high=7)
            num_deficit_stations_bikes = np.random.randint(
                low=self.min_deficit_bound, high=self.max_deficit_bound + 1,
                size=num_deficit_stations)
        self.num_avail_bikes -= num_deficit_stations_bikes.sum()

        # generate rand num of bikes for non-deficit bike stations
        while num_deficit_stations < self.num_bike_stations:
            n = np.random.randint(low=0, high=min(self.max_station_bikes + 1,
                                                  self.num_avail_bikes + 1))
            while (self.num_avail_bikes - n) >= 0 and (
                    self.num_avail_bikes - n) / (
                    self.num_bike_stations - num_deficit_stations - 1) > 10:
                n = np.random.randint(low=0,
                                      high=min(self.max_station_bikes + 1,
                                               self.num_avail_bikes + 1))
            self.num_avail_bikes -= n
            num_deficit_stations += 1
            random_num_bikes.append(n)

        # merge the rand num of bikes and randomly shuffle it
        random_num_bikes.extend(num_deficit_stations_bikes)
        np.random.shuffle(random_num_bikes)

        # randomly locations of the bike stations and intersections
        bike_station_indexes = np.concatenate((np.ones(self.num_bike_stations),
                                               np.zeros(
                                                   self.num_street_intersections)))
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

    def topology_generator(self, idx: int = 1):
        vertices = self.bike_data['vertices']
        bike_vertices = [idx for idx, v in enumerate(vertices) if 'b' in v]
        bike_stations = [x for x in vertices if 'b' in x]
        restart = True
        while restart:
            count = 0
            edges = []

            # join two vertices at random until all edges have been filled
            while count < self.num_edges:

                # delta(20, 40) so far is a good fit..
                edge_weight = np.random.randint(low=20, high=41)
                rand_pair = tuple(random.sample(vertices, 2))
                rand_pair = (rand_pair[0], rand_pair[1], edge_weight)
                if rand_pair not in edges and rand_pair[::-1] not in edges:
                    edges.append(rand_pair)
                    count += 1

                    # # noob hack to find all paths from source to source..
                    # if rand_pair[0] == 'at_depot':
                    #     edges.append(('at_depot_p', rand_pair[1], edge_weight))
                    # elif rand_pair[1] == 'at_depot':
                    #     edges.append((rand_pair[0], 'at_depot_p', edge_weight))
            graph = Graph()
            graph.add_weighted(connections=edges)
            if graph.is_connected():
                restart = False

        # a = graph.shortestPath('at_depot', 'at_depot')
        # write to file using the same format as guidelines
        filename = f'{ROOT_DIR}/sample_data/topology_{idx}.txt'
        with open(filename, 'w') as f:
            directed_graph = Graph(directed=True)
            directed_graph.add_weighted(connections=edges)
            f.write(f'{self.num_vertices} {self.num_edges}\n')
            f.write(f'{self.num_bike_stations}\n')
            f.write(f"{','.join(bike_stations).replace(',', ' ')}\n")
            f.write(f'{len(directed_graph.graph)}\n')
            for station in directed_graph.graph:
                destination_weight = []
                for destination in directed_graph.graph[station]:
                    destination_weight.append((destination, directed_graph.weights[station, destination]))
                destination_weight = ','.join(map(str, destination_weight)).replace(',', ' ')
                f.write(f'{station} {destination_weight}\n')

        # graph = Graph()
        # bike_stations = [x for x in vertices if 'b' in x]
        # for edge in edges:
        #     graph.add_edge(*edge)
        # stp = {}
        # for bike_station in bike_stations:
        #     stp[bike_station] = dijsktra(graph, 'at_depot', bike_station)
        # edges_dict = defaultdict(set)
        # for edge in edges:
        #     edges_dict[edge[0]].add(edge[1])
        #     edges_dict[edge[1]].add(edge[0])

        # edges_dict = {"a": ["d"],
        #               "b": ["c"],
        #               "c": ["b", "c", "d", "e"],
        #               "d": ["a", "c"],
        #               "e": ["c"],
        #               "f": []
        #             }
        # graph = Graph(graph_dict=edges_dict)
        # print(graph.find_all_paths('at_depot', 'b3'))
        stp = {}
        for bike_station in bike_stations:
            stp[bike_station] = graph.shortestPath('at_depot', bike_station)
        graph
        # need to check generate random floats s.t each vehicle can travel 4 bike stations in 8 hours
        #

    def _generate_bike_data(self, idx: int = 1):
        filename = f'{ROOT_DIR}/sample_data/bike_data_{idx}.txt'
        with open(filename, 'w') as f:
            f.write(f"{sum([el[-1] for el in self.bike_data['bike_data']])}\n")
            for station in self.bike_data['bike_data']:
                f.write(f'{station[0]} {station[1]}\n')

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
        print(self.bike_data)


if __name__ == '__main__':
    obj = Generator()
    data = obj.data_loader()
    obj.data_generator()
    obj.topology_generator()
    print(data)
    obj.data_loader(type='topology')
