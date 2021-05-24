import sys
import datetime as dt
import numpy as np
import scipy.stats
from write_round_scores import find_round_files,get_latest_round_file,\
                               write_differences
import glob

def running_total(contestant_rounds_dict,rounds_completed):
   '''
    Calculate the running total for each contestant given the dictionary for all contestants with the rounds as the keys

   INPUTS: 
   1: contestant_rounds_dict : dict
        dictionary with keys of the rounds, and values being another dictionary
        with keys of contestant and values that are the scores for that round
   2: rounds_completed : int
        number of rounds that have been completed

   OUTPUTS:
   3: running_total_dict : dict
        dictionary with keys of contestant name and value is the running total
        for the number of rounds completed
   '''

   #Initialize running total dictionary
   running_total_dict = {}

   #Loop through contestants (for this to work, there must be round 1 info in the 'contestant_rounds_dict'
   for contestant in contestant_rounds_dict[1].keys():
      #get the scores for the contestant for each round through completed rounds
      contestant_scores = []
      for iround in range(rounds_completed):
         contestant_scores.append(contestant_rounds_dict[iround+1][contestant])

      #Account for "CUT" if the contestant was cut after round 2
      if "CUT" in contestant_scores:
         running_total = "CUT"
      else:
      #If not cut, total up the scores to this point
         running_total = sum(contestant_scores)

      #Update the running dictionary for this contestant
      running_total_dict.update({contestant:running_total})

   return running_total_dict

def sort_running_total(running_total_dict):

   '''
   Sort the running total dictionary created by the 'running_total' function
  
   INPUTS:
   1: runing_total_dict : dict
       dictionary with keys of the contestant, and values of their running total

   OUTPUTS:
   1: sorted_dict : dict
       the input dictionary that is sorted, with all contestants having a value
       'CUT' at the bottom in no particular order
   '''
   
   #Going to seperate the original dictionary into two different ones, for 
   # cut and not cut players
   nocut_dict = {}
   cut_dict = {} 

   #Loop through each contestant and sort them in either dictionary depending on
   # whether they were cut or not
   for contestant in running_total_dict.keys():
      if running_total_dict[contestant] == "CUT":
         cut_dict.update({contestant:running_total_dict[contestant]})
      else:
         nocut_dict.update({contestant:running_total_dict[contestant]})

   #Sort the contestants that were not cut, then merge that dictionary and the 
   # ones that were cut together and return
   nocut_dict_sorted = sort_dict(nocut_dict)
   nocut_dict_sorted.update(cut_dict)
   sorted_dict = nocut_dict_sorted

   return sorted_dict


def sort_dict(mydict):
   '''
   sort a dictionary by values, if they arent all the same type this is going to crash
   '''
   return {k: v for k, v in sorted(mydict.items(), key=lambda item: item[1])} 


