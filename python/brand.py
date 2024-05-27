# BRAND CORE v.1.1.0
# additional module: 5e v.1.0.0

from math import floor
import os

FUNCTIONS_REQUIRING_EXTRA_PARAMETERS = {"save":["profbonus"], "opposedcheck":["profbonus"]}
AUTOMATIC_VARIABLES = ["str", "dex", "con", "int", "wis", "cha"]
NEWLINE = "\\\\"
LINEBREAK = "\\bigskip"
include_functions = {}
ABILITIES_SPELLOUT = {
    "str":"Strength",
    "dex":"Dexterity",
    "con":"Constitution",
    "int":"Intelligence",
    "wis":"Wisdom",
    "cha":"Charisma"
}
SKILL_ABILITY = {
    "athletics":"str",
    "acrobatics":"dex",
    "sleight of hand":"dex",
    "stealth":"dex",
    "arcana":"int",
    "history":"int",
    "investigation":"int",
    "nature":"int",
    "religion":"int",
    "animal handling":"wis",
    "insight":"wis",
    "medicine":"wis",
    "perception":"wis",
    "survival":"wis",
    "deception":"cha",
    "intimidation":"cha",
    "performance":"cha",
    "persuasion":"cha"
}
SKILL_PRETTYNAME = {
    "athletics":"Athletics",
    "acrobatics":"Acrobatics",
    "sleight of hand":"Sleight of Hand",
    "stealth":"Stealth",
    "arcana":"Arcana",
    "history":"History",
    "investigation":"Investigation",
    "nature":"Nature",
    "religion":"Religion",
    "animal handling":"Animal Handling",
    "insight":"Insight",
    "medicine":"Medicine",
    "perception":"Perception",
    "survival":"Survival",
    "deception":"Deception",
    "intimidation":"Intimidation",
    "performance":"Performance",
    "persuasion":"Persuasion"
}
CR_TO_XP = {
    0:"10",
    "1/8":"25",
    "1/4":"50",
    "1/2":"100",
    1:"200",
    2:"450",
    3:"700",
    4:"1,100",
    5:"1,800",
    6:"2,300",
    7:"2,900",
    8:"3,900",
    9:"5,000",
    10:"5,900",
    11:"7,200",
    12:"8,400",
    13:"10,000",
    14:"11,500",
    15:"13,000",
    16:"15,000",
    17:"18,000",
    18:"20,000",
    19:"22,000",
    20:"25,000",
    21:"33,000",
    22:"41,000",
    23:"50,000",
    24:"62,000",
    25:"75,000",
    26:"90,000",
    27:"105,000",
    28:"120,000",
    29:"135,000",
    30:"155,000",
}


# returns in the form of "result (dice + bonus)"
def roll(num, size, *bonuses):
    total_bonus = 0
    for bonus in bonuses:
        total_bonus += bonus
    total = floor(num * (size / 2 + 0.5)) + total_bonus
    string = str(total) + " (" + str(num) + "d" + str(size)
    if total_bonus != 0:
        if total_bonus > 0:
            string += " + "
        else:
            string += " - "
        string += str(abs(total_bonus))
    return string + ")"


def index_plural(num, *name):
    name = _separate(name)
    string = str(num) + " " + name
    if num != 1:
        if name[-2:] in ["sh", "ch", "x"]:
            return string + "es"
        elif name[-1] in ["s", "z"]:
            if name[-2] == name[-1]:
                return string + "es"
            return string + name[-1] + "es"
        return string + "s"
    return string


# adds all the inputs and returns them as a string
def sum(*numbers):
    total = 0
    for number in numbers:
        total += number
    return str(total)


# returns the name with the proper indefinite article prefixed to it
def articulate(capitalized, *name):
    name = _separate(name)
    string = "a"
    if name[0].lower() in ["a", "e", "i", "o", "u"]:
        string += "n"
    if capitalized:
        string = string.title()
    return string + " " + name


# returns spellname in italics
def spell(*spellname):
    return "\\textit{" + _separate(spellname) + "}"


# returns monster name in bold
def monster(*monstername):
    return "\\textbf{" + _separate(monstername) + "}"


# bolds input
def bold(*stuff):
    return "\\textbf{" + _separate(stuff) + "}"


# italicizes input
def italics(*stuff):
    return "\\textit{" + _separate(stuff) + "}"


# makes input bold and italic
def bolditalics(*stuff):
    return "\\textbf{\\textit{" + _separate(stuff) + "}}"


# collects all parameters as a brand-recognized string group
def bind(*stuff):
    return "<" + _separate(stuff) + ">"


# returns a table mapping the roll of a die to ampersand-separated entries
def dicetable(diesize, title, *entries):
    final_entries = ["1d" + str(diesize), "&", title, "&", 1, "&"]
    die_index = 1
    for item in entries:
        final_entries.append(item)
        if item == "&":
            die_index += 1
            final_entries.append(die_index)
            final_entries.append("&")
    return table("cX", final_entries)


# creates a table based on given columns and ampersand-separated entries
def table(cols, *entries):
    if type(entries[0]) == list:
        entries = entries[0]
    tablestring = NEWLINE + "\\bigskip\\begin{tabular"
    if "X" in cols:
        tablestring += "x}{0.8\\columnwidth"
    tablestring += "}{|"
    for char in cols:
        tablestring += char + "|"
    tablestring += "}\\hline "
    line_count = 0
    for item in entries:
        if item == "&":
            line_count += 1
            if line_count < len(cols):
                tablestring += "&"
            else:
                tablestring += NEWLINE + "[2pt]\\hline "
                line_count = 0
        else:
             tablestring += str(item) + " "
    tablestring += NEWLINE + "\\hline\\end{tabular"
    if "X" in cols:
        tablestring += "x"
    return tablestring + "}"


