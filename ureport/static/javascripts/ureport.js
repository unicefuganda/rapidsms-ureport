function load_freeform_polls() {

    $('#polls').load('/ureport/freeform_polls/');
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


$(document).ready(function() {

    load_freeform_polls();
});