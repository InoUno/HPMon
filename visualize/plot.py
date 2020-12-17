import matplotlib.pyplot as plt
import numpy as np
import csv
import itertools
import re

##########################################
## Group mappings                       ##
##########################################

families = dict()
families['Snipper'] = 'Crab'
families['Clipper'] = 'Crab'
families['Bigclaw'] = 'Crab'

families['Sylvestre'] = 'Mandragora'
families['Pygmaioi'] = 'Mandragora'
families['Death Jacket'] = 'Bee'
families['Makara'] = 'Pugil'
families['Akbaba'] = 'Bird'
families['Raven'] = 'Bird'
families['Carrion Crow'] = 'Bird'
families['Sand Hare'] = 'Rabbit'
families['Zu'] = 'Bird'


familiesRegex = dict()
familiesRegex['Crawler'] = 'Crawler'
familiesRegex['Crab'] = 'Crab'
familiesRegex['Beetle'] = 'Beetle'
familiesRegex['Bee'] = 'Bee'
familiesRegex['Dhalmel'] = 'Dhalmel'
familiesRegex['Rarab'] = 'Rabbit'
familiesRegex['Leech'] = 'Leech'
familiesRegex['Mandragora'] = 'Mandragora'
familiesRegex['Pugil'] = 'Pugil'
familiesRegex['Lizard'] = 'Lizard'
familiesRegex['Sapling'] = 'Sapling'
familiesRegex['Spider'] = 'Spider'
familiesRegex['Sheep'] = 'Sheep'
familiesRegex['Worm'] = 'Worm'
familiesRegex[r'\w+fly'] = 'Fly'

def familyMatcher(name):
    if name in families:
        return families[name]

    for needle in familiesRegex:
        if re.search(r'\b' + needle + r'\b', name):
            return familiesRegex[needle]



##########################################
## Read data and group it               ##
##########################################

rng = np.random.RandomState(0)

unmatched = 'Unmatched'
marker_colors = dict()
marker_colors[unmatched] = [ 0, 0, 0 ]

groups = dict()
with open('./data/db.csv','r') as csvfile:
    plots = csv.reader(csvfile, delimiter=',')
    for row in plots:
        toMatch = row[0]
        family = familyMatcher(row[0])
        if family:
            toMatch = family

        if not toMatch in groups:
            marker_colors[toMatch] = [ rng.randint(256)/256.0, rng.randint(256)/256.0, rng.randint(256)/256.0 ]
            groups[toMatch] = {}
            groups[toMatch][0] = []
            groups[toMatch][1] = []
            groups[toMatch][2] = []

        groups[toMatch][0].append(int(row[1]))
        groups[toMatch][1].append(float(row[2]))
        groups[toMatch][2].append(row[0])


fig, ax = plt.subplots()
markers = itertools.cycle(('o', '*', 'v', '^', 'p', 'X', '<', '>', 'd'))
colors = itertools.cycle(('red', 'blue', 'green', 'orange', 'black'))

dataGroups = []
dataNames = []
for groupName in sorted(groups.keys()):
    group = groups[groupName]
    dataGroups.append(ax.scatter(group[0], group[1], color=next(colors), label=groupName, marker=next(markers)))
    dataNames.append(group[2])


##########################################
## Set up interactive parts of the plot ##
##########################################
legend = ax.legend(loc='upper left', fancybox=True, shadow=True)

# Map legend groups to plotted groups
legendMapping = {}
for legendGroup, plotGroup in zip(legend.get_texts(), dataGroups):
    legendGroup.set_picker(5)
    legendMapping[legendGroup] = plotGroup


def toggleGroup(legendGroup, visible=None):
    plotGroup = legendMapping[legendGroup]
    vis = visible
    if vis == None:
        vis = not plotGroup.get_visible()
    plotGroup.set_visible(vis)

    if vis:
        legendGroup.set_alpha(1.0)
    else:
        legendGroup.set_alpha(0.2)

def on_pick(event):
    toggleGroup(event.artist)
    fig.canvas.draw()

def on_click(event):
    if event.button == 3:
        visible = False
    elif event.button == 2:
        visible = True
    else:
        return

    for legendGroup in legendMapping:
        toggleGroup(legendGroup, visible)
    fig.canvas.draw()


annot = ax.annotate("", xy=(0,0), xytext=(-175,50), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(pos, name):
    annot.xy = pos
    annot.set_text("{} (Level: {}, HP: {})".format(name, int(pos[0]), pos[1]))
    annot.get_bbox_patch().set_alpha(0.4)

def getPointDetails(event):
    for i in range(len(dataGroups)):
        dataGroup = dataGroups[i]
        cont, ind = dataGroup.contains(event)
        if cont:
            subIndex = ind['ind'][0]
            return dataGroup.get_offsets()[subIndex], dataNames[i][subIndex]
    return None, None

def on_hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        pos, name = getPointDetails(event)
        if pos is None:
            if vis:
                annot.set_visible(False)
                fig.canvas.draw_idle()
        else:
            update_annot(pos, name)
            annot.set_visible(True)
            fig.canvas.draw_idle()


fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_hover)
fig.suptitle('Left-click legend to toggle group\nRight-click to hide all\nMiddle-click to show all', va='top', size='small')



## Show plot
plt.ylabel('HP')
plt.ylim(bottom=0)
plt.xlabel('Level')
plt.xlim(left=0)
ax.set_axisbelow(True)
fig.set_size_inches(20, 12)
plt.grid(True)
plt.show()
