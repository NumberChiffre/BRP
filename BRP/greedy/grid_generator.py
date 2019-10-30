import numpy as np
import random
import copy

import BRP
from BRP import *
from BRP.greedy.graph import Graph
from BRP.greedy.generator import Generator


class GridGenerator(Generator):
    def __init__(self, idx):
        super().__init__(idx)

    def data_generator(self):
        random_num_bikes = []
        bike_stations = [f'b{i}' for i in range(num_bike_stations_2)]
        self.bike_stations = bike_stations

        # get 45 deficit bike stations
        num_deficit_stations = int(num_bike_stations_2 * deficit_prop)

        # use proportion of avail bikes/bike stations to determine
        # the avail bikes for part II
        num_avail_bikes = BRP.num_avail_bikes
        num_avail_bikes = num_bike_stations_2 * (
                num_avail_bikes // num_bike_stations)

        # with 45 deficit stations, they have about [0, 45*5) bikes
        num_deficit_stations_bikes = np.random.randint(
            low=min_deficit_bound, high=max_deficit_bound + 1,
            size=num_deficit_stations)

        while (num_avail_bikes - num_deficit_stations_bikes.sum()) / (
                num_bike_stations_2 - num_deficit_stations) > 10:
            num_deficit_stations_bikes = np.random.randint(
                low=min_deficit_bound, high=max_deficit_bound + 1,
                size=num_deficit_stations)
        num_avail_bikes -= num_deficit_stations_bikes.sum()

        # generate rand num of bikes for non-deficit bike stations
        while num_deficit_stations < num_bike_stations_2:
            n = np.random.randint(low=0, high=min(max_station_bikes + 1,
                                                  num_avail_bikes + 1))
            while (num_avail_bikes - n) >= 0 and (
                    num_avail_bikes - n) / (
                    num_bike_stations_2 - num_deficit_stations - 1) > max_station_bikes:
                n = np.random.randint(low=min_station_bikes,
                                      high=min(max_station_bikes + 1,
                                               num_avail_bikes + 1))
            num_avail_bikes -= n
            num_deficit_stations += 1
            random_num_bikes.append(n)

        # merge the rand num of bikes and randomly shuffle it
        random_num_bikes.extend(num_deficit_stations_bikes)
        np.random.shuffle(random_num_bikes)
        self.bike_data['bike_data'] = list(zip((bike_stations),
                                           [int(x) for x in random_num_bikes]))
        self._generate_bike_data()

    def topology_generator(self):
        edges = []
        vertices = []

        # O(11*13)
        for i in range(num_intersections_i):
            row_vertices = []
            for j in range(num_intersections_j):
                row_vertices.append(f'i{i * num_intersections_j + j}')
            vertices.append(row_vertices)

        # O(11*13*2)
        for i in range(num_intersections_i):
            for j in range(num_intersections_j):
                # delta(20, 40) so far is a good fit..
                edge_weight = np.random.randint(low=lower_edge_weight,
                                                high=upper_edge_weight + 1)
                if j < num_intersections_j - 1:
                    edges.append(
                        (vertices[i][j], vertices[i][j + 1], edge_weight))
                    edges.append(
                        (vertices[i][j + 1], vertices[i][j], edge_weight))
                if i < num_intersections_i - 1:
                    edges.append(
                        (vertices[i][j], vertices[i + 1][j], edge_weight))
                    edges.append(
                        (vertices[i + 1][j], vertices[i][j], edge_weight))

        # dealing with arc removal while ensuring graph is connected
        # can also result in removal of all arcs between (u, v) pair
        graph = Graph()
        graph.add_weighted(connections=edges)
        temp_graph = copy.deepcopy(graph)
        removed = []
        remove_prop = int(len(edges) * single_arc_prop)
        count = 0
        while count < remove_prop:
            connected = False
            while not connected:
                edge = random.sample(edges, 1)[0]
                edge_no_w = (edge[0], edge[1])
                tmp = copy.deepcopy(temp_graph)
                temp_graph.remove(edge_no_w)
                if temp_graph.is_connected():
                    graph.remove(edge_no_w)
                    edges.remove(edge)
                    removed.append(edge)
                    connected = True
                    count += 1
                else:
                    temp_graph = copy.deepcopy(tmp)
                    connected = False

        # generate random bike station between intersections
        # half the original intersection weight for the bike edges
        bike_edges = []
        removed = []
        for i in range(num_bike_stations_2):
            inter = random.sample(edges, 1)[0]
            edge_weight = inter[-1] / 2
            bike_v = f'b{i}'

            # add/remove single arcs u->v to u->b, b->v
            bike_edges.append((inter[0], bike_v, edge_weight))
            bike_edges.append((bike_v, inter[1], edge_weight))
            edges.remove(tuple(inter))
            removed.append(tuple(inter))

            # add/remove the double arcs v->b, b->u
            if (inter[1], inter[0], inter[-1]) in edges:
                bike_edges.append((bike_v, inter[0], edge_weight))
                bike_edges.append((inter[1], bike_v, edge_weight))
                removed.append((inter[1], inter[0], inter[-1]))
                edges.remove((inter[1], inter[0], inter[-1]))

        # combine intersection edges with bike edges
        edges.extend(bike_edges)

        # finally, add the depot to a random vertex
        source = 'at_depot'
        vertices.append(source)
        edge_weight = np.random.randint(low=lower_edge_weight,
                                        high=upper_edge_weight + 1)
        edges.append((source, random.sample(edges, 1)[0][0], edge_weight))
        edges.append((random.sample(edges, 1)[0][0], source, edge_weight))
        vertices = [x[0] for x in edges]
        vertices.extend([x[1] for x in edges])
        vertices = list(set(vertices))
        self.bike_data['edges'] = edges
        self.bike_data['vertices'] = vertices
        self.edges = edges
        self.vertices = vertices
        self.graph = Graph()
        self.graph.add_weighted(connections=edges)
        self._generate_topology_data()

    def _generate_bike_data(self):
        filename = f'{ROOT_DIR}/sample_data/bike_data_partII_{self.idx}.txt'
        with open(filename, 'w') as f:
            f.write(f"{sum([el[-1] for el in self.bike_data['bike_data']])}\n")
            for station in self.bike_data['bike_data']:
                f.write(f'{station[0]} {station[1]}\n')

    def _generate_topology_data(self):
        filename = f'{ROOT_DIR}/sample_data/topology_partII_{self.idx}.txt'
        with open(filename, 'w') as f:
            directed_graph = Graph(directed=True)
            directed_graph.add_weighted(connections=self.edges)
            f.write(f"{len(self.vertices)} {len(self.edges)}\n")
            f.write(f'{num_bike_stations_2}\n')
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
