
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
    forceLink:  {
      autoStop: true,
      maxIterations: 1000,
      iterationsPerRender: 10,
    },

    // design plugin settings
    // custom color palette (placeholder)
    palette: {
      type: {
        // preliminary color scheme from colorbrewer http://bl.ocks.org/mbostock/5577023
        // node types
        'Person': '#a6cee3',
        'Journal': '#1f78b4',
        'Place': '#b2df8a',
        'School': '#33a02c',
        // edge types
        'edited': '#fb9a99',
        'editor': '#e31a1c',
        'contributor': '#fdbf6f',
        'co-editor': '#ff7f00',
        'co-author': '#cab2d6',
        'translator': '#6a3d9a',
        'edited': '#ffff99',
        'translated': '#b15928',
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
    $('#graph-container').trigger('graph:design_applied');

    // update the graph with the added nodes + edges, and design styles
    s.refresh();

    // run forceLink implementation of force atlas2 algorithm
    status.text('Running force-directed layout');
    console.log('running force directed layout');
    var fa = sigma.layouts.startForceLink(s, settings.forceLink);
    fa.bind('stop', function(event) {
        $('#graph-status').hide();
        $('#graph-container').trigger('graph:layout_complete');
    });
  });

  // return the generated sigma instance
  return s;

}