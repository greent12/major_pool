import datetime as dt
from pull_pga import *
import requests
from bs4 import BeautifulSoup
import json
import datetime as dt
import parse_input
import sys
import tournament_status
import create_tournament_directory
import print_info
import write_round_scores
import get_players
import verify_entries
import os
from wgr import get_wgr,get_key

#The purpose of this script is to make sure there are no
# conflicts with the contestants entries for the tournament
# By contestants I mean the actualy people who have entered
# the golf pool, and by entries I mean the players in the tournament 
# they have selected 

#The steps will be as follows: 
# 1: Read in the contestants file which will be located in:
#    PGALiveLeaderboard/contestants and be named 'contestants.txt'
#    This will give a dictionary of the actualy 'long' name of 
#    each contestant and their 'short' name. The short name
#    will be used to search for their entry file, for example if the
#    contestant's name is 'Aaron' then the short name would be 'aaron'
#    and their entry file would be located in PGALiveLeaderboard/entries
#    the entry file will hold a list of players they have selected
# Each contestant will now be looped through and the following will happen
# 2: Make sure that they have an actual file in the 'entries' directory
#    and if not record that error
# 3: Read their entries into a list
# 4: Make sure their entries are in the WRG, this step is mainly for making 
#    sure their names are spelled correctly. If their are entries that are not in#    the WGR this does not not necisarily mean the player's name is spelled 
#    incorectly but might mean they are old and not ranked like some of the 
#    older players who still continue to play in the Masters. If the entry is 
#    not in WGR, it will print it to the output file as flagged but will
#    not count it as a descrepency.
# 5: Make sure that the each entry is in the tournament. For this it will 
#    get the list of players in the tournament form ESPN (this could be 
#    tournament specific in the future) and make sure that each entry is 
#    there. If the name is not it will count as a descrepency.
# 6: Print details of how man descrepancies there were 
# If it is ok to continue to the calculating scores step, a file will be created in the "contestants" directory called "verified"

#########################################################
# PREPROCESSING
#########################################################

#Parse inputs
html_source,eventName,outputDir,_\
       = parse_input.parse_input("input.txt")

#Get current time for outputting scores
now = dt.datetime.now()
datestr = now.strftime("%Y%m%d_%H_%M")

#Parse HTML code 
result = requests.get(html_source)
soup = BeautifulSoup(result.text, "html.parser")

#Verify we have the right tournament
eventNameHTML=tournament_status.get_tournament_name(soup)
if not eventName == eventNameHTML:
   print("The event name given in 'inputs.txt' does not match Web data... exitting.")
   sys.exit()

#Get the players in the tournament
players = get_players.get_tournament_players(soup)

#Get WGR
wgr_dict = get_wgr()

#Read contestants long and short names into dictionary
contestants_dict = verify_entries.read_contestants("contestants/contestants.txt")

#Open a file for descrepancies to write to and start a tally
f_discrep = open("contestants/discrepancies.txt","w")
n_discrep = 0

#Loop through contestants
for contestant in contestants_dict.keys():

   #Check for entry file, if it doesn't exist add to descrepancies and cycle the loop
   short_name = contestants_dict[contestant]
   if not os.path.exists("entries/entries_{}.txt".format(short_name)):
      f_discrep.write("Contestant: {} does not have an entry file: {}\n".format(contestant,"entries_{}.txt".format(short_name)))
      n_discrep+=1
      continue

   #Check entries in each contestants file
   entries = verify_entries.read_entries("entries/entries_{}.txt".format(short_name))
   
   #Do WRG check and write conflicts to discrepencies if there are any
   there_are_conflicts,conflicts = \
       verify_entries.verify_with_wgr(entries,wgr_dict)

   if there_are_conflicts:
      print("WARNING: Contestant: {}, file: {}, wgr conflicts:".format(contestant,"entries_{}.txt".format(short_name)))
      for conflict in conflicts:
         print("   ",conflict)

   #Check with contestants in tournament, discrepancies here will count 
   there_are_conflicts,conflicts = \
    verify_entries.verify_entries_with_tournament_players(entries,players)
   n_discrep = n_discrep + len(conflicts)

   if there_are_conflicts:
      line_to_write = "Contestant: {}, file: {}, tournament entry conflicts:\n".format(contestant,"entries_{}.txt".format(short_name))
      f_discrep.write(line_to_write)
      for conflict in conflicts:
         line_to_write="   "+conflict+"\n"
         f_discrep.write(line_to_write)
     
f_discrep.close()

#If there were no discrepancies, go ahead and remove the file
if n_discrep == 0:
   os.remove("contestants/discrepancies.txt")
   os.system("touch contestants/verified")
   print("No discrepancies, removing contestants/discrepancies.txt")
else:
   print("THERE WERE {} CONFLICTS FOUND WITH CONTESTANT ENTRIES\nDO NOT CONTINUE UNTIL THEY ARE FIXED".format(n_discrep))
