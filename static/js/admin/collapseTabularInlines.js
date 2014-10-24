django.jQuery(document).ready(function(){
    // Array of the tabular inlines you want to collapse
    var tabNames = ['Schools','Associated People','Journal'];
    for (var x in tabNames)
    {
        var selector = "h2:contains(" + tabNames[x] + ")";
        django.jQuery(selector).parent().addClass("collapsed");
        django.jQuery(selector).append(" (<a class=\"collapse-toggle\" id=\"customcollapser\""+ x + " href=\"#\"> Show </a>)");
    };    
    django.jQuery(".collapse-toggle").click(function(e) {
        django.jQuery(this).parent().parent().toggleClass("collapsed");
        var text = django.jQuery(this).html();
        if (text==' Show ') {
            django.jQuery(this).html(' Hide ');
            }
        else {
            django.jQuery(this).html(' Show ');
        };
        e.preventDefault();
    });
});
