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
import verify_entries
import results_tools
import scipy.stats

def print_results(contestant_rounds_dict,running_total_iround,rounds_completed,contestant_columnw):

   #Get ranks in the running total dictionary
   running_total_scores = [ running_total_iround[player] for player in running_total_iround.keys() ]
   ranks = scipy.stats.rankdata(running_total_scores,method="min")

   #Format for the header line and write the header line
   contestant_part = "{:{:d}s}".format("Contestant",contestant_columnw+1)
   rounds_part = ("Round {} "*rounds_completed).format(*range(1,rounds_completed+1))
   total_part = "Total"
   rank_part = " Rank"
   header_line = contestant_part+rounds_part+total_part+rank_part
   seperator = "*"*len(header_line)
  
   print(seperator)
   print(header_line)
   print(seperator)

   #Loop through the contestants and write their scores for  
   for i,contestant in enumerate(running_total_iround.keys()):
      scores = []
      for iround in range(rounds_completed):
         scores.append(str(contestant_rounds_dict[iround+1][contestant]))

      firstpart = "{:>{:d}s}".format(contestant,contestant_columnw)
      secondpart = (" {:>7s}"*rounds_completed).format(*scores)
      thirdpart = " {:>5s}".format(str(running_total_iround[contestant]))
      fourthpart = "{:5d}".format(ranks[i])
      print(firstpart+secondpart+thirdpart+fourthpart)

#Parse inputs
htmlSource,eventName,outputDir,nplayers_cut=\
       parse_input.parse_input("input.txt")

#Get current time for outputting scores
now = dt.datetime.now()

#Parse HTML code 
result = requests.get(htmlSource)
soup = BeautifulSoup(result.text, "html.parser")

#Verify we have the right tournament
eventNameHTML=tournament_status.get_tournament_name(soup)

#Create tournament directory and get modified tournament name
eventName,outputDir=create_tournament_directory.create_dir(eventNameHTML,outputDir)

#Check tournament status, get the rounds completed and if we're live or not
rounds_completed,live=tournament_status.check_status(soup)
if rounds_completed == 4:
   print("4 rounds completed, cannot do live scoring")
   sys.exit()
thisround = rounds_completed + 1

#Get pool file for the amount of rounds completed
pool_dir = outputDir+"/pool_results"
pool_files = write_round_scores.find_round_files(eventName,pool_dir,rounds_completed)

if len(pool_files) == 0:
   print("No pool files were found for round {}, please run 'main_results.py' to get the updated pool.".format(rounds_completed))
   sys.exit()

pool_file = write_round_scores.get_latest_round_file(pool_dir,eventName,pool_files,rounds_completed)

#Get contestants
contestants_dict = verify_entries.read_contestants("contestants/contestants.txt")
contestants = list(contestants_dict.keys())
contestant_name_len = max([ len(name) for name in contestants ])

#Get the scores up to the round completed for all contestants
contestant_rounds_dict,running_total = results_tools.read_pool(pool_file,rounds_completed,contestant_name_len)

#If rounds completed is 2 or more, we'll have to account for contestants getting cut
scores_dir = outputDir+"/scores"
round_files = write_round_scores.find_round_files(eventName,scores_dir,rounds_completed)
round_file = write_round_scores.get_latest_round_file(scores_dir,eventName,round_files,rounds_completed)
round_dict = write_round_scores.read_round_file(round_file)

#Get the players scores today
players = get_today_scores(soup)

entry_dir = outputDir+"/entries"

contestant_round_dict = { contestant:0 for contestant in contestants_dict.keys() }
#Loop through contestants to put together their cores for the live round
for contestant in contestants:

   #Get the contestants players
   entries = verify_entries.read_entries(entry_dir+"/entries_{}.txt".format(contestants_dict[contestant]))
   contestant_scores_iround = []

   #Loop through the contestants players and make a list of their scores
   for entry in entries:
      entry_score = players[entry]['SCORE']
      try:
         contestant_scores_iround.append(int(entry_score))
      except:
         contestant_scores_iround.append(entry_score)

   #Remove "CUT", "DQ", or "WD"
   if "CUT" in contestant_scores_iround:
      contestant_scores_iround = \
        [ item for item in contestant_scores_iround if item != "CUT"]
   if "DQ" in contestant_scores_iround:
      contestant_scores_iround = \
        [ item for item in contestant_scores_iround if item != "DQ"]
   if "WD" in contestant_scores_iround:
      contestant_scores_iround = \
        [ item for item in contestant_scores_iround if item != "WD"]

   #See if contestant got cut
   if len(contestant_scores_iround) < nplayers_cut:
      this_round_total = "CUT"
   else:
      #If not cut, trim any "--" from their score which would represent players who might not have teed off yet
      if "-" in contestant_scores_iround:
         contestant_scores_iround = \
           [ item for item in contestant_scores_iround if item != "-" ]
      #Get the 5 best scores, if not 5, get the top however many scores
      if len(contestant_scores_iround) < 5:
         this_round_total = sum(contestant_scores_iround)
      elif len(contestant_scores_iround) == 0:
         this_round_total = 0
      else:
         this_round_total = sum(sorted(contestant_scores_iround)[0:5])
      

   #Update round total for the contestant
   contestant_round_dict[contestant] = this_round_total 

#Update the contestant roundSSSS dict with the live round
contestant_rounds_dict.update({thisround:contestant_round_dict})

#Get running total
running_total_thisround=results_tools.running_total(contestant_rounds_dict,thisround)

#Sort the running total
running_total_thisround_sorted = results_tools.sort_running_total(running_total_thisround)

print_results(contestant_rounds_dict,running_total_thisround_sorted,thisround,contestant_name_len)





