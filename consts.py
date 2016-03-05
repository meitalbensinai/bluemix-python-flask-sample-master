__author__ = 'Meital'
from pymongo import MongoClient
import time
import sys
import os
import json
import pprint

LOCAL = False


def mongodb_uri():
    #services = json.loads(os.getenv("VCAP_SERVICES", "{}"))
    #mongo_lab = os.getenv("MONGOLAB_URL", "")
    if LOCAL:
        uri = "mongodb://localhost"
        return uri
    mongo_lab = 'mongodb://meitalbs:n40h10@ds063929.mongolab.com:63929/af_ltdow-meitalbensinai'
    return mongo_lab
    """
    if services:
        creds = services['mongodb-1.8'][0]['credentials']
        uri = "mongodb://%s:%s@%s:%d/%s" % (
            creds['username'],
            creds['password'],
            creds['hostname'],
            creds['port'],
            creds['db'])
        print >> sys.stderr, uri
        return uri
    else:
        uri = "mongodb://localhost"
        return uri
    """

#try to connect to mongodb
try:
    from pymongo import Connection
    uri = mongodb_uri()
    client = Connection(uri)

except:
    """
    #open server if not available
    print "opening mongo.."
    print subprocess.Popen("mongod")
    time.sleep(5)
    print "mongo is up!"
    client = MongoClient()
    """
    print "failed"


#db consts
if LOCAL:
    DB = client.sof
    WEB_DB = DB['pairs_new']
    #DB = client.web
    #WEB_DB = DB['wrong']
else:
    DB = client.get_default_database()
    WEB_DB = DB['pairs_new']

WEB_RES_DB = DB['results_with_related']
NEW_IDS_DB = DB['ids_to_take_from']

WEB_ERROR_DB = DB['errors']
DONT_KNOW_DB = DB['dont_know']
COUNTER = DB['counters']
GOOD_PAIRS = DB['good_tags']

DOWNLOADS = DB["downloaders"]
# dictionary from strings to values
STRING_TO_GRADE = {"Related, but not similar": 6, "Very similar": 5, "Pretty similar": 4, "Comme ci comme ca": 3, "Pretty different": 2,"Totally different": 1}

SCORE_SIM_THRESHOLD = 0.4
SCORE_DIFF_THRESHOLD = 0.04
