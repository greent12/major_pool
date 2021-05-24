import requests
from bs4 import BeautifulSoup

wgr_url = "http://www.owgr.com/ranking?pageNo=1&pageSize=All&country=All"

def get_wgr():
   result = requests.get(wgr_url)
   soup = BeautifulSoup(result.text, "html.parser")
   
   main_content = soup.find_all("div",{"id": "main_content"})[0]
   
   wgr_table = main_content.find_all("table")[0]
   table_header = wgr_table.find_all("thead")[0]
   cols = table_header.find_all("th")
   colnames = [ cols[i].text for i in range(len(cols)) ]
   
   indx_rank = colnames.index("This Week")
   indx_name = colnames.index("Name")
   
   table_rows = wgr_table.find_all("tr")
   
   wgr_dict = {}
   for row in table_rows[1:]:
      rank = row.find_all("td")[indx_rank].text
      player = row.find_all("td")[indx_name].text
      wgr_dict.update({int(rank):player})

   return wgr_dict


def get_key(my_dict,val):
    for key, value in my_dict.items():
         if val == value:
             return key
 
    return "Unknown"

def write_wgr():
   wgr_dict = get_wgr()
   i=0
   for i,player in enumerate(wgr_dict.keys()):
      if i > 150:
         break
      print(player,wgr_dict[player])

   print(wgr_dict)

   return
#PGA champ field: 
#https://www.pgatour.com/tournaments/pga-championship/field.html
