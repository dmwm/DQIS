from WMCore.Database.CMSCouch import Database, Document

# Tests are written with demo mofration data
# TODO: test DQISResult ,filter_keys,filter_by_b, find out bvalues exception, null-none

class DatabaseNotSetException(Exception):
    """
    Raised when DQISResult tries to makes actions with DB,  DB connection is not set
    """
    
    def __init__(self, value):
        """      
        Database is not set. Exception raised by dummy_test_for_coverage
        """
        self.value = value
        
    def __str__(self):
        return "Database is not set. Exception raised by %s" % str(self.value)
    
class DQISResultNotSavable(Exception): 
    """
    Raised when DQISResult tries to be saved, but DQISResult don't have ID.
    """
    
    def __init__(self, value):
        """
        DQISResult is not saveable. Exception raised by dummy_test_for_coverage
        """
        self.value = value
        
    def __str__(self):
        return "DQISResult is not saveable. Exception raised by %s" % str(self.value)


class DQISResult(Document):  
    __getattr__= dict.__getitem__
    
    #TODO: dqis_db should be private? 
    def __init__(self, dqis_db=None, savable=False, *args, **kwargs): 
        Document.__init__(self, *args, **kwargs)
        self.dqis_db = dqis_db
        #self.savable = savable #savable, when has id or _id
        
    def _require_db_connection(self):
        """
        If DB is not set then it is raised DatabaseNotSetException        
        """
        if not self.dqis_db or not isinstance(self.dqis_db, Database):
            raise DatabaseNotSetException(self)
            
    def _find_id(self):
        """
        Tries to find document ID or returns empty string
        
        """
        #in normal case is set one, one or both with the smae value.
        doc_id = self.get('id', "") #because "" can not be database name
        doc_id = self.get('_id', doc_id)
        return doc_id
            
    def _require_savable(self):
        """
        Document is saveable if pssible to find "_id". Gettable if has "_id" or "id"      
        """
        if not self.get('_id', False):
            raise DQISResultNotSavable(self)
        
        
    def save(self, *args, **kwargs):
        """
        Even document is deleted, deletion has to be saved.
        Instant saving. If you need to modify a lot of documents - use 
        saving_queue        
        """
        self._require_db_connection()
        self._require_savable()
        #for avoiding generating random id
        return self.dqis_db.commitOne(self,*args, **kwargs) 
    
    
    def saveToQueue(self, *args, **kwargs):
        """
        Adding document to parent database saving queue. It is lazy saving 
        so it is required to coll commit byt DB object in the end of commits.
        #possible to add exception testing      
        """
        self._require_db_connection()
        self._require_savable()
        return self.dqis_db.queue(self,*args, **kwargs)
        
    def get_document(self):
        """
        If object has id or _id atributes and has connection, then get whole document.        
        """
        #get doc and save - both requires ID
        doc_id = self._find_id()
        if doc_id:
            return DQISResult(dict = self.dqis_db.document(doc_id), savable=True, dqis_db=self.dqis_db)
        else:
            raise DQISResultNotSavable(self) 

    
