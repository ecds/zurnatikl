// honor nav menu status in local storage on load (shows by default on desktop widths)
// NOTE: runing before document.ready to avoid visible transition/jump
if (window.sessionStorage && sessionStorage.getItem('nav') == 'hide') {
  $("#wrapper").addClass('toggled');
}

$( document ).ready(function() {
    // remove preload class (which disables transitions)
    // after nav status is checked/updated and page is loaded
    $("body").removeClass('preload');

  // enable nav menu toggle behavior
  $("#menu-toggle").click(function(e) {
    e.preventDefault();
    var wrapper = $("#wrapper");
    wrapper.toggleClass("toggled");
    // store hidden status
    if (window.sessionStorage) {
        if (wrapper.hasClass('toggled')) {
            sessionStorage.setItem('nav', 'hide');
        } else {
            sessionStorage.removeItem('nav');
        }
    }
  });

});


