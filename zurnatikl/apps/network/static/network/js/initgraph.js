
function init_sigma_graph(opts) {

  var defaults = {
    // required configuration: json_url

    // force link defaults; if any forcelink opts are specified,
    // it will override these, so include *all* desired options
    forceLink:  {
      autoStop: true,
      maxIterations: 1000,
      iterationsPerRender: 10,
    }

  };
  var settings = $.extend({}, defaults, opts);

  var s = new sigma({
    renderer: {
      container: document.getElementById('graph-container'),
      type: 'canvas',

    },
    settings: {
      labelThreshold: 0.5,
      defaultNodeColor: '#777',
    }
  });

  // custom color palette (placeholder)
  var palette = {
    type: {
      'Person': '#7fc97f',
      'Journal': '#beaed4',
      'Place': '#fdc086',
      'School': '#fdc086'
    }
  };

  var styles = {
    nodes: {
      size: {
        by: 'degree',
        // bins: 7,   ??
        min: 5,
        max: 20
      },
/*    color: {
        by: 'type',
        scheme: 'type'
      },  */
    }
  };



  // load graph data via json
  sigma.parsers.json(settings.json_url,  s,  function() {
    // init nodes with random placement
    $.each(s.graph.nodes(), function(i, node) {
      node.x = Math.random();
      node.y = Math.random();
      // calculate and store degree for each node, to use for size
      node.degree = s.graph.degree(node.id);
    });
    // set curved edges
    $.each(s.graph.edges(), function(i, edge) {
      edge.type = 'curve';
    });

    // update the graph with the added nodes + edges
    s.refresh();

    // load configured design (currently just sizing nodes by degree)
    var design = sigma.plugins.design(s, {
      styles: styles,
      palette: palette
    });
    design.apply();

    // run forceLink implementation of force atlas2 algorithm
    var fa = sigma.layouts.startForceLink(s, settings.forceLink);
  });

  // return the generated sigma instance
  return s;

}
