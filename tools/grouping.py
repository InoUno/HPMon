import re

##########################################
## Group mappings                       ##
##########################################

group_match = dict()
group_match['Snipper'] = 'Crab'
group_match['Clipper'] = 'Crab'
group_match['Bigclaw'] = 'Crab'
group_match['Thickshell'] = 'Crab'
group_match['Ironshell'] = 'Crab'

group_match['Sylvestre'] = 'Mandragora'
group_match['Pygmaioi'] = 'Mandragora'
group_match['Death Jacket'] = 'Bee'
group_match['Makara'] = 'Pugil'
group_match['Akbaba'] = 'Bird'
group_match['Carrion Crow'] = 'Bird'
group_match['Raven'] = 'Bird'
group_match['Screamer'] = 'Bird'
group_match['Marsh Murre'] = 'Bird'
group_match['Vulture'] = 'Bird'
group_match['Zu'] = 'Bird'
group_match['Broo'] = 'Sheep'
group_match['Bats'] = 'Bat'
group_match['Bat'] = 'Bat'
group_match['Goblin Smithy'] = 'Goblin WAR'
group_match['Goblin Butcher'] = 'Goblin WAR'
group_match['Goblin Fisher'] = 'Goblin WAR'


group_regex = dict()
group_regex['Crawler'] = 'Crawler'
group_regex['Crab'] = 'Crab'
group_regex['Beetle'] = 'Beetle'
group_regex['Bee'] = 'Bee'
group_regex['Wasp'] = 'Bee'
group_regex['Dhalmel'] = 'Dhalmel'
group_regex['Rarab'] = 'Rabbit'
group_regex['Hare'] = 'Rabbit'
group_regex['Bunny'] = 'Rabbit'
group_regex['Leech'] = 'Leech'
group_regex['Mandragora'] = 'Mandragora'
group_regex['Pugil'] = 'Pugil'
group_regex['Lizard'] = 'Lizard'
group_regex['Sapling'] = 'Sapling'
group_regex['Spider'] = 'Spider'
group_regex['Sheep'] = 'Sheep'
group_regex['Karakul'] = 'Sheep'
group_regex['Worm'] = 'Worm'
group_regex['Eater'] = 'Worm'
group_regex['Tiger'] = 'Tiger'
group_regex['Smilodon'] = 'Tiger'
group_regex[r'\w+fly'] = 'Fly'
group_regex[r'\w+bat'] = 'Bat'
group_regex['Bat'] = 'Bat'
group_regex['Bats'] = 'Bat'

job_to_group = dict()
job_to_group['WAR'] = ['Tiger', 'Lizard', 'Dhalmel', 'Goblin WAR', 'Sapling', 'Spider', 'Sheep', 'Fly', 'Rabbit', 'Bird', 'Pugil', 'Sheep']



group_to_job = dict()
for job in job_to_group.keys():
    for group in job_to_group[job]:
        group_to_job[group] = job


def group_matcher(name):
    if name in group_match:
        return group_match[name]

    for needle in group_regex:
        if re.search(r'\b' + needle + r'\b', name):
            return group_regex[needle]

filter_regex = {
    'Goblin\s',
    'Gigas\s',
    'Orcish',
    'Yagudo',
    'Quadav',
    'Sahagin',
}

def filter_matcher(name):
    for needle in filter_regex:
        if re.search(needle, name):
            return True
    return False


def is_pet(name):
    return "'s" in name