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


$('#wl').bind('input propertychange', function () {
    $('#wl_value').html(" ");
    $('#wl_value').html($(this).val());
})

$('#we').bind('input propertychange', function () {
    $('#we_value').html(" ");
    $('#we_value').html($(this).val());
});

$("#weight").on("click", function () {
    var data = $("#datasetSelect").val()
    let wl = $("#wl").val();
    let we = $("#we").val();
    $.post("/adjustscatter", {
        // query table
        "dataset": data,
        "data": JSON.stringify(dataset),
        "wl": wl,
        "we": we
    })
        .done(function (response) {
            dataset = JSON.parse(response);
            for (var i = 0; i < dataset.length; i++) {
                dataset[i]["x"] = parseFloat(dataset[i]["x"])
                dataset[i]["y"] = parseFloat(dataset[i]["y"])
                dataset[i]["score"] = parseFloat(dataset[i]["score"])
            }
            let svg = d3.select("#scatter").select("svg")
            var o = document.getElementById("scatter");
            var width = o.clientWidth || o.offsetWidth;
            var height = o.clientHeight || o.offsetHeight;
            let padding = 60
            //x轴标尺
            let xScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["x"])])
                .range([padding, width - padding * 2])

            //y轴标尺
            let yScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["y"])])
                .range([height - padding, padding])

            svg.selectAll("circle").style("stroke-width", 0)
            svg.selectAll("circle")
                .data(dataset)
                .attr("cx", (d) => {
                    return xScale(d["x"])
                })
                .attr("cy", (d) => {
                    return yScale(d["y"])
                })
            svg.selectAll("image").remove()
            svg.selectAll("path").remove()
            $(".closeimg").remove()
        })
})

$("#confirm").on("click", function () {
    var div = document.getElementById("chartview")
    var child = div.firstChild
    var id = child.id.replace("editor", "")
    var data = editedvis
    // for (var i = 0; i < dataset.length; i++) {
    //     if (dataset[i]["id"] == id) {
    //         data = dataset[i]
    //     }
    // }
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

function show_fliter_vis(data) {
    data.forEach((d) => {
        var container = document.createElement("div");
        container.className = "dialogadd"
        var img_select = document.createElement("img");
        img_select.className = "editor"
        img_select.src = "../static/img/select.png"
        img_select.onclick = function () {
            var obj = document.getElementById("selected_fact_id")
            var selected_facts = obj.value
            if (selected_facts.indexOf(d.id) == -1) {
                selected_facts += d.id
                selected_facts += " "
                obj.value = selected_facts
            }
        }
        var vis = document.createElement("div");
        vis.id = d["id"]
        vis.className = "content"
        var pEle = document.createElement("p");//创建元素节点p
        pEle.className = "message";//设置p标签的样式
        var textEle = document.createTextNode("ID: #" + d.id);
        pEle.appendChild(textEle);//将文本追加到p中
        container.appendChild(vis)
        container.appendChild(pEle)
        container.appendChild(img_select)
        document.getElementById('story_add_fact_view').appendChild(container);
        var spec = d["vis"]
        spec['width'] = 400
        spec['height'] = 400
        vegaEmbed(document.getElementById(d["id"]), spec, vegaOptMode)
    })
}

function adjust() {
    var resize = document.getElementById("resize");
    var left = document.getElementById("scatter");
    var right = document.getElementById("show_storyline");
    var box = document.getElementById("box");
    resize.onmousedown = function (e) {
        var startY = e.clientY;
        resize.top = resize.offsetTop - 45;
        document.onmousemove = function (e) {
            var endY = e.clientY;

            var moveLen = resize.top + (endY - startY);
            var maxT = box.clientHeight - resize.offsetHeight;
            if (moveLen < 150) moveLen = 150;
            if (moveLen > maxT - 150) moveLen = maxT - 150;

            resize.style.top = moveLen;
            left.style.height = moveLen + "px";
            right.style.height = (box.clientHeight - moveLen - 5) + "px";
            var o = document.getElementById("scatter");
            var width = o.clientWidth || o.offsetWidth;
            var height = o.clientHeight || o.offsetHeight;
            let padding = 60
            let svg = d3.select("#scatter").select("svg")

            svg.attr("width", width)
                .attr("height", height)
            //x轴标尺
            let xScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["x"])])
                .range([padding, width - padding * 2])

            //y轴标尺
            let yScale = d3.scaleLinear()
                .domain([0, d3.max(dataset, (d) => d["y"])])
                .range([height - padding, padding])


            svg.selectAll("circle")
                .data(dataset)
                .attr("cx", (d) => {
                    return xScale(d["x"])
                })
                .attr("cy", (d) => {
                    return yScale(d["y"])
                })

            svg.selectAll("image").remove()
            svg.selectAll("path").remove()
            draw_storyline(storyline_data, dataset)
        }
        document.onmouseup = function (evt) {
            document.onmousemove = null;
            document.onmouseup = null;
            resize.releaseCapture && resize.releaseCapture();

        }
        resize.setCapture && resize.setCapture();
        return false;
    }
}

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