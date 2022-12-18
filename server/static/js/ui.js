// Stores list of visualization recommendations
var path = "../static/vis/happiness.json"
var editedvis = {}
var task_distribution = {}
var vis_distribution = {}
var task = ["distribution", "proportion", "correlation", "trend", "derived_value", "aggregation"]
var mark = ["bar", "arc", "tick", "boxplot", "point"]
var storyline_data = {}
var color11 = {"distribution": '#8dd3c7', "derived_value": '#ffffb3', "correlation": '#bebada', "trend": '#fb8072',}
var clr12 = ['#E0EBE9', '#8dd3c7', '#ffffb3', '#bebada', '#fb8072', '#80b1d3', '#fdb462', '#b3de69', '#fccde5', '#4BEBEB', '#06bd00', '#ccebc5', '#06BD00']
// var clr11 = ["#ADADAD", "#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c", "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a", "#ffff99", "#b15928", "#fbb4ae", "#b3cde3", "#ccebc5", "#decbe4", "#fed9a6", "#ffffcc", "#e5d8bd", "#fddaec"]
// var clr11 = ["#ADADAD", '#80b1d3', '#fdb462', '#8dd3c7', '#bebada', '#fb8072', '#b6de96', '#fccde5', '#ffffb3', '#d9d9d9', '#bc80bd', '#a4c7eb']
var clr11 = ["#4e79a7", "#f28e2c", "#76b7b2", "#59a14f", "#edc949", "#af7aa1", "#ff9da7", "#9c755f", "#bab0ab"]
//All attributes of the table
var Attributes = []

var path = "../static/vis/happiness.json"


function storyline(data, level, custom) {

    $.post("/storyline", {
        "dataset": JSON.stringify(data),
        "level": level,
        "custom": custom
    })
        .done(function (response) {
            let Storyline = JSON.parse(response)["storyline"];
            let Dataset = JSON.parse(response)["dataset"]
            storyline_data = Storyline
            console.log(storyline)
            dataset = JSON.parse(response)["dataset"]
            draw_storyline(Storyline, Dataset)
            for (var i = 0; i < dataset.length; i++) {
                d3.select("#circle" + dataset[i]["id"])
                    .attr("fill", clr11[parseInt(dataset[i]["label"]) + 1])
                    .attr("opacity", 0.7)
            }
        })
}

function draw_storyline(data, all_data) {

    cross_cluster(data["cross_cluster"], all_data)
}

function cross_cluster(Data, all_data) {

    let svg = d3.select("#scatter").select("svg")
    let paths = []
    var sizeScale = d3.scaleLinear()
        .domain([0, d3.max(dataset, (d) => d["score"])])
        .range([1, 5])

    for (var k in Data) {
        let data = Data[k]

        let line = []
        let flag = []
        for (var i = 0; i < data.length; i++) {
            let source = data[i]["source"]
            let target = data[i]["target"]
            if (flag.indexOf(source.id) == -1) {
                flag.push(source.id)
                line.push(source)
            }
            if (flag.indexOf(target.id) == -1) {
                flag.push(target.id)
                line.push(target)
            }
            d3.select("#circle" + source.id).style("stroke", "#8c564b")
            d3.select("#circle" + source.id).style("stroke-width", 1)
            d3.select("#circle" + target.id).style("stroke", "#8c564b")
            d3.select("#circle" + target.id).style("stroke-width", 1)
            let x1 = parseFloat(d3.select("#circle" + source.id).attr("cx"))
            let y1 = parseFloat(d3.select("#circle" + source.id).attr("cy"))
            let x2 = parseFloat(d3.select("#circle" + target.id).attr("cx"))
            let y2 = parseFloat(d3.select("#circle" + target.id).attr("cy"))
            let Source = {"x": x1, "y": y1, "r": sizeScale(parseFloat(data[i]["source"]["score"]))}
            let Target = {"x": x2, "y": y2, "r": sizeScale(parseFloat(data[i]["target"]["score"]))}
            paths.push(metaball(Source, Target, 1000, 2.4, 0.5))
        }
        let label = ""
        for (var i = 0; i < all_data.length; i++) {
            if (all_data[i]["id"] == k) {
                label += (parseInt(all_data[i]["label"]) + 2).toString()
            }
        }
        console.log(label)
        let src = "../static/img/" + label + ".png"
        let x = parseFloat(d3.select("#circle" + k).attr("cx"))
        let y = parseFloat(d3.select("#circle" + k).attr("cy"))
        var svgimg = document.createElementNS('http://www.w3.org/2000/svg', 'image');
        svgimg.setAttributeNS(null, 'height', 30);
        svgimg.setAttributeNS(null, 'width', 30);
        svgimg.setAttributeNS(null, 'class', "location");
        svgimg.setAttributeNS('http://www.w3.org/1999/xlink', 'href', src);
        svgimg.setAttributeNS(null, 'x', x - 15);
        svgimg.setAttributeNS(null, 'y', y - 30);
        svgimg.setAttributeNS(null, 'visibility', 'visible');
        svgimg.onclick = function () {
            console.log("已经被点击了")
            // draw_storyline_sankey({"cross_cluster": data})
            show_storyline(line)
        }
        document.getElementById('scatterplot').appendChild(svgimg);
    }
    svg.selectAll("path")
        .data(paths)
        .enter()
        .append("path")
        .attr("d", (d) => {
            return d
        })
        .style("fill", "#bf5b17")
}