# returns a bulleted list of items
def bulletlist(*items):
    return NEWLINE + "\\begin{itemize}" + _get_list_body(items) + "\\end{itemize}"


# returns a numbered list of items 
def numberlist(*items):
    return NEWLINE + "\\begin{enumerate}" + _get_list_body(items) + "\\end{enumerate}"


# internal function that takes a list and returns it as a list for LaTeX
def _get_list_body(items):
    list_body = ""
    entry = ""
    for item in items:
        if item == "&":
            list_body += "\\item " + entry
            entry = ""
        else:
            entry += str(item) + " "
    return list_body + "\\item " + entry


# Return array as string with each item separated by a given sequence
def _separate(array, spacer=" "):
    string = ""
    for item in array:
        if string != "":
            string += spacer
        string += str(item)
    return string


# Returns a number as a string with proper sign indication
def format_bonus(bonus):
    if bonus >= 0:
        return "+" + str(bonus)
    else:
        return str(bonus)


# returns string of number with proper ordinary suffix
def format_index(index):
    index = str(index)
    if not (len(index) == 2 and index[0] == "1"):
        if index[-1] == "1":
          return index + "st"
        elif index[-1] == "2":
          return index + "nd"
        elif index[-1] == "3":
            return index + "rd"
    return index + "th"


# returns string with proper possessive suffix
def possessive(*name):
    name = _separate(name)
    if name[-1] == "s":
        return name + "'"
    else:
        return name + "'s"


def include(include_type, filename):
    global include_functions
    if include_type in include_functions:
        return "\\begin{quote}" + include_functions[include_type](filename) + "\\end{quote}"
    return ""


def percent():
    return "\\%"


def newline():
    return NEWLINE


# builds and executes function from bracketed command string
def _format_and_execute(field, params):
    if field in params:
        return eval_string(str(params[field]), params)

    formatted_field = ""
    in_function_body = False
    in_string_block = False
    arg_text = ""
    function_name = ""
    # the extra space at the end of field causes the last argument to be processed
    for char in field + " ":
        if char == "<":
            in_string_block = True
        elif char == ">":
            in_string_block = False
        elif char == " " and not in_string_block:
            if in_function_body:
                if formatted_field[-1] != "(":
                    formatted_field += ", "
                if arg_text in AUTOMATIC_VARIABLES:
                    arg_text = eval_string(str(params[arg_text]), params)
                elif arg_text in ["t", "T", "true", "True"]:
                    arg_text = "True"
                elif arg_text in ["f", "F", "false", "False"]:
                    arg_text = "False"
                elif not arg_text.isdigit():
                    arg_text = "\"" + arg_text + "\""
                formatted_field += arg_text
                arg_text = ""
            else:
                formatted_field += "("
                in_function_body = True
        else:
            if in_function_body:
                arg_text += char
            else:
                formatted_field += char
                function_name += char
    if function_name in FUNCTIONS_REQUIRING_EXTRA_PARAMETERS:
        for param_name in FUNCTIONS_REQUIRING_EXTRA_PARAMETERS[function_name]:
            if formatted_field[-1] != "(":
                formatted_field += ", "
            formatted_field += eval_string(str(params[param_name]), params)
    return eval(formatted_field + ")")


# processes a string to extract and execute all bracketed command sequences
def eval_string(string, params):
    updated_string = ""
    field = ""
    field_started = False
    indentation_level = 0
    nested = False
    for char in string:
        if char == "[":
            if field_started:
                indentation_level += 1
                nested = True
                field += "["
            else:
                field_started = True
        elif char == "]":
            if indentation_level > 0:
                indentation_level -= 1
                field += "]"
            else:
                field_started = False
                if nested:
                    field = eval_string(field, params)
                updated_string += _format_and_execute(field, params)
                field = ""
                nested = False
        elif field_started:
            field += char
        else:
            updated_string += char
    return updated_string


# returns CR with XP value
def cr(cr):
    return str(cr) + " (" + CR_TO_XP[cr] + " XP)"


# returns in the form of "DC challenge Ability (Skill) check"
def check(dc, *skill):
    skill = _separate(skill)
    return "DC " + str(dc) + " " + ABILITIES_SPELLOUT[SKILL_ABILITY[skill]] + " (" + SKILL_PRETTYNAME[skill] + ") check"


# similar to the save function, but with a skill
def opposedcheck(ability, abilitybonus, profbonus):
    dc = 8 + abilitybonus + profbonus
    ability_name = ""
    if ability != "w/none":
        ability_name = ABILITIES_SPELLOUT[ability[2:]] + " "
    return "DC " + str(dc) + " " + ability_name + "check"


# returns in the form of "DC challenge Ability saving throw"
def save(ability, abilitybonus, profbonus):
    dc = 8 + abilitybonus + profbonus
    ability_name = ""
    if ability != "w/none":
        ability_name = ABILITIES_SPELLOUT[ability[2:]] + " "
    return "DC " + str(dc) + " " + ability_name + "saving throw"


# returns in the form of "DC challenge Ability saving throw"
def basicsave(ability, difficulty):
    ability_name = ""
    if ability != "w/none":
        ability_name = ABILITIES_SPELLOUT[ability[2:]] + " "
    return "DC " + str(difficulty) + " " + ability_name + "saving throw"


def _score_to_bonus(score):
    return floor(score / 2) - 5


# returns in the form of "score (bonus)"
def stat(score):
    return str(score) + " (" + format_bonus(_score_to_bonus(score)) + ")"