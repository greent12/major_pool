def parse_input(inputfile):
   f = open(inputfile,"r")
   line=f.readline().strip("\n")
   html_source = line.split(",")[-1].strip()
   line=f.readline().strip("\n")
   event = line.split(",")[-1].strip()
   line=f.readline().strip("\n")
   output_dir = line.split(",")[-1].strip()
   line=f.readline().strip("\n")
   nplayers_cut = int(line.split(",")[-1].strip())
   return html_source,event,output_dir,nplayers_cut

