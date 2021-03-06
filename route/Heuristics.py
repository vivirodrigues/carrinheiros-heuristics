from route import Graph
import networkx as nx
import osmnx as ox
from collections import deque
from Constants import *
from route import Graph_Collect
import random
import more_itertools


def bellman_ford(G, initial_node, target_node, weight):
    weight = Graph._weight(G, weight)
    distance, route = nx.single_source_bellman_ford(G, initial_node, target_node, weight)
    return distance, route


def bidirectional_dijkstra(G, initial_node, target_node, weight):
    weight = Graph._weight(G, weight)
    distance, route = nx.bidirectional_dijkstra(G, initial_node, target_node, weight)
    return distance, route


def _shortest_path_faster(G, source, weight):
    """
    This function returns the single-source shortest path in
    weighted directed graph based on Shortest Path Faster
    Algorithm (SPFA). It is an improvement of the Bellman–
    Ford algorithm.

    The pseudocode of the SPFA:
    https://en.wikipedia.org/wiki/Shortest_Path_Faster_Algorithm

    :param G:           NetworkX graph.
                        input graph

    :param source:      Float
                        Id of the start node

    :param target:      Float
                        Id of the goal node

    :param weight:      Function

    :return:            List
                        List with all nodes of the
                        shortest path
    """

    weight = Graph._weight(G, weight)
    last_edge = {source: (None, None)}
    pred_edge = {source: None}
    source = [source]
    q = deque(source)
    G_adjacents = G.succ if G.is_directed() else G.adj
    n_G = len(G_adjacents)

    count = {}
    dist = {}
    parent = {}

    inf = float("inf")

    # Initialization
    for i in G.nodes:
        dist.update([(i, inf)])
        parent.update([(i, None)])

    dist.update([(source[0], 0)])

    while q:
        u = q.popleft()

        # for each edge between the node u and their adjacent nodes
        for v, e in G_adjacents[u].items():

            # Relaxing
            new_dist_v = dist.get(u) + weight(u, v, e)

            if new_dist_v < dist.get(v):

                if v in last_edge[u]:
                    print("Error: Negative cost cycle.")
                    return False

                if v in pred_edge and pred_edge[v] == u:
                    last_edge[v] = last_edge[u]
                else:
                    last_edge[v] = (u, v)

                dist.update([(v, new_dist_v)])
                parent.update([(v, u)])

                if v not in q:

                    q.append(v)
                    count_v = count.get(v, 0) + 1
                    if count_v == n_G:
                        print("Error: Negative cost cycle")
                        return False
                    count[v] = count_v
                    pred_edge[v] = u

    return dist, parent


def verifying_nodes(path, nodes):
    for i in nodes:
        if i not in list(path):
            return True
    return False


def nearest_neighbor(G, H, source, target, impedance, heuristic):
    """

    :param G:           NetworkX graph.
                        input graph

    :param source:      Float
                        Id of the start node

    :param target:      Float
                        Id of the goal node

    :param weight:      Function

    :return:            List
                        List with all nodes of the
                        shortest path
    """
    if source not in H:
        print("Error")
        return False

    open = [source]
    closed = []
    current_vehicle_mass = VEHICLE_MASS
    nodes_graph = list(H.nodes)
    nodes_graph.remove(target)
    route = []
    route1 = []
    cost_total = 0
    edges_update_mass = []

    while len(open) > 0:
        dist = {}
        node = open.pop(0)
        closed.append(node)
        missing = verifying_nodes(closed, nodes_graph)

        # if current node is the target (objective) and
        # there is not nodes missing to be visited
        if node == target and missing is False:
            if impedance == 'weight':
                G = Graph.update_weight(G, VEHICLE_MASS)

            fig, ax = ox.plot_graph_route(G, route1[-1], route_linewidth=6, node_size=0, bgcolor='w')
            return cost_total, route, edges_update_mass
        else:

            # checks nodes that have not yet been added in closed
            possibilities = set(H.adj[node]) - set(closed)

            for u in possibilities:
                # checks the edge weight according to the vehicle's mass +
                # mass increase at the current vertex
                edge_cost, path = Graph_Collect.cost_path(G, node, u, current_vehicle_mass, impedance, heuristic)
                dist.update([(u, [edge_cost, path])])

            # sorting the dict according to edge weights
            dist = dict(sorted(dist.items(), key=lambda item: item[1][0]))

            # if starting and arrival point is the same node
            if len(dist) < 1 and source == target:
                new_node = target

            else:
                new_node = list(dist.keys())[0]

                # if there are more than one not visited node
                # and the nearest node is the arrival point
                if len(dist) > 1 and new_node == target:
                    new_node = list(dist.keys())[1]
                    route.extend(list(dist.values())[1][1][:-1])
                    route1.append(list(dist.values())[1][1][:-1])
                    cost_total += float(list(dist.values())[1][0])
                    edges_update_mass.append(list(dist.values())[0][1][:2])
                elif new_node == target:
                    route.extend(list(dist.values())[0][1])
                    route1.append(list(dist.values())[0][1])
                    cost_total += float(list(dist.values())[0][0])
                    edges_update_mass.append(list(dist.values())[0][1][:2])
                else:
                    route.extend(list(dist.values())[0][1][:-1])
                    route1.append(list(dist.values())[0][1][:-1])
                    cost_total += float(list(dist.values())[0][0])
                    edges_update_mass.append(list(dist.values())[0][1][:2])

            open.append(new_node)
            current_vehicle_mass += H.nodes[new_node]['mass']


