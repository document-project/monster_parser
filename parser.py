import python.brand as brand
import python.tables as tables
import python.parser_utility as pp
from time import time

MULTIATTACK_SPLICE_KEY = "\n%multiattack-splice-key\n"
NO_NEWLINE_TRIGGERS = ["\\end{enumerate}", "\\end{itemize}", "\\end{quote}"]
SOURCE_YAML_DIRECTORY = "monsters"
ABILITY_LIST = ["str", "dex", "con", "int", "wis", "cha"]
NEWLINE = "\\\\"
LINEBREAK = "\\bigskip"
PAGEBREAK = "\n\\clearpage\n"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

monsters_by_habitat = {}
monsters_by_type = {}
monsters_by_cr = {}
errors = []
appendicies = {}
appendix_count = 0
monster_count = 0


def add_appendix(name, contents):
    global appendicies, appendix_count
    appendicies["Appendix " + ALPHABET[appendix_count] + ": " + name] = contents
    appendix_count += 1


def entry(header, body):
    body = body.replace("\n", "")
    if body.endswith("}"):
        for string in NO_NEWLINE_TRIGGERS:
            if body.endswith(string):
                return "\\entrynonewline{" + header + "}{" + body + "}"
    return "\\entry{" + header + "}{" + body + "}"
# The entrynonewline is required to avoid LaTeX errors for having
# a newline after a list-type command.


def hitpoints(num, size, conbonus):
    return brand.roll(num, tables.HIT_DIE_SIZE[size], conbonus * num)


def partition(title):
    return "\\textbf{" + title + "}" + NEWLINE + "\\halfline "


def ac(dex, bonus, reasons):
    ac_string = str(10 + dex + bonus)
    if len(reasons) > 0:
        ac_string += " (" + pp.comma_separate(reasons) + ")"
    return ac_string


def skill_profs(skill_prof_list, params):
    skill_profs_dict = {}
    for skill in skill_prof_list:
        if skill in skill_profs_dict:
            skill_profs_dict[skill] += params["profbonus"]
        else:
            skill_profs_dict[skill] = params[brand.SKILL_ABILITY[skill]] + params["profbonus"]
    skill_profs_string = ""
    for skill in skill_profs_dict:
        if skill_profs_string != "":
            skill_profs_string += ", "
        bonus = skill_profs_dict[skill]
        skill_profs_string += brand.SKILL_PRETTYNAME[skill] + " "
        skill_profs_string += brand.format_bonus(bonus)
    return {"string":skill_profs_string, "dict":skill_profs_dict}


def save_profs(save_prof_list, params):
    save_profs_dict = {}
    for save in save_prof_list:
        if save in save_profs_dict:
            save_profs_dict[save] += params["profbonus"]
        else:
            save_profs_dict[save] = params[save] + params["profbonus"]
    save_profs_string = ""
    for save in save_profs_dict:
        if save_profs_string != "":
            save_profs_string += ", "
        bonus = save_profs_dict[save]
        save_profs_string += save.capitalize() + " "
        save_profs_string += brand.format_bonus(bonus)
    return save_profs_string


def create_stat_table(scores, bonuses):
    table = """\\smallskip
    \\begin{footnotesize}
    \\resizebox{\\columnwidth}{!}{
    \\begin{tabular}{llllll}
    \\hline""" + NEWLINE
    for ability in ABILITY_LIST:
        table += "\\textbf{" + ability.upper() + "}"
        if ability != "cha":
            table += "&"
    table += NEWLINE
    for ability in ABILITY_LIST:
        table += str(scores[ability]) + " (" + brand.format_bonus(bonuses[ability]) + ")"
        if ability != "cha":
            table += "&"
    table += NEWLINE + NEWLINE + """\\hline
    \\end{tabular}}
    \\end{footnotesize}
    \\smallskip"""
    return table


