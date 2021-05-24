import os
import sys
import datetime as dt
import glob
import numpy as np

#This module is used for writting the scores for individual rounds 
#The main function is 'write_round_scores' 

def write_round_scores(event_name,output_dir,round_dict):
   '''
    Loop through the dictionary holding scores for each round and write out to files in 'output_dir'
    It will first see if the output file for the round exists, and if it does, it will check to see if all the scores are identical. If they aren't, it will write a new file with a time stamp appended to it so it will not overwrite the original round file

   INPUTS:
   1: event_name, str
      the name of the tournament
   2: output_dir, str
      path to the output directory for this tournament
   3: round_dict, dict
      dictionary with integer keys corresponding to the round number, the values are dictioanries holding the player information for the round

   OUTPUTS: No outputs, just writes files 
   '''
                
   #Loop through rounds, which are the keys to the round_dict
   for iround in round_dict.keys():

      #Time stamp
      now = (dt.datetime.now()).strftime("%Y%m%d_%H_%M")

      #This will be the output file
      output_file = output_dir + "/" + event_name + "_round_"+str(iround)+"_"+now+".txt"
#      output_file = output_dir + "/" + event_name + "_round_"+str(iround)+".txt"      
      #See how many output files have been written for this round
      prev_round_files = find_round_files(event_name,output_dir,iround)

      #If there were no previous files for this round, go ahead and write the output
      if len(prev_round_files) == 0:
         print("Round {} file does not exist yet, writting to: {}".format(iround,output_file))
         write_round_file(output_file,round_dict[iround],event_name,iround)
      else: #If not well have to check the latest file to see if there are any differences
         latest_round_file=get_latest_round_file(output_dir,event_name,prev_round_files,iround)
         print("Round {} file does already exist, but will check for differences in the latest file {}".format(iround,latest_round_file))
         num_diff,diff_list = retro_check_round_file(latest_round_file,output_dir,round_dict[iround])       
         if num_diff>0:
            diff_file = output_dir + "/" + event_name + "_round_"+str(iround)+"_"+now+"_diff.txt"
            print("Differences found between current soup and {}, writting a new file: {} along with differences in {}".format(latest_round_file,output_file,diff_file))
            write_round_file(output_file,round_dict[iround],event_name,iround)
            write_differences(diff_file,diff_list)
         else:
            print("No differences found between latest soup and {}".format(latest_round_file))
   return 

def write_round_file(round_file,players_dict,event_name,iround):
   '''
    Write player dictionary for a round to file

    INPUTS:
    1: round_file, str
       file to write too, provide full path
    2: players_dict, dict
       dictionary with keys being the player names, and values of 'SCORE','TO PAR', 'WD' and 'DQ'
    3: event_name, str
       tournament name
    4: iround, int
       Round number

    OUTPUT: none, will just write output to 'round_file'
   
   '''
  
   #Open file
   f = open(round_file,"w")

   #Write header lines
   f.write("{} Round: {}\n".format(event_name,iround))
   f.write("-"*60+"\n")
   f.write("{:30s} {:5s}   {:6s}   {:>3s} {:>2s} {:>2s}\n".format("PLAYER","SCORE","TO PAR","CUT","WD","DQ"))
   f.write("-"*60+"\n")

   #Loop through players and write a row for each one
   players_iround = players_dict
   for player in players_iround.keys():
      if players_iround[player]['SCORE'] == "CUT" or \
         players_iround[player]['SCORE'] == "DQ"  or \
         players_iround[player]['SCORE'] == "WD":
         formatter = "{:30s} {:>5s}   {:>6s}   {:>3s} {:>2s} {:>2s}\n"
      else:
         formatter = "{:30s} {:5d}   {:6d}   {:>3s} {:>2s} {:>2s}\n"
      f.write(formatter.format(player,players_iround[player]['SCORE'],players_iround[player]['TO PAR'],players_iround[player]['CUT'],players_iround[player]['WD'],players_iround[player]['DQ']))

   f.close() 
   return


