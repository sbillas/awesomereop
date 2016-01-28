from pprint import pprint
import json

""" JSON file that gets all the statistics keys from Isilon OneFS 7.2,
to keys where collected at /platform/1/statistics/keys. """

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
    



def usr_lookup(userid):
    """ Function to resolve the username from the UID or SID, this can be done
    agains this "/platform/1/auth/users/ [userid]"
    """

with open('isilon_quotas.json') as data_file:
    data = json.load(data_file)

print ""
print "User quotas:"
for k in range(len(data["quotas"])):
    if data["quotas"][k]["type"] == "user":
        if data["quotas"][k]["path"]:
            path = data["quotas"][k]["path"]
        else:
            path = "None"
        if data["quotas"][k]["persona"]:    
            user = data["quotas"][k]["persona"]["id"]
        else:
            user = "None"
        usage = data["quotas"][k]["usage"]["logical"]
        print user, path, sizeof_fmt(usage)
 
print ""
print "Group quotas:"
for k in range(len(data["quotas"])):
    if data["quotas"][k]["type"] == "group":
        if data["quotas"][k]["path"]:
            path = data["quotas"][k]["path"]
        else:
            path = "None"
        if data["quotas"][k]["persona"]:    
            user = data["quotas"][k]["persona"]["id"]
        else:
            user = "None"
        usage = data["quotas"][k]["usage"]["logical"]
        print user, path, sizeof_fmt(usage)
 
print ""
print "Directory quotas:"
for k in range(len(data["quotas"])):
    if data["quotas"][k]["type"] == "directory":
        if data["quotas"][k]["path"]:
            path = data["quotas"][k]["path"]
        else:
            path = "None"
        if data["quotas"][k]["persona"]:    
            user = data["quotas"][k]["persona"]["id"]
        else:
            user = "None"
        usage = data["quotas"][k]["usage"]["logical"]
        print path, sizeof_fmt(usage)
        
print ""