def create_attack(attack, params):
    global errors
    attack_string = "\\textit{"
    bonus = params[attack["ability"]] + params["profbonus"]
    if "bonus" in attack:
        bonus += attack["bonus"]
    if attack["type"] == "mw":
        attack_string += "Melee Weapon Attack:} "
        attack_string += brand.format_bonus(bonus) + " to hit, reach " + str(pp.get_key_if_exists(attack, "reach", 5)) + " ft."
    elif attack["type"] == "rw":
        attack_string += "Ranged Weapon Attack:} "
        attack_string += brand.format_bonus(bonus) + " to hit, range " + str(attack["range"]) + " ft."
    elif attack["type"] == "ms":
        attack_string += "Melee Spell Attack:} "
        attack_string += brand.format_bonus(bonus) + " to hit, reach " + str(pp.get_key_if_exists(attack, "reach", 5)) + " ft."
    elif attack["type"] == "rs":
        attack_string += "Ranged Spell Attack:} "
        attack_string += brand.format_bonus(bonus) + " to hit, range " + str(attack["range"]) + " ft."
    elif attack["type"] == "m/rw":
        attack_string += "Melee or Ranged Weapon Attack:} "
        attack_string += brand.format_bonus(bonus) + " to hit, reach " + str(pp.get_key_if_exists(attack, "reach", 5)) + " ft. or range "
        attack_string += str(attack["range"]) + " ft."
    else:
        errors.append("unknown attack type \"" + attack["type"] + "\"")
        
    attack_string += ", " + pp.get_key_if_exists(attack, "target", "one target") + "." + NEWLINE + "\\textit{Hit:} "
    attack_string += brand.eval_string(attack["onhit"], params)
    if "special" in attack:
        attack_string += NEWLINE + brand.eval_string(attack["special"], params)
    return entry(attack["name"], attack_string)


def dmg_attributes(attributes):
    standard_attributes = []
    special_attribute = ""
    for attr in attributes:
        if "and" in attr:
            special_attribute = attr
        else:
            standard_attributes.append(attr)
    standard_attributes.sort()
    attribute_string = pp.comma_separate(standard_attributes)
    if special_attribute != "":
        if len(standard_attributes) > 0:
            attribute_string += "; "
        attribute_string += special_attribute
    return attribute_string


def cond_immunities(immunities, creature_type):
    default_immunities = []
    if creature_type in tables.DEFAULT_IMMUNITIES:
        default_immunities = tables.DEFAULT_IMMUNITIES[creature_type].copy()
    for immunity in immunities:
        if immunity[0:1] == "n/":
            if immunity[2:] in default_immunities:
                default_immunities.erase(immunity[2:])
        else:
            default_immunities.append(immunity)
    return pp.comma_separate(sorted(default_immunities))


def get_spell_slots(slot_formulae, level):
    slots = []
    for formula in slot_formulae:
        slots.append(formula(level))
    return slots


def spellcasting(slot_type, level, spells, params):
    bonus = params[tables.SPELLCASTING_ABILITY[slot_type]] + params["profbonus"]
    string = get_ability_text(
        "spellcasting",
        {
            "name":params["name"],
            "level":level,
            "ability":brand.ABILITIES_SPELLOUT[tables.SPELLCASTING_ABILITY[slot_type]],
            "save_dc":8 + bonus,
            "attack_bonus":bonus
        }
    ) + NEWLINE
    string += "\\textbf{Cantrips:} " + brand.spell(pp.comma_separate(sorted(spells[0])))
    slots = get_spell_slots(tables.SPELL_SLOTS[slot_type], level)
    for i in range(0, len(spells) - 1):
        slot_num = slots[i]
        string += NEWLINE + "\\textbf{" + brand.format_index(i + 1) + " Level"
        if slot_num != 0:
            string += " (" + str(slot_num) + " slots)"
        string += ":} " + brand.spell(pp.comma_separate(sorted(spells[i + 1])))
    return entry("Spellcasting", string)


