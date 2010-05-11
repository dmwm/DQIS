// !code _attachments/js/json2.js
function(head, req){
  var row;
  send('[');
  var body = JSON.parse(req.body);
  send('\n');
  var first;
  first = 0;
  while(row = getRow()) {
  	var sendRow;
  	sendRow = true;
  	// If there's a bfield requested it better match the doc, else we don't care
  	if (body.bfield) {
  		sendRow = (parseInt(body.bfield) == parseInt(row.value.bfield));
  	}
  	// If we get a map we'd better make sure the doc matches the keys
  	if (body.map) {
  		for (key in body.map) {
  			sendRow = sendRow & (body.map[key] == row.value.map[key])
  		}
  	}
  	if (sendRow == true) {
	    if (first > 1) {
		    send(', \n');
		  }
  		send(toJSON(row));
      first += 1;
  	}
  }
  send(']');
}