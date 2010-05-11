'''
Created on 7 May 2010

@author: metson
'''
from WMCore.Database.CMSCouch import CouchServer
from DQIS.API.Document import Document
from DQIS.API.Database import Database
import json, unittest, commands

class TestDatabase(unittest.TestCase):
    def setUp(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        
        couch = CouchServer(dburl='admin:password@localhost:5984')
        if dbname not in couch.listDatabases():
            couch.createDatabase(dbname)
        couch.connectDatabase(dbname)
        self.db = Database(dbname, couch.url)
    
        #insert 5 known records
        self.db.queue({
               "_id": "1234-1-f28ca5a7388b8f6ade71b43c4f4b7669",
               "bfield": 4000,
               "map": {
                   "dt_shift_online": True,
                   "hlt_shift_online": True,
                   "_meta": {
                       "timestamp": "2010-04-14 18:04:58.087723",
                       "user": "metson"
                   }
               },
               "run": 1234,
               "map_history": [
               ],
               "dataset": [
                   "Cosmics",
                   "Commissioning09-MuAlStandAloneCosmics-v2",
                   "ALCARECO"
               ],
               "lumi": 1
            })
        self.db.queue({
               "_id": "1234-2-f28ca5a7388b8f6ade71b43c4f4b7669",
               "bfield": 4000,
               "map": {
                   "dt_shift_online": True,
                   "hlt_shift_online": False,
                   "_meta": {
                       "timestamp": "2010-04-14 18:04:58.087723",
                       "user": "metson"
                   }
               },
               "run": 1234,
               "map_history": [
               ],
               "dataset": [
                   "Cosmics",
                   "Commissioning09-MuAlStandAloneCosmics-v2",
                   "ALCARECO"
               ],
               "lumi": 2
            })
        self.db.queue({
               "_id": "1234-3-f28ca5a7388b8f6ade71b43c4f4b7669",
               "bfield": 2000,
               "map": {
                   "dt_shift_online": True,
                   "hlt_shift_online": True,
                   "_meta": {
                       "timestamp": "2010-04-14 18:04:58.087723",
                       "user": "metson"
                   }
               },
               "run": 1234,
               "map_history": [
               ],
               "dataset": [
                   "Cosmics",
                   "Commissioning09-MuAlStandAloneCosmics-v2",
                   "ALCARECO"
               ],
               "lumi": 3
            })      
        self.db.queue({
               "_id": "5678-2-f28ca5a7388b8f6ade71b43c4f4b7669",
               "bfield": 2000,
               "map": {
                   "dt_shift_online": False,
                   "hlt_shift_online": True,
                   "_meta": {
                       "timestamp": "2010-04-14 18:04:58.087723",
                       "user": "metson"
                   }
               },
               "run": 5678,
               "map_history": [
               ],
               "dataset": [
                   "Cosmics",
                   "Commissioning09-MuAlStandAloneCosmics-v2",
                   "ALCARECO"
               ],
               "lumi": 2
            })
        self.db.queue({
               "_id": "5678-1-f28ca5a7388b8f6ade71b43c4f4b7669",
               "bfield": 4000,
               "map": {
                   "dt_shift_online": True,
                   "hlt_shift_online": True,
                   "_meta": {
                       "timestamp": "2010-04-14 18:04:58.087723",
                       "user": "metson"
                   }
               },
               "run": 5678,
               "map_history": [
               ],
               "dataset": [
                   "Cosmics",
                   "Commissioning09-MuAlStandAloneCosmics-v2",
                   "ALCARECO"
               ],
               "lumi": 1
            })
          
        self.db.commit()
        
        cmd = "couchapp push ../../../../src/couchapp/dqis/. http://admin:password@localhost:5984/%s" % dbname
        commands.getstatusoutput(cmd)
                
    def tearDown(self):
        if self._exc_info()[0] == None:
            testname = self.id().split('.')[-1].lower()
            CouchServer(dburl='admin:password@localhost:5984').deleteDatabase('dqis_%s' % testname)
    
    def testWriteDoc(self):
        d = Document(1, 2, '/foo/bar/baz', 'metson', 3990, {'ecal': True})
        self.db.queue(d)
        self.db.commit()
        
        d_from_db = self.db.document(d['_id'])
        for k, v in d_from_db.iteritems():
            if k != '_rev':
                assert d[k] == v, 'Failed for %s: %s != %s' % (k, v, d[k])
        
    def testCRABSearch(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        uri = '/%s/_design/dqis/_list/crab/run_lumi/' % dbname
        
        data = {'bfield': 4000}
        
        crab_list = self.db.post(uri, data)
        
        assert len(crab_list['1234']) == 2, 'wrong number of records returned'

    def testBFieldSearch(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        uri = '/%s/_design/dqis/_list/search/run_lumi/' % dbname
        
        data = {'bfield': 2000}
        
        search_list = self.db.post(uri, data)
        
        assert len(search_list) == 2, 'wrong number of records returned'
        for doc in search_list:
             assert doc['value']['bfield'] == data['bfield'], 'wrong records returned'
    
    def testMapSearch(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        uri = '/%s/_design/dqis/_list/search/run_lumi/' % dbname
        
        data = {'map':{"dt_shift_online": True, "hlt_shift_online": True}}
        
        search_list = self.db.post(uri, data)
        
        for record in search_list:
            for key in data['map'].keys():
                assert record["value"]["map"][key] == data['map'][key], "key didn't match query" 
            
    def testCombinedSearch(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        uri = '/%s/_design/dqis/_list/search/run_lumi/' % dbname
        
        data = {'bfield': 4000, 
                'map':{"dt_shift_online": True, "hlt_shift_online": True}}
        
        search_list = self.db.post(uri, data)
        
        for record in search_list:
            assert record["value"]["bfield"] == data['bfield'], "bfield didn't match query"
            for key in data['map'].keys():
                assert record["value"]["map"][key] == data['map'][key], "key didn't match query" 
            
    def testSearchRunLimit(self):
        dbname = 'dqis_%s' % self.id().split('.')[-1].lower()
        uri = '/%s/_design/dqis/_list/search/run_lumi/?startkey=1234&endkey=1236' % dbname
        
        data = {'bfield': 4000, 
                'map':{"dt_shift_online": True, "hlt_shift_online": True}}
        
        search_list = self.db.post(uri, data)
        
        for record in search_list:
            # this next one is really a test of CouchDB not this code...
            assert record["value"]["run"] == record["key"]
            assert 1234 <= record["value"]["run"] <= 1236
            assert record["value"]["bfield"] == data['bfield'], "bfield didn't match query"
            for key in data['map'].keys():
                assert record["value"]["map"][key] == data['map'][key], "key didn't match query"         
        
if __name__ == '__main__':
    unittest.main()