def _path(source, target, parent, path):
    """
    This function finds the path from source to the target
    according to the parent dictionary. It must be used for
    shortest_path_faster function.

    :param source:      Float
                        Id of the start node

    :param target:      Float
                        Id of the goal node

    :param parent:      Dictionary
                        The value of each key is the parent
                        node (predecessor node).

    :param path:        list
                        The list contains the id of the nodes
                        of the path from source to the target.

    :return:            list
                        The list contains the id of the nodes
                        of the path from source to the target.
    """

    if len(path) == 0:
        path.append(target)

    if target == source:
        pass

    elif parent.get(target) is None:
        print("Target cannot be reached")
        return False
    else:
        path.append(parent.get(target))
        _path(source, parent.get(target), parent, path)

    return path[::-1]


def updates_vehicle_mass(path, mass):
    """

    :param path:    list
    :param mass:    dict

    :return:
    """
    vehicle_mass = VEHICLE_MASS
    for i in path:
        vehicle_mass += mass.get(i)
    return vehicle_mass


def closest_insertion(G, H, source, target, impedance, heuristic):
    current_vehicle_mass = VEHICLE_MASS
    path = [source]
    costs_to_source = {}
    total_path = []

    # create a dictionary with the nodes and respective mass increments of the vehicle
    mass = {}
    for i in H.nodes:
        mass.update([(i, H.nodes[i]['mass'])])

    # verify the cost of the source to the nodes
    for u in H.adj[source]:
        edge_cost, _ = Graph_Collect.cost_path(G, source, u, current_vehicle_mass, impedance, heuristic)
        costs_to_source.update([(u, [edge_cost])])

    # sorting the dict according to edge weights
    costs_to_source = dict(sorted(costs_to_source.items(), key=lambda item: item[1][0]))

    # add the closest node of the source
    path.append(list(costs_to_source.keys())[0])

    # updates the vehicle mass according to current path
    current_vehicle_mass = updates_vehicle_mass(path, mass)

    nodes = list(H.nodes)
    nodes.remove(target)
    possibilities = set(nodes) - set(path)

    # all nodes must be visited
    while len(possibilities) > 0:  # len(path) < len(nodes):

        # get the closest node of any node inside the path
        min_cost = float('inf')
        k_node = float('inf')

        for a in path:
            for b in possibilities:
                cost, way = Graph_Collect.cost_path(G, a, b, current_vehicle_mass, impedance, heuristic)
                if cost < min_cost:
                    min_cost = cost
                    k_node = b

        # the k node must be inserted in a position of the path
        # where the cost (cost_IK + cost_KJ - cost_IJ) is minimum
        min_cost = float('inf')
        position = float('inf')
        k_way = 0

        for i in range(len(path) - 1):
            current_vehicle_mass = updates_vehicle_mass(path[:i], mass)
            cost_IK, _ = Graph_Collect.cost_path(G, path[i], k_node, current_vehicle_mass, impedance, heuristic)
            cost_KJ, _ = Graph_Collect.cost_path(G, k_node, path[i + 1], current_vehicle_mass, impedance, heuristic)
            cost_IJ, _ = Graph_Collect.cost_path(G, path[i], path[i + 1], current_vehicle_mass, impedance, heuristic)
            total_cost = cost_IK + cost_KJ - cost_IJ
            # print('costs', cost_IK, cost_KJ, cost_IJ, total_cost)
            if total_cost < min_cost:
                min_cost = total_cost
                position = i + 1

        path.insert(position, k_node)
        current_vehicle_mass = updates_vehicle_mass(path, mass)

        # nodes not yet visited
        possibilities = set(nodes) - set(path)

    path.append(target)

    if impedance == 'weight':
        G = Graph.update_weight(G, VEHICLE_MASS)

    # get all paths
    cost_total, paths, edges_update = Graph_Collect.sum_costs_route(G, H, path, VEHICLE_MASS, impedance, heuristic)

    return cost_total, paths, edges_update


