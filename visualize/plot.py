import matplotlib.pyplot as plt
import numpy as np
import csv

rng = np.random.RandomState(0)

hp = []
lvls = []
cols = []
marker_colors = dict()
next_c = 0

with open('./data/db.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        if not row[0] in marker_colors:
            marker_colors[row[0]] = [ rng.randint(256)/256.0, rng.randint(256)/256.0, rng.randint(256)/256.0 ]
        cols.append(marker_colors[row[0]])

        lvls.append(int(row[1]))
        hp.append(float(row[2]))



plt.scatter(lvls, hp, c=cols)
plt.ylabel('HP')
plt.xlabel('Level')
plt.show()
