$( document ).ready(function() {

  // enable nav menu toggle behavior
  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    var wrapper = $("#wrapper");
    wrapper.toggleClass("toggled");
    if (window.localStorage) {
        if (wrapper.hasClass('toggled')) {
            localStorage.setItem('nav', 'hide');
        } else {
            localStorage.removeItem('nav');
        }
    }
  });

  // honor nav menu status in local storage on load
  if (window.localStorage && localStorage.getItem('nav') == 'hide') {
        console.log('hiding nav');
      $("#wrapper").addClass('toggled');
  }

});


