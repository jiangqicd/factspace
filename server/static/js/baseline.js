var trend = []
var distribution = []
var correlation = []
var proportion = []
var aggregation = []
var record = {
    "Distribution": [0, 5],
    "Correlation": [0, 5],
    "Trend": [0, 5],
    "Aggregation": [0, 5],
    "Proportion": [0, 5]
}
var dataset = {}
var fliter_task = []
var fliter_attributes = []
var subspace = {}
var map_attr_type = {}
var score = ["", "0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1"]
var all_topic_data = []
var top_k_topic_data = []
var task_distribution = {}
var vis_distribution = {}
var vegaOptMode = {
    "actions": true,
    "renderer": "svg",
    "hover": false,
    "tooltip": true
};

function showCorr() {
    var margin = {top: 20, right: 20, bottom: 20, left: 20},
        width = 500 - margin.left - margin.right,
        height = 500 - margin.top - margin.bottom

// Create the svg area
    var svg = d3.select("#correlation")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");



    let data = $("#datasetSelect").val()
    data=data.replace(".csv","")
    let path = "../static/data/"+data+"_person.csv"
    d3.csv(path, function (error, rows) {
             console.log(path)
        console.log(rows)
        // Going from wide to long format
        var data = [];
        rows.forEach(function (d) {
            var x = d[""];
            delete d[""];
            for (prop in d) {
                var y = prop,
                    value = d[prop];
                data.push({
                    x: x,
                    y: y,
                    value: +value
                });
            }
        });
        console.log(data)

        // List of all variables and number of them
        var domain = d3.set(data.map(function (d) {
            return d.x
        })).values()
        var num = Math.sqrt(data.length)

        // Create a color scale
        var color = d3.scaleLinear()
            .domain([-1, 0, 1])
            .range(["#6e0220", "#fff", "#083363"]);

        // Create a size scale for bubbles on top right. Watch out: must be a rootscale!
        var size = d3.scaleSqrt()
            .domain([0, 1])
            .range([0, 9]);

        // X scale
        var x = d3.scalePoint()
            .range([0, width])
            .domain(domain)

        // Y scale
        var y = d3.scalePoint()
            .range([0, height])
            .domain(domain)

        // Create one 'g' element for each cell of the correlogram
        var cor = svg.selectAll(".cor")
            .data(data)
            .enter()
            .append("g")
            .attr("class", "cor")
            .attr("transform", function (d) {
                return "translate(" + x(d.x) + "," + y(d.y) + ")";
            });

        // Low left part + Diagonal: Add the text with specific color
        cor
            .filter(function (d) {
                var ypos = domain.indexOf(d.y);
                var xpos = domain.indexOf(d.x);
                return xpos <= ypos;
            })
            .append("text")
            .attr("y", 5)
            .text(function (d) {
                if (d.x === d.y) {
                    return d.x;
                } else {
                    return d.value.toFixed(2);
                }
            })
            .style("font-size", 11)
            .style("text-align", "center")
            .style("fill", function (d) {
                if (d.x === d.y) {
                    return "#000";
                } else {
                    return color(d.value);
                }
            });


        // Up right part: add circles
        cor
            .filter(function (d) {
                var ypos = domain.indexOf(d.y);
                var xpos = domain.indexOf(d.x);
                return xpos > ypos;
            })
            .append("circle")
            .attr("r", function (d) {
                return size(Math.abs(d.value))
            })
            .style("fill", function (d) {
                if (d.x === d.y) {
                    return "#000";
                } else {
                    return color(d.value);
                }
            })

    })
}

