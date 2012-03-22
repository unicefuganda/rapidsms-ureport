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

(function($) {
    $.PeriodicalUpdater = function(options, callback){

        settings = jQuery.extend({
            url: '',                // URL of ajax request
            method: 'get',          // method; get or post
            sendData: '',           // array of values to be passed to the page - e.g. {name: "John", greeting: "hello"}
            minTimeout: 1000,       // starting value for the timeout in milliseconds
            maxTimeout: 8000,       // maximum length of time between requests
            multiplier: 2,          // if set to 2, timerInterval will double each time the response hasn't changed (up to maxTimeout)
            type: 'text'            // response type - text, xml, json etc - as with $.get or $.post
        }, options);

        // should we be GETting or POSTing the URL?
        f = settings.method == 'post' || settings.method == 'POST' ? $.post : $.get;

        // you really, really don't want multipliers of less than 1 - it will cause lots of strain on the server!
        settings.multiplier = settings.multiplier < 1 ? 1:settings.multiplier;

        // set some initial values, then begin
        var prevContent;
        var timerInterval = settings.minTimeout;
        getdata();

        function getdata()
        {
            f(settings.url+new Date().getTime(), settings.sendData, function(d){
                if(1){
                    if(callback)
                    {
                        callback(d);
                    }

                    // recursive call to getdata(). You can stop ajax requests from this plugin by calling clearTimeout(PeriodicalTimer);
                    // (on a button click, for example)
                    PeriodicalTimer = setTimeout(getdata, settings.minTimeout);
                }else{
                    // content hasn't changed - re-calculate timers and recursively call getdata() again
                    if(timerInterval < settings.maxTimeout)
                    {
                        timerInterval = timerInterval * settings.multiplier;
                    }

                    if(timerInterval > settings.maxTimeout)
                    {
                        timerInterval = settings.maxTimeout;
                    }

                    PeriodicalTimer = setTimeout(getdata, timerInterval);
                }
            }, settings.type)
        }
    };
})(jQuery);