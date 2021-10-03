import csv
import pprint

##########################################
## Read data
##########################################

special_zones = set(range(1, 45)) # CoP zones
special_zones.add(169) # Toraimai Canal


def parse_groups():
    group_lookup = dict()
    level_lookup = dict()

    csvfile = open('./data/db.csv','r')
    data = csv.DictReader(csvfile, delimiter=',')

    for row in data:
        if row['Level'] == '?':
            continue


        name = row['Name']
        zone = int(row['Zone'])
        group_id = (zone, name)

        level = int(row['Level'])

        node = dict()
        node['id'] = group_id
        node['neighbours'] = []
        node['zone'] = zone
        node['name'] = name
        node['level'] = level
        node['min'] = int(row['Min'])
        node['max'] = int(row['Max'])
        node['special_zone'] = zone in special_zones

        if not group_id in group_lookup:
            group_lookup[group_id] = [node]
        else:
            for other_node in group_lookup[group_id]:
                other_node['neighbours'].append(node)
                node['neighbours'].append(other_node)

            group_lookup[group_id].append(node)


        if not level in level_lookup:
            level_lookup[level] = [node]
        else:
            for other_node in level_lookup[level]:
                if other_node['min'] > node['max'] or other_node['max'] < node['min'] or other_node['special_zone'] != node['special_zone']:
                    continue

                other_node['neighbours'].append(node)
                node['neighbours'].append(other_node)

            level_lookup[level].append(node)


    groups = []
    for level in level_lookup:
        for node in level_lookup[level]:
            if node.get('visited'):
                continue

            group = []
            to_visit = [node]
            while len(to_visit) > 0:
                current = to_visit.pop(0)
                if current.get('visited'):
                    continue
                current['visited'] = True
                group.append(current)

                for nb in current['neighbours']:
                    to_visit.append(nb)

            groups.append(group)


    csvfile.close()
    sorted_groups = sorted(groups, key=lambda el: len(el), reverse=True)
    collected_groups = []
    for idx, group in enumerate(sorted_groups):
        collected_group = dict()
        sorted_group = sorted(group, key=lambda node: node['level'])
        for node in sorted_group:
            if not node['level'] in collected_group:
                collection = dict()
                collection['nodes'] = []
                collection['hp'] = set()
                collected_group[node['level']] = collection

            collection['nodes'].append(node['id'])

            if node['min'] == node['max']:
                hp = node['min']
            else:
                hp = f"{node['min']}-{node['max']}"

            collection['hp'].add(hp)

        if len(collected_group) > 2:
            collected_groups.append(collected_group)

    for idx, collected_group in enumerate(collected_groups):
        if idx > 30:
            break
        print("Group ", idx)
        for level in collected_group:
            collection = collected_group[level]
            print(f"{level}: HP: {collection['hp']} - {collection['nodes']}")

        print("")


parse_groups()