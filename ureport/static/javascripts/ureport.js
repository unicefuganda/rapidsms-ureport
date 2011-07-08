var category_colors = [];
var category_color_lookup = {};
var category_offset = 0;

/**
 * Registers a category name with a particular color,
 * for consistency across multiple visualizations.  If the
 * category name hasn't been passed to this function yet, it
 * will be added to category_color_lookup (as a key), and
 * the next available color from the color list will be
 * the value.  See ureport/templates/layout.html for the
 * loading of the colors into the category_colors based on
 * the values in ureport/settings.py
 * @param category the category name, e.g. 'yes','no',etc
 * @return the color value in css form e.g., '#ABff07'
 */
function get_color(category) {
    if (!category_color_lookup[category]) {
        if (category_colors.length <= category_offset) {
            category_color_lookup[category] = '#000000';
        } else {
            category_color_lookup[category] = category_colors[category_offset];
            category_offset += 1;
        }
    }
    return category_color_lookup[category];
}

/**
 * Clear the visualization area of previous visuals
 */
function remove_selection() {
    $('#map_legend').hide();
    $('.module ul li img').each(function() {
        $(this).removeClass('selected');
    });
    $('#visual').children().each(function() {
        $(this).empty();
        $(this).hide();
    });
}

function ajax_loading(element)
{
    var t=$(element);
    var offset = t.offset();
                var dim = {
                    left:    offset.left,
                    top:    offset.top,
                    width:    t.outerWidth(),
                    height:    t.outerHeight()
                };
    $('<div class="ajax_loading"></div>').css({
                    position:    'absolute',
                    left:        dim.left + 'px',
                    top:        dim.top + 'px',
                    width:        dim.width + 'px',
                    height:        dim.height + 'px'
                }).appendTo(document.body).show();
}

var bar_opts = {
    chart: {renderTo: 'bar',defaultSeriesType: 'column'},
    title: {text: ''},
    subtitle: {text: ''},
    xAxis: {categories: []},
    yAxis: {min: 0,title: {text: 'Count'}},
    tooltip: {formatter: function() {return '' + this.x + ': ' + this.y;}},
    plotOptions: {column: {pointPadding: 0.2,borderWidth: 0}},
    series: [{data:[]}]
};

function plot_histogram(data, element_id) {
    var chart;
    max = Math.ceil(data[0][0]);
    min = Math.floor(data[data.length - 1][0]);
    num_bars = 6;
    while (((max - min) % num_bars) != 0 && min >= 0) {
        min--;
    }
    while (((max - min) % num_bars) != 0) {
        max++;
    }
    increment = (max - min) / num_bars;
    offset = data.length - 1;
    bar_data = [];
    categories = [];
    for (i = min; i < max; i += increment) {
        category = '' + i + '-' + (i + increment);
        count = 0;
        categories[categories.length] = category;
        if (i + increment == max) {
            // the last range should be inclusive, otherwise we won't
            // count one of the numbers
            increment += 1;
        }
        while (offset > -1 && data[offset][0] >= i && data[offset][0] < (i + increment)) {
            count += data[offset][1];
            offset -= 1;
        }
        bar_data[bar_data.length] = count;
    }
    bar_opts.series[0].data = bar_data;
    bar_opts.xAxis.categories = categories;
    bar_opts.chart.renderTo = element_id;
    chart = new Highcharts.Chart(bar_opts);
}

function load_histogram(poll_id, element_id, url) {
    remove_selection();
    $('#' + element_id).show();
    $('img.bar'+element_id).addClass('selected');
    var id_list = "";
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            plot_histogram(data, element_id);
        }
    });
}

var pie_opts = {
    chart: {renderTo: 'pie',margin: [5,5,5,5]},
    title: {text: ''},
    plotArea: {shadow: true,borderWidth: 30,backgroundColor: null},
    tooltip: {formatter: function() {return '<b>' + this.point.name + '</b>: ' + this.y.toFixed(1) + ' %';}},
    plotOptions: {pie: {allowPointSelect: true,cursor: 'pointer',dataLabels: {
                enabled: true,
                formatter: function() {},
                color: 'white',
                style: {font: '13px Trebuchet MS, Verdana, sans-serif'}}}},
    legend: {layout: 'horizontal',style: {left: 'auto',bottom: 'auto',right: '10px',top: '525px'}},
    credits:false,
    subtitle: {text: ''},
    series: [{type: 'pie',name: '',data: []}]
}

