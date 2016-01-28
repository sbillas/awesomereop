import json

""" JSON file that gets all the statistics keys from Isilon OneFS 7.2,
to keys where collected at /platform/1/statistics/keys. """

with open('isilon_stat_keys.json') as data_file:
    data = json.load(data_file)

for k in range(len(data["keys"])):
      key = data["keys"][k]["key"]
      desc = data["keys"][k]["description"]
      print "Statistics key: ", key
      print "Description: ", desc
      print "\n"