function show_storyline(data) {
    data.forEach((d) => {
        var obj = document.getElementById("Instoryline" + d.id);
        if (obj) {
            console.log("啥也不干")
        } else {
            var container = document.createElement("div");
            container.id = "Instoryline" + d.id
            container.className = "dialogstory"
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
            var img_left = document.createElement("img");
            img_left.className = "left"
            img_left.src = "../static/img/left.png"
            img_left.onclick = function () {
                if ($(this).parent().prev()) {
                    $(this).parent().prev().insertAfter($(this).parent())
                }
            }

            var img_right = document.createElement("img");
            img_right.className = "right"
            img_right.src = "../static/img/right.png"
            img_right.onclick = function () {
                if ($(this).parent().next()) {
                    $(this).parent().next().insertBefore($(this).parent())
                }
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
                editedvis = d
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
            container.appendChild(img_right)
            container.appendChild(img_left)
            document.getElementById('storyline').appendChild(container);
            var spec = d["vis"]
            spec['width'] = 200
            spec['height'] = 200
            vegaEmbed(document.getElementById(d["id"]), spec, vegaOptMode)
        }
    })
}

function show_vis(d, id, scenes) {

    var container = document.createElement("div");
    container.className = "dialogpath"
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
    if (scenes == "search") {
        var img_story = document.createElement("img");
        img_story.className = "story"
        img_story.src = "../static/img/story.png"
        img_story.onclick = function () {
            show_storyline([d])
        }
        container.className = "dialogpathsearch"
        container.appendChild(img_story)
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
        editedvis = d
        spec['width'] = 200
        spec['height'] = 200
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
    vis.id = scenes + d["id"]
    vis.className = "content"
    container.appendChild(vis)
    container.appendChild(pEle)
    container.appendChild(img)
    container.appendChild(img_editor)
    document.getElementById(id).appendChild(container);
    var spec = d["vis"]
    spec['width'] = 200
    spec['height'] = 200
    vegaEmbed(document.getElementById(scenes + d["id"]), spec, vegaOptMode)
}

function initialize() {
    $("#scatter").empty()
    $("#storyline").empty()
    $("#search_result_show").empty()
    $("#chartview").empty()
    $("#task_dis").empty()
    $("#vis_dis").empty()
    var selected_table = $("#datasetSelect").val().replace(".csv", "")
    var all_path = "../static/data/" + selected_table + "_topic.json"
    var top_k_path = "../static/data/" + selected_table + "_top_k_topic.json"
    $.getJSON(all_path, function (data) {
        all_topic_data = data
    })
    $.getJSON(top_k_path, function (data) {
        top_k_topic_data = data
    })
}

$("#cancel_facts").on("click", function () {
    document.getElementById('story_add_fact_view').innerHTML = ""
    document.getElementById("selected_fact_id").value = ""
})

$(document).ready(function () {
    initialize();
    adjust()
})