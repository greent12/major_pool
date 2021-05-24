import sys
sys.path.insert(0,"..")
import requests
from bs4 import BeautifulSoup
import parse_input
from wgr import get_wgr,get_key
from results_tools import sort_dict
from abbreviations import correct_abbreviations_WGR

#Function to get the "player" column in the espn leaderboard
def get_col_indecies(soup):
   header_rows = soup.find_all("tr", class_="Table__TR")
   player_fields = ['PLAYER']
   header_col = header_rows[0].find_all("th")
   player_col = None
   for i in range(len(header_col)):
      col_txt = header_col[i].text.strip().upper()
      if col_txt in player_fields:
         player_col = i
         continue
   return player_col

#Function to get the players in the field
def get_players(soup,player_col):
   #Get all the rows 
   rows = soup.find_all("tr", class_="Table__TR")

   #Intialize players
   players = []

   for row in rows[1:]:
      cols = row.find_all("td")
      player = cols[player_col].text.strip()
      players.append(player)

   return players

def write_field(players,wgr_dict):
   players_dict = {}
   players_dict_unknown = {}
   for player in players:
      rank = get_key(wgr_dict,player)
      if rank == "Unknown":
         players_dict_unknown.update({player:rank})
      else:
         players_dict.update({player:rank})
   players_dict_sorted = sort_dict(players_dict)
   players_dict_ranked = players_dict_sorted.copy()
   players_dict_sorted.update(players_dict_unknown)

   f = open("PGA_Championship_field.txt","w")
   #Write the first 30 entries whether they are in the field or not
   for i in range(30):
      player = get_key(players_dict_sorted,i+1)
      if player == "Unknown":
         unknown_player = wgr_dict[i+1]
         f.write("{:3d} {} (NOT IN FIELD)\n".format(i+1,unknown_player))
      else:
         f.write("{:3d} {}\n".format(i+1,player))
   f.write("*********************************************\n")

   #Write th rest of the field
   last_player_ranked = list(players_dict_ranked.keys())[-1]
   for i in range(31,players_dict_ranked[last_player_ranked]+1):
      player = get_key(players_dict_ranked,i)
      if player == "Unknown":
         continue
      f.write("{:3d} {}\n".format(i,player))

   #Write the unknown rankings
   for player in players_dict_unknown.keys():
      f.write("{:>3s} {}\n".format("UK",player))

   f.close()

   return players_dict_sorted,players_dict_unknown
 
#Parse inputs
htmlSource,eventName,outputDir,_\
      = parse_input.parse_input("../input.txt")

#Parse HTML code 
result = requests.get(htmlSource)
soup = BeautifulSoup(result.text, "html.parser")

#Get the player column
player_col = get_col_indecies(soup)

#Get players
players = get_players(soup,player_col)

#correct player names for comparing to WGR
correct_abbreviations_WGR(players)
#Get WGR
wgr_dict = get_wgr()

rankings_dict,unknown_dict = write_field(players,wgr_dict)

