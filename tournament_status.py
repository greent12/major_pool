import sys

def check_status(soup):
   status = soup.find_all("div", class_="status")[0].find_all("span")[0].text.upper()
   active = 'FINAL' not in status

   if not active:
      rounds_complete = 4
      live=False
   else:
     if "Play Complete".upper() in status:
        status_split = status.split(" ")
        rounds_complete = int(status_split[1])
        live=False
     elif "In Progress".upper() in status: 
        status_split = status.split(" ")
        rounds_complete=int(status_split[1])-1
        live=True
     elif "Suspended".upper() in status:
        status_split = status.split(" ")
        print("Play suspended in round: {}".format(status_split[1]))
        live=False
        rounds_complete = int(status_split[1]) - 1
     else: 
        print("Unknown tournament status...exitting")
        sys.exit()

   return rounds_complete,live

def get_par(soup):
   course_info = soup.find_all("div",class_="Leaderboard__Course__Location__Detail")[0]

   return int(course_info.text[3:5])

def get_tournament_name(soup):
    #4/12/21 Tyler changed the class tag
    tournament_name = soup.find_all("h1",class_="headline headline__h1 Leaderboard__Event__Title")[0].text
    return tournament_name

