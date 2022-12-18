/*Interactions in the fact space*/

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
            var f=""
            if(Array.isArray(dataset[i]["vis"]["title"]["text"])){
                for(let j of dataset[i]["vis"]["title"]["text"]){
                    f+=j
                }
            }else {
                f=dataset[i]["vis"]["title"]["text"]
            }
            if(f.indexOf(subspaceattr)>-1&&f.indexOf(subspacevalue)>-1){
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

/*Interactions in the storyline*/

$("#queryStoryline").on("click", function () {
    var obj = document.getElementsByName("distance")
    var level = ""
    for (var i in obj) {
        if (obj[i].checked) {
            level = obj[i].value
        }
    }
    var custom = document.getElementById("custom").value
    storyline(dataset, level, custom)
})

/*Transition path*/

$("#search").on("click", function () {
    var start = document.getElementById("start_fact").value
    var end = document.getElementById("end_fact").value
    // var encoding = document.getElementById("encoding").value
    // var logical = document.getElementById("logical").value
    // var score = document.getElementById("score").value
    var table = $("#datasetSelect").val()
    $.post("/searchpath", {
        "start": start,
        "end": end,
        // "encoding": encoding,
        // "logical": logical,
        // "score": score,
        "dataset": JSON.stringify(dataset),
        "table": table
    })
        .done(function (response) {
            // $("#search_result_show").innerHTML=""
            $(".month-detail-box").remove();
            let path = JSON.parse(response)["data"];
            let title = '<p class="timer-year"><i class="icon-year"></i><span style="font-size: 16px">' + 'From #' + start + ' to #' + end + '</span></p>'
            $("#search_result_show").append(title)
            for (let i = 0; i < path.length; i++) {
                // let div = '<div class="month-detail-box" id="searchpath' + path[i].id + '"><span class="month-title">' + path[i].id + '</span></div>'
                // $("#search_result_show").append(div)
                // show_vis(path[i], "searchpath" + path[i].id, "search")
                path[i]["id"] = start + end + i.toString()
                let div = '<div class="month-detail-box" id="searchpath' + path[i].id + '"><span class="month-title">' + path[i].id + '</span></div>'
                $("#search_result_show").append(div)
                show_vis(path[i], "searchpath" + path[i].id, "search")
            }
        });
})

/*Edit storyline*/

$("#searchid").on("click", function () {
    var id = document.getElementById("search_fact_by_id").value
    var data = []
    for (var i = 0; i < dataset.length; i++) {
        if (id == dataset[i]["id"]) {
            data.push(dataset[i])
        }
    }
    show_fliter_vis(data)
})

$("#submit_facts").on("click", function () {
    var obj = document.getElementById("selected_fact_id")
    var fact = obj.value.split(" ")
    var data = []
    for (var i = 0; i < dataset.length; i++) {
        if (fact.includes(dataset[i]["id"])) {
            data.push(dataset[i])
        }
    }
    show_storyline(data)
    document.getElementById('story_add_fact_view').innerHTML = ""
    document.getElementById("selected_fact_id").value = ""

})
function compare(p){ //这是比较函数
    return function(m,n){
        var a = m[p];
        var b = n[p];
        return b - a; //升序
    }
}

$("#fliterid").on("click", function () {
    var obj = document.getElementsByName("fact")
    var task = []
    for (var i in obj) {
        if (obj[i].checked) {
            task.push(obj[i].value)
        }
    }
    var data = []
    for (var i = 0; i < dataset.length; i++) {
        if (task.includes(dataset[i]["task"])) {
            data.push(dataset[i])
        }
    }
    data.sort(compare("score"))
    show_fliter_vis(data)
})