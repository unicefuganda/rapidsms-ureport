jQuery.fn.forms = function () {
  var btn = $("input[type=submit]");
  btn.parent().prepend("<span class=\"loader\" title=\"Sending...\">&nbsp;</span>");

  this.bind("submit",
            function() {
              $("input[type=submit]").hide();
              $("span.cancel").hide();
              $("span.loader").show();
            }
           );
};

jQuery.fn.addHover = function() {
  return this.hover(
    function(){ jQuery(this).addClass("hover"); },
    function(){ jQuery(this).removeClass("hover"); }
  )
};