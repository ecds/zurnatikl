
function init_sigma_graph(opts) {

  var defaults = {
    // required configuration: json_url

    // sigma settings
    sigma: {
      labelThreshold: 0.5,
      defaultNodeColor: '#777',
    },

    // force link defaults
    forceLink:  {
      autoStop: true,
      maxIterations: 1000,
      iterationsPerRender: 10,
    },

    // design plugin settings
    // custom color palette (placeholder)
    palette: {
      type: {
        'Person': '#7fc97f',
        'Journal': '#beaed4',
        'Place': '#fdc086',
        'School': '#fdc086'
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
  /*    color: {
          by: 'type',
          scheme: 'type'
        },  */
      }
    }

  };
  // using deep merge so nested settings can be extended
  var settings = $.extend(true, {}, defaults, opts);
  // console.log(settings);

  var s = new sigma({
    renderer: {
      container: document.getElementById('graph-container'),
      type: 'canvas',
    },
    settings: settings.sigma
  });


  console.log('loading data');

  // load graph data via json
  sigma.parsers.json(settings.json_url,  s,  function() {
    console.log('data loaded');
    $('#graph-container').trigger('graph:data_loaded');
    // init nodes with random placement
    $.each(s.graph.nodes(), function(i, node) {
      node.x = Math.random();
      node.y = Math.random();
      // calculate and store degree for each node, to use for size
      // node.degree = s.graph.degree(node.id);
    });
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

    // update the graph with the added nodes + edges, and design styles
    s.refresh();

    console.log('running force directed layout');
    // run forceLink implementation of force atlas2 algorithm
    var fa = sigma.layouts.startForceLink(s, settings.forceLink);
    // debugging to determine force layout timings
    fa.bind('start stop interpolate', function(event) {
      console.log(event.type);
    });
  });

  // return the generated sigma instance
  return s;

}
