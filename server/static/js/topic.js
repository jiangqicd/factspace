var Paths = []
var ExpanedNodes = []
var ExpanedPaths = []

function show_top_k_topic() {
    var paths = []
    for (var key in top_k_topic_data) {
        var score = ""
        for (var el of dataset) {
            if (el.id == key) {
                score = el.score
            }
        }
        var node = top_k_topic_data[key]
        paths = paths.concat(drawpath(key, score, node["taskfacts"], "taskfacts"))
        paths = paths.concat(drawpath(key, score, node["attributesfacts"], "attributesfacts"))
        paths = paths.concat(drawpath(key, score, node["subspacefacts"], "subspacefacts"))
    }
    let svg = d3.select("#scatter").select("svg")
    svg.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .attr("d", (d) => {
            return d.path
        })
        .style("fill", (d) => {
            return d.color
        })
}


function drawpath(source_id, source_score, data, type) {

    data.sort(compare("score"));

    var sizeScale = d3.scaleLinear()
        .domain([0, d3.max(dataset, (d) => d["score"])])
        .range([0.1, 1])

    let paths = []

    let ct = 0
    let ca = 0
    let cs = 0

    for (var el of data) {

        var target_id = el.id
        var target_score = el.score

        // d3.select("#circle" + source_id).style("stroke", "#004655")
        // d3.select("#circle" + source_id).style("stroke-width", 1)

        let x1 = parseFloat(d3.select("#circle" + source_id).attr("cx"))
        let y1 = parseFloat(d3.select("#circle" + source_id).attr("cy"))
        let x2 = parseFloat(d3.select("#circle" + target_id).attr("cx"))
        let y2 = parseFloat(d3.select("#circle" + target_id).attr("cy"))

        let Source = {"x": x1, "y": y1, "r": sizeScale(parseFloat(source_score))}
        let Target = {"x": x2, "y": y2, "r": sizeScale(parseFloat(target_score))}

        if (type == "taskfacts") {
            if (ct < 10) {
                d3.select("#circle" + target_id).style("stroke", '#755c65')
                d3.select("#circle" + target_id).style("stroke-width", 1)
                paths.push({
                    "path": metaball(Source, Target, 1000, 2.4, 0.5),
                    "color": '#755c65',
                    "source": source_id,
                    "target": target_id
                })
                ct += 1
            }
        } else if (type == "attributesfacts") {
            if (ca < 10) {
                d3.select("#circle" + target_id).style("stroke", '#793000')
                d3.select("#circle" + target_id).style("stroke-width", 1)
                paths.push({
                    "path": metaball(Source, Target, 1000, 2.4, 0.5),
                    "color": '#793000',
                    "source": source_id,
                    "target": target_id
                })
                ca += 1
            }
        } else if (type == "subspacefacts") {
            if (cs < 10) {
                d3.select("#circle" + target_id).style("stroke", '#004655')
                d3.select("#circle" + target_id).style("stroke-width", 1)
                paths.push({
                    "path": metaball(Source, Target, 1000, 2.4, 0.5),
                    "color": '#004655',
                    "source": source_id,
                    "target": target_id
                })
                cs += 1
            }
        }
    }
    return paths
}

function isOverLoad(d, e, t) {
    let f = true
    d.forEach((el, index) => {
        let dis = Math.sqrt((el[0] - e[0]) ** 2 + (el[1] - e[1]) ** 2)
        if (dis < t) {
            f = false
        }
    })
    if (f) {
        return true
    } else return false
}

