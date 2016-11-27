# -*- coding: utf-8 -*-

import character
import action_commands
import transcript
import book

protagonist = character.generatePirateShip()
antagonist = character.generateTheSea()
con = action_commands.Conflict(action_commands.actcat_ship_voyage, protagonist, antagonist)
for i in range(30):
    con.performActions()
    print(con.currentState())
    print("===")
    
script = con.outputTranscript()

output = transcript.compileTranscript(script)
output = transcript.makeTitlePageFromShip(script) + "\n" + output
print("*************\n*   Story   *\n*************\n")
print(output)
book.makeBook(output)