def write_results(eventName,outputDir,contestants,contestant_rounds_dict,running_total_iround,rounds_completed,contestant_columnw):

   '''
   Take the contestant_rounds_dict and the running total dict and write the results for a specific round to an output file

   INPUTS: 
   1: evntName : str
       name of the event (without spaces or special characters)
   2: outputDir : str
       path to the 'pool_results' directory inside the event directory, this is
       where the output files for each round will be written
   3: contestant_rounds_dict : dict
       dictionary with keys of round and values of dict with keys contestant
       and values of their score for the round
   4: running_total_iround : dict
       dcitionary with keys of contestnat and values of running total up to total
       rounds completed
   5: rounds_completed : int
       the total rounds completed
   6: contestant_columnw : int
       length of the longest contestant name, needed for formatting file output

   OUTPUTS: No outputs

   NOTES: This will write all the scores up to the round completed, so for example, if you say rounds completed is 3, it will write a file with 5 columns, being the contestant name, rounds 1,2,& 3, and then the total. The total columns will be N+2 where N is the number of roundsd completed.

   It will look through the previous written files to make sure nothing has changed, if anything has, it will write out a new pool file and anothe file noting the differences
   '''

   #Time stamp for writing files
   now = (dt.datetime.now()).strftime("%Y%m%d_%H_%M") 

   #Name of the output file
   output_file = outputDir+ "/" + eventName + "_round_"+str(rounds_completed)+"_"+now+".txt"

   #Find files that might have already been written for this round
   prev_files = find_round_files(eventName,outputDir,rounds_completed)
  
   #If there were no previous files, go ahead and write them out  
   if len(prev_files) == 0:
      print("Round {} file does not exist yet, writting to: {}".format(rounds_completed,output_file))
      write_pool(output_file,contestant_rounds_dict,running_total_iround,rounds_completed,contestant_columnw)
   #If there were previous files, were going to go through them and verify
   # that the information we have now is the exact same as what is already
   # written, if it is not, were going to have to write a new file
   else:
      latest_file = get_latest_round_file(outputDir,eventName,prev_files,rounds_completed)
      print("Round {} file does already exist, but will check for differences in the latest file {}".format(rounds_completed,latest_file))
      contestant_rounds_dict_org,running_total_iround_org = read_pool(latest_file,rounds_completed,contestant_columnw)
      diff_list = find_contestant_differences(contestants,contestant_rounds_dict_org,contestant_rounds_dict,running_total_iround_org,running_total_iround,rounds_completed)
      if len(diff_list) > 0:
         diff_file = outputDir + "/" + eventName + "_round_"+str(rounds_completed)+"_"+now+"_diff.txt"
         print("Differences found between current pool data and previous, writting a new file: {} along with differences in {}".format(latest_file,output_file,diff_file))
         write_pool(output_file,contestant_rounds_dict,running_total_iround,rounds_completed,contestant_columnw)
         write_differences(diff_file,diff_list)
      else:
         print("No differences found between latest pool and previous pool")
      
   return

def write_pool(output_file,contestant_rounds_dict,running_total_iround,rounds_completed,contestant_columnw):

   '''
   Write the pool data to an output file
  
   INPUTS: 
   1: output_file : str
       full path to file to write to
   2: contestant_rounds_dict : dict
       dictionary with kesy of the round and values of dictionary with keys contestant and values of their scores
   3: running_total_iround : dict
       dictionary with keys contestant and values of their running score total
   4: rounds_completed : int
       number of rounds that have been completed, will write this many to the file
   5: contestant_columnw : length of the longest contestant name in the pool, used for formatting output file

   OUTPUTS: none, just writes the output to 'output_file'
   '''

   #Get ranks in the running total dictionary
   running_total_scores = [ running_total_iround[player] for player in running_total_iround.keys() ]
   ranks = scipy.stats.rankdata(running_total_scores,method="min")
   
   #Open the output file for writting
   f = open(output_file,"w")

   #Format for the header line and write the header line
   contestant_part = "{:{:d}s}".format("Contestant",contestant_columnw+1)
   rounds_part = ("Round {} "*rounds_completed).format(*range(1,rounds_completed+1))
   total_part = "Total"
   rank_part = " Rank"
   header_line = contestant_part+rounds_part+total_part+rank_part
   seperator = "*"*len(header_line)
   f.write(header_line+"\n")
   f.write(seperator+"\n")
  
   #Loop through the contestants and write their scores for  
   for i,contestant in enumerate(running_total_iround.keys()):
      scores = []
      for iround in range(rounds_completed):
         scores.append(str(contestant_rounds_dict[iround+1][contestant]))

      firstpart = "{:>{:d}s}".format(contestant,contestant_columnw)
      secondpart = (" {:>7s}"*rounds_completed).format(*scores)
      thirdpart = " {:>5s}".format(str(running_total_iround[contestant]))
      fourthpart = "{:5d}".format(ranks[i])
      f.write(firstpart+secondpart+thirdpart+fourthpart+"\n")

   f.close()

   return