function drawBezierPath(source_id, source_score, dn, type) {

    dn.sort(compare("score"));

    let paths = []
    var nodes = []

    let ct = 0
    let ca = 0
    let cs = 0

    let scoreScale = d3.scaleLinear()
        .domain([d3.min(dn, (d) => d["score"]), d3.max(dn, (d) => d["score"])])
        // .range([0.1, 1])
        .range([1, 2])

    for (var el of dn) {


        var target_id = el.id
        var target_score = el.score

        // d3.select("#circle" + source_id).style("stroke", "#004655")
        // d3.select("#circle" + source_id).style("stroke-width", 1)

        let x1 = parseFloat(d3.select("#circle" + source_id).attr("cx"))
        let y1 = parseFloat(d3.select("#circle" + source_id).attr("cy"))
        let x2 = parseFloat(d3.select("#circle" + target_id).attr("cx"))
        let y2 = parseFloat(d3.select("#circle" + target_id).attr("cy"))
        let r1 = parseFloat(d3.select("#circle" + source_id).attr("r"))
        let r2 = parseFloat(d3.select("#circle" + target_id).attr("r"))

        let path = createCPath(x1, y1, x2, y2, r1, r2)

        if (type == "taskfacts") {
            if (ct < 10) {
                if (isOverLoad(nodes, [x2, y2], 10)) {
                    d3.select("#circle" + target_id).style("stroke", '#755c65')
                    d3.select("#circle" + target_id).style("stroke-width", 1)
                    paths.push({
                        "path": path,
                        "color": '#755c65',
                        "source": source_id,
                        "target": target_id,
                        "width": scoreScale(el.score)
                    })
                    ct += 1
                    nodes.push([x2, y2])
                }
            }
        } else if (type == "attributesfacts") {
            if (ca < 10) {
                if (isOverLoad(nodes, [x2, y2], 10)) {
                    d3.select("#circle" + target_id).style("stroke", '#755c65')
                    d3.select("#circle" + target_id).style("stroke-width", 1)
                    paths.push({
                        "path": path,
                        "color": '#755c65',
                        "source": source_id,
                        "target": target_id,
                        "width": scoreScale(el.score)
                    })
                    ca += 1
                    nodes.push([x2, y2])
                }
            }
        } else if (type == "subspacefacts") {
            if (cs < 10) {
                if (isOverLoad(nodes, [x2, y2], 10)) {
                    d3.select("#circle" + target_id).style("stroke", '#755c65')
                    d3.select("#circle" + target_id).style("stroke-width", 1)
                    paths.push({
                        "path": path,
                        "color": '#755c65',
                        "source": source_id,
                        "target": target_id,
                        "width": scoreScale(el.score)
                    })
                    cs += 1
                    nodes.push([x2, y2])
                }
            }
        }
    }
    return paths
}

function show_selected_fact_topic(selected_fact) {

    var paths = []
    var node = all_topic_data[selected_fact.id]

    paths = paths.concat(drawpath(selected_fact.id, selected_fact.score, node["taskfacts"], "taskfacts"))
    paths = paths.concat(drawpath(selected_fact.id, selected_fact.score, node["attributesfacts"], "attributesfacts"))
    paths = paths.concat(drawpath(selected_fact.id, selected_fact.score, node["subspacefacts"], "subspacefacts"))

    var transform = d3.select("#circle" + selected_fact.id).attr("transform")

    let g = d3.select("#scatter").select("svg").append("g")

    g.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .attr("d", (d) => {
            return d.path
        })
        .style("fill", (d) => {
            return d.color
        })
        .attr("transform", transform)
}

function compare(p) {
    return function (m, n) {
        var a = m[p];
        var b = n[p];
        return b - a; //降序
    }
}

