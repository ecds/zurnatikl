
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
        // 'Person': '#a6cee3',
        // 'Journal': '#1f78b4',
        // 'Place': '#b2df8a',
        // 'School': '#33a02c',
        // edge types
        // 'edited': '#fb9a99',
        // 'editor': '#e31a1c',
        // 'contributor': '#fdbf6f',
        // 'co-editor': '#ff7f00',
        // 'co-author': '#cab2d6',
        // 'translator': '#6a3d9a',
        // 'edited': '#ffff99',
        // 'translated': '#b15928',

        // colors from resonance
        // node types
        'Person': '#bc1626',  // red
        'Journal': '#004052',  // first blue
        'Place': '#e5c951',   // yellow
        'School': '#996628', // brown
        // edge types
        'edited': '#0c7549',  // green
        'editor': '#d84f05',  // orange
        'contributor': '#11203d',  // dark blue
        'co-editor': '#872675',    // light purple
        'co-author': '#de03a7',   // pink
        'translator': '#0aa3aa',  // teal
        'edited': '#577469',      // green-gray
        'translated': '#a2d23a',  // light green


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
      if (node_types.indexOf(type) != -1) {  // node type
        nodecolor_key.append(dt);
        nodecolor_key.append(dd);
      } else {   // edge type
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
  sigma.parsers.json(settings.json_url,  s,  function() {
    console.log('data loaded (' + s.graph.nodes().length + ' nodes, '
                 + s.graph.edges().length + ' edges)');
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

/* off-canvas menu for graph control panel & color key
adapted from http://tympanus.net/Development/OffCanvasMenuEffects/cornermorph.html
*/
$(document).ready(function(){
    var menu_openbtn = $('#open-button'),
      menu_isopen = false;

  function toggleMenu() {
    if (menu_isopen) {
      $(document.body).removeClass('show-menu');
    } else {
      $(document.body).addClass('show-menu');
    }
    menu_isopen = !menu_isopen;
  }

  menu_openbtn.on("click", toggleMenu);
});