def read_pool(pool_file,rounds_completed,contestant_columnw):
   '''
   Read a pool file that was written by 'write_pool'
   
   INPUTS:
   1: pool_file : str
       full path to the written pool file
   2: rounds_completed : int
       number of rounds that have been completed
   3: contestant_columnw : int
       length of the logest contestant name

   OUTPUTS: 
   1: contestant_rounds_dict: dict
        dictionary with keys of round and values of dictionary with keys of contestant and values of their score
   2: running_total_iround : dict
        dictionary with keys of contestant and values of their running total
   '''

   #Initialize dictionaries for the two output dictionaries
   contestant_rounds_dict={}
   running_total_iround={}

   #Open pool file for reading and read contestants as well as scores into lists
   f = open(pool_file,"r")
   f.readline()
   f.readline()
   contestants = []
   scores = []
   for line in f.readlines():
      contestant_str = line[:contestant_columnw].strip()
      contestants.append(contestant_str)
      scores_str = line[contestant_columnw:].strip("\n").split()
      scores_checkcut = [ int(score) if score !="CUT" else score for score in scores_str ]
      scores.append(scores_checkcut)
   f.close()

   #Put together the contestant_rounds_dict
   for iround in range(rounds_completed):
      round_dict = {contestants[i]:scores[i][iround] for i in range(len(contestants))}

      contestant_rounds_dict.update({iround+1:round_dict}) 

   #Put together the running_total_iround dict
   for i,contestant in enumerate(contestants):
      running_total_iround.update({contestant:scores[i][-2]})

   #Done
   return contestant_rounds_dict,running_total_iround

def write_contestant_player_scores(outputDir,contestant_shortname,iround,players,scores):
   '''
   Write a contestants players scores for a round 

   INPUTS:
   1: ouputDir : str
       full path to the directory to write the files in
   2: contestant_shortname : str
       shortname for the contestant that will be used to name the file written to
   3: iround : int
       the round number to look for
   4: players : list of strings
       their players to find
   5: scores : list of either ints or strings
 
   OUTPUTS:
     None, just write a file with name {short_name}_round{}.txt
       
   '''

   #Time stamp for writing files
   now = (dt.datetime.now()).strftime("%Y%m%d_%H_%M")

   #Sort players by score
   cut_players=[]
   cut_players_scores=[]
   nocut_players=[]
   nocut_players_scores=[]

   #Go through players and seperate those who might have either
   # got cut, wd, or dq
   for player,score in zip(players,scores):
      if score == "CUT" or score == "DQ" or score == "WD":
         cut_players.append(player)
         cut_players_scores.append(score)
      else:
         nocut_players.append(player)
         nocut_players_scores.append(score)

   #sort players by score
   nocut_players=np.array(nocut_players)
   nocut_players_scores=np.array(nocut_players_scores)
   sort_indx = np.argsort(nocut_players_scores)

   #Put lists back together
   players = list(nocut_players[sort_indx]) + cut_players
   scores = list(nocut_players_scores[sort_indx]) + cut_players_scores

   #See if any previous files for this contestant exist
   prev_files = find_contestant_player_files(outputDir,contestant_shortname,iround)

   #Name of the output file   
   outputFile = outputDir+"/{}_round{}_{}.txt".format(contestant_shortname,iround,now)
   max_player_name_len = max([len(item) for item in players])

   #If there are no previous files written for this contestnat and round, write them now
   if len(prev_files) == 0:
      write_players_scores(outputFile,players,scores,max_player_name_len)
   else:
   #If there is a previous file, read in the latest one and compare for differences
      latest_file=get_latest_contestant_player_file(outputDir,contestant_shortname,prev_files,iround)
      
      #Read in the players and scores
      players_org,scores_org = read_contestant_player_scores(latest_file)

      #See if theyre are any differences
      diff_list = compare_players_scores(players_org,scores_org,players,scores)

      #If theyre were any differences then write them out to a new file
      if len(diff_list) > 0:
         write_players_scores(outputFile,players,scores,max_player_name_len)

   return
 
