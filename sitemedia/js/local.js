

$(document).ready(function(){
var options = {
  valueNames: [ 'categoryauthor','categoryeditor', 'categorytranslator' ],
  page:1000
};

var featureList = new List('lovely-things-list', options);

$('#filter-author').click(function() {
  $(this).addClass('active').siblings().removeClass('active');
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
  $(this).addClass('active').siblings().removeClass('active');
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
  $(this).addClass('active').siblings().removeClass('active');
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
  $(this).addClass('active').siblings().removeClass('active');
  featureList.filter();
  return false;
});


});