import matplotlib.pyplot as plt
import numpy as np
import csv
import itertools
import re
from grouping import filter_matcher, group_matcher

##########################################
## Read data and group it               ##
##########################################

rng = np.random.RandomState(0)

unmatched = 'Unmatched'
marker_colors = dict()
marker_colors[unmatched] = [ 0, 0, 0 ]

groups = dict()
with open('./data/db.csv','r') as csvfile:
    plots = csv.DictReader(csvfile, delimiter=',')
    for row in plots:
        if row['Level'] == '?':
            continue
        to_match = row['Name']
        family = group_matcher(to_match)
        if family:
            to_match = family

        if filter_matcher(to_match):
            continue

        if not to_match in groups:
            marker_colors[to_match] = [ rng.randint(256)/256.0, rng.randint(256)/256.0, rng.randint(256)/256.0 ]
            groups[to_match] = {}
            groups[to_match][0] = []
            groups[to_match][1] = []
            groups[to_match][2] = []

        groups[to_match][0].append(int(row['Level']))
        groups[to_match][1].append(float(row['Mid']))
        groups[to_match][2].append(row['Name'])


fig, ax = plt.subplots()
markers = itertools.cycle(('o', '*', 'v', '^', 'p', 'X', '<', '>', 'd'))
colors = itertools.cycle(('red', 'blue', 'green', 'orange', 'black'))

data_groups = []
data_names = []
for group_name in sorted(groups.keys()):
    group = groups[group_name]
    data_groups.append(ax.scatter(group[0], group[1], color=next(colors), label=group_name, marker=next(markers)))
    data_names.append(group[2])


##########################################
## Set up interactive parts of the plot ##
##########################################
legend = ax.legend(loc='upper left', fancybox=True, shadow=True)

# Map legend groups to plotted groups
legend_mapping = {}
for legend_group, plot_group in zip(legend.get_texts(), data_groups):
    legend_group.set_picker(5)
    legend_mapping[legend_group] = plot_group


def toggle_group(legend_group, visible=None):
    plot_group = legend_mapping[legend_group]
    vis = visible
    if vis == None:
        vis = not plot_group.get_visible()
    plot_group.set_visible(vis)

    if vis:
        legend_group.set_alpha(1.0)
    else:
        legend_group.set_alpha(0.2)

def on_pick(event):
    toggle_group(event.artist)
    fig.canvas.draw()

def on_click(event):
    if event.button == 3:
        visible = False
    elif event.button == 2:
        visible = True
    else:
        return

    for legend_group in legend_mapping:
        toggle_group(legend_group, visible)
    fig.canvas.draw()


annot = ax.annotate("", xy=(0,0), xytext=(-175,50), textcoords="offset points",
                    bbox=dict(boxstyle="round", fc="w"),
                    arrowprops=dict(arrowstyle="->"))
annot.set_visible(False)

def update_annot(pos, name):
    annot.xy = pos
    annot.set_text("{} (Level: {}, HP: {})".format(name, int(pos[0]), pos[1]))
    annot.get_bbox_patch().set_alpha(0.4)

def get_point_details(event):
    for i in range(len(data_groups)):
        data_group = data_groups[i]
        cont, ind = data_group.contains(event)
        if cont:
            sub_index = ind['ind'][0]
            return data_group.get_offsets()[sub_index], data_names[i][sub_index]
    return None, None

def on_hover(event):
    vis = annot.get_visible()
    if event.inaxes == ax:
        pos, name = get_point_details(event)
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
