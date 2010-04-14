#!/usr/bin/env python

import sys, os, pickle, hashlib
import datetime
from DBSAPI.dbsException import *
from DBSAPI.dbsApiException import *
from DBSAPI.dbsApi import DbsApi
from DBSAPI.dbsDQFlag import DbsDQFlag
from DBSAPI.dbsRunLumiDQ import DbsRunLumiDQ
from DBSAPI.dbsConfig import DbsConfig
from WMCore.Database.CMSCouch import CouchServer

def false_or_true(test_string):
	if test_string.upper() == 'GOOD':
		return True
	else:
		return False

def process_raw_dbs(full_dq_info):
	good_dq_info = []
	dq_keys = set()
	for k in full_dq_info.keys():
		for dq in full_dq_info[k]:
			if dq['DQFlagList'] != []:
				migrated_dq = {'run': dq['RunNumber'], 
							   'lumi': dq['LumiSectionNumber'], 
							   'map': {'_meta':{
						    			'user':'metson',
									    'timestamp':str(datetime.datetime.now())
									    }
							   }, 
							   'map_history':[], 
							   'dataset':k}
				for flag in dq['DQFlagList']:
					dq_keys.add(flag['Name'].lower())
					if flag['Name'].lower() == 'bfield':
						migrated_dq['bfield'] = int(flag['Value'])
					else:
						migrated_dq['map'][flag['Name'].lower()] = false_or_true(flag['Value'])
				good_dq_info.append(migrated_dq)
	return good_dq_info, dq_keys

def get_good_dq_for(dataset):
	try:
		opts = {}
		opts['url'] = str(DbsConfig(opts).url())
		run_dq_search_criteria = []
		full_dq_info = []

		api = DbsApi(opts)
		full_dq_info =  {dataset: api.listRunLumiDQ(dataset=dataset, runLumiDQList=[run_dq_search_criteria], dqVersion="")}
		
		good_dq_info, dq_keys = process_raw_dbs(full_dq_info)
		
		return good_dq_info, dq_keys, full_dq_info
	except DbsApiException, ex:
  		print "Caught API Exception %s: %s "  % (ex.getClassName(), ex.getErrorMessage() )
  		if ex.getErrorCode() not in (None, ""):
    			print "DBS Exception Error Code: ", ex.getErrorCode()

def build_dq_json(dq):
	if '_id' not in dq[0].keys():
		for d in dq:
			ds_hash = hashlib.md5(d["dataset"]).hexdigest()
			d['_id'] = "%s-%s-%s" % (d["run"], d["lumi"], ds_hash)
			d['dataset'] = d['dataset'].strip('/').split('/')
			if 'bfield' in d.keys():
				d['bfield'] = int(d['bfield'])
			else:
				d['bfield'] = None
	print dq[0]
	return dq

if __name__ == "__main__":
	dq = []
	keys = set()

	if os.path.exists('keys.pkle') and os.path.exists('dq.pkle'):
		print 'loading keys and dq from pickle'
		dq_pkl = open('dq.pkle', 'r')
		ky_pkl = open('keys.pkle', 'r')
		keys = pickle.load(ky_pkl)
		dq = pickle.load(dq_pkl)
		dq_pkl.close()
		ky_pkl.close()
	elif os.path.exists('dbs.pkle'):
		print 'loading raw dbs from pickle'
		raw_pkl = open('dbs.pkle', 'r')
		raw = pickle.load(raw_pkl)
		d, k = process_raw_dbs(raw)
		dq.extend(d)
		keys =  keys | k
		raw_pkl.close()
	else:
		print sys.argv[1]
		f = open(sys.argv[1], 'r')
		raw = []
		l = f.readlines()

		for d in l:
			dataset = d.strip()
			d, k, r = get_good_dq_for(dataset)
			dq.extend(d)
			raw.extend(r)
			keys =  keys | k

		print 'pickling data'
		dq_pkl = open('dq.pkle', 'w')
		ky_pkl = open('keys.pkle', 'w')
		dbs_pkl = open('dbs.pkle', 'w')
		pickle.dump(dq, dq_pkl)
		dq_pkl.close()
		pickle.dump(keys, ky_pkl)
		ky_pkl.close()
		pickle.dump(raw, dbs_pkl)
		dbs_pkl.close()

	dq = build_dq_json(dq)

	couch = CouchServer(dburl='localhost:5984')
	cdb = couch.connectDatabase('dqis')

	print 'transforming data (%s records) and writing to couch' % len(dq)

	for dq_t in dq:
		cdb.queue(dq_t)

	cdb.commit()