function plot_piechart(data, element_id) {
    var chart;
    pie_opts.chart.renderTo = element_id;

    plot_data = [];
    plot_colors = [];
    total = 0;
    for (i = 0; i < data.length; i++) {
        plot_data[plot_data.length] = [data[i].category__name, data[i].value];
        plot_colors[plot_colors.length] = get_color(data[i].category__name);
        total += plot_data[plot_data.length - 1][1];
    }
    for (i = 0; i < plot_data.length; i++) {
        plot_data[i][1] = (plot_data[i][1] * 100.0) / total;
    }
    pie_opts.colors = plot_colors;
    pie_opts.series[0].data = plot_data;
    pie_opts.series[0].data[0] = {'name':plot_data[0][0],'y':plot_data[0][1],sliced: true,selected: true};
    chart = new Highcharts.Chart(pie_opts);
}

function load_piechart(poll_id, element_id, url) {
    // ajax_loading('#visual' + divstr);
    remove_selection();
    $('#' + element_id).show();
    $('img.pie'+poll_id).addClass('selected');
    var id_list = "";
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            $('.ajax_loading').remove();
            plot_piechart(data, element_id);
        }
    });
}

function load_tag_cloud(poll_id, url) {
    // ajax_loading('#visual');
    tag_poll_pk=poll_id;
    remove_selection();
    $('#tags').show();
    var id_list = "";

    $('img.tags'+poll_id).addClass('selected');
    $('#tags').load(url,function(){
       $('.ajax_loading').remove();
    });
}

function add_tag(poll_id, add_tag_url,load_cloud_url){
    $.ajax({
        type: "GET",
        url:add_tag_url,
        dataType: "json",
        success: function() {
           load_tag_cloud(poll_id, load_cloud_url);
        }
    });
}

function remove_tag(poll_id, delete_tag_url, load_cloud_url){
    $.ajax({
        type: "GET",
        url:delete_tag_url,
        dataType: "json",
        success: function() {
           load_excluded_tags(poll_id, load_cloud_url);
        }
    });
}

function load_excluded_tags(poll_id, url) {
    $('#tagcontent').hide();
    $('#excluded').load(url);
    $('#excluded').show();
}

function load_timeseries(url, poll_id) {
	remove_selection();
	$('#poll_timeseries').show();
	$('img.series'+poll_id).addClass('selected');
	var id_list = "";
	$('#poll_timeseries').load(url);
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
        div.style.cursor = 'pointer';
        div.style.zindex = 12345;
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
    var maxsize = 1 + (10.0 / map.getZoom());
    var pointpair = [];
    var increment = parseFloat(height) / 1000.0;
    var start = new GPoint(parseFloat(y), parseFloat(x));
    var volume = parseInt((parseFloat(data) * 100) / maxsize);
    pointpair.push(start);
    //draw the graph as an overlay
    pointpair.push(new GPoint(parseFloat(y + increment), parseFloat(x + increment)));
    var line = new GPolyline(pointpair, color, volume);

    var label = new Label(new GLatLng(parseFloat(x), parseFloat(y)), parseInt(data * 100) + "%", "f", new GSize(-15, 0));

    map.addOverlay(label);
    map.addOverlay(line);
    //line.setDraggableCursor('pointer');
    GEvent.addListener(line,'click',function(para)
        {map.openInfoWindowHtml(para,desc)});
    GEvent.addListener(line, "mouseover", function() {
        $('#map').css("cursor" ,"pointer");
    });
}

