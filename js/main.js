//
// main.js
//
// A project template for using arbor.js
//


function roundRect(ctx, x, y, width, height, radius, fill, stroke) {
    if(typeof stroke == "undefined") {
        stroke = true;
    }
    if(typeof radius === "undefined") {
        radius = 5;
    }
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
    if(stroke) {
        ctx.stroke();
    }
    if(fill) {
        ctx.fill();
    }
}

function newNodes(node) {
    node.addNode('foo', {
        'color': 'orange',
        'shape': 'dot',
        'label': 'Computer Science'
    })
}

(function($) {

    var Renderer = function(canvas) {
            var canvas = $(canvas).get(0)
            var ctx = canvas.getContext("2d");
            var particleSystem

            var that = {
                init: function(system) {
                    //
                    // the particle system will call the init function once, right before the
                    // first frame is to be drawn. it's a good place to set up the canvas and
                    // to pass the canvas size to the particle system
                    //
                    // save a reference to the particle system for use in the .redraw() loop
                    particleSystem = system

                    // inform the system of the screen dimensions so it can map coords for us.
                    // if the canvas is ever resized, screenSize should be called again with
                    // the new dimensions
                    particleSystem.screenSize(canvas.width, canvas.height)
                    particleSystem.screenPadding(80) // leave an extra 80px of whitespace per side
                    // set up some event handlers to allow for node-dragging
                    that.initMouseHandling()
                },

                redraw: function() {
                    //
                    // redraw will be called repeatedly during the run whenever the node positions
                    // change. the new positions for the nodes can be accessed by looking at the
                    // .p attribute of a given node. however the p.x & p.y values are in the coordinates
                    // of the particle system rather than the screen. you can either map them to
                    // the screen yourself, or use the convenience iterators .eachNode (and .eachEdge)
                    // which allow you to step through the actual node objects but also pass an
                    // x,y point in the screen's coordinate system
                    //
                    ctx.fillStyle = "white"
                    ctx.fillRect(0, 0, canvas.width, canvas.height)

                    particleSystem.eachEdge(function(edge, pt1, pt2) {
                        // edge: {source:Node, target:Node, length:#, data:{}}
                        // pt1: {x:#, y:#} source position in screen coords
                        // pt2: {x:#, y:#} target position in screen coords
                        // draw a line from pt1 to pt2
                        ctx.strokeStyle = "rgba(0,0,0, .333)"
                        ctx.lineWidth = 2
                        ctx.beginPath()
                        ctx.moveTo(pt1.x, pt1.y)
                        ctx.lineTo(pt2.x, pt2.y)
                        ctx.stroke()
                    })

                    particleSystem.eachNode(function(node, pt) {
                        // node: {mass:#, p:{x,y}, name:"", data:{}}
                        // pt: {x:#, y:#} node position in screen coords
                        ctx.font = '12px Helvetica';
                        var metrics = ctx.measureText(node.data.label);
                        var width = metrics.width;
                        var height = 20

                        // draw a rectangle or circle centered at pt
                        // ctx.beginPath()
                        ctx.fillStyle = node.data.color
                        if(node.data.shape == 'square') {
                            // ctx.fillRect(pt.x-width/2, pt.y-height/2, width, height)
                            roundRect(ctx, pt.x - width / 2, pt.y - height / 2, width, height, 3, true)
                        } else {
                            ctx.beginPath();
                            ctx.arc(pt.x, pt.y, width / 2, 0, 2 * Math.PI, false);
                            ctx.fill()
                        }
                        // Add a stroke to give inner text a border
                        ctx.lineWidth = 10;
                        ctx.strokeStyle = node.data.color
                        ctx.stroke();

                        // Draw text
                        ctx.fillStyle = 'white'
                        ctx.textAlign = 'center';
                        ctx.textBaseline = 'middle';
                        ctx.fillText(node.data.label, pt.x, pt.y + 10);

                    })
                },

                initMouseHandling: function() {
                    // no-nonsense drag and drop (thanks springy.js)
                    var dragged = null;

                    // set up a handler object that will initially listen for mousedowns then
                    // for moves and mouseups while dragging
                    var handler = {
                        hover: function(e) {
                            console.log(e);
                        },
                        clicked: function(e) {
                            var pos = $(canvas).offset();
                            _mouseP = arbor.Point(e.pageX - pos.left, e.pageY - pos.top)
                            dragged = particleSystem.nearest(_mouseP);

                            if(dragged && dragged.node !== null) {
                                // while we're dragging, don't let physics move the node
                                dragged.node.fixed = true
                            }

                            console.log(dragged.node);

                            // if(dragged.distance < 20) {
                            //     console.log(dragged.node.name)
                            //     particleSystem.graft({
                            //         nodes: {
                            //             main: {
                            //                 'color': 'red',
                            //                 'shape': 'dot',
                            //                 'label': 'binary tree'
                            //             },
                            //             foobar: {
                            //                 'color': 'orange',
                            //                 'shape': 'dot',
                            //                 'label': 'foobar'
                            //             }
                            //         },
                            //         edges: {
                            //             main: {
                            //                 foobar: {}
                            //             }
                            //         }
                            //     });

                            // }

                            $(canvas).bind('mousemove', handler.dragged)
                            $(window).bind('mouseup', handler.dropped)

                            return false
                        },
                        dragged: function(e) {
                            var pos = $(canvas).offset();
                            var s = arbor.Point(e.pageX - pos.left, e.pageY - pos.top)

                            if(dragged && dragged.node !== null) {
                                var p = particleSystem.fromScreen(s)
                                dragged.node.p = p
                            }

                            return false
                        },

                        dropped: function(e) {
                            if(dragged === null || dragged.node === undefined) return
                            if(dragged.node !== null) dragged.node.fixed = false
                            dragged.node.tempMass = 1000
                            dragged = null
                            $(canvas).unbind('mousemove', handler.dragged)
                            $(window).unbind('mouseup', handler.dropped)
                            _mouseP = null
                            return false
                        }
                    }

                    // start listening
                    $(canvas).mousedown(handler.clicked);
                    // $(canvas).mousemove(handler.hover);
                },

            }
            return that
        }

    $(document).ready(function() {
        var sys = arbor.ParticleSystem(1000, 500, 0.5) // create the system with sensible repulsion/stiffness/friction
        sys.parameters({
            gravity: true
        }) // use center-gravity to make the graph settle nicely (ymmv)
        sys.renderer = Renderer("#viewport") // our newly created renderer will have its .init() method called shortly by sys...
        // add some nodes to the graph and watch it go...
        // sys.addEdge('a','b')
        // sys.addEdge('a','c')
        // sys.addEdge('a','d')
        // sys.addEdge('a','e')
        // sys.addNode('f', {alone:true, mass:.25})

        $.getJSON('py/binary%20tree', function(data) {
            console.log(data)
            sys.graft(data)
        })

        // var data = {
        //     nodes: {
        //         'main': {
        //             'color': '#005AFF',
        //             'shape': 'dot',
        //             'label': 'Computer Science'
        //         },
        //         'categories': {
        //             'color': '#B2B19D',
        //             'shape': 'dot',
        //             'label': 'Categories'
        //         },
        //         'links': {
        //             'color': '#B2B19D',
        //             'shape': 'dot',
        //             'label': 'Synonyms'
        //         },
        //     },
        //     'edges': {
        //         'main': {
        //             'categories': {},
        //             'links': {}
        //         }
        //     }
        // };

        // sys.graft(data);

        // or, equivalently:
        // sys.graft({
        //   nodes:{
        //     f:{alone:true, mass:.25}
        //   },
        //   edges:{
        //     a:{ b:{},
        //       c:{},
        //       d:{},
        //       e:{}
        //     }
        //   }
        // })
    })

})(this.jQuery)