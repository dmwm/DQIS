function(keys, values){

  var set = {};
  for each (var v in values){
    set[v] = true;
  }
  distinct_values = [];
  for (var k in set){
    distinct_values.push(k);
  }
  return distinct_values;

}