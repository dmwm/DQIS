function(head, req){
  send('{\n');
  var row;
  while(row = getRow()) {
    //send(row.value);
	  send('\"' + row.key + '\":[');
	  var v;
	  for each (v in row.value){
		  send('[' + v + ',' + v + '],');
	  }
	  send('],\n');
  }
  send('}');
}


//{
//	'1': [[1, 33], [35, 35], [37, 47], [49, 75], [77, 130], [133, 136]],
//	'2': [[1,45],[50,80]]
//	}
// I used double quotes

//http://127.0.0.1:5984/dqis/_design/dqis/_list/crab/crab?group=true
//for proper examle - shoud be 2 documents with same run, but differen lumi