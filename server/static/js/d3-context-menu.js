d3.contextMenu = function (menu, openCallback) {

    // create the div element that will hold the context menu
    d3.selectAll('.d3-context-menu').data([1])
        .enter()
        .append('div')
        .attr('class', 'd3-context-menu');

    // close menu
    d3.select('body').on('click.d3-context-menu', function () {
        d3.select('.d3-context-menu').style('display', 'none');
    });

    // this gets executed when a contextmenu event occurs
    return function (data, index) {

        var elm = this;

        d3.selectAll('.d3-context-menu').html('');
        var list = d3.selectAll('.d3-context-menu').append('ul');
        list.selectAll('li').data(menu).enter()
            .append('li')
            .html(function (d) {
                var node = all_topic_data[data.id]
                var text = d.title
                if (d.title == 'task-based expansion') {
                    var n = node["taskfacts"].length
                    if (n > 10) {
                        text += " | N: 10"
                    } else {
                        text += " | N: " + n.toString()
                    }
                } else if (d.title == 'attr-based expansion') {
                    var n = node["attributesfacts"].length
                    if (n > 10) {
                        text += " | N: 10"
                    } else {
                        text += " | N: " + n.toString()
                    }
                } else if (d.title == 'slice-based expansion') {
                    var n = node["subspacefacts"].length
                    if (n > 10) {
                        text += " | N: 10"
                    } else {
                        text += " | N: " + n.toString()
                    }
                }
                return text;
            })
            .on('click', function (d, i) {
                d.action(elm, data, index);
                d3.select('.d3-context-menu').style('display', 'none');
            });

        // the openCallback allows an action to fire before the menu is displayed
        // an example usage would be closing a tooltip
        if (openCallback) openCallback(data, index);

        // display context menu
        d3.select('.d3-context-menu')
            .style('left', (d3.event.pageX - 2) + 'px')
            .style('top', (d3.event.pageY - 2) + 'px')
            .style('display', 'block');

        d3.event.preventDefault();
    };
};