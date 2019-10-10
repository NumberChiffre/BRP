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

        for v in self.graph:
            dist[v] = float("inf")
            prev[v] = None
            Q.add(v)
        dist[source] = 0

        while Q:
            u = self.findMin(Q, dist)
            Q.remove(u)
            neighbor = self.getNeighbors(u)
            for i in neighbor:
                alt = dist[u] + self.getEdgeWeight(u, i)
                if alt < dist[i]:
                    dist[i] = alt
                    prev[i] = u
        return (dist, prev)

    def shortestPath(self, source, target):
        d, p = self.dijkstras(source)
        s = []
        u = target
        while p[u]:
            s = [u] + s
            u = p[u]
        s = [u] + s
        return [s, d[s[-1]]]

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
