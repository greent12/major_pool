from abbreviations import correct_abbreviations
from results_tools import sort_dict

def process_completed_rounds(soup,rounds_completed,par,output_dir):

   '''
    Go through the completed round scores and write to output files.
    If rounds have already been written, check to verify the scores are still the same.
   '''

   #Will only need column numbers for the player and round numbers
   player_col,score_col,_,_, round_cols = get_col_indecies(soup)
 
   #Get all the rows 
   rows = soup.find_all("tr", class_="Table__TR")

   #round_dict will hold data for each round, keys are integers matching the 
   # round number
   round_dict={}

   #Loop through the rounds
   for round in range(rounds_completed):
      #Dictionary to hold player information for each round
      players={}
      for row in rows[1:]:
         cols = row.find_all("td")
         if len(cols) < 5: #Cutline seperator
            continue
         player = cols[player_col].text.strip()
         try:
            score = int(cols[round_cols[round]].text.strip().upper())
            topar = score-par
         except:
              score = cols[round_cols[round]].text.strip().upper()
              topar = score
         players[player] = {'SCORE' : score, "TO PAR" : topar}

      #Check for possible WD or DQ
      to_par_dict = get_to_par(soup,player_col,score_col)
      players_checked = check_for_DQ_WD_CUT(players,to_par_dict,round+1)

      #Check for possible abbreviations
      players_checked_abbrv = correct_abbreviations(players_checked)

      #Sort by score and save
      sorted_player_list = sort_round_dict(players_checked_abbrv)
      players_sorted = { player : { 'SCORE' : players_checked_abbrv[player]['SCORE'],\
                                    'TO PAR' : players_checked_abbrv[player]['TO PAR'],\
                                    'CUT' : players_checked_abbrv[player]['CUT'],\
                                    'WD' : players_checked_abbrv[player]['WD'],\
                                    'DQ' : players_checked_abbrv[player]['DQ'] }\
                         for player in sorted_player_list }

      round_dict[round+1] = players_sorted

   return round_dict

def sort_round_dict(round_dict):
   nocut_dict = {}
   cut_dict = {}
   
   for player in round_dict.keys():
      if round_dict[player]['TO PAR'] == "CUT" or \
         round_dict[player]['TO PAR'] == "WD"  or \
         round_dict[player]['TO PAR'] == "DQ" :
         cut_dict.update({player:round_dict[player]['TO PAR']})
      else:
         nocut_dict.update({player:int(round_dict[player]['TO PAR'])})

   nocut_dict_sorted = sort_dict(nocut_dict)
   nocut_dict_sorted.update(cut_dict)
   sorted_players = list(nocut_dict_sorted.keys())

   return sorted_players
   
def get_col_indecies(soup):
    #4/12/21 Tyler, change class name of header row
    header_rows = soup.find_all("tr", class_="Table__TR")

    # other possible entries for what could show up, add here.
    player_fields = ['PLAYER']
    to_par_fields = ['TO PAR', 'TOPAR', 'TO_PAR']
    thru_fields = ['THRU']
    today="TODAY"
    round1="R1"
    round2="R2"
    round3="R3"
    round4="R4"

    header_col = header_rows[0].find_all("th")

    player_col = None
    score_col = None
    thru_col = None
    today_col = None
    round1_col = None
    round2_col = None
    round3_col = None
    round4_col = None

    for i in range(len(header_col)):
        col_txt = header_col[i].text.strip().upper()

        if col_txt in player_fields:
            player_col = i
            continue
        if col_txt in to_par_fields:
            score_col = i
            continue
        if col_txt in thru_fields:
            thru_col = i
            continue
        if col_txt == today:
            today_col = i
            continue
        if col_txt == round1:
            round1_col = i
            continue
        if col_txt == round2:
            round2_col = i
            continue
        if col_txt == round3:
            round3_col = i
            continue
        if col_txt == round4:
            round4_col = i
            continue

    if player_col is None or score_col is None:
        print("Unable to track columns")
        exit()
    
    return player_col, score_col, thru_col,today_col, [ round1_col, round2_col, round3_col,round4_col]

def verify_scrape(players):
    if len(players) < 25:
        print("Less than 25 players, seems suspucious, so exiting")
        exit()

    bad_entry_count = 0
    bad_score_count = 0
    for key, value in players.items():
        scr = players[key]['TO PAR']
        if scr == '?':
            bad_entry_count += 1
        if type(scr) is int and (scr > 50 or scr < -50):
            print("Bad score entry, exiting")
            exit()

    if bad_entry_count > 3:
        # arbitrary number here, I figure this is enough bad entries to call it a bad pull
        print("Multiple bad entries, exiting")
        exit()

def get_to_par(soup,player_col,score_col):
   rows = soup.find_all("tr", class_="Table__TR")
   to_par_dict={}
   for row in rows[1:]:
      cols = row.find_all("td")
      if len(cols) < 5:
         continue
      player = cols[player_col].text.strip()
      score = cols[score_col].text.strip().upper() 
      score = cols[score_col].text.strip().upper()  
      if score == 'CUT':
         to_par_dict[player] = {'TO PAR': 'CUT'}
         continue
      elif score == 'WD':
         to_par_dict[player] = {'TO PAR': 'WD'}
         continue
      elif score == 'DQ':
         to_par_dict[player] = {'TO PAR': 'DQ'}
         continue
      elif score == 'E':
         to_par_dict[player] = {'TO PAR': 0}
      else:
         try:
            to_par_dict[player] = {'TO PAR': int(score)}
         except ValueError:
            to_par_dict[player] = {'TO PAR': '?'}
   return to_par_dict


def check_for_DQ_WD_CUT(players,to_par_dict,round):
   for player in players.keys():
      dq="N"; wd="N"; cut="N"
      if to_par_dict[player]['TO PAR'] == "WD":
         if players[player]['SCORE'] == "--":
            players[player]['SCORE'] = "WD"
            players[player]['TO PAR'] = "WD"
         wd="Y"
      if to_par_dict[player]['TO PAR'] == "DQ":
         if players[player]['SCORE'] == "--":
            players[player]['SCORE'] = "DQ"
            players[player]['TO PAR'] = "DQ"
         dq="Y"
      if to_par_dict[player]['TO PAR'] == "CUT":
         cut="Y"
         if round>2:
            players[player]['SCORE'] = "CUT"
            players[player]['TO PAR'] = "CUT"
 
      players[player].update({"CUT":cut,"WD":wd,"DQ":dq})

   return players

def get_today_scores(soup):

   #Will only need column numbers for the player and round numbers
   player_col, score_col, thru_col,today_col,_ = get_col_indecies(soup)

   #Get all the rows 
   rows = soup.find_all("tr", class_="Table__TR")

   #Dictionary to hold player information for each round
   players={}

   #Get today's score
   for row in rows[1:]:
      cols = row.find_all("td")
      if len(cols) < 5: #Cutline seperator
         continue
      player = cols[player_col].text.strip()
      try:
         today_score = int(cols[today_col].text.strip())
      except:
         today_score = cols[today_col].text.strip()
      if today_score == "E":
         today_score = 0

      score = cols[score_col].text.strip().upper()
      if score == 'CUT':
         today_score = "CUT"
      elif score == 'WD':
         today_score = "WD"
      elif score == 'DQ':
         today_score = "DQ"
    
      players[player] = {'SCORE' : today_score}

   return players