def write_players_scores(file,players,scores,max_player_name_len):
   f = open(file,"w")
   for i in range(len(players)):
      if isinstance(scores[i],str):
         f.write("{0:{2:d}s}  {1:>3s}\n".format(players[i],scores[i],max_player_name_len))
      else:
         f.write("{0:{2:d}s}  {1:3d}\n".format(players[i],scores[i],max_player_name_len))
   f.close()

   return

def compare_players_scores(players_org,scores_org,players_new,scores_new):
   #First make sure they have the same players
   if not sorted(players_org) == sorted(players_new):
      print("In results_tools.compare_players_score : list of players are not the same...exiting")
      sys.exit()

   diff_list = []
   #Loop through players and make sure their scores match
   for player in players_new:
      indx_org = players_org.index(player)
      indx_new = players_new.index(player)
      if not scores_org[indx_org] == scores_new[indx_new]:
         diff_list.append("Player: {}, org score: {}, new score: {}".format(player,scores_org[indx_org],scores_new[indx_new]))

   return diff_list
   
  
def read_contestant_player_scores(player_file):
   '''
   Read a contestants players scores written by write_contestant_player_scores

   INPUTS: 
   1: player_file : str
       file written by write_contestant_player_scores with player scores and names
   OUTPUTS:
   1 : players : list of strings
        list of players names
   2 : scores : list of either ints or strs
        list of the corresponding scores for each player
   '''

   #Initialize lists for storing players names and socres 
   players = []
   scores = []

   #Loop through input file and read the player names and scores
   f = open(player_file,"r")
   for line in f.readlines():
      line = line.split()
      player = " ".join(line[0:-1]) 
      players.append(player)
      try:
         score = int(line[-1])
      except: 
         score = line[-1] 
      scores.append(score)

   #Done
   return players,scores

def find_contestant_differences(contestants,round_dict1,round_dict2,running_total1,running_total2,rounds_completed):
   '''
   Given org and new dictionaries for contestants round dicts, and running total dicts, find any differences

   INPUTS:
   1: contestants : list of strings
        The contestants that should be keys in the dictionaries inputted
   2: round_dict1 : dict
        Dictionary with keys round and values of dict, with keys contestant and values of scores, ORG
   3: Same as 2 but for NEW
   4: running_total1 : dict
        Dcitionary with keys contestant and values total running score
   5: Same as 4 but for OLD
   6: rounds_completed : int
        Number of rounds that have been completed

   OUTPUTS:
   1: differences : list of strings
        list of strings holding the messages for what was different
   '''
   
   differences = []
   for iround in range(rounds_completed):
      for contestant in contestants:
         org_score = round_dict1[iround+1][contestant]
         new_score = round_dict2[iround+1][contestant]
         if org_score != new_score:
            differences.append("Round: {}, contestant: {}, org score: {}, new score: {}".format(iround+1,contestant,org_score,new_score))

   for contestant in contestants:
      org_total = running_total1[contestant]
      new_total = running_total2[contestant]
      if org_total != new_total:
         differences.append("Contestant: {}, org total: {}, new total: {}".format(contestant,org_total,new_total))

   return differences

def find_contestant_player_files(outputDir,contestant_shortname,iround):
   found_files = glob.glob(outputDir+"/"+"{}_round{}*.txt".format(contestant_shortname,iround))
   return found_files

def get_latest_contestant_player_file(outputDir,contestant_shortname,prev_files,iround):
   dates=[]
   for ifile in prev_files:
      datestr = ifile[-18:-4]
#      datestr = ifile.strip(outputDir+"/"+contestant_shortname+"_round"+str(iround)).strip(".txt")
      dates.append(dt.datetime.strptime(datestr,"%Y%m%d_%H_%M"))
   dates = np.array(dates)
   latest_file_indx = np.where(dates==np.max(dates))[0][0]
   return prev_files[latest_file_indx] 
