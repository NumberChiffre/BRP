from BRP import *
from BRP.greedy.graph import Graph
from BRP.greedy.greedy import Greedy
import copy
from typing import Dict


class GreedyTraversalThird(Greedy):
    def __init__(self, graph: Graph, bike_data: Dict):
        super().__init__(graph, bike_data)

    # generate clusters of path from source and back to source for all vehicles
    def _generate_clusters(self, source: str, main_source: str):
        assert len(self.above_thresh_b) + len(self.below_thresh_b) + len(
            self.between_thresh_b) == num_bike_stations_2
        idx = 1
        clusters = {}
        total_excess, total_deficit = 0, 0

        # estimate number of vehicles and cluster sets of bike station paths
        while sum([1 for v in self.below_thresh_b.values() if
                   not v[-1]]) > 0 or sum(
            [1 for v in self.above_thresh_b.values() if not v[-1]]) > 0:
            cluster_path = []
            capacity = 0
            time = 0
            num_bike_stations_satisfied = 0

            # fill vehicle till full capacity
            while capacity < vehicle_cap:
                # avoid excess bike stations that got rid of their excess
                avoid = [k[1] for k, v in self.above_thresh_b.items() if v[-1]]

                if source == main_source:
                    for k, val in self.above_thresh_b.items():
                        if val[-2] > num_excess_bikes and not val[-1]:
                            v = self.above_thresh_b[k]
                            break
                else:
                    if len(avoid) != len(self.above_thresh_b):
                        neighbors = dict([(k, v) for k, v in
                                          self.min_depot_bike_stations.items()
                                          if v[-2] > num_excess_bikes and k[
                                              0] == source and k[
                                              1] not in avoid])
                    else:

                        # corner case, when capacity not full but all excess
                        # stations have been satisfied
                        if self.num_above_thresh > self.num_below_thresh:
                            break

                        avoid_between = [k[1] for k, v in
                                         self.between_thresh_b.items() if v[-1]]
                        neighbors = dict([(k, v) for k, v in
                                          self.min_depot_bike_stations.items()
                                          if v[-2] > num_deficit_bikes and v[
                                              -2] <= num_excess_bikes and k[
                                              0] == source and k[
                                              1] not in avoid_between])

                    # go to the closest excess bike station
                    for k, val in neighbors.items():
                        if val[-2] > num_excess_bikes and not val[-1]:
                            v = neighbors[k]
                            break

                # still have excess bikes and have not been totally consumed
                if v[-2] > num_excess_bikes and not v[-1]:
                    excess_bikes = min(vehicle_cap - capacity,
                                       v[-2] - num_excess_bikes)

                    # if excess bikes have been consumed, avoid going back again
                    if v[-2] - excess_bikes <= num_excess_bikes:
                        self.above_thresh_b[(main_source, v[0][-1])][
                            -1] = True
                        num_bike_stations_satisfied += 1

                    # adjust vehicle capacity and time
                    capacity += excess_bikes
                    source = v[0][-1]
                    time += v[1]

                    # add to cluster
                    cluster_path.append(v)
                    total_excess += excess_bikes

                elif v[-2] > num_deficit_bikes and not v[-1] and len(
                        avoid) == len(self.above_thresh_b):
                    excess_bikes = min(vehicle_cap - capacity,
                                       v[-2] - num_deficit_bikes)

                    # if excess bikes have been consumed, avoid going back again
                    if v[-2] - excess_bikes == num_deficit_bikes:
                        self.between_thresh_b[(main_source, v[0][-1])][
                            -1] = True

                    # adjust vehicle capacity and time
                    capacity += excess_bikes
                    source = v[0][-1]
                    time += v[1]

                    # add to cluster
                    cluster_path.append(v)
                    total_excess += excess_bikes

            # when capacity has remaining but all deficits have been satisfied
            # must go to satisfied stations
            while capacity > 0:
                avoid = [k[1] for k, v in self.below_thresh_b.items() if v[-1]]
                if len(avoid) != len(self.below_thresh_b):
                    neighbors = dict(
                        [(k, v) for k, v in self.min_depot_bike_stations.items()
                         if v[-2] < num_deficit_bikes and k[0] == source and k[
                             1] not in avoid])
                else:
                    avoid_between = [k[1] for k, v in
                                     self.between_thresh_b.items() if v[-1]]
                    neighbors = dict(
                        [(k, v) for k, v in self.min_depot_bike_stations.items()
                         if v[-2] >= num_deficit_bikes and v[
                             -2] < num_excess_bikes and k[0] == source and k[
                             1] not in avoid_between])

                for k, val in neighbors.items():
                    if k[1] != main_source:
                        v = neighbors[k]
                        break

                if v[-2] < num_deficit_bikes and source != v[0][-1]:
                    # check if there is enough time to return
                    v_to_main = self.min_depot_bike_stations[
                        (v[0][-1], main_source)]
                    if v[1] + v_to_main[1] <= vehicle_shift - time:
                        deficit_bikes = min(num_deficit_bikes - v[-2],
                                            capacity)
                        if v[-2] + deficit_bikes >= num_deficit_bikes:
                            self.below_thresh_b[(main_source, v[0][-1])][
                                -1] = True
                            num_bike_stations_satisfied += 1

                        cluster_path.append(v)
                        capacity -= deficit_bikes
                        time += v[1]
                        source = v[0][-1]
                        total_deficit += deficit_bikes
                    else:
                        break

                elif v[-2] < num_excess_bikes and not v[-1] and len(
                        avoid) == len(self.below_thresh_b):
                    # check if there is enough time to return
                    v_to_main = self.min_depot_bike_stations[
                        (v[0][-1], main_source)]

                    if v[1] + v_to_main[1] <= vehicle_shift - time:
                        deficit_bikes = min(num_excess_bikes - v[-2],
                                            capacity)
                        if v[-2] + deficit_bikes == num_excess_bikes:
                            self.between_thresh_b[(main_source, v[0][-1])][
                                -1] = True
                        cluster_path.append(v)
                        capacity -= deficit_bikes
                        time += v[1]
                        source = v[0][-1]
                        total_deficit += deficit_bikes
                    else:
                        break

            if source != main_source:
                # this means we have time to go from last bike station to depot
                cluster_path.append(v_to_main)
                time += v_to_main[1]
                source = main_source

            # save into clusters
            clusters[f'c{idx}'] = cluster_path + [num_bike_stations_satisfied]
            idx += 1
        assert total_deficit == total_excess
        return clusters

    # generate shortest path for every pair of vertices
    # to have shortest path between points -> check for transitivity
    def greedy_traversal(self):
        main_source, source = 'at_depot', 'at_depot'
        dist_prev, stp = {}, {}

        # distance from each bike station to each other with depot
        # O(B*(|E|+|V|)*log(|V|)
        bike_stations = [x for x in self.bike_data['vertices'] if 'b' in x]
        for source in list(bike_stations + [main_source]):
            (dist, prev) = self.graph.dijkstras(source)
            dist_prev[source] = (dist, prev)
            for b in list(bike_stations + [main_source]):
                if source != b:
                    stp[(source, b)] = self.graph.getShortestPath(
                        dist_prev[source][0], dist_prev[source][1], b)

        # Sort based on lowest time for each pair
        # O((B+depot)^2*log(B+depot))
        min_depot_bike_stations = dict(
            sorted(stp.items(), key=lambda kv: kv[1][1]))
        for k, v in min_depot_bike_stations.items():
            if k[1] != main_source:
                min_depot_bike_stations[k] = v + [
                    self.bike_data['bike_data'][int(k[1].replace('b', '')) - 1][
                        1]] + [False]
            else:
                min_depot_bike_stations[k] = v + [0] + [False]
        self.min_depot_bike_stations = min_depot_bike_stations

        # choose the min or choose randomly
        above_thresh_b = dict(
            [(k, v) for k, v in min_depot_bike_stations.items() if
             v[-2] > num_excess_bikes and k[0] == 'at_depot'])
        below_thresh_b = dict(
            [(k, v) for k, v in min_depot_bike_stations.items() if
             v[-2] < num_deficit_bikes and k[0] == 'at_depot'])
        between_thresh_b = dict(
            [(k, v) for k, v in min_depot_bike_stations.items() if
             v[-2] >= num_deficit_bikes and v[-2] <= num_excess_bikes and k[
                 0] == 'at_depot'])

        # static bike stations, avoid confusion
        self.above_thresh_b = copy.deepcopy(above_thresh_b)
        self.below_thresh_b = copy.deepcopy(below_thresh_b)
        self.between_thresh_b = copy.deepcopy(between_thresh_b)

        # number bikes in each category
        self.num_above_thresh = sum(
            [v[-2] - num_excess_bikes for v in self.above_thresh_b.values()])
        self.num_below_thresh = sum(
            [num_deficit_bikes - v[-2] for v in self.below_thresh_b.values()])

        # get clusters which maximize the number of bikes with satisfied demand
        clusters = self._generate_clusters(source, main_source)

        # travel through each cluster
        vehicles = dict(zip([f'v{i}' for i in range(1, len(clusters) + 1)],
                            [[0, 0] for _ in range(len(clusters))]))
        idx = 1
        for k, v in clusters.items():
            vehicles[f'v{idx}'] = [len(v) - 1, v[-1]]
            idx += 1
        return vehicles
