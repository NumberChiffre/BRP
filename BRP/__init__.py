import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

num_test_iterations = 10
lower_edge_weight, upper_edge_weight = 30, 40

# params given for part I
num_bike_stations = 10
num_avail_bikes = 60
min_deficit_stations = 3
min_deficit_bound = 0
max_deficit_bound = 4
num_street_intersections = 20
num_edges = 70
num_vehicles = 100
max_station_bikes = 10
min_station_bikes = 5
min_station_visits = 4
vehicle_shift = 8 * 60  # in minutes

# bikes + intersections + at_depot, where deposit is the 0th index
num_vertices = num_bike_stations + num_street_intersections