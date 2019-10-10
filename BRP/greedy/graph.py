from collections import defaultdict


class Graph:
    def __init__(self, directed=False):
        self.graph = defaultdict(set)
        self.weights = defaultdict(set)
        self.directed = directed

    def add(self, node1, node2):
        """ Add connection between node1 and node2 vice-versa """
        self.graph[node1].add(node2)
        if not self.directed:
            self.graph[node2].add(node1)

    def add_weighted(self, connections):
        """ Add connections for a weighted graph """
        for x in connections:
            self.add_edges((x[0], x[1]), x[-1])
        self.graph = dict(sorted(self.graph.items(), key=lambda x: x[0]))

    def add_edges(self, pair, edge):
        """ Add connection for node pairs with weight of edge """
        self.add(pair[0], pair[1])
        self.weights[pair] = edge
        if not self.directed:
            self.weights[(pair[1], pair[0])] = edge

    def add_connections(self, connections):
        """ Add connections (list of tuple pairs) to graph """
        for x in connections:
            self.add(x[0], (x[-1], 1))

    def findMin(self, array, weights):
        arbitrary = array.pop()
        minVertex = arbitrary
        minWeight = weights[minVertex]
        for i in array:
            if weights[i] < minWeight:
                minVertex = i
        array.add(arbitrary)
        return minVertex

    def getNeighbors(self, v):
        return self.graph[v]

    def getEdgeWeight(self, v, u):
        return self.weights[(v, u)]

    def dijkstras(self, source):
        """ Shortest paths algorithm using a set """
        Q = set()
        dist = dict()
        prev = dict()
        paths = dict()

        for v in self.graph:
            dist[v] = float("inf")
            prev[v] = None
            Q.add(v)
        dist[source] = 0

        while Q:
            u = self.findMin(Q, dist)
            Q.remove(u)
            neighbor = self.getNeighbors(u)
            path = []
            for i in neighbor:
                alt = dist[u] + self.getEdgeWeight(u, i)
                if alt < dist[i]:
                    dist[i] = alt
                    prev[i] = u
                    path.append(i)
            paths[u] = path
        return (dist, prev)

    def shortestPath(self, source, target):
        d, p = self.dijkstras(source)
        s = []
        u = target
        while p[u]:
            s = [u] + s
            u = p[u]
        s = [u] + s
        return s

    """A recursive function to print all paths from 'u' to 'd'.
    visited[] keeps track of vertices in current path.
    path[] stores actual vertices and path_index is current
    index in path[]"""
    def printAllPathsUtil(self, u, d, visited, path, edge_weight=0):

        # Mark the current node as visited and store in path
        visited[u] = True
        path.append((u, edge_weight))

        # If current vertex is same as destination, then print
        # current path[]
        if u == d:
            if sum([1 for x in path if 'b' in x[0]]) >= 4 and sum([x[1] for x in path]) <= 8*60/2:
                print(path, sum([x[1] for x in path]))
                self.paths.append(path)
        else:
            # If current vertex is not destination
            # Recur for all the vertices adjacent to this vertex
            for i in self.graph[u]:
                if not visited[i]:
                    edge_weight = self.weights[(u, i)]
                    self.printAllPathsUtil(i, d, visited, path, edge_weight)

        # Remove current vertex from path[] and mark it as unvisited
        path.pop()
        visited[u] = False

    # Prints all paths from 's' to 'd'
    def printAllPaths(self, s, d):

        # Mark all the vertices as not visited
        visited = dict(zip(self.graph.keys(), [False] * len(self.graph)))

        # Create an array to store paths
        self.paths = []
        self.idx = 0
        path = []

        # Call the recursive helper function to print all paths
        self.printAllPathsUtil(s, d, visited, path)
        return self.paths


    def paths(self, v):
        """Generate the maximal cycle-free paths in graph starting at v.
        graph must be a mapping from vertices to collections of
        neighbouring vertices.

        >>> g = {1: [2, 3], 2: [3, 4], 3: [1], 4: []}
        >>> sorted(paths(g, 1))
        [[1, 2, 3], [1, 2, 4], [1, 3]]
        >>> sorted(paths(g, 3))
        [[3, 1, 2, 4]]

        """
        path = [v]  # path traversed so far
        seen = {v}  # set of vertices in path

        def search():
            dead_end = True
            for neighbour in self.graph[path[-1]]:
                if neighbour not in seen:
                    dead_end = False
                    seen.add(neighbour)
                    path.append(neighbour)
                    yield from search()
                    path.pop()
                    seen.remove(neighbour)
            if dead_end:
                yield list(path)

        yield from search()

    def is_connected(self,
                     vertices_encountered = None,
                     start_vertex=None):
        """ determines if the graph is connected """
        if vertices_encountered is None:
            vertices_encountered = set()
        gdict = self.graph
        vertices = list(gdict.keys()) # "list" necessary in Python 3
        if not start_vertex:
            # chosse a vertex from graph as a starting point
            start_vertex = vertices[0]
        vertices_encountered.add(start_vertex)
        if len(vertices_encountered) != len(vertices):
            for vertex in gdict[start_vertex]:
                if vertex not in vertices_encountered:
                    if self.is_connected(vertices_encountered, vertex):
                        return True
        else:
            return True
        return False
