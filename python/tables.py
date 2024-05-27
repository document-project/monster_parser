HIT_DIE_SIZE = {
    "tiny":4,
    "small":6,
    "medium":8,
    "large":10,
    "huge":12,
    "gargantuan":20
}
FULL_SPELLCASTER = [
    lambda level : 2 if level == 1 else (3 if level == 2 else 4),
    lambda level : 0 if level < 3 else (2 if level == 3 else 3),
    lambda level : 0 if level < 5 else (2 if level == 5 else 3),
    lambda level : 0 if level < 7 else (1 if level == 7 else (2 if level == 8 else 3)),
    lambda level : 0 if level < 9 else (1 if level == 9 else (2 if level < 18 else 3)),
    lambda level : 0 if level < 11 else (1 if level < 19 else 2),
    lambda level : 0 if level < 13 else (1 if level < 20 else 2),
    lambda level : 0 if level < 15 else 1,
    lambda level : 0 if level < 17 else 1
]
SEMI_SPELLCASTER = [
    lambda level : 0 if level == 1 else (2 if level == 2 else (3 if level < 5 else 4)),
    lambda level : 0 if level < 5 else (2 if level < 7 else 3),
    lambda level : 0 if level < 9 else (2 if level < 11 else 3),
    lambda level : 0 if level < 13 else (1 if level < 15 else (2 if level < 17 else 3)),
    lambda level : 0 if level < 17 else (1 if level < 19 else 2)
]
WARLOCK = [
    lambda level : 1 if level == 1 else (2 if level == 2 else 0),
    lambda level : 2 if level > 2 and level < 5 else 0,
    lambda level : 2 if level > 4 and level < 7 else 0,
    lambda level : 2 if level > 6 and level < 9 else 0,
    lambda level : 0 if level < 9 else (2 if level < 11 else (3 if level < 17 else 4))
]
SPELL_SLOTS = {
    "bard":FULL_SPELLCASTER,
    "cleric":FULL_SPELLCASTER,
    "druid":FULL_SPELLCASTER,
    "paladin":SEMI_SPELLCASTER,
    "ranger":SEMI_SPELLCASTER,
    "sorcerer":FULL_SPELLCASTER,
    "warlock":WARLOCK,
    "wizard":FULL_SPELLCASTER
}
SPELLCASTING_ABILITY = {
    "bard":"cha",
    "cleric":"wis",
    "druid":"wis",
    "paladin":"cha",
    "ranger":"wis",
    "sorcerer":"cha",
    "warlock":"cha",
    "wizard":"int"
}
DEFAULT_IMMUNITIES = {
    "elemental":[
        "exhaustion",
        "paralyzed",
        "petrified",
        "poisoned",
        "unconcious"
    ],
    "plant":[
        "exhaustion",
        "blinded",
        "deafened",
    ],
    "fiend":[
        "poisoned",
        "exhaustion",
    ],
    "celestial":[
        "poisoned",
        "exhaustion",
    ],
    "ooze":[
        "blinded",
        "deafened",
        "exhaustion",
        "prone",
    ],
    "construct":[
        "charmed",
        "frightened",
        "exhaustion",
        "paralyzed",
        "petrified",
        "poisoned"
    ],
    "undead":[
        "exhaustion",
        "poisoned"
    ]
}
NATURES = {
    "elemental":{
        "header":"Elemental Nature",
        "text":"[articulate True [name]] does not require air, food, drink, or sleep."
    },
    "undead":{
        "header":"Undead Nature",
        "text":"[articulate True [name]] does not require air, food, drink, or sleep."
    },
    "construct":{
        "header":"Constructed Nature",
        "text":"[articulate True [name]] does not require air, food, drink, or sleep."
    },
    "fiend":{
        "header":"Fiendish Nature",
        "text":"[articulate True [name]] does not require air, food, drink, or sleep."
    },
    "celestial":{
        "header":"Celestial Nature",
        "text":"[articulate True [name]] does not require air, food, drink, or sleep."
    },
    "ooze":{
        "header":"Ooze",
        "text":"[articulate True [name]] does not require air or sleep."
    },
    "plant":{
        "header":"Plant",
        "text":"[articulate True [name]] does not require sleep."
    }
}
MONSTER_TYPE_PLURALS = {
    "elemental":"elementals",
    "undead":"undead",
    "construct":"constructs",
    "fiend":"fiends",
    "celestial":"celestials",
    "ooze":"oozes",
    "plant":"plants",
    "humanoid":"humanoids",
    "giant":"giants",
    "monstrosity":"monstrosities",
    "fey":"fey",
    "dragon":"dragons",
    "aberration":"aberrations",
    "beast":"beasts",
}
GROUP_ATTRIBUTES_NOT_TO_COPY = ["name", "headername", "sorttype", "flavor", "description", "include-monster-headers", "lair"]
