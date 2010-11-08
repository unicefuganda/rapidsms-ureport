var points = {}; // hash to store layers with their description for each marker
var markers = {};
var infopanel;
var start_value;
var end_value;
var bbox;
var current_zoom;
var layers = {};
var urls = {};
var colors = [];
//make description global
var description = "";

var hf;


function load_freeform_polls() {

    $('#polls').load('/ureport/polls/t/');
}

function load_tag_cloud() {
    var id_list = "";
    $("#poll_list").find('input').each(function() {

        if ($(this).attr("checked")) {

            id_list = id_list + '+' + String(this.id);
        }

    });

    var url = "/ureport/tag_cloud/" + "?pks=" + id_list;

    $('#tag_cloud').load(url);
}
function plot_piechart() {
    var id_list = "";
    $("#poll_list").find('input').each(function() {

        if ($(this).attr("checked")) {

            id_list = id_list + '+' + String(this.id);
        }

    });

    var url = "/ureport/pie_graph/" + "?pks=" + id_list;
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            plot_pie(data);

        }
    });
}

function plot_histogram() {
    var id_list = "";
    $("#poll_list").find('input').each(function() {

        if ($(this).attr("checked")) {

            id_list = id_list + '+' + String(this.id);
        }

    });

    var url = "/ureport/histogram/" + "?pks=" + id_list;
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            plot_barchart(data);

        }
    });
}
//function to create label
function Label(point, html, classname, pixelOffset) {
    // Mandatory parameters
    this.point = point;
    this.html = html;

    // Optional parameters
    this.classname = classname || "";
    this.pixelOffset = pixelOffset || new GSize(0, 0);


    this.prototype = new GOverlay();

    this.initialize = function(map) {
        // Creates the DIV representing the label
        var div = document.createElement("div");
        div.style.position = "absolute";
        div.innerHTML = '<div class="' + this.classname + '">' + this.html + '</div>';
        map.getPane(G_MAP_FLOAT_SHADOW_PANE).appendChild(div);
        this.map_ = map;
        this.div_ = div;
    }
// Remove the label DIV from the map pane
    this.remove = function() {
        this.div_.parentNode.removeChild(this.div_);
    }
// Copy the label data to a new instance
    this.copy = function() {
        return new Label(this.point, this.html, this.classname, this.pixelOffset);
    }
// Redraw based on the current projection and zoom level
    this.redraw = function(force) {
        var p = this.map_.fromLatLngToDivPixel(this.point);
        var h = parseInt(this.div_.clientHeight);
        this.div_.style.left = (p.x + this.pixelOffset.width) + "px";
        this.div_.style.top = (p.y + this.pixelOffset.height - h) + "px";
    }


}


//add graph to point
function addGraph(data, x, y, color, desc) {
    //get map width and height in lat lon
    var d = map.getBounds().toSpan();
    var height = d.lng();
    var width = d.lat();
    var maxsize = 0.9;
    var pointpair = [];
    var increment = (parseFloat(height) / 10.0) / 100;
    var start = new GPoint(parseFloat(x), parseFloat(y));
    var volume = parseInt((parseFloat(data) * 100) / maxsize);

    pointpair.push(start);
    //draw the graph as an overlay
    pointpair.push(new GPoint(parseFloat(x + increment), parseFloat(y + increment)));
    var line = new GPolyline(pointpair, color, volume);
    map.addOverlay(line);
    var label = new Label(new GLatLng(parseFloat(y), parseFloat(x)), parseInt(data * 100) + "%", "f", new GSize(0, 0));


    map.addOverlay(label);


}


function load_layers() {
    var id_list = "";
    $("#poll_list").find('input').each(function() {

        if ($(this).attr("checked")) {

            id_list = id_list + '+' + String(this.id);
        }

    });

    var url = "/ureport/map/" + "?pks=" + id_list;
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            //add legend
            $('#map_legend table').text(' ');
            map.clearOverlays();

            $.each(data['colors'], function(ky, vl) {

                var elem = '<tr><td><span style="width:15px;height:15px;background-color:' + vl + ';float:left;display:block;margin-top:10px;"></span><td><td >' + ky + '</td></tr>';
                $('#map_legend table').append(elem);

            });


            $.each(data, function(key, value) {
                if (!key.match('color')) {
                    var max = 0;
                    var total = 0;
                    var category = "";

                    $.each(value['data'], function(k, v) {

                        total = total + v;
                        if (v > max) {
                            max = v;
                            category = k;
                        }

                    });
                    d = max / total;
                    console.log(d);
                    addGraph(d, parseFloat(value['lon']), parseFloat(value['lat']), data['colors'][category]);
                }
            }


                    );
        }
    });

}

//	function to draw simple map
function init_map() {

    //initialise the map object
    map = new GMap2(document.getElementById("map"));
    //add map controls
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());

    //make sure the zoom fits all the points
    var bounds = new GLatLngBounds;
    bounds.extend(new GLatLng(parseFloat(minLat), parseFloat(minLon)));
    bounds.extend(new GLatLng(parseFloat(maxLat), parseFloat(maxLon)));
    map.setCenter(bounds.getCenter(), 9);


}


$(document).ready(function() {


    load_freeform_polls();
    init_map();
});