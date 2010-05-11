'''
Created on 7 May 2010

@author: metson
'''
from WMCore.Database.CMSCouch import Document as CouchDocument
from datetime import datetime
from hashlib import md5

class Document(CouchDocument):
    def __init__(self, run, lumi, dataset, user, bfield=0, initial_map = {}):
        '''
        Instantiate the Couch document and set the appropriate values 
        '''
        CouchDocument.__init__(self, id=self._generate_id(run, lumi, dataset))
        self.setdefault('run', run)
        self.setdefault('lumi', lumi)
        self.setdefault('dataset', dataset.strip('/').split('/'))
        self.setdefault('bfield', bfield)
        self.setdefault('map_history', [])
        self.setdefault('map', initial_map)
        self['map']['_meta'] = {'user': user, 
                       'timestamp': str(datetime.now())}
        
    def _generate_id(self, run, lumi, dataset):
        '''
        Internal helper function to correctly generate and set the _id for a
        document.
        '''
        id = '%s-%s-%s' % (run, lumi, md5(dataset).hexdigest())
        self.setdefault('_id', id)
        
    def set_key(self, user, key, value=False):
        '''
        Set a DQ key and record/update the history 
        '''
        self['map_history'].append(self['map'])
        self['map'][key] = value
        self['map']['_meta'] = {'user': user, 
                               'timestamp': str(datetime.now())}
        
    def set_keys(self, user, new_map={}):
        '''
        Set a bunch of keys at once
        '''
        self['map_history'].append(self['map'])
        self['map'].update(new_map)
        self['map']['_meta'] = {'user': user, 
                               'timestamp': str(datetime.now())}