def innate_spellcasting(spellcasting, params):
    ability = spellcasting["ability"]
    spells = spellcasting["spells"]
    bonus = params[ability] + params["profbonus"]
    string = get_ability_text(
        "innate-spellcasting",
        {
            "name":params["name"],
            "ability":brand.ABILITIES_SPELLOUT[ability],
            "save_dc":8 + bonus,
            "attack_bonus":bonus
        }
    )
    for category in spells:
        string += NEWLINE + "\\textbf{" + category["frequency"].title() + ":} " + brand.spell(pp.comma_separate(sorted(category["spells"])))
    header = "Innate Spellcasting"
    if "tags" in spellcasting:
        header += " ("  + pp.comma_separate(sorted(spellcasting["tags"])).title() + ")"
    return entry(header, string)


def speeds(speed_dict):
    speed_string = str(speed_dict["land"]) + " ft."
    speed_type_list = sorted(speed_dict)
    for speed_type in speed_type_list:
        if speed_type != "land":
            if speed_type == "fly-hover":
                speed_string += ", fly " + str(speed_dict[speed_type]) + " ft. (hover)"
            else:
                speed_string += ", " + speed_type + " " + str(speed_dict[speed_type]) + " ft."
    return speed_string


def check_missing_fields(monster):
    global errors
    error = False
    monster_name = ""
    if not "name" in monster:
        print("ERROR: " + "Unnamed monster!")
        error = True
    else:
        monster_name = monster["name"]
        if not "cr" in monster:
            errors.append(monster_name + " does not have a CR")
            error = True
        if not "size" in monster:
            errors.append(monster_name + " does not have a size")
            error = True
        if not "type" in monster:
            errors.append(monster_name + " does not have a type")
            error = True
        if not "hd" in monster:
            errors.append(monster_name + " does not have hit dice")
            error = True
        if not "speed" in monster:
            errors.append(monster_name + " does not have a speed")
            error = True
        elif not "land" in monster["speed"]:
            errors.append(monster_name + " does not have a land speed")
            error = True
        if not "stats" in monster:
            errors.append(monster_name + " does not have ability scores")
            error = True
    return error


def format_actions(actions, params, key="effect"):
    global ability_effects
    action_string = ""
    action_name_dict = {}
    for action in actions:
        action_name_dict[action["name"]] = action
    for action_name in sorted(action_name_dict):
        action = action_name_dict[action_name]
        if action_name in ability_effects and not key in action:
            action[key] = ability_effects[action_name]
        if "uses" in action:
            action_name += " (" + action["uses"].title() + ")"
        # the "cost" clause is for legendary actions
        elif "cost" in action:
            action_name += " (Costs " + str(action["cost"]) + " Actions)"
        action_string += entry(action_name, brand.eval_string(action[key], params)) + LINEBREAK
    return action_string


def abilities(abilities, params):
    return format_actions(abilities, params)


def variants(diffs, params):
    return partition("Variants") + format_actions(diffs, params, key="mods")


def description(descriptions, monster_type, name, include_default=True):
    string = ""
    if monster_type in tables.NATURES and include_default:
        descriptions.append(tables.NATURES[monster_type].copy())
    for description in descriptions:
        if type(description["header"]) != type(None) and type(description["text"]) != type(None):
            description["text"] = brand.eval_string(description["text"], {"name":name})
            string += entry(description["header"], description["text"])
    return string


def get_ability_text(ability_name, params):
    global ability_effects
    return brand.eval_string(ability_effects[ability_name], params)


def legendary_actions(actions, params):
    string = partition("Legendary Actions")
    if "uses" in actions:
        params["uses"] = actions["uses"]
        actions = actions["actions"]
    else:
        params["uses"] = 3
    string += get_ability_text("legendary-actions", params) + NEWLINE + LINEBREAK
    return string + format_actions(actions, params)


def lair_actions(actions, params):
    string = partition("Lair Actions") + get_ability_text("lair-actions", params) + NEWLINE + LINEBREAK
    return string + format_actions(actions, params)


