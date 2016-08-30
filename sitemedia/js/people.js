$( document ).ready(function() {
    var options = {
        valueNames: ['title', 'author', 'editor', 'translate']
    };
    var authorList = new List('authors', options);

     $(".filter").click(function(e) {
        $(".filter").removeClass("active");
        $(this).toggleClass("active");
        var mode = $(this).attr("data");
        // add mode to brower location so it appears in browser history
        document.location = '#' + mode;
        if (mode == 'all') {
            // remove all filters
            authorList.filter();
        } else {
            // filter based on specified mode
            authorList.filter(function(item) {
                // value is empty string if there is no count
                return item.values()[mode] != "";
            });
        }
    });

    // trigger a filter based on a mode hash in the document location
    function filterByHash() {
        if (document.location.hash) {
            var mode = document.location.hash.substring(1);
            var filter = $('.filter[data="' + mode + '"]');
            // if filter is not already active, activate it
            if (!filter.hasClass('active')) {
                filter.addClass('active').click();
            }
        }
     }

    // check for filter on document load
    filterByHash();
    // also check whenever the hash changes, to catch moving back in history
    $(window).on('hashchange', function() {
        filterByHash();
    });

     authorList.on("updated", function() {
        // update tile heights after a filter is applied or removed
        // or a search is completed
        $('.tile').matchHeight();
     })

   // set person name tiles to match
   $('.tile').matchHeight();
});
