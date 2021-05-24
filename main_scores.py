import datetime as dt
from pull_pga import *
import requests
from bs4 import BeautifulSoup
import datetime as dt
import parse_input
import sys
import tournament_status
import create_tournament_directory
import print_info
import write_round_scores

#########################################################
# PREPROCESSING
#########################################################

#Parse inputs
htmlSource,eventName,outputDir,_\
      = parse_input.parse_input("input.txt")

#Get current time for outputting scores
now = dt.datetime.now()

#Parse HTML code 
result = requests.get(htmlSource)
soup = BeautifulSoup(result.text, "html.parser")

#Verify we have the right tournament
eventNameHTML=tournament_status.get_tournament_name(soup)
if not eventName == eventNameHTML:
   print("The event name given in 'inputs.txt' does not match Web data... exitting.")
   sys.exit()

#Create tournament directory and get modified tournament name
eventName,outputDir=create_tournament_directory.create_dir(eventNameHTML,outputDir)

#Get par for the course
par = tournament_status.get_par(soup)

#Check tournament status, get the rounds completed and if we're live or not
rounds_completed,live=tournament_status.check_status(soup)

#Print information
print_info.print_info(now,eventName,outputDir+"/scores",par,rounds_completed,live)

#Collect round info
round_dict=process_completed_rounds(soup,rounds_completed,par,outputDir)

#Write round output
write_round_scores.write_round_scores(eventName,outputDir+"/scores",round_dict)

