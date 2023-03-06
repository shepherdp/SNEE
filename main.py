# (S)ocial (N)etwork (E)volution (E)ngine
# Author: Patrick Shepherd, PhD

import matplotlib.pyplot as plt

from SocialNetwork import SocialNetwork

def main():
    s = SocialNetwork(n=300, topology='scale free', rewire=.1, sat=.1, selfloops=False,
                      weight_dist='uniform', weight_mean=150, weight_stdev=50,
                      weight_min=100, weight_max=200)
    # s._generate_edge_weights()
    w = []
    for u, v in s.edges():
        print(u, v, s[u][v])
        w.append(s[u][v]['weight'])
    plt.scatter(w, [1 for i in w], alpha=.5)
    plt.show()


if __name__ == '__main__':
    main()