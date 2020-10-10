var isTooltipHidden = true;


(function() {
    if ($('#js-searchForm').length > 0) {
        $('#js-searchForm').on('submit', search);
        $('#search').on('change', change);
    }

    // set a width and height for our SVG
    var width = document.getElementById('d3-map').clientWidth || "100%"
        height = document.getElementById('d3-map').clientHeight || window.innerHeight - 100;

    // a list of node objects and link objects
    // nodes are represented as {id: <id>, ....}
    // links are represnted as {source: <node>, target: <node>}
    var nodes = [], links = []

    // create the force layout. after a call to force.start(), the tick method
    // will be called repeatedly until the layout "gels" in a stable configuration
    var force = d3.layout.force()
        .nodes(nodes)
        .links(links)
        .size([width, height])
        .linkStrength(0.5)
        .friction(0.4)
        .linkDistance(75)
        .charge(-100)
        .gravity(0.05)
        .on("tick", tick);

    // add an SVG element inside the d3-map element
    var svg = d3.select('#d3-map').append('svg')
        .attr('width', width)
        .attr('height', height)
        .on('click', hideTooltip)

    // https://stackoverflow.com/questions/5489946/how-to-wait-for-the-end-of-resize-event-and-only-then-perform-an-action
    var rtime;
    var timeout = false;
    var delta = 200;
    $(window).resize(function() {
        rtime = new Date();
        if (timeout === false) {
            timeout = true;
            setTimeout(resizeend, delta);
        }
    });

    function resizeend() {
        if (new Date() - rtime < delta) {
            setTimeout(resizeend, delta);
        } else {
            timeout = false;
            width = document.getElementById('d3-map').clientWidth || "100%"
            height = document.getElementById('d3-map').clientHeight || window.innerHeight - 100;
            force.size([width, height])
            svg.attr('width', width).attr('height', height)
        }
    }

    // add a tooltip div to the body
    var tooltip = d3.select("body")
        .append("div")
        .attr("class", "tooltip")
        .style("position", "absolute")
        .text("");

    function update_graph() {
        // the call to <selection>.data() gets the link objects
        // and associates them with the corresponding DOM elements, 
        // in this case, SVG line elements. The first argument, force.links()
        // simply returns our links[] array. The second argument is a function
        // that produces a unique and invariate identifier for each link. This
        // makes it possible for d3 to correctly associate each link object
        // with each line element in the DOM, even if the link object moves
        // around in memory. 

        // link_update, in addition to processing objects that need updating, 
        // defines two custom methods, .enter() and .exit(), that refer to link
        // objects that are newly added and that have been deleted (respectively).
        var link_update = svg.selectAll('.link').data(
            force.links(), //previously this was just links
            function(d) { return d.source.tooltip + "-" + d.target.tooltip; }
        );

        // link_update.enter() creates an svg line element for each new link 
        // object. note that we call .insert("line", ".node") to add SVG line 
        // elements to the DOM before any elements with class="node". This 
        // guarantees that the lines will be drawn first. 
        link_update.enter()
            .insert('line', '.node') //previously this was .append('line') ?
            .attr('class', 'link')
            .on('click', hideTooltip);

        // link_update.exit() processes link objects that have been removed 
        // by removing its corresponding SVG line element.
        link_update.exit()
            .remove();

        // node_selection.data() returns a selection of nodes that need 
        // updating and defines two custom methods, .enter() and .exit()
        // that will process newly created node objects and deleted node objects.

        // note that, similar to what we did for links, we've provided an id
        // method that returns a unique and invariate identifier for each node.
        // this is what lets D3 associate each node object with its corresponding 
        // circle element in the DOM, even if the node object moves around in memory.
        var node_update = svg.selectAll('.node').data(
            force.nodes(),
            function(d) { return d.tooltip; }
        );

        // create an SVG circle for each new node added to the graph. 
        var new_nodes = node_update.enter()
            .append('g')
            .attr('class', 'node')

        new_nodes
            .append('circle') // this was a new node.append
            .attr("x", -5)
            .attr("y", -5)
            .attr('r', 8)
            .on('click', showTooltip)

        new_nodes
            .append("text") // this was a new node.append
            .attr("dx", 12)
            .attr("dy", ".35em")
            .text(function(d) { return d.label });

        // remove the SVG circle whenever a node vanishes from the node list
        node_update.exit()
            .remove();

        // start calling the tick() method repeatedly to lay out the graph
        force.start();
    }

    // this tick method is called repeatedly until the layout stabilizes
    // NOTE: the order in which we update nodes and links does NOT determine which 
    // gets drawn first -- the drawing order is determined by the ordering in the 
    // DOM. See the notes under link_update.enter() above for one technique for 
    // setting the ordering in the DOM. 
    function tick(e) {
        svg.selectAll(".node")
            .attr('cx', function(d) { return d.x; })
            .attr('cy', function(d) { return d.y; })
            .call(force.drag);
            
        svg.selectAll(".link")
            .attr('x1', function(d) { return d.source.x; })
            .attr('y1', function(d) { return d.source.y; })
            .attr('x2', function(d) { return d.target.x; })
            .attr('y2', function(d) { return d.target.y; });

        svg.selectAll('.node').attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    }

    // click handler for nodes
    function showTooltip(node) {
       // check that we're not dragging
        if (!d3.event.defaultPrevented) {
            d3.event.stopPropagation()
            tooltip.html(node.tooltip);
            tooltip
                .style("top", (d3.event.pageY -10) + "px")
                .style("left", (d3.event.pageX + 10) + "px")
                .style("display", "block");
            isTooltipHidden = false;

            $('.js-disconnect').on('click', disconnectNodes);

            $('.js-connect').on('click', connectNodes);

            $('.js-person-add').on('click', connectPerson);
        }
    }

    // hide tooltip - click handler for links and the SVG
    function hideTooltip() {
        if (!isTooltipHidden) {
            tooltip.text("").style("display", "none")
            isTooltipHidden = true
        }
    }
    
    function connectNodes(e) {
        e.preventDefault();
        url = $(e.currentTarget).attr('href')
        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.onreadystatechange = function () {
            if (request.readyState !=4 || request.status != 200) {
                return;
            }

            data = JSON.parse(request.responseText)

            data.nodes[1].x = parseFloat(data.nodes[1].x)
            data.nodes[1].y = parseFloat(data.nodes[1].y)
            delete data.nodes[1].x
            delete data.nodes[1].y

            for (var i=0; i<nodes.length; i++) {
                if (nodes[i].id === data.nodes[1].id) {
                    nodes.splice(i, 1);
                    break;
                }
            }

            nodes.push(data.nodes[1])

            data.edges[0].source = nodes.filter(function(item) {
                return item.id == data.edges[0].source
            })[0]
            data.edges[0].target = nodes.filter(function(item) {
                return item.id == data.edges[0].target
            })[0]

            links.push(data.edges[0])

            //update all other links to point to the new node
            for (var i=0; i<links.length; i++) {
                if (links[i].source.id === nodes[nodes.length-1].id) {
                    links[i].source = nodes[nodes.length-1]
                }
                if (links[i].target.id === nodes[nodes.length-1].id) {
                    links[i].target = nodes[nodes.length-1]
                }
            }

            hideTooltip();
            update_graph();

        };
        request.send();
    }

    function disconnectNodes(e) {
        e.preventDefault();
        url = $(e.currentTarget).attr('href')
        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.onreadystatechange = function () {
            if (request.readyState !=4 || request.status != 200) {
                return;
            }

            data = JSON.parse(request.responseText)

            data.nodes[0].x = parseFloat(data.nodes[0].x)
            data.nodes[0].y = parseFloat(data.nodes[0].y)
            delete data.nodes[0].x
            delete data.nodes[0].y
            data.nodes[1].x = parseFloat(data.nodes[1].x)
            data.nodes[1].y = parseFloat(data.nodes[1].y)
            delete data.nodes[1].x
            delete data.nodes[1].y

            for (var j=0; j<data.nodes.length; j++) {
                for (var i=0; i<nodes.length; i++) {
                    if (nodes[i].id === data.nodes[j].id) {
                        nodes.splice(i, 1);
                        break;
                    }
                }                
            }
            nodes.push.apply(nodes, data.nodes)

            // first update all the links to point to the new nodes
            for (var i=0; i<links.length; i++) {
                if (links[i].source.id === data.nodes[0].id) {
                    links[i].source = nodes[nodes.length-2]
                }
                if (links[i].target.id === data.nodes[0].id) {
                    links[i].target = nodes[nodes.length-2]
                }
                if (links[i].source.id === data.nodes[1].id) {
                    links[i].source = nodes[nodes.length-1]
                }
                if (links[i].target.id === data.nodes[1].id) {
                    links[i].target = nodes[nodes.length-1]
                }
            }

            // now delete the link
            for (var i=0; i<links.length; i++) {
                if ((links[i].source.id === data.nodes[0].id &&
                    links[i].target.id === data.nodes[1].id) ||
                    (links[i].source.id === data.nodes[1].id &&
                    links[i].target.id === data.nodes[0].id)) {
                    links.splice(i, 1);
                }
            }

            hideTooltip();
            update_graph();
            // console.log('disconnect households')

            // getMap();
        };
        request.send();
    }

    function connectPerson(e) {
        e.preventDefault();
        url = $(e.currentTarget).attr('href')
        var request = new XMLHttpRequest();
        request.open('GET', url, true);
        request.onreadystatechange = function () {
            if (request.readyState !=4 || request.status != 200) {
                return;
            }

            data = JSON.parse(request.responseText)

            data.nodes[0].x = parseFloat(data.nodes[0].x)
            data.nodes[0].y = parseFloat(data.nodes[0].y)
            delete data.nodes[0].x
            delete data.nodes[0].y

            for (var i=0; i<nodes.length; i++) {
                if (nodes[i].id === data.nodes[0].id) {
                    nodes.splice(i, 1);
                    break;
                }
            }
            nodes.push.apply(nodes, data.nodes)

            // update all links to point to the 'new' node
            for (var i=0; i<links.length; i++) {
                if (links[i].source.id === data.nodes[0].id) {
                    links[i].source = nodes[nodes.length-1]
                }
                if (links[i].target.id === data.nodes[0].id) {
                    links[i].target = nodes[nodes.length-1]
                }
            }

            hideTooltip();
            update_graph();

        };
        request.send();
    }

    function search(e) {
        e.preventDefault();
        e.stopPropagation();
        var searchData = $(e.currentTarget).serializeArray();
        var searchEndpoint = $(e.currentTarget).attr('action') + '?search=' + searchData[0].value;
        var request = new XMLHttpRequest();
        request.open('GET', searchEndpoint, true);
        request.onreadystatechange = function() {
            if (request.readyState != 4 || request.status != 200) {
                return;
            }

            data = JSON.parse(request.responseText)

            var searchResults = document.getElementById("js-searchResults")
            var template = document.getElementById("search-result-template");

            for (var i=0; i<data.results.length; i++) {
                var searchResult = template.content.cloneNode(true);

                var place_name = searchResult.querySelector(".js-place_name");
                var member_count = searchResult.querySelector(".js-member_count");
                var zip_code = searchResult.querySelector(".js-zip_code");

                place_name.textContent = data.results[i].name;
                member_count.textContent = data.results[i].member_count + " household member";
                if (data.results[i].member_count > 1) {
                    member_count.textContent += "s"
                }
                zip_code.textContent = "Zip Code: " + data.results[i].zip_code;

                searchResults.appendChild(searchResult);
            }
        };

        request.send();
    };

    function change(e) {
        var searchResults = document.getElementById("js-searchResults")
        searchResults.innerHTML = ""
    }

    var request = new XMLHttpRequest();
    request.open('GET', '/data', true);
    request.onreadystatechange = function () {
        if (request.readyState != 4 || request.status != 200) {
            return;
        }

        data = JSON.parse(request.responseText)

        data.nodes.forEach(function(node) {
            node.x = parseFloat(node.x)
            node.y = parseFloat(node.y)
            delete node.x
            delete node.y
            nodes.push(node)
        })

        data.edges.forEach(function(link) {
            link.source = nodes.filter(function(item) {
                return item.id == link.source
            })[0]
            link.target = nodes.filter(function(item) {
                return item.id == link.target
            })[0]
            links.push(link)
        })

        // nodes.push.apply(nodes, data.nodes)
        // links.push.apply(links, data.edges)
        update_graph();
    };
    request.send();
    
})();