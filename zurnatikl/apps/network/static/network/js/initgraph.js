
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
      type: 'canvas'
    }
  });

  // load graph data via json
  sigma.parsers.json(settings.json_url,  s,  function() {
    // init nodes with random placement
    $.each(s.graph.nodes(), function(i, node) {
      node.x = Math.random();
      node.y = Math.random();
      node.size = 1;     // is this actually doing anything?
      node.color = '#666';
    });
    // set curved edges
    $.each(s.graph.edges(), function(i, edge) {
      edge.type = 'curve';
    });

    // adjust node size by degree
    // sigma.plugins.relativeSize(s, 1);
    // NOTE: this works, but ends up with nearly all the nodes
    // being unlabeled because they are so small
    // leaving disabled for now

    // update the graph with the added nodes + edges
    s.refresh();

    // run forceLink implementation of force atlas2 algorithm
    var fa = sigma.layouts.startForceLink(s, settings.forceLink);
  });

  // return the generated sigma instance
  return s;

}