function load_map(poll_id, element_id, url) {
    // ajax_loading('#visual' + divstr);
    remove_selection();

    $('img.map'+poll_id).addClass('selected');
    $('#' + element_id).show();
    if($('.init').length > 0)
    {
        init_map(poll_id, element_id);
    }
    $('#' + element_id).removeClass('init');
    var id_list = "";
    $.ajax({
        type: "GET",
        url:url,
        dataType: "json",
        success: function(data) {
            map.clearOverlays();
            $('.ajax_loading').remove();

            location_name = data[0].location_name;
            lat = data[0].lat;
            lon = data[0].lon;
            max = 0;
            category = data[0].category__name;
            total = 0;
            popup_description = "<b>" + location_name + "</b>";
            for (i = 0; i < data.length; i++) {
                if (location_name != data[i].location_name) {
                    d = max / total;
                    popup_description += "<p>Total number of responses:"+total+"</p>";
                    addGraph(d, parseFloat(lat), parseFloat(lon), get_color(category),popup_description);

                    location_name = data[i].location_name;
                    lat = data[i].lat;
                    lon = data[i].lon;
                    category = data[i].category__name;
                    max = 0;
                    total = 0;
                    popup_description = "<b>" + location_name + "</b>";
                }
                popup_description += "<p>" + data[i].category__name + ":" + data[i].value + "</p>";
                total += data[i].value;
                if (data[i].value > max) {
                    max = data[i].value;
                    category = data[i].category__name;
                }
            }
            d = max / total;
            popup_description += "<p>Total number of responses:"+total+"</p>";
            addGraph(d, parseFloat(lat), parseFloat(lon), get_color(category),popup_description);
            //add legend
            $('#' + element_id + "_legend").show();
            $('#' + element_id + '_legend table').html(' ');
            for (category in category_color_lookup) {
                category_span = '<span style="width:15px;height:15px;background-color:' + category_color_lookup[category] + ';float:left;display:block;margin-top:10px;"></span>'
                $('#' + element_id + '_legend table').append('<tr><td>' + category + '</td><td>' + category_span + '</td></tr>')
            }
        }
    });
}

// function to draw simple map
function init_map(poll_id, element_id) {

    //initialise the map object
    map = new GMap2(document.getElementById(element_id));
    //add map controls
    map.addControl(new GLargeMapControl());
    map.addControl(new GMapTypeControl());

    //make sure the zoom fits all the points
    var bounds = new GLatLngBounds;
    bounds.extend(new GLatLng(parseFloat(minLat), parseFloat(minLon)));
    bounds.extend(new GLatLng(parseFloat(maxLat), parseFloat(maxLon)));
    map.setCenter(bounds.getCenter(), map.getBoundsZoomLevel(bounds));
    
    GEvent.addListener(map,'zoomend',function() {
        load_map(poll_id, element_id)
    });
}

function load_responses(poll_id, url) {
    // ajax_loading('#visual');
    remove_selection();
    $('#poll_responses').show();
    $('#poll_responses').load(url,function(){
       $('.ajax_loading').remove();
    });
}

function load_report(poll_id, url) {
    // ajax_loading('#visual');
    remove_selection();
    $('#poll_report').show();
    $('#poll_report').load(url,function(){
       $('.ajax_loading').remove();
    });
}

/**
 * See ureport/templates/ureport/partials/dashboard/poll_row.html
 * This function collapses the poll list to allow the visualization
 * to occupy the majority of the screen.
 */
function collapse() {
    $('#show_results_list').show();
    $('#object_list').hide();
}

function expand() {
    $('#show_results_list').hide();
    $('#object_list').show();
}

function deleteReporter(elem, pk, name) {
    if (confirm('Are you sure you want to remove ' + name + '?')) {
        $(elem).parents('tr').remove();
        $.post('../reporter/' + pk + '/delete/', function(data) {});
    }
}

function editReporter(elem, pk) {
    overlay_loading_panel($(elem).parents('tr'));
    $(elem).parents('tr').load('../reporter/' + pk + '/edit/', '', function() {
        $('#div_panel_loading').hide();
    });
}

function toggleReplyBox(anchor, phone, msg_id){
    anchor.innerHTML = (anchor.text == '- send message -')? '- hide message box -' : '- send message -';
    var _currentDiv = document.getElementById('replyForm_'+msg_id);
    $(_currentDiv).append($('#formcontent'));
    $('#formcontent').show();
    $(_currentDiv).slideToggle(300);
    $('#id_recipient').val(phone);
    $('#id_in_response_to').val(msg_id);
}

function submitForm(link, action, resultDiv) {
    form = $(link).parents("form");
    form_data = form.serializeArray();
    resultDiv.load(action, form_data);
}

$(document).ready(function() {
	//Accordion based messaging history list
    if($('#accordion').length > 0) {
    	$(function() {
    		$( "#accordion" ).accordion({ autoHeight: false, collapsible: true });
    	});
    }
	$(function() {    		
        $('.replyForm').hide();
	});
});
