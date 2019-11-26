from collections import defaultdict


class Graph:
    def __init__(self, directed=False):
        self.graph = defaultdict(set)
        self.weights = defaultdict(set)
        self.directed = directed

    def remove(self, pair):
        self.graph[pair[0]].remove(pair[1])
        del self.weights[pair]

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
        dist, prev = dict(), dict()
        Q = set()

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

    def getShortestPath(self, dist, prev, target):
        d, p = dist, prev
        s = []
        u = target
        while p[u]:
            s = [u] + s
            u = p[u]
        s = [u] + s
        return [s, d[s[-1]]]

    def shortestPath(self, source, target):
        d, p = self.dijkstras(source)
        s = []
        u = target
        while p[u]:
            s = [u] + s
            u = p[u]
        s = [u] + s
        return [s, d[s[-1]]]

    def is_connected(self, visited = None, vertex=None):
        if visited is None:
            visited = set()
        graph_d = self.graph
        vertices = list(graph_d.keys())
        if not vertex:
            vertex = vertices[0]
        visited.add(vertex)
        if len(visited) != len(vertices):
            for v in graph_d[vertex]:
                if v not in visited:
                    if self.is_connected(visited, v):
                        return True
        else:
            return True
        return False
