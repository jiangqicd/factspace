// Stores list of visualization recommendations
var visList = [];

// Stores list of visualization recommendations
var vis_history_List = [];

var vis_recommend_history_List = [];

var feedback = "init_feedback";

var query_history_list = []

var is_click = false

var task_Now = []

var task_Next = []

var path = "../static/vis/happiness.json"
// oldNewAmbiguousAttribute
var oldNewAmbiguousAttribute = {};

// oldNewAmbiguousValues
var oldNewAmbiguousValues = {};

// Data to QueryPhrase Mapping
var dataQueryPhraseMapping = {};

// QueryPhrase to Attribute Mapping
var queryPhraseToAttrMapping = {};

// Attribute to Data Mapping
var attrToDataMapping = {};

// List of attribute ambiguities
var attributeAmbiguityList = [];

// List of value ambiguities
var valueAmbiguityList = [];

// The AttributeMap: Response from NL4DV
var attributeMap = {};

var color11 = {"distribution": '#8dd3c7', "derived_value": '#ffffb3', "correlation": '#bebada', "trend": '#fb8072',}

var dataset = {}

function emptyDatasetContainers() {
    $(globalConfig.extractedMetaDataContainer + " table tbody").empty();
}

function emptyQueryResponseContainers() {
    // Variables
    visList = [];
    oldNewAmbiguousValues = {};
    oldNewAmbiguousAttribute = {};
    attrToDataMapping = {};
    queryPhraseToAttrMapping = {};
    dataQueryPhraseMapping = {};
    attributeAmbiguityList = [];
    valueAmbiguityList = [];
    attributeMap = {};

    // Generated Ambiguity Dropdowns and the Formattted Query
    // document.getElementById("inputQueryContainer").innerHTML = "No query executed!"

    // VIS
    $(globalConfig.visContainer).empty();
}

$(globalConfig.queryBtn).on("click", function () {
    //获取用户选中的fact和data attribute
    var fact = []
    var checkbox_fact = document.getElementsByName("fact")
    for (var i = 0; i < checkbox_fact.length; i++) {
        if (checkbox_fact[i].checked) {
            fact.push(checkbox_fact[i].value)
        }
    }

    var attribute = []
    var Q = []
    var checkbox_attribute = document.getElementsByName("Q")
    for (var i = 0; i < checkbox_attribute.length; i++) {
        if (checkbox_attribute[i].checked) {
            Q.push(checkbox_attribute[i].value)
        }
    }
    var T = []
    var checkbox_attribute = document.getElementsByName("T")
    for (var i = 0; i < checkbox_attribute.length; i++) {
        if (checkbox_attribute[i].checked) {
            T.push(checkbox_attribute[i].value)
        }
    }
    var N = []
    var checkbox_attribute = document.getElementsByName("N")
    for (var i = 0; i < checkbox_attribute.length; i++) {
        if (checkbox_attribute[i].checked) {
            N.push(checkbox_attribute[i].value)
        }
    }
    attribute.push(Q)
    attribute.push(T)
    attribute.push(N)
    var data = $(globalConfig.datasetSelect).val();
    var wl = $("#wl").val();
    var we = $("#we").val();
    console.log(attribute)
    $.post("/scatter", {
        "fact": JSON.stringify(fact),
        "attribute": JSON.stringify(attribute),
        "dataset": data,
        "wl": wl,
        "we": we
    })
        .done(function (response) {
            console.log(response)
            dataset = JSON.parse(response)["data"];
            let wl = $("#wl").val();
            let we = $("#we").val();
            for (var i = 0; i < dataset.length; i++) {
                dataset[i]["x"] = parseFloat(dataset[i]["ex"]) * we + parseFloat(dataset[i]["lx"]) * wl
                dataset[i]["y"] = parseFloat(dataset[i]["ey"]) * we + parseFloat(dataset[i]["ly"]) * wl
            }
            let width = 1000
            let height = 600
            let padding = 60
            // var tooltip = d3.select('body')
            //     .append('div')
            //     .attr('class', 'tooltip')
            //     .style("opacity", 0);
            let svg = d3.select("#scatter")
                .append("svg")
                .attr("width", width)
                .attr("height", height)
            let svgGroup = d3.select('svg').append('g');
            //x轴标尺
            let xScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["x"])])
                .range([padding, width - padding * 2])

            //y轴标尺
            let yScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["y"])])
                .range([height - padding, padding])

            // 建立拖拽缩放
            let zoom = d3.zoom()
                .on("zoom", function () {
                    svgGroup.attr("transform", d3.event.transform);
                });
            svg.call(zoom);

            function createTooltip() {
                return d3.select('body')
                    .append('div')
                    .classed('tooltip', true)
                    .style('opacity', 0)
                    .style('display', 'none');
            };
            let tooltip = createTooltip();

            //tooltip显示
            function tipVisible(textContent) {
                tooltip.transition()
                    .duration(400)
                    .style('opacity', 0.9)
                    .style('display', 'block');
                tooltip.html(textContent)
                    .style('left', (d3.event.pageX + 15) + 'px')
                    .style('top', (d3.event.pageY + 15) + 'px');
            }

            //tooltip隐藏
            function tipHidden() {
                tooltip.transition()
                    .duration(400)
                    .style('opacity', 0)
                    .style('display', 'none');
            }

            svg.selectAll("circle")
                .data(dataset)
                .enter()
                .append("circle")
                .attr("cx", (d) => {
                    return xScale(d["x"])
                })
                .attr("cy", (d) => {
                    return yScale(d["y"])
                })
                .attr("r", (d) => {
                    return 5
                })
                .attr("fill", (d) => {
                    return color11[d["task"]]
                })
                .attr("id", (d) => {
                    return "circle" + d.id
                })
                .on('mouseover', function (d) {
                    let text = "id: " + d.id + "</br>" + "task: " + d.task + "</br>" + "vis: " + d.vis.mark.type
                    tipVisible(text);
                })
                .on('mouseout', function (d) {
                    tipHidden();
                })
                .on('click', function (d) {
                    d3.select(this).style("stroke", "orange")
                    d3.select(this).style("stroke-width", 3)
                    let x = xScale(d["x"])
                    let y = yScale(d["y"])
                    var e = document.getElementById("tooltip" + d.id)
                    if (e) {
                        console.log("existed")
                    } else {
                        show_vis(d, x, y)
                    }
                })
        })

})


