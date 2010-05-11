'''
Created on 7 May 2010

@author: metson
'''
from WMCore.Database.CMSCouch import CouchServer
from WMCore.Database.CMSCouch import Database as CouchDatabase
import urllib

class Database(CouchDatabase):
    """
    A class that knows how to query DQIS views
    """
    def search(self, start_run = False, end_run = False, map = {}, bfield = 0):
        """
        Find documents in a run range that match a set of bfield or key 
        conditions
        """
        uri = '/%s/_design/dqis/_list/search/run_lumi/' % self.name
        
        data = {'bfield': bfield, 'map': map}
        
        run_keys = {}
        if start_run and not end_run:
            run_keys['key'] = start_run
        elif start_run and end_run:
            run_keys['start_run'] = start_run
            run_keys['end_run'] =  end_run
        
        if len(run_keys.keys()) > 0:
            uri = '%s?%s' % (uri, urllib.urlencode(run_keys))
        
        return self.post(uri, data)
    
    def crab(self, start_run = False, end_run = False, map = {}, bfield = 0):
        """
        Find documents in a run range that match a set of bfield or key 
        conditions and return a CRAB consumable JSON file of Run:Lumi
        """
        uri = '/%s/_design/dqis/_list/crab/run_lumi/' % self.name
        
        data = {'bfield': bfield, 'map': map}
        
        run_keys = {}
        if start_run and not end_run:
            run_keys['key'] = start_run
        elif start_run and end_run:
            run_keys['start_run'] = start_run
            run_keys['end_run'] =  end_run
        
        if len(run_keys.keys()) > 0:
            uri = '%s?%s' % (uri, urllib.urlencode(run_keys))
        
        return self.post(uri, data)