def create_regional_effects(effects, death_effect, params):
    string = partition("Regional Effects") + get_ability_text("regional-effects", params) + NEWLINE + LINEBREAK
    string += format_actions(effects, params) + " "
    string += brand.eval_string(death_effect, params)
    return string


def lair(lair, params):
    string = "\\subsection*{" + brand.articulate(True, brand.possessive(params["name"])) + " Lair}"
    if "description" in lair:
        string += lair["description"] + NEWLINE + LINEBREAK
    if "actions" in lair:
        string += lair_actions(lair["actions"], params)
    if "regional-effects" in lair:
        regional_effects = lair["regional-effects"]
        string += create_regional_effects(regional_effects["effects"], regional_effects["ondeath"], params)
    return string


def reactions(actions, params):
    return partition("Reactions") + format_actions(actions, params)


def create_header(name, title=True, label=True, addtoc=True):
    header = ""
    if label:
        header += "\\label{" + name + "}"
    if addtoc:
        header += "\\addcontentsline{toc}{subsection}{" + name + "}"
    if title:
        header += "\\section*{" + name + "}\\halfline" + LINEBREAK
    return header


def format_languages(languages):
    string = ""
    languages.sort()
    for language in languages:
        if string != "":
            if language == languages[-1]:
                if len(languages) > 2:
                    string += ","
                string += " and "
            else:
                string += ", "
        if language.startswith("telepathy"):
            string  += "T" + language[1:]
            if language.endswith("ft"):
                string += "."
        else:
            string += language.title()
    return string


def languages(langs):
    string = ""
    if len(langs) > 0:
        if langs[0] == "nospeak":
            string += "understands " + format_languages(langs[1:]) + " but cannot speak"
        else:
            string += format_languages(langs)
    else:
        string += "\\textbf{---}"
    return string


def senses(monster_senses, perception_bonus):
    string = ""
    if len(monster_senses) > 0:
        for sense in sorted(monster_senses):
            string += sense
            if sense.endswith("ft"):
                string += "."
            string += ", "
    string += "passive Perception " + str(10 + perception_bonus)
    return string


def create_spell(spell, include=False):
    string = ""
    if include:
        string += "\\textbf{" + spell["name"] + "}" + NEWLINE
    else:
        string += create_header(spell["name"])
    string += "\\textit{" + brand.format_index(int(spell["level"])) + "-level " + spell["school"].lower()
    if "ritual" in spell:
        string += ", ritual"
    string += "}" + NEWLINE
    string += "\\textbf{Casting Time:} " + spell["casting_time"] + NEWLINE
    string += "\\textbf{Range:} " + spell["range"] + NEWLINE
    string += "\\textbf{Components:} " + spell["components"] + NEWLINE
    string += "\\textbf{Duration:} " + spell["duration"] + NEWLINE
    if "classes" in spell:
        string += "\\textbf{Classes:} " + pp.comma_separate(spell["classes"]).title() + NEWLINE
    string += brand.eval_string(spell["effect"], {}) + NEWLINE
    if "higher_levels" in spell:
        string += entry("At Higher Levels", brand.eval_string(spell["higher_levels"], {}))
    return string


def create_item(item, include=False):
    string = ""
    if include:
        string += "\\textbf{" + item["name"] + "}" + NEWLINE
    else:
        string += create_header(item["name"])
    string += item["type"]
    if "tags" in item:
        string += " (" + pp.comma_separate(item["tags"]) + ")"
    string += ", " + item["rarity"]
    if "attunement" in item:
        string += " (requires attunement"
        if type(item["attunement"]) == str:
            string += item["attunement"]
        string += ")"
    string += NEWLINE + brand.eval_string(item["properties"], {})
    if "curse" in item:
        string += NEWLINE + entry("Curse", brand.eval_string(item["curse"], {}))
    if "destruction" in item:
        string += NEWLINE + entry("Destruction", brand.eval_string(item["destruction"], {}))
    return string


