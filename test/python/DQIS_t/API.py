import sys, os, unittest
import commands
from WMCore.Database.CMSCouch import CouchServer, Database

from DQIS import API
from DQIS.API import *
import test_data

class TestDQISResult(unittest.TestCase):
    DB_NAME = 'dqis_test'
    DB_URL = 'localhost:5984'

    def setUp(self):        
        couch = CouchServer(dburl=self.DB_URL)
        if self.DB_NAME in couch.listDatabases():
            couch.deleteDatabase(self.DB_NAME)
        
        cdb = couch.connectDatabase(self.DB_NAME)

        #for dq_t in test_data.demo_data:
        #    cdb.queue(dq_t)
        
        cdb.commit()
        
        self.db = Database(dbname=self.DB_NAME)
        
    
    def test_init(self):        
        #self.assertEqual(1,2)
        pass

    def test_save_and_delete(self):
        #Shoud document get revision number after save?
        #Document can not be saved and then deleted. Because save returns not a DQISResult object!
        
        #Tests document saving 
        document = {"_id": "abc", "test":"data"}
        r = API.DQISResult(dqis_db = self.db, dict = document)
        all_docs_count_before = len(self.db.allDocs()['rows'])
        r.save()
        all_docs_count_after_insert = len(self.db.allDocs()['rows'])        
        
        self.assertEqual(all_docs_count_before +1, all_docs_count_after_insert)
        
        
        #Test delete
        doc = self.db.document("abc")
        r = API.DQISResult(dict=doc, dqis_db = self.db)
        self.assertEqual(doc["test"], "data")
        r.delete()
        self.db.commitOne(r)
        all_docs_count_after_deleting = len(self.db.allDocs()['rows']) 
        self.assertEqual(all_docs_count_before, all_docs_count_after_deleting )
        
    def test_savable(self):
        #Does ID has to raise exception
        rez = API.DQISResult(dict = {'_id': "123"})._require_savable()
        self.assertEqual(rez, None)
        self.assertRaises(DQISResultNotSavable, 
                    API.DQISResult(dict = {'id': "123"})._require_savable )
        self.assertRaises(DQISResultNotSavable, 
                    API.DQISResult(dict = {'abc': "123"})._require_savable )
        
    def test_find_id(self): #similar to test_savable
        self.assertEqual(DQISResult()._find_id(), "")
        self.assertEqual(DQISResult(dict = {'id': "123"})._find_id(), "123")
        self.assertEqual(DQISResult(dict = {'_id': "123"})._find_id(), "123") 
        
    def test_find_id(self):
        id1 = API.DQISResult()._find_id()
        id2 = API.DQISResult(dict = {'id': "123"})._find_id()
        id3 = API.DQISResult(dict = {'_id': "abc"})._find_id()
        self.assertEqual(id1, "")
        self.assertEqual(id2, '123')
        self.assertEqual(id3, 'abc')
        
    def test_require_saveable(self):
        dr1 = API.DQISResult()._require_savable
        #dr2 = API.DQISResult(dict = {'_id': "123"})._require_savable
        self.assertRaises(DQISResultNotSavable, dr1)
        #self.assertEqual(None, dr2())
        
    def test_save_to_queue(self):
        r = DQISResult(dqis_db = Database(), dict = {"_id": "abc"})
        queue_size_before = len(r.dqis_db._queue)
        r.saveToQueue()
        queue_size_after = len(r.dqis_db._queue) 
        self.assertEqual(queue_size_before, 0)
        self.assertEqual(queue_size_after, 1)
        r.dqis_db._reset_queue()
        
        
    def test_require_db(self):
        f = DQISResult()._require_db_connection
        self.assertRaises(DatabaseNotSetException, f)  
        
        f = DQISResult(dqis_db = "dqis_db")._require_db_connection
        self.assertRaises(DatabaseNotSetException, f)  
        
        f = DQISResult(dqis_db = Database())._require_db_connection
        self.assertEqual(None, f())



    def test_get_document(self):
        doc_id = '100215-0-38bc1d29bd22844103e86f9a000500e2' 
        r = API.DQISResult(API.Database(dbname="dqis"))
        r['id'] = doc_id
        doc = r.get_document()
        self.assertEqual(doc.run, 100215)
        doc_id = '' 
        r = DQISResult(Database(dbname="dqis"))
        r['id'] = doc_id
        fdoc = r.get_document 
        fdoc()
        self.assertRaises(DQISResultNotSavable, fdoc) # because get and s
                                                      # savable shares _id
                
 

   

if __name__ == '__main__':
    unittest.main()