def read_round_file(round_file):
   ''' 
    Read a round file written by 'write_round_file'. This is essetially the inverse of 'write_round_file', as it will read the round data back into a dictionary

    INPUTS:
    1 : round_file, str
        filepath to the file to read

    OUTPUTS:
    1 : players, dict
        dictionary with keys of the player names, and values of 'SCORE','TO PAR', 'WD' and 'DQ'
   '''
   
   #Initialize player dictionary
   players={}

   #Open the round file and read the header lines
   f = open(round_file,"r")
   f.readline()
   f.readline() 
   f.readline()
   f.readline()

   #Read the player name, score, to_par, WD, and DQ and update the dictionary
   for line in f.readlines():
      line = line.strip()
      player = line[0:30].strip()
      try:
         score = int(line[31:36])
         topar = int(line[39:45])
      except:
         score = line[31:36].strip()
         topar = line[39:45].strip()
      cut = line[49:51].strip()
      wd = line[52:54].strip()
      dq = line[55:57].strip()

      players.update({player:{"SCORE":score,"TO PAR":topar,"CUT":cut,"WD":wd,"DQ":dq}})

   f.close()

   return players 

def write_differences(outputfile,diff_list):
   f = open(outputfile,"w")
   for diff in diff_list:
      f.write(diff+"\n")
   f.close()

def retro_check_round_file(round_file,output_dir,current_round_dict):

   '''
   Compare the keys (player names) for a round file that exists, and a round dictionary variable to see if there are differences

   INPUTS: 
   1: round_file, str
      filepath to the round file to read
   2: output_dir, str
      path specifying the output directory for this tournament
   3: current_round_dict, dict
      dictionary of the current round with keys of players and alues of 'SCORE','TO PAR', 'WD' and 'DQ'

   OUTPUTS:
   1: num_differences, int
      number of differences found in the two datasets

   NOTES:
   5/11/21, changed so that changes in the CUT, DQ, or WD are not counted as 
            differences so new files will not be written. This makes it so
            only score changes are reported. WD and DQ are printed though.
   '''

   #Read the original round file
   old_round_dict = read_round_file(round_file)
 
   #Loop through each key in the original round dict, and compare with the current one, count differences 
   num_differences=0
   diff_list=[]
   for player in old_round_dict:

      #Original data
      old_score = old_round_dict[player]['SCORE']
      old_topar = old_round_dict[player]['TO PAR']
      old_CUT = old_round_dict[player]['CUT']
      old_WD = old_round_dict[player]['WD']
      old_DQ = old_round_dict[player]['DQ']

      #New ( or current data )
      new_score = current_round_dict[player]['SCORE']
      new_topar = current_round_dict[player]['TO PAR']
      new_CUT = current_round_dict[player]['CUT']
      new_WD = current_round_dict[player]['WD']
      new_DQ = current_round_dict[player]['DQ']
     
      #Find differences 
      if old_score != new_score:
         num_differences+=1
         diff_list.append("Player: {}, SCORE, org: {}, new: {}".format(\
                          player,old_score,new_score))
      if old_topar != new_topar:
         num_differences+=1
         diff_list.append("Player: {}, TO PAR, org: {}, new: {}".format(\
                          player,old_topar,new_topar))
      if old_CUT != new_CUT:
          pass
#         num_differences+=1
#         diff_list.append("Player: {}, CUT, org: {}, new: {}".format(\
#                          player,old_CUT,new_CUT))
      if old_WD != new_WD:
         print("  retro_check: Player: {} WD".format(player)) 
#         num_differences+=1
#         diff_list.append("Player: {}, WD, org: {}, new: {}".format(\
#                          player,old_WD,new_WD))
      if old_DQ != new_DQ:
         print("  retro_check: Player: {} DQ".format(player))
#         num_differences+=1
#         diff_list.append("Player: {}, DQ, org: {}, new: {}".format(\
#                          player,old_DQ,new_DQ))
 
   return num_differences,diff_list 

#Function to find how many times round file exists already in directory
def find_round_files(event_name,output_dir,iround):
   found_files = glob.glob(output_dir+"/"+event_name+"_round_"+str(iround)+"*")
   valid_files = []
   #Get rid of any diff files
   for ifile in found_files:
      if "diff" not in ifile:
         valid_files.append(ifile) 
   return valid_files

#Function to get the round file with the most recent time stamp        
def get_latest_round_file(output_dir,event_name,prev_files,iround):
   dates = []
   for ifile in prev_files:
      datestr = ifile.strip(output_dir+"/"+event_name+"_round_"+str(iround)).strip(".txt") 
      dates.append(dt.datetime.strptime(datestr,"%Y%m%d_%H_%M"))
   dates = np.array(dates)
   latest_file_indx = np.where(dates==np.max(dates))[0][0]
   return prev_files[latest_file_indx]
