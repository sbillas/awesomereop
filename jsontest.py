import json

with open('isilon_stat_keys.json') as data_file:
    data = json.load(data_file)

for k in range(len(data["keys"])):
      key = data["keys"][k]["key"]
      desc = data["keys"][k]["description"]
      print "Statistics key: ", key
      print "Description: ", desc
      print "\n"
