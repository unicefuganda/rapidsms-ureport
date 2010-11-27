
function ajax_loading(element)
{
    var t=$(element) ;
    var offset = t.offset();
                var dim = {
                    left:	offset.left,
                    top:	offset.top,
                    width:	t.outerWidth(),
                    height:	t.outerHeight()
                };
    $('<div class="ajax_loading"></div>').css({
                    position:	'absolute',
                    left:		dim.left + 'px',
                    top:		dim.top + 'px',
                    width:		dim.width + 'px',
                    height:		dim.height + 'px'
                }).appendTo(document.body).show();


}
var bar_opts = {
    chart: {
        renderTo: 'bar',
        defaultSeriesType: 'column'
    },
    title: {
        text: 'Poll Results For'
    },
    subtitle: {
        text: 'polls'
    },
    xAxis: {
        categories: [


        ]
    },
    yAxis: {
        min: 0,
        title: {
            text: 'Number'
        }
    },
    legend: {
        layout: 'vertical',
        backgroundColor: '#FFFFFF',
        align: 'left',
        verticalAlign: 'top',
        x: 100,
        y: 70
    },
    tooltip: {
        formatter: function() {
            return '' +
                    this.x + ': ' + this.y;
        }
    },
    plotOptions: {
        column: {
            pointPadding: 0.2,
            borderWidth: 0
        }
    },
    series: []
};

function plot_barchart(data) {


    var chart;
    bar_opts.series = data['data'];
    bar_opts.xAxis.categories = data['categories'];
    bar_opts.subtitle.text = data['title'] + "</br>" + "mean:" + parseInt(data["mean"]) + " median:" + data["median"];


    chart = new Highcharts.Chart(bar_opts);


}
var pie_opts = {
    chart: {
        renderTo: 'pie',
        margin: [10, 10, 50, 50]
    },
    title: {
        text: 'Poll Results For'
    },
    plotArea: {
        shadow: true,
        borderWidth: 30,
        backgroundColor: null
    },
    tooltip: {
        formatter: function() {
            return '<b>' + this.point.name + '</b>: ' + this.y + ' %';
        }
    },
    plotOptions: {
        pie: {
            allowPointSelect: true,
            cursor: 'pointer',
            dataLabels: {
                enabled: true,
                formatter: function() {
                    //if (this.y > 5) return this.point.name;
                },
                color: 'white',
                style: {
                    font: '13px Trebuchet MS, Verdana, sans-serif'
                }
            }
        }
    },
    legend: {
        layout: 'horizontal',
        style: {
            left: 'auto',
            bottom: 'auto',
            right: '10px',
            top: '500px'
        }
    },
    credits:false,
    subtitle: {
        text: 'test'
    },
    series: [
        {
            type: 'pie',
            name: 'Poll Results',
            data: []
        }
    ]
}
function plot_pie(data) {
    var chart;


    pie_opts.series[0].data = data['data'];
    pie_opts.subtitle.text = data['poll_names'];
    pie_opts.series[0].data[0] = {'name':data['data'][0][0],'y':data['data'][0][1],sliced: true,selected: true};
    chart = new Highcharts.Chart(pie_opts);


}
function load_freeform_polls() {

    $('#poll_list').load('/ureport/polls/freeform/');
}

function remove_selection() {
    $('#map_legend').hide();
    $('.module   ul li img').each(function() {

        $(this).removeClass('selected');
    });
    $('#visual').children().each(function() {

        $(this).hide();
    });

}
function load_tag_cloud(pk) {
     ajax_loading('#visual');
    remove_selection();
    $('#tags').show();
    var id_list = "";

    $('img.tags'+pk).addClass('selected');

    var url = "/ureport/tag_cloud/" + "?pks=+" + pk;

    $('#tags').load(url,function(){
       $('.ajax_loading').remove();
    });


}
function add_tag(tag){
    var url="/ureport/add_tag/?tag="+tag +"&poll="+$("input:checked")[0].id

    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function() {

           load_tag_cloud();
        }
    });
}

function remove_tag(tag){
     var url="/ureport/delete_tag/?tag="+tag

    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function() {

           load_excluded_tags();
        }
    });

}
function load_excluded_tags()
{

    $('#tags').hide();
    $('#visual').append("<div id='excluded'></div>") ;

   $('#excluded').load("/ureport/show_excluded/");
    $('#excluded').show();
}
function plot_piechart(pk) {
    ajax_loading('#visual');
    remove_selection();
    $('#pie').show();
    $('img.pie'+pk).addClass('selected');
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
            $('.ajax_loading').remove();
            plot_pie(data);

        }
    });

}

function plot_histogram(pk) {
    remove_selection();
    $('#bar').show();
    $('img.bar'+pk).addClass('selected');
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
        map.getPane(G_MAP_MAP_PANE).parentNode.appendChild(div);
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
        if (!force) return;
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



    var label = new Label(new GLatLng(parseFloat(y), parseFloat(x)), parseInt(data * 100) + "%", "f", new GSize(-15, 0));

    map.addOverlay(label);
    map.addOverlay(line);
    GEvent.addListener(line,'click',function(para)
		{map.openInfoWindowHtml(para,desc )});
    

}


function load_layers(pk) {
    ajax_loading('#visual');
    remove_selection();

    $('img.map'+pk).addClass('selected');
    $('#map').show();
    $('#map_legend').show();
    if($('.init').length > 0 )
    {
    init_map();
    }
$('#map').removeClass('init');
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
              $('.ajax_loading').remove();
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
                    var desc="<b>"+key+"</b><p>Total number of responses:"+total+"</p>";
                    addGraph(d, parseFloat(value['lon']), parseFloat(value['lat']), data['colors'][category],desc);
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
    map.setCenter(bounds.getCenter(), map.getBoundsZoomLevel(bounds));
    
    GEvent.addListener(map,'zoomend',function()
    		{load_layers()});

}

function toggle_show_hide(elem)
{
	if($(elem).is(':visible'))
	{
		$(elem).hide();
	}
	else
	{
		$(elem).show();
	}
}
$(document).ready(function() {


          //check if a map div is defined
          if($('#map').length > 0 )
          {
                init_map();
          }

        if($('.freeform').length > 0 )
        {
              load_freeform_polls();
        }



});
