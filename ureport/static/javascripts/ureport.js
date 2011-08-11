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
	if (data.length < 1) {
		return;
	}

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
            plot_piechart(data['data'], element_id);
        }
    });
}
/**
 * Fetches an HTML fragment of tags and loads them into the div with id "tags."
 * (see ureport/partials/tag_cloud/tag_cloud.html and ureport.views.generate_tag_cloud).
 * @param url the url, containing a poll id, that will be ajax loaded for the HTML fragment
 */
function load_tag_cloud(url) {
    // ajax_loading('#visual');
    remove_selection();
    $('#tags').show();
    $('#tags').load(url,function(){
       $('.ajax_loading').remove();
    });
}

/**
adds a word to the ignored list and returns a call to  load_tag_cloud on success.
The call to load_tag_cloud returns an updated tagcloud.
@param  add_tag_url  the url containing the word to be added to drop list
@param load_cloud_url the url parameter to load_tag_cloud
 */
function add_tag(add_tag_url,load_cloud_url){
    $.ajax({
        type: "GET",
        url:add_tag_url,
        dataType: "json",
        success: function() {
           load_tag_cloud(load_cloud_url);
        }
    });
}

/**
removes a word to the ignored list and returns a call to  load_tag_cloud on success.
The call to load_tag_cloud returns an updated tagcloud.
@param  add_tag_url  the url containing the primary key of the word to be deleted from the drop list
@param load_cloud_url the url parameter to load_tag_cloud
 */
function remove_tag(delete_tag_url, load_cloud_url){
    $.ajax({
        type: "GET",
        url:delete_tag_url,
        dataType: "json",
        success: function() {
           load_excluded_tags(load_cloud_url);
        }
    });
}

/**
 * Fetches an HTML component  containing ignored words and loads them into div#excluded
 * (refer to ureport/templates/ureport/partials/tag_cloud/ignored_tags.html and ureport.views.show_ignored_tags)
 * @param url the url, containing a poll id for a poll whose excluded tags will be ajax loaded into div#excluded
 */
function load_excluded_tags(url) {
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


function load_responses(url) {
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
