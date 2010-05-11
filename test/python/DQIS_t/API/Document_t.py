'''
Created on 11 May 2010

@author: metson
'''
from DQIS.API.Document import Document
from hashlib import md5
import unittest

class TestDocument(unittest.TestCase):
    def testCreateAndModifyDoc(self):
        run = 1
        lumi = 2
        dataset = '/foo/bar/reco'
        
        d = Document(run, lumi, dataset, 'metson', 3990, {'ecal': True})
        
        assert d['_id'] == '%s-%s-%s' % (run, lumi, md5(dataset).hexdigest()), \
            'Document named with an incorrect _id: ' + d['_id']
        assert len(d['map_history']) == 0, \
            'map_history is incorrect: ' + d['map_history'] 
        assert d['map']['ecal'] == True, \
            'ecal key incorrectly set: ' + d['map']['ecal']
        assert d['map']['_meta']['user'] == 'metson', \
            'Map _meta field incorrect: ' + d['map']['_meta']['user']
            
        d.set_key('fred', 'hcal', False)
        
        assert d['map']['hcal'] == False, \
            'hcal key incorrectly set: ' + d['map']['hcal']
        assert d['map']['_meta']['user'] == 'fred', \
            'Map _meta field incorrect: ' + d['map']['_meta']['user']
            
        d.set_keys('john', {'tracker': False, 'hcal': True, 'ecal': True})
        
        assert d['map']['_meta']['user'] == 'john', \
            'Map _meta field incorrect: ' + d['map']['_meta']['user']
        assert d['map']['tracker'] == False, \
            'tracker key incorrectly set: ' + d['map']['tracker']
        assert d['map']['hcal'] == True, \
            'hcal key incorrectly set: ' + d['map']['hcal']
        assert d['map']['ecal'] == True, \
            'ecal key incorrectly set: ' + d['map']['ecal']
        
if __name__ == '__main__':
    unittest.main()