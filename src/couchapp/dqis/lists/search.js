// !code _attachments/js/json2.js
function(head, req){
  var row;
  send('[');
  var body = JSON.parse(req.body);
  send('\n');
  while(row = getRow()) {
  	var sendRow;
  	sendRow = false;
  	if (body.bfield) {
  		sendRow = (body.bfield == row.value.bfield);
  	}
  	if (body.map) {
  		for (key in body.map) {
  			sendRow = (body.map[key] == row.value.map[key]);
  		}
  	}
  	if (sendRow == true) {
  		send(toJSON(row));
  		send(',');
  	}
  }
  send(']');
}