$( document ).ready(function() {
    var options = {
        valueNames: ['title', 'author', 'editor', 'translate']
    };
    var authorList = new List('authors', options);

     $(".filter").click(function(e) {
        $(".filter").removeClass("active");
        $(this).toggleClass("active");
        var mode = $(this).attr("data");
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
    })

     authorList.on("updated", function() {
        // update tile heights after a filter is applied or removed
        // or a search is completed
        $('.tile').matchHeight();
     })

   // set person name tiles to match
   $('.tile').matchHeight();
});
