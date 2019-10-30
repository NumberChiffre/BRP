from BRP import *
import BRP


class GreedyTraversalSecond:
    def __init__(self, graph, bike_data):
        self.graph = graph
        self.bike_data = bike_data

    # generate shortest path for every pair of vertices
    # to have shortest path between points -> check for transitivity
    def greedy_traversal(self):
        vehicles = dict(zip([f'v{i}' for i in range(1, num_vehicles + 1)],
                            [[0, 0] for _ in range(num_vehicles)]))
        idx = 1
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
                    self.bike_data['bike_data'][int(k[1].replace('b', '')) - 1][1]]
            else:
                min_depot_bike_stations[k] = v + [0]

        # choose the min or choose randomly
        above_thresh_b = dict(
            [(k, v) for k, v in min_depot_bike_stations.items() if
             v[-1] > min_station_bikes and k[0] == 'at_depot'])
        below_thresh_b = dict(
            [(k, v) for k, v in min_depot_bike_stations.items() if
             v[-1] <= min_station_bikes and k[0] == 'at_depot'])

        # keep going till all deficit stations get min_station_bikes
        while sum([1 for v in below_thresh_b.values() if
                   v[-1] < min_station_bikes]) > 0:
            num_stations_visited = 0

            # in case there were remaining bikes from last vehicle, take them
            if idx > 1:
                vehicles[f'v{idx}'][1] = vehicles[f'v{idx - 1}'][1]

            # fill bikes to satisfy remaining deficit stations
            max_station_bikes = min(BRP.max_station_bikes, sum(
                [min_station_bikes - v[-1] for v in below_thresh_b.values()]))

            # for each vehicle, fill bikes until max cap
            # start from the closest to depot, then closest to bike station
            while vehicles[f'v{idx}'][1] < max_station_bikes:
            # for v in above_thresh_b.values():
                if v[-1] > min_station_bikes and vehicles[f'v{idx}'][
                    1] < max_station_bikes:
                    # find the shortest node from source to the remaining stations
                    source_to_v = stp[(source, v[0][-1])] + \
                                  [self.bike_data['bike_data'][
                                       int(v[0][-1].replace('b', '')) - 1][1]]
                    vehicles[f'v{idx}'].append(source_to_v)

                    # fill vehicle with bikes to satisfy remaining deficit stations
                    bikes = min(v[-1] - min_station_bikes,
                                max_station_bikes - vehicles[f'v{idx}'][1])
                    vehicles[f'v{idx}'][1] += bikes
                    above_thresh_b[(main_source, v[0][-1])][-1] -= bikes

                    # path weights
                    vehicles[f'v{idx}'][0] += source_to_v[1]
                    source = v[0][-1]
                    num_stations_visited += 1

                # vehicle has reached max capacity, moving on to other deficit stations
                if vehicles[f'v{idx}'][1] == max_station_bikes:
                    break

            # once vehicle reached full capacity, go fill bikes
            num_stations_satisfied = 0
            for v in below_thresh_b.values():
                if source != v[0][-1] and v[-1] < min_station_bikes and \
                        vehicles[f'v{idx}'][1] > 0:
                    source_to_v = stp[(source, v[0][-1])]
                    v_to_main = stp[(v[0][-1], main_source)]

                    # get shortest path from u->v, v->depot
                    # choose u->depot if not enough time
                    if source_to_v[1] + v_to_main[1] <= vehicle_shift - \
                            vehicles[f'v{idx}'][0]:
                        source_to_v += [self.bike_data['bike_data'][
                                            int(v[0][-1].replace('b', '')) - 1][
                                            1]]
                        vehicles[f'v{idx}'].append(source_to_v)

                        # fill deficit stations with bikes
                        bikes = min(min_station_bikes - v[-1],
                                    vehicles[f'v{idx}'][1])
                        vehicles[f'v{idx}'][1] -= bikes
                        below_thresh_b[(main_source, v[0][-1])][-1] += bikes
                        if below_thresh_b[(main_source, v[0][-1])][
                            -1] >= min_station_bikes:
                            num_stations_satisfied += 1

                        # path weights
                        vehicles[f'v{idx}'][0] += source_to_v[1]
                        source = v[0][-1]
                        num_stations_visited += 1
                    else:
                        break

            # done with deficit stations and have enough time to go back
            if source != main_source:
                source_to_v = self.graph.shortestPath(source,
                                                      main_source) + [0]
                vehicles[f'v{idx}'][0] += source_to_v[1]
                vehicles[f'v{idx}'].append(source_to_v)
                vehicles[f'v{idx}'].append(num_stations_visited)
                vehicles[f'v{idx}'].append(num_stations_satisfied)
                source = main_source
            idx += 1
        return dict(
            [(k, v) for k, v in vehicles.items() if v[0] != 0])
