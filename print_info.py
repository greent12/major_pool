def print_info(date,event,output_dir,par,RC,live):
   print("*******************************************************************")
   print(" Tournament: {}, Par: {}".format(event,par))
   print(" Rounds completed: {}".format(RC))
   print(" Live scoring: {}".format(live))
   print(" Time stamp: {}".format(date.strftime("%I:%M%p %A %B, %d %Y") ))
   print(" Output will be in : {}".format(output_dir))
   print("*******************************************************************")

   return