function show_vis(d, x, y) {

    function createTooltip(id) {
        return d3.select('body')
            .append('div')
            .classed('tooltip', true)
            .attr('id', "tooltip" + id)
            .style('opacity', 0)
            .style('display', 'none');
    };
    let tooltip = createTooltip(d.id);

    //tooltip显示
    function tipVisible(textContent) {
        tooltip.transition()
            .duration(400)
            .style('opacity', 0.9)
            .style('display', 'block');
        tooltip.html(textContent)
            .style('left', (d3.event.pageX + 15) + 'px')
            .style('top', (d3.event.pageY + 15) + 'px');
    }

    tipVisible("id: #" + d.id)

    var loc = document.getElementById("tooltip" + d.id)

    console.log(x, y, loc.style.left, loc.style.top)

    let svg = d3.select("#scatter").select("svg")

    svg.append("line")
        .attr("x1", x)
        .attr("y1", y)
        .attr("x2", parseFloat(loc.style.left) - 355.54)
        .attr("y2", parseFloat(loc.style.top) - 15 - 78.72)
        .attr("id", "line" + d.id)
        .attr("stroke", "grey")
        .attr("stroke-width", "1px");

    dragBox(document.getElementById("tooltip" + d.id), d.id)

    //tooltip隐藏
    function tipHidden() {
        tooltip.transition()
            .duration(400)
            .style('opacity', 0)
            .style('display', 'none');
    }

    var container = document.createElement("div");
    container.className = "dialog"
    var img = document.createElement("img");
    img.className = "close"
    img.src = "../static/img/delete.png"
    img.onclick = function () {
        $(this).parent().remove()
        d3.select("#tooltip" + d.id).remove()
        d3.select("#line" + d.id).remove()
        d3.select("#circle" + d.id).style("stroke-width", 0)
        console.log($(this).parent())
    }
    var pEle = document.createElement("p");//创建元素节点p
    pEle.className = "message";//设置p标签的样式
    var textEle = document.createTextNode("ID: #" + d.id);
    pEle.appendChild(textEle);//将文本追加到p中
    var vis = document.createElement("div");
    vis.id = d["id"]
    vis.className = "content"
    container.appendChild(vis)
    container.appendChild(pEle)
    container.appendChild(img)
    document.getElementById('visview').appendChild(container);
    spec = d["vis"]
    spec['width'] = 200
    spec['height'] = 200
    vegaEmbed(document.getElementById(d["id"]), spec, vegaOptMode)

}