function fliterPath(source_id) {
    let g = d3.select("#scatter").select("svg").append("g")
    ExpanedNodes.push(source_id)
    for (let iter of Paths) {
        if (iter.target == source_id) {
            let source = iter.source
            ExpanedPaths.push(source + source_id)
            d3.select("#arrowpath" + source + source_id)
                .style("fill", '#c68109')
            d3.select("#path" + source + source_id)
                .style("stroke-dasharray", "")
                .style("stroke", '#c68109')

            // g.append("text")
            // // 给text添加textPath元素
            //     .append("textPath")
            //     // 给textPath设置path的引用
            //     .attr("xlink:href", d => {
            //         return "#path" + source + source_id
            //     })
            //     // 字体居中
            //     .style("text-anchor", "middle")
            //     // .style("text-decoration","underline")
            //     .style("fontWeight", "bold")
            //     .attr("startOffset", "50%")
            //     // 父节点的name
            //     .style("fill", '#c68109')
            //     .style("font-size", 20)
            //     .style("opacity", 0.7)
            //     .text(source + "-->" + source_id)

            // d3.select("#arrow" + source + source_id)
            //     .style("fill", '#c68109')
            for (let i = 0; i < Paths.length; i++) {
                if (Paths[i].source == source) {
                    if (ExpanedPaths.indexOf(Paths[i].source + Paths[i].target) == -1) {
                        if (document.getElementById("path" + Paths[i].source + Paths[i].target)) {
                            d3.select('#path' + Paths[i].source + Paths[i].target)
                                .transition()
                                .duration(200)
                                .remove()
                        }
                        Paths.splice(i, 1);
                        i--;
                    }
                }
            }
            d3.select('#path' + source_id + source)
                .transition()
                .duration(200)
                .remove()
        }
    }
    let linkedNodes = []
    for (let iter of Paths) {
        if (linkedNodes.indexOf(iter.source) == -1) {
            linkedNodes.push(iter.source)
        }
        if (linkedNodes.indexOf(iter.target) == -1) {
            linkedNodes.push(iter.target)
        }
    }
    for (let iter of dataset) {
        if (linkedNodes.indexOf(iter.id) == -1 && ExpanedNodes.indexOf(iter.id) == -1) {
            d3.select("#circle" + iter.id).style("stroke-width", 0)
        }
        if (linkedNodes.indexOf(iter.id) > -1 && ExpanedNodes.indexOf(iter.id) > -1) {
            d3.select("#circle" + iter.id).style("stroke", '#c68109')
        }
    }

}


function selectTaskExpansion(d) {

    var paths = []
    var node = all_topic_data[d.id]

    // paths = paths.concat(drawpath(d.id, d.score, node["taskfacts"], "taskfacts"))\
    // fliterPath(d.id)
    paths = paths.concat(drawBezierPath(d.id, d.score, node["taskfacts"], "taskfacts"))
    Paths = unique(Paths.concat(paths))
    console.log(Paths)

    let transform = d3.select("#circle" + d.id).attr("transform")

    let svg = d3.select("#scatter").select("svg")
    let g = d3.select("#scatter").select("svg").append("g")

    svg.append("defs").selectAll("marker")
        .data(paths)
        .enter()
        .append("marker")
        .attr("id", function (d) {
            return "arrow" + d.source + d.target
        })
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", "8")
        .attr("markerHeight", "8")
        .attr("viewBox", "0 0 12 12")
        .attr("refX", "6")
        .attr("refY", "6")
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
        .attr("id", function (d) {
            return "arrowpath" + d.source + d.target
        })
        .style("fill", (d) => {
            return d.color
        })


    g.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .transition()
        .duration(100)
        .attr("d", (d) => {
            return d.path
        })
        .attr("id", (d) => {
            return "path" + d.source + d.target
        })
        .style("fill", (d) => {
            return "none"
        })
        .style("stroke-width", (d) => {
            return d.width
        })
        .style("stroke", (d) => {
            return d.color
        })
        // .style("stroke-dasharray", (d) => {
        //     return "3, 2"
        // })
        .attr("transform", transform)
        .attr("marker-end", function (d) {
            return "url(#" + "arrow" + d.source + d.target + ")"
        });
    fliterPath(d.id)
}

function selectAttrExpansion(d) {
    var paths = []
    var node = all_topic_data[d.id]

    // fliterPath(d.id)
    // paths = paths.concat(drawpath(d.id, d.score, node["attributesfacts"], "attributesfacts"))
    paths = paths.concat(drawBezierPath(d.id, d.score, node["attributesfacts"], "attributesfacts"))
    Paths = unique(Paths.concat(paths))

    let transform = d3.select("#circle" + d.id).attr("transform")

    let svg = d3.select("#scatter").select("svg")
    let g = d3.select("#scatter").select("svg").append("g")

    svg.append("defs").selectAll("marker")
        .data(paths)
        .enter()
        .append("marker")
        .attr("id", function (d) {
            return "arrow" + d.source + d.target
        })
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", "8")
        .attr("markerHeight", "8")
        .attr("viewBox", "0 0 12 12")
        .attr("refX", "6")
        .attr("refY", "6")
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
        .attr("id", function (d) {
            return "arrowpath" + d.source + d.target
        })
        .style("fill", (d) => {
            return d.color
        })

    g.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .transition()
        .duration(100)
        .attr("d", (d) => {
            return d.path
        })
        .attr("id", (d) => {
            return "path" + d.source + d.target
        })
        .style("fill", (d) => {
            return "none"
        })
        .style("stroke-width", (d) => {
            return d.width
        })
        .style("stroke", (d) => {
            return d.color
        })
        // .style("stroke-dasharray", (d) => {
        //     return "3, 2"
        // })
        .attr("transform", transform)
        .attr("marker-end", function (d) {
            return "url(#" + "arrow" + d.source + d.target + ")"
        });
    fliterPath(d.id)
}