def create_monster(monster, title=True, addtoc=True, count=True):
    global ability_effects, monster_count

    if "trait_set" in monster:
        monster = pp.combine_dictionaries(monster, pp.open_yaml("trait_sets/" + monster["trait_set"] + ".yaml", show=False), [])

    if check_missing_fields(monster):
        return ""

    monster_string = ""
    header_name = pp.headername(monster)
    short_name = pp.shortname(monster)
    plainname = monster["name"]

    print("compiling", plainname)
    if count:
        monster_count += 1

    scores = monster["stats"]
    bonuses = pp.ability_scores_to_bonuses(scores)
    profbonus = pp.cr_to_prof(monster["cr"])

    params = {"name":short_name, "profbonus":profbonus}
    for ability in bonuses:
        params[ability] = bonuses[ability]

    if "params" in monster:
        for param in monster["params"]:
            params[param] = monster["params"][param]
    monster_string += create_header(header_name, title=title, addtoc=addtoc)

    if "flavor" in monster and type(monster["flavor"]) != type(None):
        monster_string += "\\textit{" + monster["flavor"] + "}" + NEWLINE + LINEBREAK

    if "description" in monster:
        monster_string += description(monster["description"], monster["type"], short_name) + LINEBREAK

    monster_string += "\\textbf{" + plainname.upper() + "}" + NEWLINE
    alignment = "unaligned"
    if "alignment" in monster:
        alignment = monster["alignment"]
    if "swarm" in monster:
        monster_string += "\\textit{" + monster["size"].title() + " Swarm of " + (monster["swarm"] + " " + monster["type"]).title() + "s"
        swarm_ability = ability_effects["Swarm"].replace("[name]", short_name).replace("[swarmsize]", monster["swarm"].title())
        if "abilities" in monster:
            swarm_override = False
            for ability in monster["abilities"]:
                if ability["name"] == "Swarm":
                    swarm_override = True
                    break
            if not swarm_override:
                monster["abilities"].append({"name":"Swarm", "effect":swarm_ability})
        else:
            monster["abilities"] = [swarm_ability]
    else:
        monster_string += "\\textit{" + (monster["size"] + " " + monster["type"]).title()
    if "tags" in monster:
        monster_string += " (" + pp.comma_separate(sorted(monster["tags"])) + ")"
    monster_string +=  ", " + alignment.title() + "}" + NEWLINE

    acbonus = 0
    acreasons = []
    if "ac" in monster:
        acbonus = monster["ac"][0]
        acreasons = monster["ac"][1:]
    monster_string += "\\textbf{Armor Class} " + ac(bonuses["dex"], acbonus, acreasons) + NEWLINE

    monster_string += "\\textbf{Hit Points} " + hitpoints(monster["hd"], monster["size"], bonuses["con"]) + NEWLINE

    monster_string += "\\textbf{Speed} " + speeds(monster["speed"]) + NEWLINE    

    monster_string += create_stat_table(scores, bonuses) + NEWLINE

    if "saves" in monster:
        monster_string += "\\textbf{Saving Throws} " + save_profs(monster["saves"], params) + NEWLINE

    perception_bonus = bonuses["wis"]
    if "skills" in monster:
        skills = skill_profs(sorted(monster["skills"]), params)
        perception_bonus = pp.get_key_if_exists(skills["dict"], "perception", bonuses["wis"])
        monster_string += "\\textbf{Skills} " + skills["string"] + NEWLINE

    if "vulnerable" in monster:
        monster_string += "\\textbf{Damage Vulnerabilities} " + dmg_attributes(monster["vulnerable"]) + NEWLINE

    if "resist" in monster:
        monster_string += "\\textbf{Damage Resistances} " + dmg_attributes(monster["resist"]) + NEWLINE

    if "immune" in monster:
        monster_string += "\\textbf{Damage Immunities} " + dmg_attributes(monster["immune"]) + NEWLINE

    if "cond-immune" in monster or monster["type"] in tables.DEFAULT_IMMUNITIES:
        monster_string += "\\textbf{Condition Immunities} "
        monster_string += cond_immunities(pp.get_key_if_exists(monster, "cond-immune", []), monster["type"]) + NEWLINE

    monster_string += "\\textbf{Senses} " + senses(pp.get_key_if_exists(monster, "senses", []), perception_bonus) + NEWLINE
    
    monster_string += "\\textbf{Languages} " + languages(pp.get_key_if_exists(monster, "languages", [])) + NEWLINE

    monster_string += "\\textbf{Challenge} " + brand.cr(monster["cr"]) + NEWLINE + LINEBREAK

    if "abilities" in monster:
        monster_string += abilities(monster["abilities"], params)

    if "innate-spellcasting" in monster:
        monster_string += innate_spellcasting(monster["innate-spellcasting"], params)
        monster_string += LINEBREAK
    
    if "spellcasting" in monster:
        ability = monster["spellcasting"]
        monster_string += spellcasting(ability["type"], ability["level"], ability["spells"], params)
        monster_string += LINEBREAK
    
    if "attacks" in monster or "actions" in monster:
        monster_string += partition("Actions") + MULTIATTACK_SPLICE_KEY

    if "attacks" in monster:
        attack_name_dict = {}
        for attack in monster["attacks"]:
            attack_name_dict[attack["name"]] = attack
        for attack_name in sorted(attack_name_dict):
            monster_string += create_attack(attack_name_dict[attack_name], params) + LINEBREAK

    if "actions" in monster:
        action_name_dict = {}
        for action in monster["actions"]:
            if action["name"] == "Multiattack":
                monster_string = monster_string.replace(
                    MULTIATTACK_SPLICE_KEY,
                    format_actions([action], params)
                )
                monster["actions"].remove(action)
                break
        monster_string += format_actions(monster["actions"], params)

    if "reactions" in monster:
        monster_string += reactions(monster["reactions"], params)
    
    if "legendary-actions" in monster:
        monster_string += legendary_actions(monster["legendary-actions"], params)
    
    if "variants" in monster:
        monster_string += variants(monster["variants"], params)

    if "lair" in monster:
        monster_string += lair(monster["lair"], params)
    
    monster_string += "\\label{End " + header_name + "}"
    
    add_to_appendices(monster)
    return monster_string


