import sys
from pull_pga import get_col_indecies

def get_tournament_players(soup):
   player_col,_,_,_,_ = get_col_indecies(soup)
   rows = soup.find_all("tr", class_="Table__TR")
   players = []
   for row in rows[1:]:
      cols = row.find_all("td")
      if len(cols) < 5: #Cutline seperator
            continue
      players.append(cols[player_col].text.strip())

   return players


