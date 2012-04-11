

(function($) {
    $.PeriodicalUpdater = function(options, callback){

        settings = jQuery.extend({
            url: '',                // URL of ajax request
            method: 'get',          // method; get or post
            sendData: '',           // array of values to be passed to the page - e.g. {name: "John", greeting: "hello"}
            minTimeout: 15000,       // starting value for the timeout in milliseconds
            maxTimeout: 15000,       // maximum length of time between requests
            multiplier: 1,          // if set to 2, timerInterval will double each time the response hasn't changed (up to maxTimeout)
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
(function($, undefined) {

/**
 * Unobtrusive scripting adapter for jQuery
 *
 * Requires jQuery 1.6.0 or later.
 * adapted from
 * https://github.com/ureport/jquery-ujs
 */

  // Shorthand to make it a little easier to call public ureport functions from within ureport.js
  var ureport;

  $.ureport = ureport = {
    // Link elements bound by jquery-ujs
    linkClickSelector: 'a[data-confirm], a[data-method], a[data-remote], a[data-disable-with]',

    // Select elements bound by jquery-ujs
    inputChangeSelector: 'select[data-remote], input[data-remote], textarea[data-remote]',

    // Form elements bound by jquery-ujs
    formSubmitSelector: 'form',

    // Form input elements bound by jquery-ujs
    formInputClickSelector: 'form input[type=submit], form input[type=image], form button[type=submit], form button:not(button[type])',

    // Form input elements disabled during form submission
    disableSelector: 'input[data-disable-with], button[data-disable-with], textarea[data-disable-with]',

    // Form input elements re-enabled after form submission
    enableSelector: 'input[data-disable-with]:disabled, button[data-disable-with]:disabled, textarea[data-disable-with]:disabled',

    // Form required input elements
    requiredInputSelector: 'input[name][required]:not([disabled]),textarea[name][required]:not([disabled])',

    // Form file input elements
    fileInputSelector: 'input:file',

    // Link onClick disable selector with possible reenable after remote submission
    linkDisableSelector: 'a[data-disable-with]',

    // Make sure that every Ajax request sends the CSRF token
    CSRFProtection: function(xhr) {
      var token = $('meta[name="csrf-token"]').attr('content');
      if (token) xhr.setRequestHeader('X-CSRF-Token', token);
    },

    // Triggers an event on an element and returns false if the event result is false
    fire: function(obj, name, data) {
      var event = $.Event(name);
      obj.trigger(event, data);
      return event.result !== false;
    },

    // Default confirm dialog, may be overridden with custom confirm dialog in $.ureport.confirm
    confirm: function(message) {
      return confirm(message);
    },

    // Default ajax function, may be overridden with custom function in $.ureport.ajax
    ajax: function(options) {
      return $.ajax(options);
    },

    // Default way to get an element's href. May be overridden at $.ureport.href.
    href: function(element) {
      return element.attr('href');
    },

    // Submits "remote" forms and links with ajax
    handleRemote: function(element) {
      var method, url, data, crossDomain, dataType, options;

      if (ureport.fire(element, 'ajax:before')) {
        crossDomain = element.data('cross-domain') || null;
        dataType = element.data('type') || ($.ajaxSettings && $.ajaxSettings.dataType);

        if (element.is('form')) {
          method = element.attr('method');
          url = element.attr('action');
          data = element.serializeArray();
          // memoized value from clicked submit button
          var button = element.data('ujs:submit-button');
          if (button) {
            data.push(button);
            element.data('ujs:submit-button', null);
          }
        } else if (element.is(ureport.inputChangeSelector)) {
          method = element.data('method');
          url = element.data('url');
          data = element.serialize();
          if (element.data('params')) data = data + "&" + element.data('params');
        } else {
          method = element.data('method');
          url = ureport.href(element);
          data = element.data('params') || null;
        }

        options = {
          type: method || 'GET', data: data, dataType: dataType, crossDomain: crossDomain,
          // stopping the "ajax:beforeSend" event will cancel the ajax request
          beforeSend: function(xhr, settings) {
            if (settings.dataType === undefined) {
              xhr.setRequestHeader('accept', '*/*;q=0.5, ' + settings.accepts.script);
            }
            return ureport.fire(element, 'ajax:beforeSend', [xhr, settings]);
          },
          success: function(data, status, xhr) {
            element.trigger('ajax:success', [data, status, xhr]);
          },
          complete: function(xhr, status) {
            element.trigger('ajax:complete', [xhr, status]);
          },
          error: function(xhr, status, error) {
            element.trigger('ajax:error', [xhr, status, error]);
          }
        };
        // Only pass url to `ajax` options if not blank
        if (url) { options.url = url; }

        return ureport.ajax(options);
      } else {
        return false;
      }
    },

    // Handles "data-method" on links such as:
    // <a href="/users/5" data-method="delete" rel="nofollow" data-confirm="Are you sure?">Delete</a>
    handleMethod: function(link) {
      var href = ureport.href(link),
        method = link.data('method'),
        target = link.attr('target'),
        csrf_token = $('meta[name=csrf-token]').attr('content'),
        csrf_param = $('meta[name=csrf-param]').attr('content'),
        form = $('<form method="post" action="' + href + '"></form>'),
        metadata_input = '<input name="_method" value="' + method + '" type="hidden" />';

      if (csrf_param !== undefined && csrf_token !== undefined) {
        metadata_input += '<input name="' + csrf_param + '" value="' + csrf_token + '" type="hidden" />';
      }

      if (target) { form.attr('target', target); }

      form.hide().append(metadata_input).appendTo('body');
      form.submit();
    },

    /* Disables form elements:
      - Caches element value in 'ujs:enable-with' data store
      - Replaces element text with value of 'data-disable-with' attribute
      - Sets disabled property to true
    */
    disableFormElements: function(form) {
      form.find(ureport.disableSelector).each(function() {
        var element = $(this), method = element.is('button') ? 'html' : 'val';
        element.data('ujs:enable-with', element[method]());
        element[method](element.data('disable-with'));
        element.prop('disabled', true);
      });
    },

    /* Re-enables disabled form elements:
      - Replaces element text with cached value from 'ujs:enable-with' data store (created in `disableFormElements`)
      - Sets disabled property to false
    */
    enableFormElements: function(form) {
      form.find(ureport.enableSelector).each(function() {
        var element = $(this), method = element.is('button') ? 'html' : 'val';
        if (element.data('ujs:enable-with')) element[method](element.data('ujs:enable-with'));
        element.prop('disabled', false);
      });
    },

   /* For 'data-confirm' attribute:
      - Fires `confirm` event
      - Shows the confirmation dialog
      - Fires the `confirm:complete` event

      Returns `true` if no function stops the chain and user chose yes; `false` otherwise.
      Attaching a handler to the element's `confirm` event that returns a `falsy` value cancels the confirmation dialog.
      Attaching a handler to the element's `confirm:complete` event that returns a `falsy` value makes this function
      return false. The `confirm:complete` event is fired whether or not the user answered true or false to the dialog.
   */
    allowAction: function(element) {
      var message = element.data('confirm'),
          answer = false, callback;
      if (!message) { return true; }

      if (ureport.fire(element, 'confirm')) {
        answer = ureport.confirm(message);
        callback = ureport.fire(element, 'confirm:complete', [answer]);
      }
      return answer && callback;
    },

    // Helper function which checks for blank inputs in a form that match the specified CSS selector
    blankInputs: function(form, specifiedSelector, nonBlank) {
      var inputs = $(), input,
        selector = specifiedSelector || 'input,textarea';
      form.find(selector).each(function() {
        input = $(this);
        // Collect non-blank inputs if nonBlank option is true, otherwise, collect blank inputs
        if (nonBlank ? input.val() : !input.val()) {
          inputs = inputs.add(input);
        }
      });
      return inputs.length ? inputs : false;
    },

    // Helper function which checks for non-blank inputs in a form that match the specified CSS selector
    nonBlankInputs: function(form, specifiedSelector) {
      return ureport.blankInputs(form, specifiedSelector, true); // true specifies nonBlank
    },

    // Helper function, needed to provide consistent behavior in IE
    stopEverything: function(e) {
      $(e.target).trigger('ujs:everythingStopped');
      e.stopImmediatePropagation();
      return false;
    },

    // find all the submit events directly bound to the form and
    // manually invoke them. If anyone returns false then stop the loop
    callFormSubmitBindings: function(form, event) {
      var events = form.data('events'), continuePropagation = true;
      if (events !== undefined && events['submit'] !== undefined) {
        $.each(events['submit'], function(i, obj){
          if (typeof obj.handler === 'function') return continuePropagation = obj.handler(event);
        });
      }
      return continuePropagation;
    },

    //  replace element's html with the 'data-disable-with' after storing original html
    //  and prevent clicking on it
    disableElement: function(element) {
      element.data('ujs:enable-with', element.html()); // store enabled state
      element.html(element.data('disable-with')); // set to disabled state
      element.bind('click.ureportDisable', function(e) { // prevent further clicking
        return ureport.stopEverything(e)
      });
    },

    // restore element to its original state which was disabled by 'disableElement' above
    enableElement: function(element) {
      if (element.data('ujs:enable-with') !== undefined) {
        element.html(element.data('ujs:enable-with')); // set to old enabled state
        // this should be element.removeData('ujs:enable-with')
        // but, there is currently a bug in jquery which makes hyphenated data attributes not get removed
        element.data('ujs:enable-with', false); // clean up cache
      }
      element.unbind('click.ureportDisable'); // enable element
    }

  };

  $.ajaxPrefilter(function(options, originalOptions, xhr){ if ( !options.crossDomain ) { ureport.CSRFProtection(xhr); }});

  $(document).delegate(ureport.linkDisableSelector, 'ajax:complete', function() {
      ureport.enableElement($(this));
  });

  $(document).delegate(ureport.linkClickSelector, 'click.ureport', function(e) {
    var link = $(this), method = link.data('method'), data = link.data('params');
    if (!ureport.allowAction(link)) return ureport.stopEverything(e);

    if (link.is(ureport.linkDisableSelector)) ureport.disableElement(link);

    if (link.data('remote') !== undefined) {
      if ( (e.metaKey || e.ctrlKey) && (!method || method === 'GET') && !data ) { return true; }

      if (ureport.handleRemote(link) === false) { ureport.enableElement(link); }
      return false;

    } else if (link.data('method')) {
      ureport.handleMethod(link);
      return false;
    }
  });

  $(document).delegate(ureport.inputChangeSelector, 'change.ureport', function(e) {
    var link = $(this);
    if (!ureport.allowAction(link)) return ureport.stopEverything(e);

    ureport.handleRemote(link);
    return false;
  });

  $(document).delegate(ureport.formSubmitSelector, 'submit.ureport', function(e) {
    var form = $(this),
      remote = form.data('remote') !== undefined,
      blankRequiredInputs = ureport.blankInputs(form, ureport.requiredInputSelector),
      nonBlankFileInputs = ureport.nonBlankInputs(form, ureport.fileInputSelector);

    if (!ureport.allowAction(form)) return ureport.stopEverything(e);

    // skip other logic when required values are missing or file upload is present
    if (blankRequiredInputs && form.attr("novalidate") == undefined && ureport.fire(form, 'ajax:aborted:required', [blankRequiredInputs])) {
      return ureport.stopEverything(e);
    }

    if (remote) {
      if (nonBlankFileInputs) {
        return ureport.fire(form, 'ajax:aborted:file', [nonBlankFileInputs]);
      }

      // If browser does not support submit bubbling, then this live-binding will be called before direct
      // bindings. Therefore, we should directly call any direct bindings before remotely submitting form.
      if (!$.support.submitBubbles && $().jquery < '1.7' && ureport.callFormSubmitBindings(form, e) === false) return ureport.stopEverything(e);

      ureport.handleRemote(form);
      return false;

    } else {
      // slight timeout so that the submit button gets properly serialized
      setTimeout(function(){ ureport.disableFormElements(form); }, 13);
    }
  });

  $(document).delegate(ureport.formInputClickSelector, 'click.ureport', function(event) {
    var button = $(this);

    if (!ureport.allowAction(button)) return ureport.stopEverything(event);

    // register the pressed submit button
    var name = button.attr('name'),
      data = name ? {name:name, value:button.val()} : null;

    button.closest('form').data('ujs:submit-button', data);
  });

  $(document).delegate(ureport.formSubmitSelector, 'ajax:beforeSend.ureport', function(event) {
    if (this == event.target) ureport.disableFormElements($(this));
  });

  $(document).delegate(ureport.formSubmitSelector, 'ajax:complete.ureport', function(event) {
    if (this == event.target) ureport.enableFormElements($(this));
  });

})( jQuery );


