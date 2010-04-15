import sys, os, unittest
import commands
from WMCore.Database.CMSCouch import CouchServer, Database

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), os.path.pardir, os.path.pardir,  os.path.pardir, ) 
#Nasty Hack
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src', 'python',))
                    


from DQIS import API
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

    def test_save(self):
        document = {"_id": "abc", "test":"data"}
        r = API.DQISResult(dqis_db = self.db, dict = document)
        all_docs_count_before = len(self.db.allDocs()['rows'])
        r.save()
        all_docs_count_after = len(self.db.allDocs()['rows'])        
        
        self.assertEqual(all_docs_count_before +1, all_docs_count_after)
        
#        >>> doc = db.document("abc")
#        >>> r = DQISResult(dict=doc, dqis_db = db)
#        >>> doc["test"]
#        'data'
#        >>> r.delete()
#        >>> db.commitOne(r) #doctest: +ELLIPSIS
#        {...}



#def testDeleteDoc(self):
#        doc = {'foo':123, 'bar':456}
#        self.db.commitOne(doc)
#        
#        
#        # The db.delete_doc is immediate
#        id = all_docs['rows'][0]['id']
#        self.db.delete_doc(id)
#        all_docs = self.db.allDocs()
#        self.assertEqual(0, len(all_docs['rows']))

        pass
        
        
        
        
                
#        >>> DQISResult()._require_savable()
#        Traceback (most recent call last):
#        ...
#        DQISResultNotSavable: DQISResult is not saveable. Exception raised by {}
#        >>> DQISResult(dict = {'_id': "123"})._require_savable()
#        
#        
#        
#        self.assertEqual(1,2)

    def test_save_to_queue(self):
#        >>> r = DQISResult(dqis_db = Database(), dict = {"_id": "abc"})
#        >>> len(r.dqis_db._queue)
#        0
#        >>> r.saveToQueue()
#        >>> len(r.dqis_db._queue) 
#        1
        # make sure the shuffled sequence does not lose any elements
        #random.shuffle(self.seq)
        #self.seq.sort()
        #self.assertEqual(self.seq, range(10))
#        self.assertEqual(1,2)
        pass

    def test_get_document(self):
#        self.assertEqual(1,2)
#        
#        >>> doc_id = '100215-0-38bc1d29bd22844103e86f9a000500e2' 
#        >>> r = DQISResult(Database(dbname="dqis"))
#        >>> r['id'] = doc_id
#        >>> doc = r.get_document()
#        >>> doc.run
#        100215
#        >>> doc_id = '' 
#        >>> r = DQISResult(Database(dbname="dqis"))
#        >>> r['id'] = doc_id
#        >>> doc = r.get_document() #doctest: +IGNORE_EXCEPTION_DETAIL
#        Traceback (most recent call last):
#        ...
#
#        DQISResultNotSavable: DQISResult is not saveable. Exception raised by {'id': ''}
        pass
        
    def test_find_id(self):
#        >>> DQISResult()._find_id() == ""
#        True
#        >>> DQISResult(dict = {'id': "123"})._find_id()
#        '123'
#        >>> DQISResult(dict = {'_id': "abc"})._find_id()
#        'abc'
        pass    

   

if __name__ == '__main__':
    unittest.main()
