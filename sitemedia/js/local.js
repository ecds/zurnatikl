$(document).ready(function(){
var options = {
  valueNames: [ 'categoryauthor','categoryeditor', 'categorytranslator' ]
};

var featureList = new List('lovely-things-list', options);

$('#filter-author').click(function() {
  featureList.filter(function(item) {
    if (item.values().categoryauthor == "author") {
      return true;
    } else {
      return false;
    }
  });
  return false;
});

$('#filter-editor').click(function() {
  featureList.filter(function(item) {
    if (item.values().categoryeditor == "editor") {
      return true;
    } else {
      return false;
    }
  });
  return false;
});

$('#filter-translator').click(function() {
  featureList.filter(function(item) {
    if (item.values().categorytranslator == "translator") {
      return true;
    } else {
      return false;
    }
  });
  return false;
});

$('#filter-none').click(function() {
  featureList.filter();
  return false;
});


$(function() {
  $('.btn-default').click( function() {
    $(this).addClass('active').siblings().removeClass('active');
  });
});
});