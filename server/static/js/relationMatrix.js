/*
 * @Author: https://github.com/18202409203
 * @Date: 2019-03-15 12:05:40
 * @Last Modified by: zhu.pengji
 * @Last Modified time: 2019-03-16 01:46:26
 */

function relationMatrix(options) {
    // basic variable
    var margin = options.margin || { top: 50, right: 50, bottom: 100, left: 100 },
        data = options.data,
        labelsData = options.labels,
        minValue = options.min.value || -1,
        maxValue = options.max.value || 1,
        minColor = options.min.color || "blue",
        maxColor = options.max.color || "red",
        cellSize = options.cellSize || 2;

    // extra variable
    console.log(data)
    let count = data.length;
    let svgSize = count * cellSize;
    let container = document.getElementById(options.container);

    // Format
    if (!Array.isArray(data) || !data.length || !Array.isArray(data[0])) {
        throw new Error("options.data must be a 2D array");
    }
    if (!Array.isArray(labelsData) || labelsData.length !== count){
        throw new Error("options.lables is not correct format")
    }
    if (container === undefined || container === null){
        throw new Error("container must be a DOM's id")
    }

    removeAllChild(container);
    let canvas = document.createElement("div");
    container.appendChild(canvas)
    let svg = d3.select(canvas)
        .append("svg")
        .attr("width", svgSize + margin.left + margin.right)
        .attr("height", svgSize + margin.top + margin.bottom)
        .append("g")
        .attr("transform", translate(margin.left, margin.top))

    // color
    var colorScale = d3.scaleLinear()
        .domain([minValue, maxValue])
        .range([minColor, maxColor]);

    // draw
    drawGrid();
    drawCircle();
    drawLabel();
    drawLegend();

    // drawCircle
    function drawCircle() {
        let group = svg
            .selectAll("g")
            .data(data)
            .enter()
            .append("g")
            .attr("class", "rows")
            .attr("transform", (v, i) => translate(0, i * cellSize));
        group
            .selectAll("circle")
            .data(v => v)
            .enter()
            .append("circle")
            .attr("cx", (d, j) => j * cellSize)
            .attr("cy", 0)
            .attr("r", d => cellSize / 2 * (options.isSymmetry ? Math.abs(d) / maxValue : (d - minValue) / (maxValue - minValue)) )
            .attr("fill", d => colorScale(d))
            .attr("transform", translate(cellSize / 2, cellSize / 2))
        return group;
    }

    // drawLabel
    function drawLabel() {
        for (let i = 0; i < count; i++) {
            // cols
            svg
                .append("text")
                .attr("x", i * cellSize)
                .attr("y", 0)
                .text(labelsData[i])
                .attr("text-anchor", "middle")
                .attr("dx", cellSize / 2)
            // rows
            svg
                .append("text")
                .attr("x", count * cellSize)
                .attr("y", i * cellSize)
                .text(labelsData[i])
                .attr("dominant-baseline", "middle")
                .attr("dy", cellSize / 2)
        }
    }

    // drawGrid
    function drawGrid() {
        for (let i = 0; i < count + 1; i++) {
            // cols
            svg
                .append("line")
                .attr("x1", 0)
                .attr("y1", i * cellSize)
                .attr("x2", count * cellSize)
                .attr("y2", i * cellSize)
                .attr("stroke", "#c9c9c9")
                .attr("stroke-width", 0.5);
            // rows
            svg
                .append("line")
                .attr("x1", i * cellSize)
                .attr("y1", 0)
                .attr("x2", i * cellSize)
                .attr("y2", count * cellSize)
                .attr("stroke", "#c9c9c9")
                .attr("stroke-width", 0.5);
        }
    }

    // drawLegend
    function drawLegend() {
        let linearGradient = svg
            .append("defs")
            .append("linearGradient")
            .attr("id", "gradient")
            .attr("x1", "0%")
            .attr("y1", "0%")
            .attr("x2", "0%")
            .attr("y2", "100%")
        linearGradient
            .append("stop")
            .attr("offset", "0%")
            .attr("stop-color", maxColor)
            .attr("stop-opacity", 1);
        linearGradient
            .append("stop")
            .attr("offset", "100%")
            .attr("stop-color", minColor)
            .attr("stop-opacity", 1);
        let legend = svg
            .append("rect")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", cellSize/2)
            .attr("height", count * cellSize)
            .style("fill", "url(#gradient)")
            .attr("transform", translate( -cellSize, 0))
        let legendScale = d3.scaleLinear()
            .domain([minValue, maxValue])
            .range([count * cellSize, 0])
        let axisLeft = d3.axisLeft(legendScale);
        let legendAxis = svg
            .append("g")
            .attr("class", "axis")
            .attr("transform", translate( -cellSize, 0))
            .call(axisLeft)
    }

    // utils
    function translate(x, y) {
        return 'translate(' + x + ',' + y + ')';
    }
    function removeAllChild(element){
        while(element.hasChildNodes()){
            element.removeChild(element.lastChild);
        }
    }
}