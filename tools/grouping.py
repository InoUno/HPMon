import re

##########################################
## Group mappings                       ##
##########################################

group_match = dict()
group_match['Snipper'] = 'Crab'
group_match['Clipper'] = 'Crab'
group_match['Cutter'] = 'Crab'
group_match['Bigclaw'] = 'Crab'
group_match['Thickshell'] = 'Crab'
group_match['Ironshell'] = 'Crab'
group_match['Steelshell'] = 'Crab'

group_match['Sylvestre'] = 'Mandragora'
group_match['Pygmaioi'] = 'Mandragora'
group_match['Mourioche'] = 'Mandragora'
group_match['Korrigan'] = 'Mandragora'

group_match['Maze Maker'] = 'Worm'

group_match['Death Jacket'] = 'Bee'

group_match['Moss Eater'] = 'Rabbit'

group_match['Crane Fly'] = 'Fly'
group_match['Skimmer'] = 'Fly'

group_match['Acrophies'] = 'Leech'
group_match['Goobbue Parasite'] = 'Leech'

group_match['Akbaba'] = 'Bird'
group_match['Carrion Crow'] = 'Bird'
group_match['Raven'] = 'Bird'
group_match['Screamer'] = 'Bird'
group_match['Marsh Murre'] = 'Bird'
group_match['Vulture'] = 'Bird'
group_match['Zu'] = 'Bird'
group_match['Flamingo'] = 'Bird'
group_match['Jubjub'] = 'Bird'
group_match['Ba'] = 'Bird'

group_match['Broo'] = 'Sheep'
group_match['Padfoot'] = 'Sheep'

group_match['Bats'] = 'Bat'
group_match['Bat'] = 'Bat'
group_match['Stirge'] = 'Bat'
group_match['Midnight Wings'] = 'Bat'
group_match['Goblin Smithy'] = 'Goblin WAR'
group_match['Goblin Butcher'] = 'Goblin WAR'
group_match['Goblin Fisher'] = 'Goblin WAR'
group_match['Magic Jar'] = 'Pot'
group_match['Magic Pot'] = 'Pot'
group_match['Magic Urn'] = 'Pot'

group_match['Big Jaw'] = 'Pugil'
group_match['Makara'] = 'Pugil'

group_match['Berry Grub'] = 'Crawler'
group_match['Meat Maggot'] = 'Crawler'

group_match['Myxomycete'] = 'Mushroom'
group_match['Fly Agaric'] = 'Mushroom'
group_match['Forest Funguar'] = 'Mushroom'
group_match['Death Cap'] = 'Mushroom'
group_match['Shrieker'] = 'Mushroom'

group_match['Geezard'] = 'Lizard'

group_match['Mimas'] = 'Giant'
group_match['Porphyrion'] = 'Giant'


group_regex = dict()
group_regex['Crawler'] = 'Crawler'
group_regex['Crab'] = 'Crab'
group_regex['Beetle'] = 'Beetle'
group_regex['Bee'] = 'Bee'
group_regex['Wasp'] = 'Bee'
group_regex['Dhalmel'] = 'Dhalmel'
group_regex['Rarab'] = 'Rabbit'
group_regex['Rabbit'] = 'Rabbit'
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
group_regex[r'\w+bee'] = 'Bee'
group_regex['Hornet'] = 'Bee'
group_regex['Doll'] = 'Doll'
group_regex['Idol'] = 'Doll'
group_regex['Bat'] = 'Bat'
group_regex['Bats'] = 'Bat'
group_regex['Gaylas'] = 'Bat'
group_regex['Giant'] = 'Giant'
group_regex['Goobbue'] = 'Goobbue'
group_regex['Lycopodium'] = 'Mandragora'


group_regex['Goblin\s'] = 'Goblin'
group_regex['Moblin\s'] = 'Moblin'
group_regex['Antican\s'] = 'Antican'
group_regex['Gigas\s'] = 'Giant'
group_regex['Orcish'] = 'Orcish'
group_regex['Fomor'] = 'Fomor'
group_regex['Yagudo'] = 'Yagudo'
group_regex['Quadav'] = 'Quadav'
group_regex['Sahagin'] = 'Sahagin'
group_regex['Tonberry'] = 'Tonberry'
group_regex['Opo-opo'] = 'Opo-opo'
group_regex['\sElemental'] = 'Elemental'


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
    # 'Goblin\s',
    # 'Moblin\s',
    # 'Antican\s',
    # 'Gigas\s',
    # 'Orcish',
    # 'Fomor',
    # 'Yagudo',
    # 'Quadav',
    # 'Sahagin',
    # 'Tonberry',
}

def filter_matcher(name):
    for needle in filter_regex:
        if re.search(needle, name):
            return True
    return False


def is_pet(name):
    return "'s" in name