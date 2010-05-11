// !code _attachments/js/json2.js
function(head, req){
  var row;
  send('{');
  var body = JSON.parse(req.body);
  var run;
  run = 0;
  var lumis;
  lumis = {};
  var first;
  first = 0;
  while(row = getRow()) {
  	if (row.value.run != run) {
  		// We've changed run, send the lumis for the last run
  		if (lumis.length > 0){
  		  distinct_lumis = [];
  		  // Can you get all the keys easily?
			  for (var k in lumis){
			    distinct_lumis.push(parseInt(k));
			  }
			  
    	  send('"' + run + '":' + toJSON(distinct_lumis.sort()));
			  
        if (first > 1) {
          send(', ');
        } else {
          first += 1;
        }
  		}
  		run = row.value.run;
  		lumis = [];
  	}
  	var sendRow;
  	// If this was set to true the queries would be inclusive - should be an option
  	sendRow = false;
  	if (body.bfield) {
  		sendRow = (parseInt(body.bfield) == parseInt(row.value.bfield));
  	}
  	// If we get a map we'd better make sure the doc matches the keys
  	if (body.map) {
  		for (key in body.map) {
  			sendRow = (body.map[key] == row.value.map[key]);
  		}
  	}
  	if (sendRow == true) {
  	  // Couldn't this be a check for the item in the list?
  		lumis[row.value.lumi] = true;
  	}
  }
  send('}');
}