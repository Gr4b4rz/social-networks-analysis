import networkx as nx
import matplotlib.pyplot as plt
from random import choice
from math import log
import collections
from sklearn.linear_model import LinearRegression
import numpy as np
import powerlaw


def get_graph_info(G):
    print("Rzad sieci: {}".format(G.number_of_nodes()))
    print("Rozmiar sieci: {}".format(G.number_of_edges()))

def plot_degree_dist(G):
    degree_sequence = sorted([d for n, d in G.degree().items()], reverse=True)  # degree sequence
    degreeCount = sorted(collections.Counter(degree_sequence).items())
    degs, cnts = sorted(zip(*degreeCount))
    cnt_prc = [cnt / float(G.number_of_nodes()) for cnt in cnts]
    plt.scatter(degs, cnt_prc, s=1)
    plt.show()

def calculate_avg_path_len(G, sampling):
    i = 0
    len_sum = 0
    while i < sampling:
        len_sum += nx.shortest_path_length(G, choice(G.nodes()), choice(G.nodes()))
        i += 1

    return len_sum / float(sampling)

def get_max_core_degree(G):
    i = 88 # start from this value not to wait too long
    while True:
        if not nx.k_core(G, i).number_of_nodes():
            return i - 1
        else:
            i += 1

def estimate_hill(lst, k):
    log_sum = 0
    for i in range(1, k):
        log_sum += log(lst[i] / float(lst[k + 1]))
    hill_estimation = 1 + 1 / float(log_sum / k)
    return hill_estimation

def draw_hill(G, k):
    degree_sequence = sorted([d for n, d in G.degree().items()], reverse=True)
    degreeCount = sorted(collections.Counter(degree_sequence).items())
    degs, cnts = sorted(zip(*degreeCount))
    cnt_prc = [cnt / float(G.number_of_nodes()) for cnt in cnts]
    x_axis = [x for x in range(2, k)]
    y_axis = [estimate_hill(cnts, x) for x in x_axis]
    plt.plot(x_axis, y_axis)
    plt.xlabel('k')
    plt.ylabel('wspolczynik rozkladu potegowego')
    # plt.show()

def calculate_alpha(G):
    degree_sequence = sorted([d for n, d in G.degree().items()], reverse=True)
    degreeCount = sorted(collections.Counter(degree_sequence).items())
    degs, cnts = sorted(zip(*degreeCount))
    cnt_prc = [cnt / float(G.number_of_nodes()) for cnt in cnts]
    result = powerlaw.Fit(cnt_prc)
    print(result.power_law.alpha)
    print(result.power_law.xmax)
    # powerlaw.plot_ccdf(cnt_prc)
    # plt.show()

    cumulation = 0
    cumulative_dist = []
    for cnt in cnt_prc:
        cumulation += cnt
        cumulative_dist.append(log(1 - cumulation, 10))

    deg_log = [log(deg, 10) for deg in degs]
    plt.scatter(deg_log, cumulative_dist)
    model = LinearRegression().fit(np.reshape(deg_log, (-1, 1)), cumulative_dist)
    print(model.score(np.reshape(deg_log, (-1, 1)), cumulative_dist))
    x_axis = [x for x in range(1, 1000)]
    y_axis = [model.coef_ * x + model.intercept_ for x in range(1, 1000)]
    plt.plot(x_axis, y_axis)
    # plt.show()
    return model.coef_

def main():
    fh = open("twitter_users.txt", 'rb')
    M = nx.MultiGraph(nx.read_edgelist(fh))
    fh.close()
    get_graph_info(M)

    G = nx.Graph(M)
    G.remove_edges_from(G.selfloop_edges())
    get_graph_info(G)
    Gc = max(nx.connected_component_subgraphs(G), key=len)
    get_graph_info(Gc)

    print("Srednia dlugosc sciezki dla proby 100: {}".format(calculate_avg_path_len(G, 100)))
    print("Srednia dlugosc sciezki dla proby 1000: {}".format(calculate_avg_path_len(G, 1000)))
    print("Srednia dlugosc sciezki dla proby 10000: {}".format(calculate_avg_path_len(G, 10000)))
    max_core_deg = get_max_core_degree(G)
    print("Maksymalny rzad rdzenia: {}".format(max_core_deg))
    print("Liczba rdzeni o trzech najwiekszych rzedach:")
    print(len(list(nx.connected_component_subgraphs(nx.k_core(G, max_core_deg)))))
    print(len(list(nx.connected_component_subgraphs(nx.k_core(G, max_core_deg - 1)))))
    print(len(list(nx.connected_component_subgraphs(nx.k_core(G, max_core_deg - 2)))))

    draw_hill(G, 500)

    plot_degree_dist(G)
    print(calculate_alpha(G))

if __name__== "__main__":
    main()
