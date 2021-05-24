import requests
from bs4 import BeautifulSoup
import parse_input
import sys
import tournament_status
import os
from write_round_scores import find_round_files
import create_tournament_directory
import glob
import verify_entries
from write_round_scores import read_round_file,get_latest_round_file,\
                               find_round_files
from results_tools import running_total,sort_running_total,write_results,\
                          write_contestant_player_scores

#Parse inputs
htmlSource,eventName,outputDir,nplayers_cut=\
        parse_input.parse_input("input.txt")

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

#Print some information
print("*******************************************************************")
print(" Calculating contestant results for: {}".format(eventName))
print(" Through rounds: {}".format(rounds_completed))
print("*******************************************************************")

#First see if the entries were verified, if not, do not continue
if not os.path.exists("contestants/verified"):
   print("Contestants entries were not verified, will not continue...")
   sys.exit()

#Copy the entry files to the entries directory 
if len(glob.glob(outputDir+"/entries/entries*.txt")) == 0:
   print("No entry files copied over yet to {}, copying...".format(outputDir+"/entries"))
   contestants_dict = verify_entries.read_contestants("contestants/contestants.txt")
   for contestant in contestants_dict.keys():
      print("   copying contestant: {}".format(contestant)) 
      print("cp entries/entries_{}.txt {}/entries".format(contestants_dict[contestant],outputDir))
      os.system("cp entries/entries_{}.txt {}/entries".format(contestants_dict[contestant],outputDir))

#Make sure that their are outputfiles for at least all the rounds that have
# been completed
for iround in range(rounds_completed):
   round_files = find_round_files(eventName,outputDir+"/scores",iround+1)
   if len(round_files) == 0:
      print("No round output files for round: {}, Try running main_scores.py again".format(iround+1))
      sys.exit()
   
entry_dir = outputDir+"/entries"

#Initialize dictionary for each contestant with their running score total
contestants_dict = verify_entries.read_contestants("contestants/contestants.txt")
contestants = list(contestants_dict.keys())
contestant_rounds_dict = {}

#Loop through the rounds
for iround in range(rounds_completed):
   
   print("Working on results for Round {}".format(iround+1))

   contestant_round_dict = { contestant:0 for contestant in contestants_dict.keys() }
   #Read in round scores for this round
   round_files = find_round_files(eventName,outputDir+"/scores",iround+1)
   round_file = get_latest_round_file(outputDir+"/scores",eventName,round_files,iround+1)
   round_dict = read_round_file(round_file)

   #Loop through each contestant
   for contestant in contestants:
#   for contestant in contestants_dict.keys():
      print("  Working on contestant: {}".format(contestant))      
     
      #Get the contestants players
      entries = verify_entries.read_entries(entry_dir+"/entries_{}.txt".format(contestants_dict[contestant]))
      contestant_scores_iround = []
      
      #Loop through the contestants players and make a list of their scores
      for entry in entries:
         entry_score = round_dict[entry]["TO PAR"]
         contestant_scores_iround.append(entry_score)

      #Save the original scores before cutting any out for writting 
      org_scores = contestant_scores_iround

      #Remove "CUT", "DQ", or "WD"
      if "CUT" in contestant_scores_iround:
         contestant_scores_iround = \
           [ item for item in contestant_scores_iround if item != "CUT"]
      if "DQ" in contestant_scores_iround:
         print("*****WARNING*******: contestant: {} has a DQ'd player in round: {}".format(contestant,iround+1))
         contestant_scores_iround = \
           [ item for item in contestant_scores_iround if item != "DQ"]
      if "WD" in contestant_scores_iround:
         print("*****WARNING*******: contestant: {} has a WD'd player in round: {}".format(contestant,iround+1))
         contestant_scores_iround = \
           [ item for item in contestant_scores_iround if item != "WD"]

      #Write each contestants player's scores to file for this round
      write_contestant_player_scores(outputDir+"/pool_results",contestants_dict[contestant],iround+1,entries,org_scores)
 
      #If less than "nplayers_cut" make the cut/ DQ/ WD, the contestant is "cut"
      if len(contestant_scores_iround) < nplayers_cut:
         this_round_total = "CUT"
      else:
         #Otherwise, sort the scores and take the sum of the best 5
         this_round_total = sum(sorted(contestant_scores_iround)[0:5])
      
      #Update round total for the contestant
      contestant_round_dict[contestant] = this_round_total
      
   #At the end of each round, add all the contestants to a higher dict
   contestant_rounds_dict.update({iround+1:contestant_round_dict})
 
#Write results in the "pool_results" file
contestant_name_len = max([ len(name) for name in contestants ])
for iround in range(rounds_completed):

   #Get running total (have to watch out for Cuts)
   running_total_iround = running_total(contestant_rounds_dict,iround+1)

   #sort dict based on running total (again watch out for cuts)
   running_total_iround_sorted = sort_running_total(running_total_iround)

   #Write them out for each round, for each round, the contestants are written based on who is winning after that round
   write_results(eventName,outputDir+"/pool_results",contestants,contestant_rounds_dict,running_total_iround_sorted,iround+1,contestant_name_len)


