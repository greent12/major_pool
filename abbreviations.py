from wgr import get_key

def list_possible_abbreviations():
   #Add to this dictionary when necessary
   # The key should be the potential abbreviation, and the value is what the name
   #  should be corrected to
   possible_abbrvs = {
         "K.H. Lee" : "Kyoung-Hoon Lee"
                     }

   return possible_abbrvs

def list_possible_abbreviations_wgr():
   #Add to this dictionary when necessary
   # The key should be the potential abbreviation, and the value is what the name
   #  should be corrected to
   possible_abbrvs = {
         "K.H. Lee" : "Kyounghoon Lee",
         "Byeong-Hun An" : "Byeong Hun An",
         "Si Woo Kim" : "Siwoo Kim",
         "Sebastian Munoz" : "Sebastian J Munoz",
         "Matt Fitzpatrick" : "Matthew Fitzpatrick"
                     }

   return possible_abbrvs

def correct_abbreviations(round_dict):
   #Correct any player names that might have been changed or abbreviated
   possible_abbrvs = list_possible_abbreviations()
  
   #Loop through round dict and see if any of the possible abbeviations are in it
   for abbrv in possible_abbrvs.keys():
      if abbrv in round_dict.keys():
         round_dict[possible_abbrvs[abbrv]] = round_dict.pop(abbrv)
         print("Abbreviation: {} replaced with {}".format(abbrv,possible_abbrvs[abbrv]))

   return round_dict
  
def correct_abbreviations_WGR(players):
   #Correct any player names that might have been changed or abbreviated
   possible_abbrvs = list_possible_abbreviations_wgr()
  
   #Loop through round dict and see if any of the possible abbeviations are in it
   for abbrv in possible_abbrvs.keys():
      if abbrv in players:
         indx = players.index(abbrv)
         players[indx] = possible_abbrvs[abbrv]

   return players
 