function dragBox(drag, id) {

    function getCss(ele, prop) {
        return parseInt(window.getComputedStyle(ele)[prop]);
    }

    var initX,
        initY,
        dragable = false,
        wrapLeft = getCss(drag, "left"),
        wrapRight = getCss(drag, "top");
    let line = d3.select("#line" + id)
    drag.addEventListener("mousedown", function (e) {
        dragable = true;
        initX = e.clientX;
        initY = e.clientY;
    }, false);

    document.addEventListener("mousemove", function (e) {
        if (dragable === true) {
            var nowX = e.clientX,
                nowY = e.clientY,
                disX = nowX - initX,
                disY = nowY - initY;
            drag.style.left = wrapLeft + disX + "px";
            drag.style.top = wrapRight + disY + "px";
            line
                .attr("x2", wrapLeft + disX - 355.54)
                .attr("y2", wrapRight + disY - 15 - 78.72)
        }
    });

    drag.addEventListener("mouseup", function (e) {
        dragable = false;
        wrapLeft = getCss(drag, "left");
        wrapRight = getCss(drag, "top");
    }, false);

};

$(function () {

    $('#wl').bind('input propertychange', function () {
        $('#wl_value').html(" ");
        $('#wl_value').html($(this).val());
        let wl = $("#wl").val();
        let we = $("#we").val();
        for (var i = 0; i < dataset.length; i++) {
            dataset[i]["x"] = parseFloat(dataset[i]["ex"]) * we + parseFloat(dataset[i]["lx"]) * wl
            dataset[i]["y"] = parseFloat(dataset[i]["ey"]) * we + parseFloat(dataset[i]["ly"]) * wl
        }
        let width = 1000
        let height = 600
        let padding = 60
        let xScale = d3.scaleLinear()
            .domain([0, d3.max(dataset, (d) => d["x"])])
            .range([padding, width - padding * 2])

        //y轴标尺
        let yScale = d3.scaleLinear()
            .domain([0, d3.max(dataset, (d) => d["y"])])
            .range([height - padding, padding])

        let svg = d3.select("#scatter").select("svg")

        svg.selectAll("circle")
            .data(dataset)
            .attr("cx", (d) => {
                var s = document.getElementById("line" + d.id);
                if (s) {
                    svg.select("#line" + d.id).attr("x1", xScale(d["x"])).attr("y1", yScale(d["y"]))
                }
                return xScale(d["x"])
            })
            .attr("cy", (d) => {
                return yScale(d["y"])
            })
            .on('click', function (d) {
                d3.select(this).style("stroke", "orange")
                d3.select(this).style("stroke-width", 3)
                let x = xScale(d["x"])
                let y = yScale(d["y"])
                var e = document.getElementById("tooltip" + d.id)
                if (e) {
                    console.log("existed")
                } else {
                    show_vis(d, x, y)
                }
            })

        // let line = d3.selectAll("line")
        //     .attr("x1", function () {
        //         let id = d3.select(this).attr("id")
        //         console.log(id)
        //         id = id.replace("line", "")
        //         return d3.select("#circle" + id).attr("cx")
        //     })
        //     .attr("y1", function () {
        //         let id = d3.select(this).attr("id")
        //         id = id.replace("line", "")
        //         return d3.select("#circle" + id).attr("cy")
        //     })
    });

})
$(function () {

    $('#we').bind('input propertychange', function () {
        $('#we_value').html(" ");
        $('#we_value').html($(this).val());
        let wl = $("#wl").val();
        let we = $("#we").val();
        for (var i = 0; i < dataset.length; i++) {
            dataset[i]["x"] = parseFloat(dataset[i]["ex"]) * we + parseFloat(dataset[i]["lx"]) * wl
            dataset[i]["y"] = parseFloat(dataset[i]["ey"]) * we + parseFloat(dataset[i]["ly"]) * wl
        }
        let width = 1000
        let height = 600
        let padding = 60
        let xScale = d3.scaleLinear()
            .domain([0, d3.max(dataset, (d) => d["x"])])
            .range([padding, width - padding * 2])

        //y轴标尺
        let yScale = d3.scaleLinear()
            .domain([0, d3.max(dataset, (d) => d["y"])])
            .range([height - padding, padding])

        let svg = d3.select("#scatter").select("svg")

        svg.selectAll("circle")
            .data(dataset)
            .attr("cx", (d) => {
                var s = document.getElementById("line" + d.id);
                if (s) {
                    svg.select("#line" + d.id).attr("x1", xScale(d["x"])).attr("y1", yScale(d["y"]))
                }
                return xScale(d["x"])
            })
            .attr("cy", (d) => {
                return yScale(d["y"])
            })
            .on('click', function (d) {
                d3.select(this).style("stroke", "orange")
                d3.select(this).style("stroke-width", 3)
                let x = xScale(d["x"])
                let y = yScale(d["y"])
                var e = document.getElementById("tooltip" + d.id)
                if (e) {
                    console.log("existed")
                } else {
                    show_vis(d, x, y)
                }
            })
    });

})
$(globalConfig.datasetSelect).change(function () {
    emptyQueryResponseContainers();
    emptyDatasetContainers();
    var dataset = $(this).val();
    configureDatabase(dataset);
});

