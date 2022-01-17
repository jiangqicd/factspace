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
    var dataset = $(globalConfig.datasetSelect).val();
    console.log(attribute)
    $.post("/scatter", {"fact": JSON.stringify(fact), "attribute": JSON.stringify(attribute), "dataset": dataset})
        .done(function (response) {
            console.log(response)

        })

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
                element.setAttribute("value", Q[i])
                element.setAttribute("name", "T")
                cell.appendChild(element)
                cell.appendChild(document.createTextNode(T[i]))
                row.appendChild(cell)
                var check_T = "<tr><td><label style='font-weight: normal'><input type='checkbox'name='Q'value=" + Q[i] + ">" + Q[i] + "</label></td></tr>"
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
                var check_N = "<tr><td><label style='font-weight: normal'><input type='checkbox'name='Q'value=" + Q[i] + ">" + Q[i] + "</label></td></tr>"
                $(globalConfig.N + " tbody").append(check_N);
            }
        });
}

function overview(path) {
    $.getJSON(path, function (data) {
        for (var fact in data) {
            console.log(fact)
        }
        var count = 0
        for (var fact in data) {
            if (count < 1000) {
                var vis = document.createElement("div");
                vis.id = fact
                document.getElementById('visoverview').appendChild(vis);
                spec = data[fact]
                spec['width'] = 200
                spec['height'] = 200
                vegaEmbed(document.getElementById(fact), spec, vegaOptMode)
                count++
            }
            // var vis = document.createElement("div");
            // vis.id = fact
            // document.getElementById('visoverview').appendChild(vis);
            // spec = data[fact]
            // spec['width'] = 50
            // spec['height'] = 50
            // vegaEmbed(document.getElementById(fact), spec, vegaOptMode)
            // count++
        }
    })
}

function initialize() {
    // var dataset = $(globalConfig.datasetSelect).val();
    // $.post("/init", {"dependency_parser": "corenlp"})
    //     .done(function (response) {
    //         configureDatabase(dataset);
    //     });
    overview(path)
}

$(document).ready(function () {
    initialize();
});