function showFacts() {

    factClassification()
    if (distribution.length > 0) {
        let key = "Distribution"
        var templte = `<div class="panel panel-primary">
                <div class="panel-heading">
                    <img src="../static/img/left.png" class="left" id="leftDistribution"> 
                    Distribution
                    <img src="../static/img/right.png" class="right" id="rightDistribution">
                </div>
                <div id="showDistribution" style=" width: 1568px; height: 300px;overflow: hidden;background: #343aa9"></div>
            </div>`
        $("#showfacts").append(templte)
        var d = distribution.slice(record[key][0], record[key][1])
        show(d, key)
        $("#leftDistribution").on("click", function () {
            if (record[key][0] >= 5) {
                record[key][0] -= 5
                record[key][1] -= 5
                $("#showDistribution").html("")
                var d = distribution.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
        $("#rightDistribution").on("click", function () {
            if (record[key][0] <= distribution.length - 5) {
                record[key][0] += 5
                record[key][1] += 5
                $("#showDistribution").html("")
                var d = distribution.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
    }
    if (correlation.length > 0) {
        let key = "Correlation"
        var templte = `<div class="panel panel-primary">
                <div class="panel-heading">
                    <img src="../static/img/left.png" class="left" id="leftCorrelation"> 
                    Correlation
                    <img src="../static/img/right.png" class="right" id="rightCorrelation">
                </div>
                <div id="showCorrelation" style=" width: 1568px; height: 300px;overflow: hidden;background: #343aa9"></div>
            </div>`
        $("#showfacts").append(templte)
        var d = correlation.slice(record[key][0], record[key][1])
        show(d, key)
        $("#leftCorrelation").on("click", function () {
            if (record[key][0] >= 5) {
                record[key][0] -= 5
                record[key][1] -= 5
                $("#showCorrelation").html("")
                var d = correlation.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
        $("#rightCorrelation").on("click", function () {
            if (record[key][0] <= correlation.length - 5) {
                record[key][0] += 5
                record[key][1] += 5
                $("#showCorrelation").html("")
                var d = correlation.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
    }
    if (trend.length > 0) {
        let key = "Trend"
        var templte = `<div class="panel panel-primary">
                <div class="panel-heading">
                    <img src="../static/img/left.png" class="left" id="leftTrend"> 
                    Trend
                    <img src="../static/img/right.png" class="right" id="rightTrend">
                </div>
                <div id="showTrend" style=" width: 1568px; height: 300px;overflow: hidden;background: #343aa9"></div>
            </div>`
        $("#showfacts").append(templte)
        var d = trend.slice(record[key][0], record[key][1])
        show(d, key)
        $("#leftTrend").on("click", function () {
            if (record[key][0] >= 5) {
                record[key][0] -= 5
                record[key][1] -= 5
                $("#showTrend").html("")
                var d = trend.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
        $("#rightTrend").on("click", function () {
            if (record[key][0] <= trend.length - 5) {
                record[key][0] += 5
                record[key][1] += 5
                $("#showTrend").html("")
                var d = trend.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
    }
    if (proportion.length > 0) {
        let key = "Proportion"
        var templte = `<div class="panel panel-primary">
                <div class="panel-heading">
                    <img src="../static/img/left.png" class="left" id="leftProportion"> 
                    Proportion
                    <img src="../static/img/right.png" class="right" id="rightProportion">
                </div>
                <div id="showProportion" style=" width: 1568px; height: 300px;overflow: hidden;background: #343aa9"></div>
            </div>`
        $("#showfacts").append(templte)
        var d = proportion.slice(record[key][0], record[key][1])
        show(d, key)
        $("#leftProportion").on("click", function () {
            if (record[key][0] >= 5) {
                record[key][0] -= 5
                record[key][1] -= 5
                $("#showProportion").html("")
                var d = proportion.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
        $("#rightProportion").on("click", function () {
            if (record[key][0] <= proportion.length - 5) {
                record[key][0] += 5
                record[key][1] += 5
                console.log(record)
                $("#showProportion").html("")
                var d = proportion.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
    }
    if (aggregation.length > 0) {
        let key = "Aggregation"
        var templte = `<div class="panel panel-primary">
                <div class="panel-heading">
                    <img src="../static/img/left.png" class="left" id="leftAggregation"> 
                    Aggregation
                    <img src="../static/img/right.png" class="right" id="rightAggregation">
                </div>
                <div id="showAggregation" style=" width: 1568px; height: 300px;overflow: hidden;background: #343aa9"></div>
            </div>`
        $("#showfacts").append(templte)
        var d = aggregation.slice(record[key][0], record[key][1])
        show(d, key)
        $("#leftAggregation").on("click", function () {
            if (record[key][0] >= 5) {
                record[key][0] -= 5
                record[key][1] -= 5
                $("#showAggregation").html("")
                var d = aggregation.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
        $("#rightAggregation").on("click", function () {
            if (record[key][0] <= aggregation.length - 5) {
                record[key][0] += 5
                record[key][1] += 5
                $("#showAggregation").html("")
                var d = aggregation.slice(record[key][0], record[key][1])
                show(d, key)
            }
        })
    }
}

function show(data, type) {
    data.forEach((d) => {
        var container = document.createElement("div");
        container.id = "fact" + d.id
        container.className = "dialogstory"
        var img = document.createElement("img");
        img.className = "close"
        img.src = "../static/img/delete.png"
        img.onclick = function () {
            $(this).parent().remove()
            console.log($(this).parent())
        }
        var img_editor = document.createElement("img");
        img_editor.className = "editor"
        img_editor.src = "../static/img/editor.png"
        img_editor.onclick = function () {
            var vis = document.createElement("div");
            vis.id = "editor" + d["id"]
            // vis.className = "content"
            document.getElementById('chartview').innerHTML = ""
            document.getElementById('chartview').appendChild(vis);
            var spec = d["vis"]
            spec['width'] = 180
            spec['height'] = 150
            vegaEmbed(document.getElementById("editor" + d["id"]), spec, vegaOptMode)

            let mark = spec["mark"]["type"]
            let x = ""
            let x_agg = ""
            let y = ""
            let y_agg = ""
            let color = ""
            let color_agg = ""
            let theta = ""
            let theta_agg = ""
            if (spec["encoding"].hasOwnProperty("x")) {
                x = spec["encoding"]["x"]["field"]
                x_agg = spec["encoding"]["x"]["aggregate"]
            }
            if (spec["encoding"].hasOwnProperty("y")) {
                y = spec["encoding"]["y"]["field"]
                y_agg = spec["encoding"]["y"]["aggregate"]
            }
            if (spec["encoding"].hasOwnProperty("color")) {
                color = spec["encoding"]["color"]["field"]
                color_agg = spec["encoding"]["color"]["aggregate"]
            }
            if (spec["encoding"].hasOwnProperty("theta")) {
                theta = spec["encoding"]["theta"]["field"]
                theta_agg = spec["encoding"]["theta"]["aggregate"]
            }


            var html = ''

            var comps = ['ch-x', 'ch-y', 'ch-color', 'ch-theta', 'ch-shape']
            comps.forEach((comp) => {
                $('#' + comp).empty()
            })
            html = '<option value="' + x + '">' + x + '</option>'
            $('#' + 'ch-x').append(html)
            html = '<option value="' + y + '">' + y + '</option>'
            $('#' + 'ch-y').append(html)
            html = '<option value="' + color + '">' + color + '</option>'
            $('#' + 'ch-color').append(html)
            html = '<option value="' + theta + '">' + theta + '</option>'
            $('#' + 'ch-theta').append(html)
            comps.forEach((comp) => {
                html = '<option value="-">-</option>'
                Attributes.forEach((d) => {
                    if (comp == "ch-x") {
                        if (d != x) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    } else if (comp == "ch-y") {
                        if (d != y) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    }
                    else if (comp == "ch-color") {
                        if (d != color) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    } else if (comp == "ch-theta") {
                        if (d != theta) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    }
                })
                $('#' + comp).append(html)
            })

            $('#ch-mark').empty()
            var marks = ['bar', 'point', 'area', 'circle', 'line', 'tick']
            html = ''
            html += '<option value="' + mark + '">' + mark + '</option>'
            $('#ch-mark').append(html)
            marks.forEach((d) => {
                if (d != mark) {
                    html += '<option value="' + d + '">' + d + '</option>'
                }
            })
            $('#ch-mark').append(html)

            var comps = ['ch-xtrans', 'ch-ytrans', 'ch-colortrans', 'ch-thetatrans']
            var aggs = ['-', 'count', 'mean', 'sum', 'bin']
            comps.forEach((comp) => {
                $('#' + comp).empty()
            })
            html = ''
            html = '<option value="' + x_agg + '">' + x_agg + '</option>'
            $('#' + 'ch-xtrans').append(html)
            html = '<option value="' + y_agg + '">' + y_agg + '</option>'
            $('#' + 'ch-ytrans').append(html)
            html = '<option value="' + color_agg + '">' + color_agg + '</option>'
            $('#' + 'ch-colortrans').append(html)
            html = '<option value="' + theta_agg + '">' + theta_agg + '</option>'
            $('#' + 'ch-thetatrans').append(html)
            comps.forEach((comp) => {
                html = ''
                aggs.forEach((d) => {
                    if (comp == "ch-xtrans") {
                        if (d != x_agg) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    } else if (comp == "ch-ytrans") {
                        if (d != y_agg) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    }
                    else if (comp == "ch-colortrans") {
                        if (d != color_agg) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    } else if (comp == "ch-thetatrans") {
                        if (d != theta_agg) {
                            html += '<option value="' + d + '">' + d + '</option>'
                        }
                    }
                })

                $('#' + comp).append(html)
            })
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
        container.appendChild(img_editor)
        var id = 'show' + type
        document.getElementById(id).appendChild(container);
        var spec = d["vis"]
        spec['width'] = 180
        spec['height'] = 180
        vegaEmbed(document.getElementById(d["id"]), spec, vegaOptMode)
    })
}

function factClassification() {
    for (var i = 0; i < dataset.length; i++) {
        if (dataset[i]["task"] == "distribution") {
            distribution.push(dataset[i])
        } else if (dataset[i]["task"] == "trend") {
            trend.push(dataset[i])
        } else if (dataset[i]["task"] == "proportion") {
            proportion.push(dataset[i])
        } else if (dataset[i]["task"] == "correlation") {
            correlation.push(dataset[i])
        } else if (dataset[i]["task"] == "aggregation") {
            aggregation.push(dataset[i])
        }
    }
    distribution.sort(descending("score"))
    correlation.sort(descending("score"))
    trend.sort(descending("score"))
    aggregation.sort(descending("score"))
    proportion.sort(descending("score"))
}

function ascending(p) { //这是比较函数
    return function (m, n) {
        var a = m[p];
        var b = n[p];
        return a - b; //升序
    }
}

function descending(p) { //这是比较函数
    return function (m, n) {
        var a = m[p];
        var b = n[p];
        return b - a; //降序
    }
}

$("#queryBtn").on("click", function () {
    // initialize()
    var data = $("#datasetSelect").val()
    $.post("/scatter", {
        // query table
        "dataset": data,
    })
        .done(function (response) {

                dataset = JSON.parse(response)["data"];
                fliter_task = JSON.parse(response)["tasks"]
                fliter_attributes = JSON.parse(response)["columns"]
                Attributes = JSON.parse(response)["columns"]
                subspace = JSON.parse(response)["subspace"]
                map_attr_type = JSON.parse(response)["map_attr_type"]
                var data = JSON.parse(response)["array"]
                var label = JSON.parse(response)["label"]
                new gridjs.Grid({
                    columns: label,
                    data: data
                }).render(document.getElementById('table'));
                showCorr()
                add_fliter(fliter_task, fliter_attributes, subspace, score)
                for (var i = 0; i < dataset.length; i++) {
                    dataset[i]["x"] = parseFloat(dataset[i]["x"])
                    dataset[i]["y"] = parseFloat(dataset[i]["y"])
                    dataset[i]["score"] = parseFloat(dataset[i]["score"])
                    if (task_distribution.hasOwnProperty(dataset[i]["task"])) {
                        task_distribution[dataset[i]["task"]] += 1
                    } else {
                        task_distribution[dataset[i]["task"]] = 1
                    }
                    if (vis_distribution.hasOwnProperty(dataset[i]["mark"])) {
                        vis_distribution[dataset[i]["mark"]] += 1
                    } else {
                        vis_distribution[dataset[i]["mark"]] = 1
                    }
                }
                show_task_dis(task_distribution)
                show_vis_dis(vis_distribution)
                showFacts()
            }
        )
})

function add_fliter(fliter_task, fliter_attributes, fliter_subspace, score) {
    add_fliter_task(fliter_task)
    add_fliter_attribute(fliter_attributes)
    add_fliter_subspace(fliter_subspace)
    add_fliter_score(score)
}

function add_fliter_task(data) {
    for (var i = 0; i < data.length; i++) {
        var html = '<option value="' + data[i] + '">' + data[i] + '</option>'
        $('#tasksSelect').append(html)
    }
}

function add_fliter_attribute(data) {
    for (var i = 0; i < data.length; i++) {
        var html = '<option value="' + data[i] + '">' + data[i] + '</option>'
        $('#attributes1Select').append(html)
        $('#attributes2Select').append(html)
    }
}

function add_fliter_subspace(data) {
    var ht = '<option value="' + "" + '">' + "" + '</option>'
    $('#subspaceattrSelect').append(ht)
    for (var key in data) {
        var option = document.createElement("option")
        option.value = key
        option.text = key
        $('#subspaceattrSelect').append(option)
    }
}

$("#subspaceattrSelect").on("change", function () {
    $('#subspacevalueSelect').empty()
    var ht = '<option value="' + "" + '">' + "" + '</option>'
    $('#subspacevalueSelect').append(ht)
    var key = $("#subspaceattrSelect").val()
    for (var i = 0; i < subspace[key].length; i++) {
        var h = '<option value="' + subspace[key][i] + '">' + subspace[key][i] + '</option>'
        $('#subspacevalueSelect').append(h)
    }
})

function add_fliter_score(data) {
    for (var i = 0; i < data.length; i++) {
        var html = '<option value="' + data[i] + '">' + data[i] + '</option>'
        $('#scoreSelect').append(html)
    }
}

function show_task_dis(data) {
    let datas = []
    for (let key in data) {
        datas.push({"key": key.substring(0, 5) + "..", "value": data[key]})
    }
    let width = 300, height = 100, padding = 20

    let svg = d3.select("#task_dis")
        .append("svg")
        .attr("width", width)
        .attr("height", height)

    let xScale = d3.scaleBand()
        .domain(datas.map(d => d.key))
        .range([padding, width - 2 * padding])
        .padding(0.5)

    let yScale = d3.scaleLinear()
        .domain([0, d3.max(datas, (d) => d.value)])
        .range([height - padding * 2, 0])

    let xAxis = d3.axisBottom(xScale)
    // let yAxis = d3.axisLeft(yScale)

    // 绘制坐标轴
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0,' + (height - padding) + ')')
        .call(xAxis)

    // svg.append('g')
    //     .attr('class', 'axis')
    //     .attr('transform', 'translate(' + padding + ',' + padding + ')')
    //     .call(yAxis);
    svg.selectAll("rect")
        .data(datas)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.key))
        .attr("y", d => yScale(d.value) + padding)
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - padding * 2 - yScale(d.value))
        .attr("fill", "grey")

    svg.append("g").selectAll("text")
        .data(datas)
        .enter()
        .append("text")
        .text(function (d) {
            return d.value;
        })
        .attr("class", "text")
        .attr("x", function (d) {
            return xScale(d.key) + xScale.bandwidth() / 2
        })
        .attr("y", function (d) {
            return yScale(d.value) + padding
        })
}

function show_vis_dis(data) {
    console.log(data)
    let datas = []
    for (let key in data) {
        datas.push({"key": key, "value": data[key]})
    }
    console.log(datas)
    let width = 300, height = 100, padding = 20

    let svg = d3.select("#vis_dis")
        .append("svg")
        .attr("id", "vis_dis_1")
        .attr("width", width)
        .attr("height", height)

    let xScale = d3.scaleBand()
        .domain(datas.map(d => d.key))
        .range([padding, width - 2 * padding])
        .padding(0.5)

    let yScale = d3.scaleLinear()
        .domain([0, d3.max(datas, (d) => d.value)])
        .range([height - padding * 2, 0])

    let xAxis = d3.axisBottom(xScale)
    // let yAxis = d3.axisLeft(yScale)

    // 绘制坐标轴
    svg.append('g')
        .attr('class', 'axis')
        .attr('transform', 'translate(0,' + (height - padding) + ')')
        .call(xAxis)

    // svg.append('g')
    //     .attr('class', 'axis')
    //     .attr('transform', 'translate(' + padding + ',' + padding + ')')
    //     .call(yAxis);

    svg.selectAll("rect")
        .data(datas)
        .enter()
        .append("rect")
        .attr("x", d => xScale(d.key))
        .attr("y", d => yScale(d.value) + padding)
        .attr("width", xScale.bandwidth())
        .attr("height", d => height - padding * 2 - yScale(d.value))
        .attr("fill", "grey")


    //添加文本
    svg.append("g").selectAll("text")
        .data(datas)
        .enter()
        .append("text")
        .attr("class", "text")
        .attr("x", function (d) {
            return xScale(d.key) + xScale.bandwidth() / 2
        })
        .attr("y", function (d) {
            return yScale(d.value) + padding
        })
        .text(function (d) {
            return d.value;
        })
}

$("#remove").on("click", function () {
    let svg = d3.select("#scatter").select("svg")
    svg.selectAll('circle').style("stroke-width", 0)
    svg.selectAll('path').remove()
})

$("#fliter").on("click", function () {
    let svg = d3.select("#scatter").select("svg")
    svg.selectAll('circle').style("stroke-width", 0)
    var id = $("#idsearch").val();
    var score = $("#scoreSelect").val();
    var task = $("#tasksSelect").val();
    var attribute1 = $("#attributes1Select").val();
    var attribute2 = $("#attributes2Select").val();
    var subspaceattr = $("#subspaceattrSelect").val();
    var subspacevalue = $("#subspacevalueSelect").val();
    var id_data = []
    var score_data = []
    var task_data = []
    var attribute_data = []
    var subspace_data = []
    for (var i = 0; i < dataset.length; i++) {
        if (id != "") {
            if (dataset[i]["id"] == id) {
                id_data.push(dataset[i])
            }
        }
        else {
            id_data.push(dataset[i])
        }
        if (task != "") {
            if (dataset[i]["task"] == task) {
                task_data.push(dataset[i])
            }
        }
        else {
            task_data.push(dataset[i])
        }
        if (score != "") {
            var l = parseFloat(score.split("-")[0])
            var h = parseFloat(score.split("-")[1])
            if (parseFloat(dataset[i]["score"]) >= l && parseFloat(dataset[i]["score"]) <= h) {
                score_data.push(dataset[i])
            }
        }
        else {
            score_data.push(dataset[i])
        }
        if (attribute1 != "" || attribute2 != "") {
            var encoding = dataset[i]["vis"]["encoding"]
            var field = []
            for (var k in encoding) {
                field.push(encoding[k]["field"])
            }
            var flag = true
            if (attribute1 != "") {
                if (field.indexOf(attribute1) == -1) {
                    flag = false
                }
            }
            if (attribute2 != "") {
                if (field.indexOf(attribute2) == -1) {
                    flag = false
                }
            }
            if (flag) {
                attribute_data.push(dataset[i])
            }
        }
        else {
            attribute_data.push(dataset[i])
        }
        if (subspaceattr != "") {
            var f = ""
            if (Array.isArray(dataset[i]["vis"]["title"]["text"])) {
                for (let j of dataset[i]["vis"]["title"]["text"]) {
                    f += j
                }
            } else {
                f = dataset[i]["vis"]["title"]["text"]
            }
            if (f.indexOf(subspaceattr) > -1 && f.indexOf(subspacevalue) > -1) {
                subspace_data.push(dataset[i])
            }
        } else {
            subspace_data.push(dataset[i])
        }
    }
    var data = task_data.filter(function (x) {
        return attribute_data.indexOf(x) > -1
    })
    var data = data.filter(function (x) {
        return subspace_data.indexOf(x) > -1
    })
    var data = data.filter(function (x) {
        return score_data.indexOf(x) > -1
    })
    var data = data.filter(function (x) {
        return id_data.indexOf(x) > -1
    })
    for (var i = 0; i < data.length; i++) {
        svg.select("#circle" + data[i].id).style("stroke", "red")
        svg.select("#circle" + data[i].id).style("stroke-width", 0.5)
    }
})
$("#confirm").on("click", function () {
    var div = document.getElementById("chartview")
    var child = div.firstChild
    var id = child.id.replace("editor", "")
    var data = {}
    for (var i = 0; i < dataset.length; i++) {
        if (dataset[i]["id"] == id) {
            data = dataset[i]
        }
    }
    var mark = $("#ch-mark").val()
    var x = $("#ch-x").val()
    var y = $("#ch-y").val()
    var color = $("#ch-color").val()
    var theta = $("#ch-theta").val()
    var x_aggr = $("#ch-xtrans").val()
    var y_aggr = $("#ch-ytrans").val()
    var color_aggr = $("#ch-colortrans").val()
    var theta_aggr = $("#ch-thetatrans").val()
    var channel = ["x", "y", "color", "theta"]
    var attr = [x, y, color, theta]
    var aggr = [x_aggr, y_aggr, color_aggr, theta_aggr]
    console.log(map_attr_type)

    if (mark) {
        data["vis"]["mark"]["type"] = mark
    }
    for (var i = 0; i < channel.length; i++) {
        var c = channel[i]
        var at = attr[i]
        var a = aggr[i]
        if (at && at != "-") {
            if (data["vis"]["encoding"].hasOwnProperty(c)) {
                data["vis"]["encoding"][c]["field"] = at
                if (map_attr_type[at] == "Q") {
                    data["vis"]["encoding"][c]["type"] = "quantitative"
                } else if (map_attr_type[at] == "N") {
                    data["vis"]["encoding"][c]["type"] = "nominal"
                } else {
                    data["vis"]["encoding"][c]["type"] = "temporal"
                }
                if (a) {
                    data["vis"]["encoding"][c]["aggregate"] = a
                }
            } else {
                data["vis"]["encoding"][c] = {}
                data["vis"]["encoding"][c]["field"] = at
                if (map_attr_type[at] == "Q") {
                    data["vis"]["encoding"][c]["type"] = "quantitative"
                } else if (map_attr_type[at] == "N") {
                    data["vis"]["encoding"][c]["type"] = "nominal"
                } else {
                    data["vis"]["encoding"][c]["type"] = "temporal"
                }
                if (a) {
                    data["vis"]["encoding"][c]["aggregate"] = a
                }
            }
        } else {
            if (data["vis"]["encoding"].hasOwnProperty(c)) {
                delete data["vis"]["encoding"][c]
            }
        }
    }

    var spec = data["vis"]
    spec['width'] = 200
    spec['height'] = 200
    vegaEmbed(document.getElementById("editor" + id), spec, vegaOptMode)
    if ($("#editor" + id).length > 0) {
        vegaEmbed(document.getElementById("editor" + id), spec, vegaOptMode)
    }
    if ($("#search" + id).length > 0) {
        vegaEmbed(document.getElementById("search" + id), spec, vegaOptMode)
    }
    if ($("#" + id).length > 0) {
        vegaEmbed(document.getElementById(id), spec, vegaOptMode)
    }

})
$("#cancel").on("click", function () {
    var div = document.getElementById("chartview")
    while (div.hasChildNodes()) //当div下还存在子节点时 循环继续
    {
        div.removeChild(div.firstChild);
    }
})