class DQISDatabase(Database):
    """
    Interface to CouchDB for DQIS (Data quality information system).
    """
    
    DESIGN = "dqis"
    VIEW_KEYS = "keys"
    VIEW_BFIELD = "bfield"
    VIEW_DATASETS = 'primary_datasets'
    
    def __init__(self, *args, **kwargs):
        Database.__init__(self, *args, **kwargs)
        
    def all_keys(self):
        """
        Returns all keys and how many times it is dounded in database.
        Returns array of DQISResult objet. Object has following attributes: key, count
        http://127.0.0.1:5984/dqis/_design/dqis/_view/keys?group=true&group_level=1
        
        >>> dqis = DQISDatabase('dqis','localhost:5984')
        >>> akeys = dqis.all_keys()
        >>> akeys[0].key
        u'csc_certification'
        >>> akeys[0].count
        11
        >>> len(akeys)
        31
        """
        
        options = {
            'group': True,
            'group_level': 1
        }
        rez = self.loadView(self.DESIGN, self.VIEW_KEYS, options)
        
        results = []      
        for hash in rez['rows']:
            dqis_r = DQISResult()
            dqis_r['key'] = hash['key'][0] 
            dqis_r['count'] = hash['value']
            results.append(dqis_r) 
        
        return results
    
    
    def filter_keys(self, key, run_start=0, run_end="a", key_flag=None, include_id=False, include_doc=False, group_level=1):
        """
        Filters documents by key and run interval (run_start, run_end).
        key_flag can be True, False and None (for True and False)
        If  include_id or include_doc is set to True, results are not grouped.
        If data is grouped, then group_levels defines:
        * 1 - group by key (returns list of DQISResult objects with attributes: key, and count)
        * 2 - group by key and run (returns list of DQISResult objects with attributes: key, run, count)
        * 3 or more - don't group at all (returns list of DQISResult objects with attributes: key, run, flag, count=1)
        
        include_id adds to each DQISResult attribute id, and  include_doc - all all document's attributes
        http://127.0.0.1:5984/dqis/_design/dqis/_view/keys?startkey=[%22csc_shift_offline%22,46700,true]&endkey=[%22csc_shift_offline%22,56700,true]&group=true
        
        >>> #include id, doc, , guven key, given run atart/end, gven same, given flag
        >>> dqis = DQISDatabase('dqis','localhost:5984')
        >>> fkeys = dqis.filter_keys("l1t_shift_offline")
        >>> fkeys[0].count
        926
        >>> fkeys = dqis.filter_keys("l1t_shift_offline", group_level=2)
        >>> fkeys[-1].run
        124008
        >>> fkeys = dqis.filter_keys("l1t_shift_offline", group_level=3)
        >>> (fkeys[-1].run, fkeys[-1].flag)
        (124008, True)
        >>> fkeys = dqis.filter_keys("l1t_shift_offline", include_id = True)
        >>> fkeys[0].id != 0 #if id does't exist - exception
        True
        >>> fkeys = dqis.filter_keys("l1t_shift_offline", include_doc = True)
        >>> b = fkeys[0].bfield #othe case - exception
        >>> fkeys = dqis.filter_keys("l1t_shift_offline", key_flag=True, group_level=3) # is it good??
        >>> fkeys[-1].run
        124008
        """
        if key_flag == None:
            flag_s = False
            flag_e = True
        else:
            flag_s = flag_e = key_flag
            
        options = {
            'startkey': [key,run_start, flag_s],
            'endkey': [key,run_end, flag_e],
            'group': True
        }
        
        if (include_id or include_doc):
            options['group'] = False
            #options['reduce'] = False
            if include_doc:
                options['include_docs'] = True
            else:
                options['include_id'] = True
            
          
        if options['group']:
            options['group_level'] = group_level
        else:
            options['reduce'] = False
            del options['group']
            
        rez = self.loadView(self.DESIGN, self.VIEW_KEYS, options)
        
        results = []
        for hash in rez['rows']:
            if include_doc:
                dqis_r = DQISResult(dict = hash['doc'], dqis_db=self)
                #dqis_r.savable = True
            else:
                dqis_r = DQISResult(dqis_db=self)
                dqis_r['key'] = hash['key'][0]
                if len(hash['key']) > 1:
                    dqis_r['run'] = hash['key'][1]
                if len(hash['key']) > 2:    
                    dqis_r['flag'] = hash['key'][2]
                dqis_r['count'] = hash['value']
                if hash.has_key('id'):
                    dqis_r['id'] = hash['id']
                    
            results.append(dqis_r)
        
        return results
        
    
    
    def primary_datasets_count(self, by_run=False):
        """
        Returns array of DQISResult objects. Each object contains primary dataset name (pdataset) and count. If flag
        by_run=True, then data is grouped by run and to object added run atribute.
        http://127.0.0.1:5984/dqis/_design/dqis/_view/primary_datasets?group=true&group_level=1
        http://127.0.0.1:5984/dqis/_design/dqis/_view/primary_datasets?group=true&group_level=2
        
        >>> dqis = DQISDatabase('dqis','localhost:5984')
        >>> dataset = dqis.primary_datasets_count()
        >>> len(dataset)
        23
        >>> dataset[22].pdataset
        u'StreamExpress'
        >>> dataset[22].count
        134
        >>> dataset = dqis.primary_datasets_count(True)
        >>> dataset[-1].pdataset
        u'StreamExpress'
        >>> dataset[-1].run
        112493
        >>> dataset[-1].count
        4
        >>> dataset[-1] == {"count":4,"run":112493,"pdataset":u'StreamExpress'}
        True

        """
        options = {
            'group': True,
            'group_level': 1,
        }
        
        if by_run:
            options['group_level'] = 2
            
        rez = self.loadView(self.DESIGN, self.VIEW_DATASETS, options)
        
        results = []
        
        for hash in rez['rows']:
            dqis_r = DQISResult(dqis_db=self)         
            dqis_r['pdataset'] = hash['key'][0]
            dqis_r['count'] = hash['value'] 
            if by_run:
                dqis_r['run'] = hash['key'][1]
            results.append(dqis_r)
            
        return results
        
            
    
    def b_values(self):
        """
        Returns array of DQISResult. Objets contains bfield and count (total count of specific bfield value in database).
        http://127.0.0.1:5984/dqis/_design/dqis/_view/bfield?group=true&group_level=1
        
        >>> dqis = DQISDatabase('dqis','localhost:5984')
        >>> bval = dqis.b_values()
        >>> len(bval)
        11
        >>> print bval[0].bfield #Without printing cannot be detected None type
        None
        >>> bval[0].count
        1979
        >>> bval[10].bfield
        3801
        >>> bval[-1].bfield
        3801
        >>> bval[-1].count
        16
        """
        
        
        options = {
            'group': True,
            'group_level': 1,
        }
        
        rez = self.loadView(self.DESIGN, self.VIEW_BFIELD, options)
        
        results = []
        
        for hash in rez['rows']:
            dqis_r = DQISResult(dqis_db=self)         
            dqis_r['bfield'] = hash['key'][0]
            dqis_r['count'] = hash['value']            
            results.append(dqis_r)
            
        return results
        
        
    
    def filter_by_b(self, bval, bval_end=None, group=False):    
        """                
        Filters documents specified b value (or values range if bval_end is set. bval_end is included).
        Returns array of DQISDocument objects.
        If group equals to False - Object contains following attributes: id, bfield, run.
        If group equals to True - Results are grouped by bfield and run and counted. Each DQISDocument contains
        bfield, run, and count.            
        
        Data is sorted by these rules: http://wiki.apache.org/couchdb/View_collation
        If group=False
        http://127.0.0.1:5984/dqis/_design/dqis/_view/bfield?startkey=[18]&endkey=[18,"a"]&reduce=false
        
        If group=True
        http://127.0.0.1:5984/dqis/_design/dqis/_view/bfield?startkey=[3800]&endkey=[3805]&group=true&group_level=2
        
        >>> dqis = DQISDatabase('dqis','localhost:5984')
        >>> bval = dqis.filter_by_b(1122)
        >>> len(bval)
        6
        >>> bval[-1] == {
        ... "id": u'61739-0-f7346619b3dd8a1ec236a5e69ed6b612',
        ... "bfield": 1122,
        ... "run": 61739
        ... }
        True
        >>> len(dqis.filter_by_b(None))
        1979
        >>> bval = dqis.filter_by_b(1122, 1133)
        >>> len(bval)
        7
        >>> sorted(bval[0].keys())
        ['bfield', 'id', 'run']
        >>> bval = dqis.filter_by_b(1122, 1133, group=True)
        >>> len(bval)
        2
        >>> sorted(bval[0].keys())
        ['bfield', 'count', 'run']
        """
        
        if bval_end == None:
            bval_end = bval
        
        options = {
            'startkey': [bval],
            'endkey': [bval_end,"a"]
        }
        
        if group == False:
            options['reduce'] = False
        else:
            options['group'] = True
            options['group_level'] = 2
        
        rez = self.loadView(self.DESIGN, self.VIEW_BFIELD, options)
        
        results = []
        
        for hash in rez['rows']:
            dqis_r = DQISResult(dqis_db=self)
            if group:
                dqis_r['count'] = hash['value']
            else:
                dqis_r['id'] = hash['id']            
            dqis_r['bfield'] = hash['key'][0]
            dqis_r['run'] = hash['key'][1]            
            results.append(dqis_r)
            
        return results
    
    
if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=False)
    