function selectSliceExpansion(d) {
    var paths = []
    var node = all_topic_data[d.id]
    // paths = paths.concat(drawpath(d.id, d.score, node["subspacefacts"], "subspacefacts"))
    paths = paths.concat(drawBezierPath(d.id, d.score, node["subspacefacts"], "subspacefacts"))
    Paths = unique(Paths.concat(paths))

    // fliterPath(d.id)

    let transform = d3.select("#circle" + d.id).attr("transform")

    let svg = d3.select("#scatter").select("svg")
    let g = d3.select("#scatter").select("svg").append("g")

    svg.append("defs").selectAll("marker")
        .data(paths)
        .enter()
        .append("marker")
        .attr("id", function (d) {
            return "arrow" + d.source + d.target
        })
        .attr("markerUnits", "strokeWidth")
        .attr("markerWidth", "8")
        .attr("markerHeight", "8")
        .attr("viewBox", "0 0 12 12")
        .attr("refX", "6")
        .attr("refY", "6")
        .attr("orient", "auto")
        .append("path")
        .attr("d", "M2,2 L10,6 L2,10 L6,6 L2,2")
        .attr("id", function (d) {
            return "arrowpath" + d.source + d.target
        })
        .style("fill", (d) => {
            return d.color
        })

    g.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .attr("d", (d) => {
            return d.path
        })
        .attr("id", (d) => {
            return "path" + d.source + d.target
        })
        .style("fill", (d) => {
            return "none"
        })
        .style("stroke", (d) => {
            return d.color
        })
        .style("stroke-width", (d) => {
            return d.width
        })
        // .style("stroke-dasharray", (d) => {
        //     return "3, 2"
        // })
        .attr("transform", transform)
        .attr("marker-end", function (d) {
            return "url(#" + "arrow" + d.source + d.target + ")"
        })

    fliterPath(d.id)
}


function createCPath(x1, y1, x2, y2, r1, r2) {
    var path = "M" + x1 + " " + y1 + " ";
    var cx1 = x1;
    var cy1 = (y1 + y2) / 2;
    var cx2 = x2;
    var cy2 = (y1 + y2) / 2;
    var c = "C" + cx1 + " " + cy1 + "," + cx2 + " " + cy2 + ",";
    var qx1 = (x1 + x2) / 2;
    var qy1 = (y1 + y2) / 2.5
    var q = "Q" + qx1 + " " + qy1 + ",";
    // let o = Math.atan((y2 - cy2) / (x2 - cx2))
    // x2 -= Math.cos(o) * r2
    // y2 -= Math.sin(o) * r2
    path = path + q + x2 + " " + y2;
    //console.log(path);
    return path;
    // var dx = x2 - x1,
    //     dy = y2 - y1,
    //     dr = Math.sqrt(dx * dx + dy * dy);
    // return "M" + x1 + "," + y1 + "A" + dr + "," + dr + " 0 0,1 " + x2 + "," + y2;`
}

function objSort(obj) {
    let newObj = {}
    //遍历对象，并将key进行排序
    Object.keys(obj).sort().map(key => {
        newObj[key] = obj[key]
    })
    //将排序好的数组转成字符串
    return JSON.stringify(newObj)
}

function unique(arr) {
    let set = new Set();
    for (let i = 0; i < arr.length; i++) {
        let str = objSort(arr[i])
        set.add(str)
    }
    //将数组中的字符串转回对象
    arr = [...set].map(item => {
        return JSON.parse(item)
    })
    return arr
}