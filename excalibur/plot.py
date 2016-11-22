# -*- coding: utf-8 -*-

import tracery
from nltk.parse.generate import generate, demo_grammar
from nltk import CFG
from tracery.modifiers import base_english
import random


rules = {
    'origin': '#hello.capitalize#, #location#!',
    'hello': ['hello', 'greetings', 'howdy', 'hey'],
    'location': ['world', 'solar system', 'galaxy', 'universe']
}

macguffins = {}


grammar = tracery.Grammar(rules)
grammar.add_modifiers(base_english)
print(grammar.flatten("#origin#")) # prints, e.g., "Hello, world!"



plot_grammar = CFG.fromstring("""
have_need -> introduce_need new_solution fulfill_need
new_solution -> introduce_solution solution_hunt perform_solution
solution_hunt -> new_solution new_solution combine_solutions | solution_hunt_failure solution_hunt_success | solution_hunt_success
solution_hunt_failure -> "EVENT_SOLUTION_HUNT_FAILURE"
fulfill_need -> "EVENT_FULFILL_GOAL"
introduce_need -> "EVENT_INTRODUCE_NEED"
introduce_solution -> "EVENT_INTRODUCE_SOLUTION"
introduce_complication -> "EVENT_INTRODUCE_COMPLICATION"
combine_solutions -> "EVENT_COMBINE_SOLUTIONS"
solution_hunt_success -> "EVENT_SOLUTION_SUCCESS"
perform_solution -> "EVENT_PERFORM_SOLUTION"

""")

tracery_plot_rules = {
#'plot':['status_quo', 'instigating_event', 'rising_action', 'climax', 'denoument']
"plot": "#have_need#",
"have_need": "#introduce_need# #new_solution# #fulfill_need#",
"new_solution": "#introduce_solution# #hunt_solution#",
"perform_solution": "EVENT_PERFORM_SOLUTION",
"introduce_solution": "EVENT_INTRODUCE_SOLUTION",
"introduce_need": "EVENT_INTRODUCE_NEED",
"hunt_solution": ["#obstacle# #find_solution# #perform_solution#", "#obstacle_fail# #fail_solution# #new_solution#"],
"find_solution": "EVENT_FIND_SOLUTION",
"fail_solution": "EVENT_FAIL_SOLUTION",
"obstacle": "EVENT_OBSTACLE",
"obstacle_fail": "EVENT_OBSTACLE_FAIL",
"fulfill_need": "EVENT_FULFILL_NEED",
"character_arc": ["#character_arc_growth#", "#character_arc_growth_flashback"],
"character_arc_growth": "#introduce_character# #character_first_act# #character_second_act# #character_third_act#",
"character_arc_growth_flashback": "#introduce_character# #character_second_act# #character_flashback_act# #character_third_act#",
"character_flashback_act": "#character_status_quo_flashback# #character_i_want_flashback# #character_inciting_incident_flashback# #character_i_want#",
"character_first_act": ["#character_status_quo# #character_i_want# #character_inciting_incident#", "#character_status_quo# #character_inciting_incident# #character_i_want#"],
"character_third_act": "#character_plot_revelation# #character_climax# #character_denoument# #character_epilog#",
"character_second_act": ["#character_plot_point# #character_in_trouble# #character_mid_point# #character_in_trouble#", "#character_plot_point# #character_in_trouble# #character_i_want# #character_mid_point# #character_in_trouble#"],
"introduce_character": "EVENT_INTRODUCE_CHARACTER",
"character_in_trouble": "EVENT_CHARACTER_IN_TROUBLE",
"character_mid_point": "EVENT_CHARACTER_MID_POINT",
"character_plot_revelation": "EVENT_CHARACTER_PLOT_REVELATION",
"character_denoument": "EVENT_CHARACTER_DENOUMENT",
"character_climax": "EVENT_CHARACTER_CLIMAX",
"character_epilog": "EVENT_CHARACTER_EPILOGUE",
"character_status_quo": "EVENT_CHARACTER_STATUS_QUO",
"character_i_want": "EVENT_CHARACTER_I_WANT",
"character_inciting_incident": "EVENT_CHARACTER_INCITING_INCIDENT",
"character_status_quo_flashback": "EVENT_CHARACTER_STATUS_QUO_FLASHBACK",
"character_i_want_flashback": "EVENT_CHARACTER_I_WANT_FLASHBACK",
"character_inciting_incident_flashback": "EVENT_CHARACTER_INCITING_INCIDENT_FLASHBACK",
"character_plot_point": "EVENT_CHARACTER_PLOT_POINT",
}



#for s in generate(plot_grammar, n=1, depth=14):
#    print(s)

#print(list(generate(plot_grammar, depth = 5)))

g = tracery.Grammar(tracery_plot_rules)
g.add_modifiers(base_english)
arcA = (g.flatten("#have_need#")).split(" ")
arcB = (g.flatten("#character_arc_growth#")).split(" ")
arcC = (g.flatten("#character_arc_growth#")).split(" ")

arcB = [i + "_CHARONE" for i in arcB]
arcC = [i + "_CHARTWO" for i in arcC]

def combine_plots(arc1, arc2):
    plot_arc = []
    consume_counter = len(arc1) + len(arc2)
    cidx1 = 0
    cidx2 = 0
    chance = len(arc1) / consume_counter
    while consume_counter > 0:
        if cidx1 >= len(arc1):
            plot_arc.extend(arc2[cidx2:])
            return plot_arc
        else:
            if cidx2 >= len(arc2):
                plot_arc.extend(arc1[cidx1:])
                return plot_arc
            else:
                if random.random() < chance:
                    plot_arc.append(arc1[cidx1])
                    cidx1 += 1
                else:
                    plot_arc.append(arc2[cidx2])
                    cidx2 += 1
        consume_counter -= 1
    print(plot_arc)
    return plot_arc
    
combo = combine_plots(arcB, arcC)
overall = combine_plots(arcA, combo)
print(overall)