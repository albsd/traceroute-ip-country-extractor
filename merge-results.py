import os

ips = set()

for filename in os.listdir(os.getcwd() + "/filtered_results"):
   print(filename)
   with open(os.path.join(os.getcwd() + "/filtered_results", filename), 'r') as f:
      for line in f:
         ips.add(line)

with open("results.txt", "w") as out:
   for ip in ips:
      out.write(ip)
