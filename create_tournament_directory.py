import os
import sys

def create_dir(tournament_name,output_dir):

   #Replace spaces with underscores for file naming 
   tournament_name=tournament_name.replace(" ","_")  
   
   #Replace any & with nothing
   tournament_name=tournament_name.replace("&","")

   #See if output_dir directory exists, if not, exit
   if not os.path.isdir(output_dir):
      print("'Output Directory' in 'inputs.txt' does not exist")
      sys.exit()

   #See if tournament directory exists, if not create it
   if not os.path.isdir(output_dir+"/"+tournament_name):
      print("Directory for tournament: {} has not been created yet, creating now".format(tournament_name))
      os.mkdir(output_dir+"/"+tournament_name)

   #Create subdirectories for tracking the scores,keeping the entries, and tracking the competion between entries
   if not os.path.isdir(output_dir+"/"+tournament_name+"/scores"):
      os.mkdir(output_dir+"/"+tournament_name+"/scores")
   if not os.path.isdir(output_dir+"/"+tournament_name+"/entries"):
      os.mkdir(output_dir+"/"+tournament_name+"/entries")
   if not os.path.isdir(output_dir+"/"+tournament_name+"/pool_results"):
      os.mkdir(output_dir+"/"+tournament_name+"/pool_results")
 
   #tournament directory path 
   tournament_dir=output_dir+"/"+tournament_name
 
   return tournament_name, tournament_dir


