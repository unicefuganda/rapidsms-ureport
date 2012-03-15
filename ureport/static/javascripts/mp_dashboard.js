

function ajax_loading(element) {
          var t = $(element);
          var offset = t.offset();
          var dim = {
              left: offset.left,
              top: offset.top,
              width: t.outerWidth(),
              height: t.outerHeight()
          };
          $('<div class="ajax_loading"></div>').css({
              position: 'absolute',
              left: dim.left + 'px',
              top: dim.top + 'px',
              width: dim.width + 'px',
              height: dim.height + 'px'
          }).appendTo(document.body).show();


}

function filter(elem,url) {
    ajax_loading(elem);
    form = $(elem).parents("form");
    form_data = form.serializeArray();
    $('#div_results_loading').show();
    $('.results').load(url, form_data, function() {
        $('.results').append('  contacts selected');
       $('.ajax_loading').remove();
    });
}