function configureDatabase(dataset) {
    $.post("/setData", {"dataset": dataset})
        .done(function (response) {
            console.log(response)
            emptyDatasetContainers();
            var result = JSON.parse(response);
            var Q = result['Q'];
            var T = result['T'];
            var N = result['N'];
            console.log(Q)
            for (var i = 0; i < Q.length; i++) {
                var row = document.createElement("tr");
                var cell = document.createElement("td");
                var element = document.createElement("input");
                element.setAttribute("type", "checkbox")
                element.setAttribute("value", Q[i])
                element.setAttribute("name", "Q")
                cell.appendChild(element)
                cell.appendChild(document.createTextNode(Q[i]))
                row.appendChild(cell)
                var check_Q = "<tr><td><label style='font-weight: normal'><input type='checkbox'name='Q'value=" + Q[i] + ">" + Q[i] + "</label></td></tr>"
                $(globalConfig.Q + " tbody").append(check_Q);
            }
            for (var i = 0; i < T.length; i++) {
                var row = document.createElement("tr");
                var cell = document.createElement("td");
                var element = document.createElement("input");
                element.setAttribute("type", "checkbox")
                element.setAttribute("value", T[i])
                element.setAttribute("name", "T")
                cell.appendChild(element)
                cell.appendChild(document.createTextNode(T[i]))
                row.appendChild(cell)
                var check_T = "<tr><td><label style='font-weight: normal'><input type='checkbox'name='Q'value=" + T[i] + ">" + T[i] + "</label></td></tr>"
                $(globalConfig.T + " tbody").append(check_T);
            }
            for (var i = 0; i < N.length; i++) {
                var row = document.createElement("tr");
                var cell = document.createElement("td");
                var element = document.createElement("input");
                element.setAttribute("type", "checkbox")
                element.setAttribute("value", N[i])
                element.setAttribute("name", "N")
                cell.appendChild(element)
                cell.appendChild(document.createTextNode(N[i]))
                row.appendChild(cell)
                var check_N = "<tr><td><label style='font-weight: normal'><input type='checkbox'name='Q'value=" + N[i] + ">" + N[i] + "</label></td></tr>"
                $(globalConfig.N + " tbody").append(check_N);
            }
        });
}

// function overview(path) {
//     $.getJSON(path, function (data) {
//         for (var fact in data) {
//             // console.log(fact)
//         }
//         var count = 0
//         for (var fact in data) {
//             if (count < 1000) {
//                 var vis = document.createElement("div");
//                 vis.id = fact
//                 document.getElementById('visoverview').appendChild(vis);
//                 spec = data[fact]["vis"]
//                 spec['width'] = 200
//                 spec['height'] = 200
//                 vegaEmbed(document.getElementById(fact), spec, vegaOptMode)
//                 count++
//             }
//             // var vis = document.createElement("div");
//             // vis.id = fact
//             // document.getElementById('visoverview').appendChild(vis);
//             // spec = data[fact]
//             // spec['width'] = 50
//             // spec['height'] = 50
//             // vegaEmbed(document.getElementById(fact), spec, vegaOptMode)
//             // count++
//         }
//     })
// }

function initialize() {
    var dataset = $(globalConfig.datasetSelect).val();
    $.post("/init", {"dependency_parser": "corenlp"})
        .done(function (response) {
            configureDatabase(dataset);
        });
    // overview(path)
}

$(document).ready(function () {
    initialize();
});