def further_insertion(G, H, source, target, impedance, heuristic):
    current_vehicle_mass = VEHICLE_MASS
    path = [source]
    costs_to_source = {}

    # create a dictionary with the nodes and respective mass increments of the vehicle
    mass = {}
    for i in H.nodes:
        mass.update([(i, H.nodes[i]['mass'])])

    # verify the cost of the source to the nodes
    for u in H.adj[source]:
        edge_cost, _ = Graph_Collect.cost_path(G, source, u, current_vehicle_mass, impedance, heuristic)
        costs_to_source.update([(u, edge_cost)])

    # sorting the dict according to edge weights
    costs_to_source = dict(sorted(costs_to_source.items(), key=lambda item: item[1], reverse=True))

    # add the closest node of the source
    path.append(list(costs_to_source.keys())[0])

    # updates the vehicle mass according to current path
    current_vehicle_mass = updates_vehicle_mass(path, mass)

    nodes = list(H.nodes)
    nodes.remove(target)
    possibilities = set(nodes) - set(path)

    # all nodes must be visited
    while len(possibilities) > 0:  # len(path) < len(nodes):

        # get the closest node of any node inside the path
        max_cost = float('-inf')
        k_node = float('inf')
        for a in path:
            for b in possibilities:
                cost, _ = Graph_Collect.cost_path(G, a, b, current_vehicle_mass, impedance, heuristic)
                if cost > max_cost:
                    max_cost = cost
                    k_node = b

        # the k node must be inserted in a position of the path
        # where the cost (cost_IK + cost_KJ - cost_IJ) is minimum
        max_cost = float('-inf')
        position = 0
        for i in range(len(path) - 1):
            current_vehicle_mass = updates_vehicle_mass(path[:i], mass)
            cost_IK, _ = Graph_Collect.cost_path(G, path[i], k_node, current_vehicle_mass, impedance, heuristic)
            cost_KJ, _ = Graph_Collect.cost_path(G, k_node, path[i + 1], current_vehicle_mass, impedance, heuristic)
            cost_IJ, _ = Graph_Collect.cost_path(G, path[i], path[i + 1], current_vehicle_mass, impedance, heuristic)
            total_cost = cost_IK + cost_KJ - cost_IJ
            # print('costs', cost_IK, cost_KJ, cost_IJ, total_cost)
            if total_cost > max_cost:
                a_1 = path[i]
                a_2 = path[i + 1]
                max_cost = total_cost
                position = i + 1

        path.insert(position, k_node)
        current_vehicle_mass = updates_vehicle_mass(path, mass)

        # nodes not yet visited
        possibilities = set(nodes) - set(path)

    path.append(target)

    # get all paths
    cost_total, paths, edges_update = Graph_Collect.sum_costs_route(G, H, path, VEHICLE_MASS, impedance, heuristic)

    if impedance == 'weight':
        G = Graph.update_weight(G, VEHICLE_MASS)

    return cost_total, paths, edges_update


def shortest_path_faster(G, source, target, weight):
    dist, parent = _shortest_path_faster(G, source, weight)
    path = []
    route = _path(source, target, parent, path)
    return route


def exact_method(G, H, source, target):
    nodes_graph = list(H.nodes)
    nodes_graph.remove(source)
    if source != target:
        nodes_graph.remove(target)
    permutations = list(more_itertools.distinct_permutations(nodes_graph, len(nodes_graph)))

    paths = []
    costs = []
    all_permutations = []
    for i in permutations:
        i = list(i)
        i.insert(0, source)
        i.append(target)
        all_permutations.append(i)
        sum_costs, paths = Graph_Collect.sum_costs_route(G, H, i, VEHICLE_MASS)
        costs.append(sum_costs)
    minimum = min(costs)
    index_minimum = costs.index(minimum)

    return minimum, all_permutations[index_minimum], paths