import glob
import os
from wgr import get_key

def read_contestants(contestants_file):
   '''
    Read the contenstant file given and return a dictionary
    of Person name : shortname for their entry file
   '''

   f = open(contestants_file,"r")
   contestant_dict = {}
   for line in f.readlines():
      line = (line.strip()).split(":")
      contestant_dict.update({line[0].strip():line[1].strip()})
   f.close()

   return contestant_dict

def read_entries(entry_file):
   '''
    Read the players in an entry file and return a  list of them
   '''

   entries=[]
   f=open(entry_file,"r")
   for line in f.readlines():
      entries.append(line.strip())
   f.close()

   return entries

def verify_with_wgr(entries,wgr_dict):

   '''
    For a given list of entries, make sure those entries are the
    WGR's. This mainly just ensures that the names are spelled correctly
    but does not ensure that the entry is legit, eg Sandy Lyle or any of the old fucks who still play in the Masters even though they should really stop

   '''
   conflicts = []
   num_entries = len(entries)
   num_verify = 0
   for entry in entries:
      if entry in wgr_dict.values():
         rank = get_key(wgr_dict,entry)
         num_verify += 1
      else:
         conflicts.append("Entry: {} NOT found in wgr...could signify their name being mispelled".format(entry))

   if num_verify == num_entries:
      ret = False
   else:
      ret = True

   #Will return true if there were conflicts
   return ret,conflicts

def verify_entries_with_tournament_players(entries,tournament_list):
   '''
   Verify that a list of entries are actually in the tournament itself
   '''
   num_conflicts = 0
   conflicts = []
   for entry in entries:
      if entry not in tournament_list:
         conflicts.append("Problem with player: {}, not found in tournament...".format(entry))
         num_conflicts+=1

   if num_conflicts > 0:
      ret = True
   else:
      ret = False

   #Will return true for ret if there were conflicts   
   return ret,conflicts
