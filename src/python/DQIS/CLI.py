"""
Handles options parsing

Calls out to CLIEditor and CLIList as appropriate
"""

import hashlib, json, sys
from optparse import OptionParser

from API import DQISDatabase, DQISResult


#import optparse_config
#from API import DQISDatabase, DQISResult
#from cli_common import get_connection
#from optparse import OptionParser
#from cli_common import  *
#import hashlib
#-------------------------
#! /usr/bin/env python
#import sys, hashlib
#from API import DQISDatabase, DQISResult 
#from cli_common import  *
#import socket
#import httplib
#import datetime

class ExpectedNullOrInteger(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return "Expected 'null' or integer value. Got: %s" % str(self.value)

class DocumentCouldNotBeDeleted(Exception):
    
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return "Document could not be deleted. It seems that docucment doesn't exist %s" % str(self.value)

class DQIS_CLI_App(object):
    #Constants
    C_DATABASE_NAME = 'db_name'
    C_DATABASE_ADDRESS = 'db_address'
    
    #Defaults
    D_DATABASE_NAME = 'dqis'
    D_DATABASE_ADDRESS = '127.0.0.1:5984'
    
    #Columns
    COLUMN_KEY = ("Keys","key", 30)
    COLUMN_COUNT = ("Count", "count", 7)
    COLUMN_BFIELD = ("bField","bfield", 5)
    COLUMN_ID = ("ID","id", 50)
    COLUMN__ID = ("ID","_id", 50)
    COLUMN_RUN = ("Run","run", 7)    
    COLUMN_PDATASET = ("Primary dataset", "pdataset", 25) 
    COLUMN_FLAG = ("Flag", "flag", 4)
    
    #TODO:
    #Update get connection constants
    
    def expect_nothing_or_int(self, value):
        if (value == None)or(value.lower() == "null"):
            return None
        else:
            try:
                return long(value)
            except:
                raise ExpectedNullOrInteger(value)
    
    def table_for_printing(self, dataset, columns):
        '''
        Takes list of records called dataset and colums. Colims is triplets of
        Captions, field name in field colum width.
        '''
        rez = ""
        caption_string = ""
        data_string = ""
        captions = []
        sizes = len(columns) - 1
        for i, (caption, fieldname, size) in enumerate(columns):
            caption_string += "{" + str(i) + ":" + str(size) + "} "
            data_string += "{" + str(fieldname) + ":" + str(size) + "} "
            sizes += size
            captions.append(caption)
        rez += caption_string.format(*captions)
        rez += "\n" + "-"  * sizes
        for data in dataset:
            rez += "\n" + data_string.format(**data)
        rez += "\n" + "-"  * sizes
        s = "{0:" + str(sizes - 8) + "} {1:7}"
        rez += "\n" + s.format("Total count", len(dataset))
        return rez
    
    
    def options_parser(self):
        op = OptionParser( version="%prog 0.1")
        op.add_option("-u", "--url",
                      type="string", 
                      action="store", 
                      dest="db_address", 
                      help="Database url. Default address 127.0.0.1:5984", 
                      default="127.0.0.1:5984")

        op.add_option("-d", "--database", 
                      type="string",
                      action="store",                
                      dest="db_name", 
                      help="Database name. Default: 'dqis'", 
                      default="dqis")
        
        op.add_option("-a", "--action", 
                      type="choice",         
                      choices=self.actions_map.keys(), 
                      dest="action", 
                      help="Choose action. Available options: %s." % 
                            ", ".join(self.actions_map.keys(),)) 
        
        op.add_option("-k", "--key", 
                      action="append", 
                      nargs=2,
                      type="string", 
                      dest="keys",
                      help="Key Value pair (e.g.-k ecal True)")
        
        op.add_option("--skey", 
                      action="append",
                      type="string", 
                      dest="single_keys",
                      help="Only key names")
        
        op.add_option("--run_interval", 
                      action="store", 
                      nargs=2,
                      type="int", 
                      dest="run_interval",
                      help="Run interval (from to)",
                      default=('','')) #runstart runend
        
        op.add_option("--run", 
                      action="store", 
                      type="int", 
                      dest="run",
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
        
        op.add_option("--bfield_interval", 
                      action="store", 
                      nargs=2,
                      type="string", #because can be null 
                      #TODO: validate 
                      dest="bfield_interval",
                      help="bfield  interval (from to)",) 
        
        op.add_option("--bfield", 
                      action="store", 
                      type="string", 
                      dest="bfield",
                      help="Dataset value")
        
        op.add_option("--id", 
                      type="string",    
                      action="store",
                      dest="doc_id", 
                      help="Document ID",) #TODO: validate
                 
        op.add_option("--filename", 
                      type="string",    
                      action="store",     
                      dest="filename", 
                      help="File name to get/store documents",)
        
        op.add_option("--includedoc",   
                      action="store_true",     
                      dest="include_doc", 
                      help="Should be included document",
                      default=False
                      )
    
        op.add_option("--includeid",   
                      action="store_true",     
                      dest="include_id", 
                      help="Should be document id included",
                      default=False)       
        
         
        op.add_option("--grouplevel", 
                      action="store", 
                      type="int", 
                      dest="group_level", 
                      help="Grouping level", 
                      default=0)  
        
        op.add_option("--keyflagt", #True, False, None
                      action="store_true",     
                      dest="keyflag", 
                      help="Flter by key value true",
                      default=None)
        
        op.add_option("--keyflagf", #True, False, None
                      action="store_false",     
                      dest="keyflag", 
                      help="Flter by key value false",
                      default=None)
        
        (o, self.args) = op.parse_args(self.arguments)
        self.options = vars(o)
        
    def debug_arguments(self):
        print self.options
        print self.args
        
    def show_keys(self):
        akeys = self.database.all_keys()    
        print self.table_for_printing(akeys, [self.COLUMN_KEY, 
                                              self.COLUMN_COUNT])
        
    def show_bvalues(self):
        bvals = self.database.b_values()
        print self.table_for_printing(bvals, [self.COLUMN_BFIELD, 
                                              self.COLUMN_COUNT])
        
    def b_value_filter(self):
        bval = self.expect_nothing_or_int(self.options['bfield_interval'][0]) #can throw ExpectedNullOrInteger
        bend = self.expect_nothing_or_int(self.options['bfield_interval'][1])        
        bvals = self.database.filter_by_b(bval, bend, self.options['group_level']>0)
    
        if self.options['group_level'] == 0:
            coulumn_set = [self.COLUMN_ID, self.COLUMN_BFIELD, self.COLUMN_RUN]
        else:
            coulumn_set = [self.COLUMN_BFIELD, self.COLUMN_RUN, 
                           self.COLUMN_COUNT]
        
        print self.table_for_printing(bvals, coulumn_set)
        
    def generate_doc_id(self, run, lumi, dataset):
        '''
        From run, lumi and dataset generated document id 
        '''
        return "{0}-{1}-{2}".format(long(run), long(lumi), hashlib.md5(dataset).hexdigest())
    
    def get_doc_rld(self):
        run = self.options['run']
        lumi = self.options['lumi']
        dataset = self.options['dataset']
        id = self.generate_doc_id(run, lumi, dataset)
        return DQISResult(dqis_db = self.database, dict= self.database.document(id))
    
    def get_document_id_or_rdl(self):
        if self.options['doc_id']:
            return DQISResult(dqis_db = self.database, dict= self.database.document(self.options['doc_id']))
        else:
            return self.get_doc_rld()
       
        
    def get_connection(self):
        '''
        From options extracts connection info and gives DQISDatabase object
        accepts dict with keys db_name, db_address. If data is not set - taken 
        defaut values {'db_name':"dqis", "db_address":""} 
        '''
        db = self.options.get(self.C_DATABASE_NAME , self.D_DATABASE_NAME)
        adr = self.options.get(self.C_DATABASE_ADDRESS, self.D_DATABASE_ADDRESS)        
        self.database = DQISDatabase(db, adr)
        
    def edit_bfield(self): #run, lumi, dataset, args, bfield
        '''
        In args has to only one parameter - bfield.
        '''

        doc = self.get_document_id_or_rdl()
        bval = self.expect_nothing_or_int(self.options['bfield'])        
        doc['bfield'] = bval
        doc.save()
        
    def primary_datasets(self): #
        dvals = self.database.primary_datasets_count(self.options['group_level']>0) #if data should be grouped
        if self.options['group_level'] >0:
            print self.table_for_printing(dvals, [self.COLUMN_PDATASET, 
                                                  self.COLUMN_COUNT, 
                                                  self.COLUMN_RUN])        
        else:
            print self.table_for_printing(dvals, [self.COLUMN_PDATASET, 
                                                  self.COLUMN_COUNT])      
            
    def del_doc_by_id(self, id):
        doc = self.get_document_id_or_rdl()    
        try:   
            doc = DQISResult(dqis_db = self.database, 
                             dict= self.database.document(id))
            doc.delete()
            doc.save()
        except:
            raise DocumentCouldNotBeDeleted(id)
        
    def del_doc_rld(self, run, lumi, dataset): # many should take data from self
        id = self.generate_doc_id(run, lumi, dataset)
        return self.del_doc_by_id(id)
    
    def delete_doc(self):
        if self.options['doc_id']:
            self.del_doc_by_id(self.options['doc_id'])
        else:
            self.del_doc_rld(self.options['run'], self.options['lumi'], self.options['dataset'])
    
    def show_doc(self):
        d = self.get_document_id_or_rdl()
        rez = "ID: {0}\nRev: {1}\nRun: {2}\nLumi: {3}\nDataset: {4}\nbField: \
        {4}\nTimestamp: {5}\nKeys:"
        rez = rez.format(d['_id'], d['_rev'], d['run'], 
                         d['lumi'], "/"+ "/".join(d['dataset']), str(d['bfield']),
                        d['timestamp']) #how about history
        for k in d['map'].keys():
            rez += "* {0:30} {1}\n".format(k, d['map'][k])
        print rez
        
    def record_map_history(self, doc):
        '''
        Add the current map to map_history and return the doc
        '''
        if not doc.has_key('map_history'):
            doc['map_history'] = []
        
        doc['map_history'].append(doc['map'])
        return doc

    def remove_key(self):
        '''
        In single_keys is list of keys for removing
        '''
        doc = self.get_document_id_or_rdl()
        doc = self.record_map_history(doc) #moved up, for avoiding multiple history entries
        for k in self.options['single_keys']:
            if doc['map'].has_key(k):                
                del doc['map'][k]
        doc.save()
        

    def edit_keys(self): # or add
        '''
        In args has to be key value pairs
        '''
        doc = self.get_document_id_or_rdl()
        doc = self.record_map_history(doc)
        for k, v in self.options['keys']:
            doc['map'][k] = v
        doc.save()

    def download_doc(self):
        '''
        Downloading document by id to file
        '''
        d = self.get_document_id_or_rdl()
        if self.options['filename']:
            try:
                #del d['_id']
                #del d['_rev']
                f = open(self.options['filename'], mode='w')
                json.dump(d, f)
                f.close()
            except: #maby to throw common exceptions
                print "Document could not be saved"
        else:
            print "File name required"  
            
    def push_doc(self):
        '''
        Pushing document by run lumi dataset. Pushing from file
        '''
        if self.options['filename']:
            try:
                f = open(self.options['filename'], 'r')
                entry = json.load(f)
            except:
                print "Bad file name or file content"
                exit() #maby to throw common exceptions
        else:
            print "File name required"
            exit()    
        dts = "/"+"/".join(entry['dataset'])
        id = self.generate_doc_id(entry['run'], entry['lumi'], dts)    
        entry['_id'] = id
        if entry.has_key('_rev'):
            del entry['_rev']
        d = DQISResult(dqis_db=self.database, dict=entry)
        d.save() #check conflict errors. delete rev

    def create_doc(self): #what to do if document ID is existing
        '''
        It takes run, lumi dataset. In args first parameter has to be bfield.
        Other following variables in args - key value pairs. 
        '''
        run = self.options['run']
        lumi = self.options['lumi']
        dataset = self.options['dataset']
        bfield = self.options['bfield']
        id = self.generate_doc_id(run, lumi, dataset)
        bfield = self.expect_nothing_or_int(bfield) #can thow exception
        doc = {'bfield': bfield, 
               '_id': id,
               'dataset': dataset.split("/")[1:],
               'run': long(run),
               'lumi': long(lumi)}
        
        doc['map'] = {}
        
        for k, v in self.option['keys']:
            doc['map'][k] = bool(v) # adding keys
            
        db = self.get_connection() #TODO give connection
        r = DQISResult(dqis_db = db, dict = doc)
        r.save()
        
    def expect_int_or_val(self, value, other_val):
        try:
            return long(value)
        except:
            return other_val  
        
    def filter_keys(self):
        rs = self.expect_int_or_val(self.options['run_interval'][0], 0)
        re = self.expect_int_or_val(self.options['run_interval'][1], "a")
        
        gl = self.options['group_level']
        if gl == 0: 
            gl = 3
            
        fkeys = self.database.filter_keys(
                    key=self.options['single_keys'][0], #was key. acept only first 
                    run_start=rs, 
                    run_end=re, 
                    key_flag=self.options['keyflag'], 
                    include_id=self.options['include_id'] , 
                    include_doc=self.options['include_doc'] , 
                    group_level=gl)
        if self.options['include_doc']:
            print self.table_for_printing(fkeys, [self.COLUMN__ID, self.COLUMN_RUN, self.COLUMN_BFIELD])
        elif self.options['include_id']:
            print self.table_for_printing(fkeys, [self.COLUMN_KEY, self.COLUMN_COUNT, self.COLUMN_ID])
        else:
            if self.options['group_level'] == 1:
                print self.table_for_printing(fkeys, [self.COLUMN_KEY,  self.COLUMN_COUNT])
            elif self.options['group_level'] == 2:
                print self.table_for_printing(fkeys, [self.COLUMN_KEY, self.COLUMN_RUN,  self.COLUMN_COUNT])
            else:
                print self.table_for_printing(fkeys, [self.COLUMN_KEY, self.COLUMN_RUN, self.COLUMN_FLAG,  self.COLUMN_COUNT])



#

#class BadAdditionalArgumetsCreateDoc(Exception):
#    
#    def __init__(self, value):
#        self.value = value
#        
#    def __str__(self):
#        return "You have togive at leat one argument (bfield) ad key and value pairs. Your arguments: %s" % str(self.value)
#    
#class BadAdditionalArgumetsEditBField(Exception):
#    
#    def __init__(self, value):
#        self.value = value
#        
#    def __str__(self):
#        return "After base arguments have to follow one value - bfield. Now is %d args" % len(self.value)
#    
#class BadAdditionalArgumetsEditKey(Exception):
#    
#    def __init__(self, value):
#        self.value = value
#        
#    def __str__(self):
#        return "After base arguments have to follow key value pairs. Now is %d args" % len(self.value)    
#    
#    
#
#def check_argument_count_create_doc(args):
#    if (len(args) < 1) or (len(args) % 2 == 0):
#        raise BadAdditionalArgumetsCreateDoc(args)
#

#    
#def choose_action(args):

#    except (DocumentCouldNotBeDeleted, BadAdditionalArgumetsCreateDoc, BadAdditionalArgumetsEditBField, BadAdditionalArgumetsEditKey) as ex:
#        print ex 
#    except ExpectedNullOrInteger, e:
#        print e
#    except (socket.error, httplib.HTTPException), e:
#        print "Socket error. Check if database is running and connection parameters(first two)."

        
    def action_not_found(self):
        pass #raise
        
    def execute(self):
        self.options_parser()
        self.get_connection()
        self.actions_map.get(self.options['action'], self.action_not_found)()
        
    def __init__(self, arguments):        
        self.arguments = arguments
        self.actions_map = {
            'keys': self.show_keys, #+
            'bvals': self.show_bvalues, #+
            'pdatasets': self.primary_datasets,#+ (uses group level as group)
            'show': self.show_doc, #+ #TODO: update history
            'download': self.download_doc,#+ #requires id/rdl
            'push': self.push_doc,#+
            'bvalfilt': self.b_value_filter,#+            
            'ebfield': self.edit_bfield, #+   
            'editk': self.edit_keys,#+
            'removek': self.remove_key,#+
            'delete': self.delete_doc,#+
                        
            'filterk': self.filter_keys,            
        } 
        
        

args = "-h".split()
#todo - show connection parameters
args = "-a keys".split()
args = "-a bvals".split()
args = "-a pdatasets".split()
args = "-a show --id=100215-0-1e3918471802abcc83d16192eb21d160".split() 
args = "-a show --run=100215 --lumi=0 --dataset=/OfflineMonitor/Commissioning09-Express-v2/FEVTDEBUGHLT".split()
args = "-a download --id=100215-0-1e3918471802abcc83d16192eb21d160 --filename=d.txt".split()
args = "-a push --filename=d.txt".split()
#DQIS_CLI_App(args).execute()
args = "-a bvalfilt --bfield_interval 20 4000".split()
args = "-a bvalfilt --bfield_interval null null".split()
args = "-a bvalfilt --bfield_interval null 4000 --grouplevel=1".split() #0 or 1. default 0
args = "-a ebfield --id=100215-0-1e3918471802abcc83d16192eb21d160 --bfield 101".split() #0 or 1. default 0
args = "-a editk --id=100215-0-1e3918471802abcc83d16192eb21d160 -k foo bar".split() #-k can be used multiple times
args = "-a removek --id=100215-0-1e3918471802abcc83d16192eb21d160 --skey foo".split()
args = "-a delete --id=100215-0-1e3918471802abcc83d16192eb21d160".split() #deleting non existing/
args = "-a filterk --skey rpc_shift_offline --grouplevel=3".split() #takes only first skey #. gl 0 does not exist
args = "-a filterk --skey rpc_shift_offline --run_interval 50000 60000 --grouplevel=3".split()  
args = "-a filterk --skey rpc_shift_offline --includedoc --grouplevel=3".split() # keyflag(f/t) shoud not be used because of incoorect views
#can be used --includeid for filter k

#TODO: if there is no connection
args = sys.argv
DQIS_CLI_App(args).execute()