def add_to_appendices(monster):
    monstername = pp.headername(monster)
    if "habitat" in monster and type(monster["habitat"][0]) != type(None):
        for region in monster["habitat"]:
            if region in monsters_by_habitat:
                monsters_by_habitat[region].append(monstername)
            else:
                monsters_by_habitat[region] = [monstername]
    elif "any" in monsters_by_habitat:
        monsters_by_habitat["any"].append(monstername)
    else:
        monsters_by_habitat["any"] = [monstername]

    monster_plural = tables.MONSTER_TYPE_PLURALS[monster["type"]]
    if monster_plural in monsters_by_type:
        monsters_by_type[monster_plural].append(monstername)
    else:
        monsters_by_type[monster_plural] = [monstername]
    monster_cr = pp.cr_to_digit(monster["cr"])
    if monster_cr in monsters_by_cr:
        monsters_by_cr[monster_cr].append(monstername)
    else:
        monsters_by_cr[monster_cr] = [monstername]


def resolve_group(group, monsters):
    global errors, monster_count
    addtoc = group["headers"]["toc"]
    title = "title" in group["headers"] and group["headers"]["title"] == "monster"
    group_string = create_header(pp.headername(group), label=False, addtoc=addtoc=="group")
    if "flavor" in group:
        group_string += "\\textit{" + group["flavor"] + "}" + NEWLINE + LINEBREAK

    if "description" in group:
        group_type = pp.get_key_if_exists(group, "type", "")
        group_shortname = pp.shortname(group)
        group_string += description(group["description"], group_type, group_shortname, include_default=not title) + LINEBREAK

    monster_dict = {}
    if "sorttype" in group:
        if group["sorttype"] == "alphabetical":
            for monster in monsters:
                monster_dict[pp.headername(monster)] = monster
        elif group["sorttype"] == "index":
            for monster in monsters:
                if monster["sortindex"] in monster_dict:
                    errors.append("duplicate indicies in group " + group["name"])
                else:
                    monster_dict[monster["sortindex"]] = monster
        
    if "collapse_group_count" in group:
        monster_count += 1
    
    for index in sorted(monster_dict):
        group_string += create_monster(
            pp.combine_dictionaries(monster_dict[index], group, tables.GROUP_ATTRIBUTES_NOT_TO_COPY),
            title=title,
            addtoc=addtoc=="monster",
            count=not "collapse_group_count" in group
        )

    if "lair" in group:
        group_string += lair(group["lair"], {"name":group["name"]})
    
    return "\\clearpage" + group_string


