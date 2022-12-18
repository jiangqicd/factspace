//All fact data, including tasks, visualizations, coordinates
var dataset = {}
var fliter_task = []
var fliter_attributes = []
var subspace = {}
var map_attr_type = {}
var score = ["", "0-0.2", "0.2-0.4", "0.4-0.6", "0.6-0.8", "0.8-1"]
var all_topic_data = []
var top_k_topic_data = []
// Get an overview of the whole facts
$(globalConfig.queryBtn).on("click", function () {
    initialize()
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


                console.log(dataset[0]["x"], typeof(dataset[0]["x"]))

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

                var o = document.getElementById("scatter");
                var width = o.clientWidth || o.offsetWidth;
                var height = o.clientHeight || o.offsetHeight;
                let padding = 60
                let svg = d3.select("#scatter")
                    .append("svg")
                    .attr("id", "scatterplot")
                    .attr("width", width)
                    .attr("height", height)
                //x轴标尺
                let xScale = d3.scaleLinear()
                    .domain([d3.min(dataset, (d) => d["x"]), d3.max(dataset, (d) => d["x"])])
                    .range([padding, width - padding * 2])

                //y轴标尺
                let yScale = d3.scaleLinear()
                    .domain([d3.min(dataset, (d) => d["y"]), d3.max(dataset, (d) => d["y"])])
                    .range([height - padding, padding])

                //size标尺
                let sizeScale = d3.scaleLinear()
                    .domain([d3.min(dataset, (d) => d["score"]), d3.max(dataset, (d) => d["score"])])
                    .range([1, 5])

                // 建立拖拽缩放
                let zoom = d3.zoom()
                    .scaleExtent([0, 16])
                    .extent([[0, 0], [width, height]])
                    .on('zoom', zoomed);

                function zoomed() {
                    d3.select('#scatter')
                        .select('svg')
                        .selectAll('circle')
                        .attr('transform', d3.event.transform)
                    d3.select('#scatter')
                        .select('svg')
                        .selectAll('g')
                        .selectAll('path')
                        .attr('transform', d3.event.transform)
                    d3.select('#scatter')
                        .select('svg')
                        .selectAll('image')
                        .attr('transform', d3.event.transform)
                    d3.select('#scatter')
                        .select('svg')
                        .selectAll('line')
                        .attr('transform', d3.event.transform)
                    // d3.select('#scatter')
                    //     .select('svg')
                    //     .selectAll('text')
                    //     .attr('transform', d3.event.transform)
                    // d3.select('#scatter')
                    //     .select('svg')
                    //     .selectAll('defs')
                    //     .attr('transform', d3.event.transform)
                    // d3.select('#scatter')
                    //     .select('svg')
                    //     .selectAll('marker')
                    //     .attr('transform', d3.event.transform)
                }

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

                var menu = [
                    {
                        title: 'task-based expansion',
                        action: function (elm, d, i) {

                            selectTaskExpansion(d)

                            console.log('Item #1 clicked!');
                            console.log('The data for this circle is: ' + d);

                        }
                    },
                    {
                        title: 'attr-based expansion',
                        action: function (elm, d, i) {
                            selectAttrExpansion(d)
                            console.log('You have clicked the second item!');
                            console.log('The data for this circle is: ' + d);
                        }
                    },
                    {
                        title: 'slice-based expansion',
                        action: function (elm, d, i) {
                            selectSliceExpansion(d)
                            console.log('You have clicked the second item!');
                            console.log('The data for this circle is: ' + d);
                        }
                    }
                ]

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
                        return sizeScale(d["score"])
                    })
                    .attr("id", (d) => {
                        return "circle" + d.id
                    })
                    .attr("fill", (d) => {
                        return clr11[parseInt(task.indexOf(d["task"]))]
                    })
                    .attr("opacity", 0.7)
                    .on('mouseover', function (d) {
                        let attr = ""
                        for (var key in d.vis.encoding) {
                            attr += "</br>" + key + " : " + d.vis.encoding[key]["field"]
                        }
                        let text = "id: " + d.id + "</br>" + "task: " + d.task + "</br>" + "vis: " + d.vis.mark.type + attr + "</br>" + d.text
                        tipVisible(text);
                    })
                    .on('mouseout', function (d) {
                        tipHidden();
                    })
                    .on('click', function (d) {
                        d3.select(this).style("stroke", "blue")
                        d3.select(this).style("stroke-width", 0.5)
                        var data = []
                        for (var i = 0; i < dataset.length; i++) {
                            if (dataset[i]["id"] == d.id) {
                                data.push(dataset[i])
                            }
                        }
                        show_storyline(data)
                    })
                    .on('contextmenu', d3.contextMenu(menu));
                // show_top_k_topic()
            }
        )
})

function getNumber(menu, d) {
    return menu
}