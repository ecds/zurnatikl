function init_sigma_graph(opts) {

    var defaults = {
        // required configuration: json_url

        // sigma settings
        sigma: {
            labelThreshold: 0.5,
            defaultNodeColor: '#777',
            // drawEdgeLabels: true,
            // enableEdgeHovering: true
        },

        // force link defaults
        forceLink: {
            autoStop: true,
            maxIterations: 1000,
            iterationsPerRender: 10,
        },

        // design plugin settings
        // custom color palette
        palette: {
            type: {
                // colors from resonance
                // node types
                'Person': '#bc1626', // red
                'Journal': '#004052', // first blue
                'Place': '#e5c951', // yellow
                'School': '#996628', // brown
                // edge types
                // 'edited': '#0c7549',  // green
                'editor': '#d84f05', // orange
                'contributor': '#11203d', // dark blue
                'co-editor': '#872675', // light purple
                'co-author': '#de03a7', // pink
                'translator': '#0aa3aa', // teal
                'edited': '#577469', // green-gray
                'translated': '#a2d23a', // light green
            }
        },
        styles: {
            nodes: {
                size: {
                    by: 'degree',
                    // bins: 7,   ??
                    min: 3,
                    max: 20
                },
                color: {
                    by: 'type',
                    scheme: 'type'
                },
            },
            edges: {
                color: {
                    by: 'label',
                    scheme: 'type'
                }
            }
        }

    };
    // using deep merge so nested settings can be extended
    var settings = $.extend(true, {}, defaults, opts);
    var status = $('#graph-status #text');

    // populate color key based on actual configured colors
    var nodecolor_key = $('#node-colors');
    var edgecolor_key = $('#edge-colors');
    var node_types = ['Person', 'Journal', 'Place', 'School'];
    var dt, dd;

    for (var type in defaults.palette.type) {
        dt = $('<dt/>').attr('style', 'background-color:' + defaults.palette.type[type]);
        dd = $('<dd/>').html(type);
        if (node_types.indexOf(type) != -1) { // node type
            nodecolor_key.append(dt);
            nodecolor_key.append(dd);
        } else { // edge type
            edgecolor_key.append(dt);
            edgecolor_key.append(dd);
        }
    }

    var s = new sigma({
        renderer: {
            container: document.getElementById('graph-container'),
            type: 'canvas',
        },
        settings: settings.sigma
    });

    console.log('loading data');
    status.text('Loading data');

    // load graph data via json
    sigma.parsers.json(settings.json_url, s, function() {
        console.log('data loaded (' + s.graph.nodes().length + ' nodes, ' +
            s.graph.edges().length + ' edges)');
        $('#graph-container').trigger('graph:data_loaded');
        // layout is now handled server side, and coordinates are included
        // in the json data

        // set curved edges
        $.each(s.graph.edges(), function(i, edge) {
            edge.type = 'curve';
        });

        // load configured design (currently just sizing nodes by degree)
        var design = sigma.plugins.design(s, {
            styles: settings.styles,
            palette: settings.palette
        });
        design.apply();
        $('#graph-container').trigger('graph:design_applied');
        // add a trigger so design can be re-applied
        $('#graph-container').on('graph:reapply_design', function() {
            design.apply();
        });

        // update the graph with the added nodes + edges, and design styles
        s.refresh();

        $('#graph-status').hide();
    });

    // configure fullscreen button
    s.renderers[0].fullScreen({
        id: 'graph-fullscreen'
    });

    // return the generated sigma instance
    return s;

}


/* off-canvas menu for graph control panel & color key
adapted from http://tympanus.net/Development/OffCanvasMenuEffects/cornermorph.html
*/
$(document).ready(function() {

    // on fullscreen change event, add or remove fullscreen class
    // to enable custom styling fullscreen graph element
    var screen_change_events = "webkitfullscreenchange mozfullscreenchange fullscreenchange MSFullscreenChange";
    $(document).on(screen_change_events, function () {
        var fullscreen_el;
        if (document.fullscreenEnabled) {
          fullscreen_el = document.fullscreenElement;
        } else if (document.mozFullScreenEnabled) {
          fullscreen_el = document.mozFullScreenElement;
        } else if (document.msFullscreenEnabled) {
          fullscreen_el = document.msFullscreenElement;
        } else if (document.webkitFullscreenEnabled) {
            fullscreen_el = document.webkitFullscreenElement;
        }

        if (fullscreen_el != undefined) {
            $(fullscreen_el).addClass('fullscreen');
        } else {
            $('.fullscreen').removeClass('fullscreen');
        }
    });

    // control panel toggle
    var menu_openbtn = $('.menu-button');
    function toggleMenu() {
        $("#graphMenu").toggle();
        $(this).toggleClass('active')
    }
    menu_openbtn.on("click", toggleMenu);
});
