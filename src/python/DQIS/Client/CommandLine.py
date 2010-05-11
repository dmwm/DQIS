'''
Created on 7 May 2010

@author: metson
'''
from DQIS.API.Database import Database
from optparse import OptionParser
import json

D_DATABASE_NAME = 'dqis'
D_DATABASE_ADDRESS = 'localhost:5984'

def do_options():
    op = OptionParser(version="%prog 0.1")
    op.add_option("-u", "--url",
                  type="string", 
                  action="store", 
                  dest="db_address", 
                  help="Database url. Default address %s" % D_DATABASE_ADDRESS, 
                  default=D_DATABASE_ADDRESS)
    
    op.add_option("-d", "--database", 
                  type="string",
                  action="store",                
                  dest="db_name", 
                  help="Database name. Default: '%s'" % D_DATABASE_NAME, 
                  default=D_DATABASE_NAME)
    
    op.add_option("-k", "--key", 
                  action="append", 
                  nargs=2,
                  type="string", 
                  dest="keys",
                  help="Key Value pair (e.g.-k ecal True)")
    
    op.add_option("--startrun", 
                  action="store", 
                  type="int", 
                  dest="start_run",
                  help="Run value")
    
    op.add_option("--endrun", 
                  action="store", 
                  type="int", 
                  dest="end_run",
                  help="Run value")
    
    op.add_option("--lumi", 
                  action="store", 
                  type="int", 
                  dest="lumi",
                  help="Lumi value")
    
    op.add_option("--dataset", 
                  action="store", 
                  type="string", 
                  dest="dataset",
                  help="Dataset value")
    
    op.add_option("--bfield", "-b",
                  action="store", 
                  type="int", 
                  dest="bfield",
                  help="Magnetic field value")
    
    op.add_option("--id", 
                  type="string",    
                  action="store",
                  dest="doc_id", 
                  help="Document ID",) #TODO: validate
    
    op.add_option("--crab",
                  "-c",
                  action="store_true", 
                  dest='crab',
                  help='Create a CRAB lumi.json file in the current directory.',
                  default=False)
    
    return op.parse_args()


options, args = do_options()
db = Database(dbname = options.db_name, url = options.db_address, size = 1000)

map = {}
for k,v  in options.keys:
    map[k] = bool(v)

if options.crab:
    data = db.crab(options.start_run, options.end_run, map, options.bfield)
    f = open('lumi.json', 'w')
    json.dump(data, f)
    f.close()
elif options.doc_id:
    print db.getDoc(doc_id)
else:
    print db.search(options.start_run, options.end_run, map, options.bfield)