function(doc) {
  for (k in doc.map){
    if (doc.map[k]!=null){
      var tmp =[k, doc.run, doc.map[k]];
      emit(tmp, 1);
    }
  }
}