def create_appendix_table(table, header):
    string = create_header(header, label=False)
    for section in sorted(table):
        section_name = section
        if type(section) != str:
            # assume it's a CR table
            section_name = "Challenge Rating " + pp.cr_to_string(section)
        string += "\\textbf{" + section_name.title() + "}" + NEWLINE
        for entry in sorted(table[section]):
            string += entry + "\\hfill p.\\pageref{" + entry + "}" + NEWLINE
        string += LINEBREAK
    return string


def add_contents_line(contents_item):
    return "\\addcontentsline{toc}{section}{" + contents_item + "}"


def create_appendices():
    global appendicies
    string = add_contents_line("Appendicies")
    for appendix_name in appendicies:
        string += create_appendix_table(appendicies[appendix_name], appendix_name) + PAGEBREAK
    return string


def create_monster_block():
    string = ""

    monster_name_dict = {}
    group_name_map = {}
    for group in pp.get_yaml_from_directory("groups"):
        monster_name_dict[pp.headername(group)] = [group]
        group_name_map[group["name"]] = pp.headername(group)
    
    for monster in pp.get_yaml_from_directory(SOURCE_YAML_DIRECTORY):
        monstername = pp.headername(monster)
        if "group" in monster:
            monster_name_dict[group_name_map[monster["group"]]].append(monster)
        else:
            monster_name_dict[monstername] = monster

    current_alphabet_letter = ""
    for monster_name in sorted(monster_name_dict):
        if monster_name[0] != current_alphabet_letter:
            current_alphabet_letter = monster_name[0]
            string += add_contents_line(current_alphabet_letter)
        if type(monster_name_dict[monster_name]) == list:
            group = monster_name_dict[monster_name]
            string += resolve_group(group[0], group[1:]) + PAGEBREAK
            continue
        monster = monster_name_dict[monster_name]

        pagebreak = PAGEBREAK
        if "one_column" in monster:
            pagebreak = "\n\\newpage\n"
        string += pagebreak + create_monster(monster)
    
    add_appendix("Monsters by Challenge Rating", monsters_by_cr)
    add_appendix("Monsters by Habitat", monsters_by_habitat)
    add_appendix("Monsters by Type", monsters_by_type)

    return string


def compile_document():
    start = time()
    framework = open("tex/framework.tex", "r")
    target = open("document.tex", "w")

    for line in framework.readlines():
        if line == "%monsters\n":
            target.write(create_monster_block())
        elif line == "%appendicies\n":
            target.write(create_appendices())
        else:
            target.write(line)
    
    target.close()
    framework.close()

    for error in errors:
        print("ERROR: ", error)
    print(monster_count, "monsters total, compiled in", str(time() - start)[0:5], "seconds")


brand.include_functions["spell"] = lambda filename: create_spell(pp.open_yaml(filename), include=True)
brand.include_functions["item"] = lambda filename: create_item(pp.open_yaml(filename), include=True)
ability_effects = pp.open_yaml("abilities.yaml")
compile_document()
