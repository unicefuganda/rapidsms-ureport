

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
/*
        BestInPlace (for jQuery)
        version: 0.1.0 (01/01/2011)
        @requires jQuery >= v1.4
        @requires jQuery.purr to display pop-up windows

        By Bernat Farrero based on the work of Jan Varwig.
        Examples at http://bernatfarrero.com

        Licensed under the MIT:
          http://www.opensource.org/licenses/mit-license.php

        Usage:

        Attention.
        The format of the JSON object given to the select inputs is the following:
        [["key", "value"],["key", "value"]]
        The format of the JSON object given to the checkbox inputs is the following:
        ["falseValue", "trueValue"]
*/

function BestInPlaceEditor(e) {
  this.element = jQuery(e);
  this.initOptions();
  this.bindForm();
  this.initNil();
  $(this.activator).bind('click', {editor: this}, this.clickHandler);
}

BestInPlaceEditor.prototype = {
  // Public Interface Functions //////////////////////////////////////////////

  activate : function() {
    var to_display = "";
    if (this.isNil) {
      to_display = "";
    }
    else if (this.original_content) {
      to_display = this.original_content;
    }
    else {
      to_display = this.element.html();
    }

    var elem = this.isNil ? "" : this.element.html();
    this.oldValue = elem;
    this.display_value = to_display;
    $(this.activator).unbind("click", this.clickHandler);
    this.activateForm();
  },

  abort : function() {
    if (this.isNil) this.element.html(this.nil);
    else            this.element.html(this.oldValue);
    $(this.activator).bind('click', {editor: this}, this.clickHandler);
    this.element.trigger($.Event("best_in_place:abort"));
  },

  abortIfConfirm : function () {
    if (confirm("Are you sure you want to discard your changes?")) {
      this.abort();
    }
  },

  update : function() {
    var editor = this;
    if (this.formType in {"input":1, "textarea":1} && this.getValue() == this.oldValue)
    { // Avoid request if no change is made
      this.abort();
      return true;
    }
    this.isNil = false;
    editor.ajax({
      "type"       : "post",
      "dataType"   : "text",
      "data"       : editor.requestData(),
      "success"    : function(data){ editor.loadSuccessCallback(data); },
      "error"      : function(request, error){ editor.loadErrorCallback(request, error); }
    });
    if (this.formType == "select") {
      var value = this.getValue();
      $.each(this.values, function(i, v) {
        if (value == v[0]) {
          editor.element.html(v[1]);
        }
      }
    );
    } else if (this.formType == "checkbox") {
      editor.element.html(this.getValue() ? this.values[1] : this.values[0]);
    } else {
      editor.element.html(this.getValue() != "" ? this.getValue() : this.nil);
    }
    editor.element.trigger($.Event("best_in_place:update"));
  },

  activateForm : function() {
    alert("The form was not properly initialized. activateForm is unbound");
  },

  // Helper Functions ////////////////////////////////////////////////////////

  initOptions : function() {
    // Try parent supplied info
    var self = this;
    self.element.parents().each(function(){
      self.url           = self.url           || jQuery(this).attr("data-url");
      self.collection    = self.collection    || jQuery(this).attr("data-collection");
      self.formType      = self.formType      || jQuery(this).attr("data-type");
      self.objectName    = self.objectName    || jQuery(this).attr("data-object");
      self.attributeName = self.attributeName || jQuery(this).attr("data-attribute");
      self.activator     = self.activator     || jQuery(this).attr("data-activator");
      self.okButton      = self.okButton      || jQuery(this).attr("data-ok-button");
      self.cancelButton  = self.cancelButton  || jQuery(this).attr("data-cancel-button");
      self.nil           = self.nil           || jQuery(this).attr("data-nil");
      self.inner_class   = self.inner_class   || jQuery(this).attr("data-inner-class");
      self.html_attrs    = self.html_attrs    || jQuery(this).attr("data-html-attrs");
      self.original_content    = self.original_content    || jQuery(this).attr("data-original-content");
    });

    // Try Rails-id based if parents did not explicitly supply something
    self.element.parents().each(function(){
      var res = this.id.match(/^(\w+)_(\d+)$/i);
      if (res) {
        self.objectName = self.objectName || res[1];
      }
    });

    // Load own attributes (overrides all others)
    self.url           = self.element.attr("data-url")           || self.url      || document.location.pathname;
    self.collection    = self.element.attr("data-collection")    || self.collection;
    self.formType      = self.element.attr("data-type")          || self.formtype || "input";
    self.objectName    = self.element.attr("data-object")        || self.objectName;
    self.attributeName = self.element.attr("data-attribute")     || self.attributeName;
    self.activator     = self.element.attr("data-activator")     || self.element;
    self.okButton      = self.element.attr("data-ok-button")     || self.okButton;
    self.cancelButton  = self.element.attr("data-cancel-button") || self.cancelButton;
    self.nil           = self.element.attr("data-nil")           || self.nil      || "-";
    self.inner_class   = self.element.attr("data-inner-class")   || self.inner_class   || null;
    self.html_attrs    = self.element.attr("data-html-attrs")    || self.html_attrs;
    self.original_content    = self.element.attr("data-original-content") || self.original_content;

    if (!self.element.attr("data-sanitize")) {
      self.sanitize = true;
    }
    else {
      self.sanitize = (self.element.attr("data-sanitize") == "true");
    }

    if ((self.formType == "select" || self.formType == "checkbox") && self.collection !== null)
    {
      self.values = jQuery.parseJSON(self.collection);
    }
  },

  bindForm : function() {
    this.activateForm = BestInPlaceEditor.forms[this.formType].activateForm;
    this.getValue     = BestInPlaceEditor.forms[this.formType].getValue;
  },

  initNil: function() {
    if (this.element.html() == "")
    {
      this.isNil = true
      this.element.html(this.nil)
    }
  },

  getValue : function() {
    alert("The form was not properly initialized. getValue is unbound");
  },

  // Trim and Strips HTML from text
  sanitizeValue : function(s) {
    if (this.sanitize)
    {
      var tmp = document.createElement("DIV");
      tmp.innerHTML = s;
      s = tmp.textContent || tmp.innerText;
    }
   return jQuery.trim(s).replace(/"/g, '&quot;');
  },

  /* Generate the data sent in the POST request */
  requestData : function() {
    // To prevent xss attacks, a csrf token must be defined as a meta attribute
    csrf_token = $('meta[name=csrf-token]').attr('content');
    csrf_param = $('meta[name=csrf-param]').attr('content');

    var data = "_method=put";
    data += "&" + this.objectName + '[' + this.attributeName + ']=' + encodeURIComponent(this.getValue());

    if (csrf_param !== undefined && csrf_token !== undefined) {
      data += "&" + csrf_param + "=" + encodeURIComponent(csrf_token);
    }
    return data;
  },

  ajax : function(options) {
    options.url = this.url;
    options.beforeSend = function(xhr){ xhr.setRequestHeader("Accept", "application/json"); };
    return jQuery.ajax(options);
  },

  // Handlers ////////////////////////////////////////////////////////////////

  loadSuccessCallback : function(data) {
    var response = $.parseJSON($.trim(data));
    if (response != null && response.hasOwnProperty("display_as")) {
      this.element.attr("data-original-content", this.element.html());
      this.original_content = this.element.html();
      this.element.html(response["display_as"]);
    }
    this.element.trigger($.Event("ajax:success"), data);

    // Binding back after being clicked
    $(this.activator).bind('click', {editor: this}, this.clickHandler);
  },

  loadErrorCallback : function(request, error) {
    this.element.html(this.oldValue);

    // Display all error messages from server side validation
    $.each(jQuery.parseJSON(request.responseText), function(index, value) {
      if( typeof(value) == "object") {value = index + " " + value.toString(); }
      var container = $("<span class='flash-error'></span>").html(value);
      container.purr();
    });
    this.element.trigger($.Event("ajax:error"));

    // Binding back after being clicked
    $(this.activator).bind('click', {editor: this}, this.clickHandler);
  },

  clickHandler : function(event) {
    event.data.editor.activate();
  },

  setHtmlAttributes : function() {
    var formField = this.element.find(this.formType);
    var attrs = jQuery.parseJSON(this.html_attrs);
    for(var key in attrs){
      formField.attr(key, attrs[key]);
    }
  }
};


// Button cases:
// If no buttons, then blur saves, ESC cancels
// If just Cancel button, then blur saves, ESC or clicking Cancel cancels (careful of blur event!)
// If just OK button, then clicking OK saves (careful of blur event!), ESC or blur cancels
// If both buttons, then clicking OK saves, ESC or clicking Cancel or blur cancels
BestInPlaceEditor.forms = {
  "input" : {
    activateForm : function() {
      var output = '<form class="form_in_place" action="javascript:void(0)" style="display:inline;">';
      output += '<input type="text" name="'+ this.attributeName + '" value="' + this.sanitizeValue(this.display_value) + '"';
      if (this.inner_class != null) {
        output += ' class="' + this.inner_class + '"';
      }
      output += '>';
      if (this.okButton) {
        output += '<input type="submit" value="' + this.okButton + '" />'
      }
      if (this.cancelButton) {
        output += '<input type="button" value="' + this.cancelButton + '" />'
      }
      output += '</form>';
      this.element.html(output);
      this.setHtmlAttributes();
      this.element.find("input[type='text']")[0].select();
      this.element.find("form").bind('submit', {editor: this}, BestInPlaceEditor.forms.input.submitHandler);
      if (this.cancelButton) {
        this.element.find("input[type='button']").bind('click', {editor: this}, BestInPlaceEditor.forms.input.cancelButtonHandler)
      }
      this.element.find("input[type='text']").bind('blur', {editor: this}, BestInPlaceEditor.forms.input.inputBlurHandler);
      this.element.find("input[type='text']").bind('keyup', {editor: this}, BestInPlaceEditor.forms.input.keyupHandler);
      this.blurTimer = null;
      this.userClicked = false;
    },

    getValue : function() {
      return this.sanitizeValue(this.element.find("input").val());
    },

    // When buttons are present, use a timer on the blur event to give precedence to clicks
    inputBlurHandler : function(event) {
      if (event.data.editor.okButton) {
        event.data.editor.blurTimer = setTimeout(function () {
          if (!event.data.editor.userClicked) {
            event.data.editor.abort();
          }
        }, 500);
      } else {
        if (event.data.editor.cancelButton) {
          event.data.editor.blurTimer = setTimeout(function () {
            if (!event.data.editor.userClicked) {
              event.data.editor.update();
            }
          }, 500);
        } else {
          event.data.editor.update();
        }
      }
    },

    submitHandler : function(event) {
      event.data.editor.userClicked = true;
      clearTimeout(event.data.editor.blurTimer);
      event.data.editor.update();
    },

    cancelButtonHandler : function(event) {
      event.data.editor.userClicked = true;
      clearTimeout(event.data.editor.blurTimer);
      event.data.editor.abort();
      event.stopPropagation(); // Without this, click isn't handled
    },

    keyupHandler : function(event) {
      if (event.keyCode == 27) {
        event.data.editor.abort();
      }
    }
  },

  "date" : {
    activateForm : function() {
      var that = this,
        output = '<form class="form_in_place" action="javascript:void(0)" style="display:inline;">';
      output += '<input type="text" name="'+ this.attributeName + '" value="' + this.sanitizeValue(this.display_value) + '"';
      if (this.inner_class != null) {
        output += ' class="' + this.inner_class + '"';
      }
      output += '></form>'
      this.element.html(output);
      this.setHtmlAttributes();
      this.element.find('input')[0].select();
      this.element.find("form").bind('submit', {editor: this}, BestInPlaceEditor.forms.input.submitHandler);
      this.element.find("input").bind('keyup', {editor: this}, BestInPlaceEditor.forms.input.keyupHandler);

      this.element.find('input')
        .datepicker({
            onClose: function() {
              that.update();
            }
          })
        .datepicker('show');
    },

    getValue :  function() {
      return this.sanitizeValue(this.element.find("input").val());
    },

    submitHandler : function(event) {
      event.data.editor.update();
    },

    keyupHandler : function(event) {
      if (event.keyCode == 27) {
        event.data.editor.abort();
      }
    }
  },

  "select" : {
    activateForm : function() {
      var output = "<form action='javascript:void(0)' style='display:inline;'><select>";
      var selected = "";
      var oldValue = this.oldValue;
      $.each(this.values, function(index, value) {
        selected = (value[1] == oldValue ? "selected='selected'" : "");
        output += "<option value='" + value[0] + "' " + selected + ">" + value[1] + "</option>";
       });
      output += "</select></form>";
      this.element.html(output);
      this.setHtmlAttributes();
      this.element.find("select").bind('change', {editor: this}, BestInPlaceEditor.forms.select.blurHandler);
      this.element.find("select").bind('blur', {editor: this}, BestInPlaceEditor.forms.select.blurHandler);
      this.element.find("select").bind('keyup', {editor: this}, BestInPlaceEditor.forms.select.keyupHandler);
      this.element.find("select")[0].focus();
    },

    getValue : function() {
      return this.sanitizeValue(this.element.find("select").val());
    },

    blurHandler : function(event) {
      event.data.editor.update();
    },

    keyupHandler : function(event) {
      if (event.keyCode == 27) event.data.editor.abort();
    }
  },

  "checkbox" : {
    activateForm : function() {
      var newValue = Boolean(this.oldValue != this.values[1]);
      var output = newValue ? this.values[1] : this.values[0];
      this.element.html(output);
      this.setHtmlAttributes();
      this.update();
    },

    getValue : function() {
      return Boolean(this.element.html() == this.values[1]);
    }
  },

  "textarea" : {
    activateForm : function() {
      // grab width and height of text
      width = this.element.css('width');
      height = this.element.css('height');

      // construct the form
      var output = '<form action="javascript:void(0)" style="display:inline;"><textarea>';
      output += this.sanitizeValue(this.display_value);
      output += '</textarea>';
      if (this.okButton) {
        output += '<input type="submit" value="' + this.okButton + '" />'
      }
      if (this.cancelButton) {
        output += '<input type="button" value="' + this.cancelButton + '" />'
      }
      output += '</form>';
      this.element.html(output);
      this.setHtmlAttributes();

      // set width and height of textarea
      jQuery(this.element.find("textarea")[0]).css({ 'min-width': width, 'min-height': height });
      jQuery(this.element.find("textarea")[0]).elastic();

      this.element.find("textarea")[0].focus();
      this.element.find("form").bind('submit', {editor: this}, BestInPlaceEditor.forms.textarea.submitHandler);
      if (this.cancelButton) {
        this.element.find("input[type='button']").bind('click', {editor: this}, BestInPlaceEditor.forms.textarea.cancelButtonHandler)
      }
      this.element.find("textarea").bind('blur', {editor: this}, BestInPlaceEditor.forms.textarea.blurHandler);
      this.element.find("textarea").bind('keyup', {editor: this}, BestInPlaceEditor.forms.textarea.keyupHandler);
      this.blurTimer = null;
      this.userClicked = false;
    },

    getValue :  function() {
      return this.sanitizeValue(this.element.find("textarea").val());
    },

    // When buttons are present, use a timer on the blur event to give precedence to clicks
    blurHandler : function(event) {
      if (event.data.editor.okButton) {
        event.data.editor.blurTimer = setTimeout(function () {
          if (!event.data.editor.userClicked) {
            event.data.editor.abortIfConfirm();
          }
        }, 500);
      } else {
        if (event.data.editor.cancelButton) {
          event.data.editor.blurTimer = setTimeout(function () {
            if (!event.data.editor.userClicked) {
              event.data.editor.update();
            }
          }, 500);
        } else {
          event.data.editor.update();
        }
      }
    },

    submitHandler : function(event) {
      event.data.editor.userClicked = true;
      clearTimeout(event.data.editor.blurTimer);
      event.data.editor.update();
    },

    cancelButtonHandler : function(event) {
      event.data.editor.userClicked = true;
      clearTimeout(event.data.editor.blurTimer);
      event.data.editor.abortIfConfirm();
      event.stopPropagation(); // Without this, click isn't handled
    },

    keyupHandler : function(event) {
      if (event.keyCode == 27) {
        event.data.editor.abortIfConfirm();
      }
    }
  }
};

jQuery.fn.best_in_place = function() {
  this.each(function(){
    if (!jQuery(this).data('bestInPlaceEditor')) {
      jQuery(this).data('bestInPlaceEditor', new BestInPlaceEditor(this));
    }
  });
  return this;
};



/**
* @name             Elastic
* @descripton           Elastic is Jquery plugin that grow and shrink your textareas automaticliy
* @version            1.6.5
* @requires           Jquery 1.2.6+
*
* @author             Jan Jarfalk
* @author-email         jan.jarfalk@unwrongest.com
* @author-website         http://www.unwrongest.com
*
* @licens             MIT License - http://www.opensource.org/licenses/mit-license.php
*/

(function(jQuery){
  jQuery.fn.extend({
    elastic: function() {
      //  We will create a div clone of the textarea
      //  by copying these attributes from the textarea to the div.
      var mimics = [
        'paddingTop',
        'paddingRight',
        'paddingBottom',
        'paddingLeft',
        'fontSize',
        'lineHeight',
        'fontFamily',
        'width',
        'fontWeight'];

      return this.each( function() {

        // Elastic only works on textareas
        if ( this.type != 'textarea' ) {
          return false;
        }

        var $textarea = jQuery(this),
          $twin   = jQuery('<div />').css({'position': 'absolute','display':'none','word-wrap':'break-word'}),
          lineHeight  = parseInt($textarea.css('line-height'),10) || parseInt($textarea.css('font-size'),'10'),
          minheight = parseInt($textarea.css('height'),10) || lineHeight*3,
          maxheight = parseInt($textarea.css('max-height'),10) || Number.MAX_VALUE,
          goalheight  = 0,
          i       = 0;

        // Opera returns max-height of -1 if not set
        if (maxheight < 0) { maxheight = Number.MAX_VALUE; }

        // Append the twin to the DOM
        // We are going to meassure the height of this, not the textarea.
        $twin.appendTo($textarea.parent());

        // Copy the essential styles (mimics) from the textarea to the twin
        var i = mimics.length;
        while(i--){
          $twin.css(mimics[i].toString(),$textarea.css(mimics[i].toString()));
        }


        // Sets a given height and overflow state on the textarea
        function setHeightAndOverflow(height, overflow){
          curratedHeight = Math.floor(parseInt(height,10));
          if($textarea.height() != curratedHeight){
            $textarea.css({'height': curratedHeight + 'px','overflow':overflow});

          }
        }


        // This function will update the height of the textarea if necessary
        function update() {

          // Get curated content from the textarea.
          var textareaContent = $textarea.val().replace(/&/g,'&amp;').replace(/  /g, '&nbsp;').replace(/<|>/g, '&gt;').replace(/\n/g, '<br />');

          // Compare curated content with curated twin.
          var twinContent = $twin.html().replace(/<br>/ig,'<br />');

          if(textareaContent+'&nbsp;' != twinContent){

            // Add an extra white space so new rows are added when you are at the end of a row.
            $twin.html(textareaContent+'&nbsp;');

            // Change textarea height if twin plus the height of one line differs more than 3 pixel from textarea height
            if(Math.abs($twin.height() + lineHeight - $textarea.height()) > 3){

              var goalheight = $twin.height()+lineHeight;
              if(goalheight >= maxheight) {
                setHeightAndOverflow(maxheight,'auto');
              } else if(goalheight <= minheight) {
                setHeightAndOverflow(minheight,'hidden');
              } else {
                setHeightAndOverflow(goalheight,'hidden');
              }

            }

          }

        }

        // Hide scrollbars
        $textarea.css({'overflow':'hidden'});

        // Update textarea size on keyup, change, cut and paste
        $textarea.bind('keyup change cut paste', function(){
          update();
        });

        // Compact textarea on blur
        // Lets animate this....
        $textarea.bind('blur',function(){
          if($twin.height() < maxheight){
            if($twin.height() > minheight) {
              $textarea.height($twin.height());
            } else {
              $textarea.height(minheight);
            }
          }
        });

        // And this line is to catch the browser paste event
        $textarea.live('input paste',function(e){ setTimeout( update, 250); });

        // Run update once when elastic is initialized
        update();

      });

        }
    });
})(jQuery);

/**
 * jquery.purr.js
 * Copyright (c) 2008 Net Perspective (net-perspective.com)
 * Licensed under the MIT License (http://www.opensource.org/licenses/mit-license.php)
 *
 * @author R.A. Ray
 * @projectDescription  jQuery plugin for dynamically displaying unobtrusive messages in the browser. Mimics the behavior of the MacOS program "Growl."
 * @version 0.1.0
 *
 * @requires jquery.js (tested with 1.2.6)
 *
 * @param fadeInSpeed           int - Duration of fade in animation in miliseconds
 *                          default: 500
 *  @param fadeOutSpeed         int - Duration of fade out animationin miliseconds
                            default: 500
 *  @param removeTimer          int - Timeout, in miliseconds, before notice is removed once it is the top non-sticky notice in the list
                            default: 4000
 *  @param isSticky             bool - Whether the notice should fade out on its own or wait to be manually closed
                            default: false
 *  @param usingTransparentPNG  bool - Whether or not the notice is using transparent .png images in its styling
                            default: false
 */

(function($) {

  $.purr = function(notice, options)
  {
    // Convert notice to a jQuery object
    notice = $(notice);

    // Add a class to denote the notice as not sticky
    notice.addClass('purr');

    // Get the container element from the page
    var cont = document.getElementById('purr-container');

    // If the container doesn't yet exist, we need to create it
    if (!cont)
    {
      cont = '<div id="purr-container"></div>';
    }

    // Convert cont to a jQuery object
    cont = $(cont);

    // Add the container to the page
    $('body').append(cont);

    notify();

    function notify ()
    {
      // Set up the close button
      var close = document.createElement('a');
      $(close).attr({
          className: 'close',
          href: '#close'
          }).appendTo(notice).click(function() {
              removeNotice();
              return false;
          });

      // If ESC is pressed remove notice
      $(document).keyup(function(e) {
        if (e.keyCode == 27) {
          removeNotice();
        }
      });

      // Add the notice to the page and keep it hidden initially
      notice.appendTo(cont).hide();

      if (jQuery.browser.msie && options.usingTransparentPNG)
      {
        // IE7 and earlier can't handle the combination of opacity and transparent pngs, so if we're using transparent pngs in our
        // notice style, we'll just skip the fading in.
        notice.show();
      }
      else
      {
        //Fade in the notice we just added
        notice.fadeIn(options.fadeInSpeed);
      }

      // Set up the removal interval for the added notice if that notice is not a sticky
      if (!options.isSticky)
      {
        var topSpotInt = setInterval(function() {
          // Check to see if our notice is the first non-sticky notice in the list
          if (notice.prevAll('.purr').length == 0)
          {
            // Stop checking once the condition is met
            clearInterval(topSpotInt);

            // Call the close action after the timeout set in options
            setTimeout(function() {
                removeNotice();
              }, options.removeTimer);
          }
        }, 200);
      }
    }

    function removeNotice()
    {
      // IE7 and earlier can't handle the combination of opacity and transparent pngs, so if we're using transparent pngs in our
      // notice style, we'll just skip the fading out.
      if (jQuery.browser.msie && options.usingTransparentPNG)
      {
        notice.css({ opacity: 0 }).animate({ height: '0px'},
            {
              duration: options.fadeOutSpeed,
              complete: function ()
              {
                notice.remove();
              }
            }
          );
      }
      else
      {
        // Fade the object out before reducing its height to produce the sliding effect
        notice.animate({ opacity: '0' },
          {
            duration: options.fadeOutSpeed,
            complete: function ()
              {
                notice.animate({ height: '0px' },
                  {
                    duration: options.fadeOutSpeed,
                    complete: function()
                      {
                        notice.remove();
                      }
                  }
                );
              }
          }
        );
      }
    };
  };

  $.fn.purr = function(options)
  {
    options = options || {};
    options.fadeInSpeed = options.fadeInSpeed || 500;
    options.fadeOutSpeed = options.fadeOutSpeed || 500;
    options.removeTimer = options.removeTimer || 4000;
    options.isSticky = options.isSticky || false;
    options.usingTransparentPNG = options.usingTransparentPNG || false;

    this.each(function()
      {
        new $.purr( this, options );
      }
    );

    return this;
  };
})( jQuery );
$('#myModal')
!function( $ ){

    "use strict"

    /* TAB CLASS DEFINITION
     * ==================== */

    var Tab = function ( element ) {
        this.element = $(element)
    }

    Tab.prototype = {

        constructor: Tab

        , show: function () {
            var $this = this.element
                , $ul = $this.closest('ul:not(.dropdown-menu)')
                , selector = $this.attr('data-target')
                , previous
                , $target

            if (!selector) {
                selector = $this.attr('href')
                selector = selector && selector.replace(/.*(?=#[^\s]*$)/, '') //strip for ie7
            }

            if ( $this.parent('li').hasClass('active') ) return

            previous = $ul.find('.active a').last()[0]

            $this.trigger({
                type: 'show'
                , relatedTarget: previous
            })

            $target = $(selector)

            this.activate($this.parent('li'), $ul)
            this.activate($target, $target.parent(), function () {
                $this.trigger({
                    type: 'shown'
                    , relatedTarget: previous
                })
            })
        }

        , activate: function ( element, container, callback) {
            var $active = container.find('> .active')
                , transition = callback
                    && $.support.transition
                    && $active.hasClass('fade')

            function next() {
                $active
                    .removeClass('active')
                    .find('> .dropdown-menu > .active')
                    .removeClass('active')

                element.addClass('active')

                if (transition) {
                    element[0].offsetWidth // reflow for transition
                    element.addClass('in')
                } else {
                    element.removeClass('fade')
                }

                if ( element.parent('.dropdown-menu') ) {
                    element.closest('li.dropdown').addClass('active')
                }

                callback && callback()
            }

            transition ?
                $active.one($.support.transition.end, next) :
                next()

            $active.removeClass('in')
        }
    }


    /* TAB PLUGIN DEFINITION
     * ===================== */

    $.fn.tab = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('tab')
            if (!data) $this.data('tab', (data = new Tab(this)))
            if (typeof option == 'string') data[option]()
        })
    }

    $.fn.tab.Constructor = Tab


    /* TAB DATA-API
     * ============ */

    $(function () {
        $('body').on('click.tab.data-api', '[data-toggle="tab"], [data-toggle="pill"]', function (e) {
            e.preventDefault()
            $(this).tab('show')
        })
    })

}( window.jQuery );

/* ============================================================
 * bootstrap-dropdown.js v2.0.2
 * http://twitter.github.com/bootstrap/javascript.html#dropdowns
 * ============================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============================================================ */


!function( $ ){

    "use strict"

    /* DROPDOWN CLASS DEFINITION
     * ========================= */

    var toggle = '[data-toggle="dropdown"]'
        , Dropdown = function ( element ) {
            var $el = $(element).on('click.dropdown.data-api', this.toggle)
            $('html').on('click.dropdown.data-api', function () {
                $el.parent().removeClass('open')
            })
        }

    Dropdown.prototype = {

        constructor: Dropdown

        , toggle: function ( e ) {
            var $this = $(this)
                , selector = $this.attr('data-target')
                , $parent
                , isActive

            if (!selector) {
                selector = $this.attr('href')
                selector = selector && selector.replace(/.*(?=#[^\s]*$)/, '') //strip for ie7
            }

            $parent = $(selector)
            $parent.length || ($parent = $this.parent())

            isActive = $parent.hasClass('open')

            clearMenus()
            !isActive && $parent.toggleClass('open')

            return false
        }

    }

    function clearMenus() {
        $(toggle).parent().removeClass('open')
    }


    /* DROPDOWN PLUGIN DEFINITION
     * ========================== */

    $.fn.dropdown = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('dropdown')
            if (!data) $this.data('dropdown', (data = new Dropdown(this)))
            if (typeof option == 'string') data[option].call($this)
        })
    }

    $.fn.dropdown.Constructor = Dropdown


    /* APPLY TO STANDARD DROPDOWN ELEMENTS
     * =================================== */

    $(function () {
        $('html').on('click.dropdown.data-api', clearMenus)
        $('body').on('click.dropdown.data-api', toggle, Dropdown.prototype.toggle)
    })

}( window.jQuery );
/* =========================================================
 * bootstrap-modal.js v2.0.1
 * http://twitter.github.com/bootstrap/javascript.html#modals
 * =========================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================= */


!function( $ ){

    "use strict"

    /* MODAL CLASS DEFINITION
     * ====================== */

    var Modal = function ( content, options ) {
        this.options = options
        this.$element = $(content)
            .delegate('[data-dismiss="modal"]', 'click.dismiss.modal', $.proxy(this.hide, this))
    }

    Modal.prototype = {

        constructor: Modal

        , toggle: function () {
            return this[!this.isShown ? 'show' : 'hide']()
        }

        , show: function () {
            var that = this

            if (this.isShown) return

            $('body').addClass('modal-open')

            this.isShown = true
            this.$element.trigger('show')

            escape.call(this)
            backdrop.call(this, function () {
                var transition = $.support.transition && that.$element.hasClass('fade')

                !that.$element.parent().length && that.$element.appendTo(document.body) //don't move modals dom position

                that.$element
                    .show()

                if (transition) {
                    that.$element[0].offsetWidth // force reflow
                }

                that.$element.addClass('in')

                transition ?
                    that.$element.one($.support.transition.end, function () { that.$element.trigger('shown') }) :
                    that.$element.trigger('shown')

            })
        }

        , hide: function ( e ) {
            e && e.preventDefault()

            if (!this.isShown) return

            var that = this
            this.isShown = false

            $('body').removeClass('modal-open')

            escape.call(this)

            this.$element
                .trigger('hide')
                .removeClass('in')

            $.support.transition && this.$element.hasClass('fade') ?
                hideWithTransition.call(this) :
                hideModal.call(this)
        }

    }


    /* MODAL PRIVATE METHODS
     * ===================== */

    function hideWithTransition() {
        var that = this
            , timeout = setTimeout(function () {
                that.$element.off($.support.transition.end)
                hideModal.call(that)
            }, 500)

        this.$element.one($.support.transition.end, function () {
            clearTimeout(timeout)
            hideModal.call(that)
        })
    }

    function hideModal( that ) {
        this.$element
            .hide()
            .trigger('hidden')

        backdrop.call(this)
    }

    function backdrop( callback ) {
        var that = this
            , animate = this.$element.hasClass('fade') ? 'fade' : ''

        if (this.isShown && this.options.backdrop) {
            var doAnimate = $.support.transition && animate

            this.$backdrop = $('<div class="modal-backdrop ' + animate + '" />')
                .appendTo(document.body)

            if (this.options.backdrop != 'static') {
                this.$backdrop.click($.proxy(this.hide, this))
            }

            if (doAnimate) this.$backdrop[0].offsetWidth // force reflow

            this.$backdrop.addClass('in')

            doAnimate ?
                this.$backdrop.one($.support.transition.end, callback) :
                callback()

        } else if (!this.isShown && this.$backdrop) {
            this.$backdrop.removeClass('in')

            $.support.transition && this.$element.hasClass('fade')?
                this.$backdrop.one($.support.transition.end, $.proxy(removeBackdrop, this)) :
                removeBackdrop.call(this)

        } else if (callback) {
            callback()
        }
    }

    function removeBackdrop() {
        this.$backdrop.remove()
        this.$backdrop = null
    }

    function escape() {
        var that = this
        if (this.isShown && this.options.keyboard) {
            $(document).on('keyup.dismiss.modal', function ( e ) {
                e.which == 27 && that.hide()
            })
        } else if (!this.isShown) {
            $(document).off('keyup.dismiss.modal')
        }
    }


    /* MODAL PLUGIN DEFINITION
     * ======================= */

    $.fn.modal = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('modal')
                , options = $.extend({}, $.fn.modal.defaults, $this.data(), typeof option == 'object' && option)
            if (!data) $this.data('modal', (data = new Modal(this, options)))
            if (typeof option == 'string') data[option]()
            else if (options.show) data.show()
        })
    }

    $.fn.modal.defaults = {
        backdrop: true
        , keyboard: true
        , show: true
    }

    $.fn.modal.Constructor = Modal


    /* MODAL DATA-API
     * ============== */

    $(function () {
        $('body').on('click.modal.data-api', '[data-toggle="modal"]', function ( e ) {
            var $this = $(this), href
                , $target = $($this.attr('data-target') || (href = $this.attr('href')) && href.replace(/.*(?=#[^\s]+$)/, '')) //strip for ie7
                , option = $target.data('modal') ? 'toggle' : $.extend({}, $target.data(), $this.data())

            e.preventDefault()
            $target.modal(option)
        })
    })

}( window.jQuery );


/* ===========================================================
 * bootstrap-tooltip.js v2.0.1
 * http://twitter.github.com/bootstrap/javascript.html#tooltips
 * Inspired by the original jQuery.tipsy by Jason Frame
 * ===========================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================== */

!function( $ ) {

    "use strict"

    /* TOOLTIP PUBLIC CLASS DEFINITION
     * =============================== */

    var Tooltip = function ( element, options ) {
        this.init('tooltip', element, options)
    }

    Tooltip.prototype = {

        constructor: Tooltip

        , init: function ( type, element, options ) {
            var eventIn
                , eventOut

            this.type = type
            this.$element = $(element)
            this.options = this.getOptions(options)
            this.enabled = true

            if (this.options.trigger != 'manual') {
                eventIn  = this.options.trigger == 'hover' ? 'mouseenter' : 'focus'
                eventOut = this.options.trigger == 'hover' ? 'mouseleave' : 'blur'
                this.$element.on(eventIn, this.options.selector, $.proxy(this.enter, this))
                this.$element.on(eventOut, this.options.selector, $.proxy(this.leave, this))
            }

            this.options.selector ?
                (this._options = $.extend({}, this.options, { trigger: 'manual', selector: '' })) :
                this.fixTitle()
        }

        , getOptions: function ( options ) {
            options = $.extend({}, $.fn[this.type].defaults, options, this.$element.data())

            if (options.delay && typeof options.delay == 'number') {
                options.delay = {
                    show: options.delay
                    , hide: options.delay
                }
            }

            return options
        }

        , enter: function ( e ) {
            var self = $(e.currentTarget)[this.type](this._options).data(this.type)

            if (!self.options.delay || !self.options.delay.show) {
                self.show()
            } else {
                self.hoverState = 'in'
                setTimeout(function() {
                    if (self.hoverState == 'in') {
                        self.show()
                    }
                }, self.options.delay.show)
            }
        }

        , leave: function ( e ) {
            var self = $(e.currentTarget)[this.type](this._options).data(this.type)

            if (!self.options.delay || !self.options.delay.hide) {
                self.hide()
            } else {
                self.hoverState = 'out'
                setTimeout(function() {
                    if (self.hoverState == 'out') {
                        self.hide()
                    }
                }, self.options.delay.hide)
            }
        }

        , show: function () {
            var $tip
                , inside
                , pos
                , actualWidth
                , actualHeight
                , placement
                , tp

            if (this.hasContent() && this.enabled) {
                $tip = this.tip()
                this.setContent()

                if (this.options.animation) {
                    $tip.addClass('fade')
                }

                placement = typeof this.options.placement == 'function' ?
                    this.options.placement.call(this, $tip[0], this.$element[0]) :
                    this.options.placement

                inside = /in/.test(placement)

                $tip
                    .remove()
                    .css({ top: 0, left: 0, display: 'block' })
                    .appendTo(inside ? this.$element : document.body)

                pos = this.getPosition(inside)

                actualWidth = $tip[0].offsetWidth
                actualHeight = $tip[0].offsetHeight

                switch (inside ? placement.split(' ')[1] : placement) {
                    case 'bottom':
                        tp = {top: pos.top + pos.height, left: pos.left + pos.width / 2 - actualWidth / 2}
                        break
                    case 'top':
                        tp = {top: pos.top - actualHeight, left: pos.left + pos.width / 2 - actualWidth / 2}
                        break
                    case 'left':
                        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left - actualWidth}
                        break
                    case 'right':
                        tp = {top: pos.top + pos.height / 2 - actualHeight / 2, left: pos.left + pos.width}
                        break
                }

                $tip
                    .css(tp)
                    .addClass(placement)
                    .addClass('in')
            }
        }

        , setContent: function () {
            var $tip = this.tip()
            $tip.find('.tooltip-inner').html(this.getTitle())
            $tip.removeClass('fade in top bottom left right')
        }

        , hide: function () {
            var that = this
                , $tip = this.tip()

            $tip.removeClass('in')

            function removeWithAnimation() {
                var timeout = setTimeout(function () {
                    $tip.off($.support.transition.end).remove()
                }, 500)

                $tip.one($.support.transition.end, function () {
                    clearTimeout(timeout)
                    $tip.remove()
                })
            }

            $.support.transition && this.$tip.hasClass('fade') ?
                removeWithAnimation() :
                $tip.remove()
        }

        , fixTitle: function () {
            var $e = this.$element
            if ($e.attr('title') || typeof($e.attr('data-original-title')) != 'string') {
                $e.attr('data-original-title', $e.attr('title') || '').removeAttr('title')
            }
        }

        , hasContent: function () {
            return this.getTitle()
        }

        , getPosition: function (inside) {
            return $.extend({}, (inside ? {top: 0, left: 0} : this.$element.offset()), {
                width: this.$element[0].offsetWidth
                , height: this.$element[0].offsetHeight
            })
        }

        , getTitle: function () {
            var title
                , $e = this.$element
                , o = this.options

            title = $e.attr('data-original-title')
                || (typeof o.title == 'function' ? o.title.call($e[0]) :  o.title)

            title = (title || '').toString().replace(/(^\s*|\s*$)/, "")

            return title
        }

        , tip: function () {
            return this.$tip = this.$tip || $(this.options.template)
        }

        , validate: function () {
            if (!this.$element[0].parentNode) {
                this.hide()
                this.$element = null
                this.options = null
            }
        }

        , enable: function () {
            this.enabled = true
        }

        , disable: function () {
            this.enabled = false
        }

        , toggleEnabled: function () {
            this.enabled = !this.enabled
        }

        , toggle: function () {
            this[this.tip().hasClass('in') ? 'hide' : 'show']()
        }

    }


    /* TOOLTIP PLUGIN DEFINITION
     * ========================= */

    $.fn.tooltip = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('tooltip')
                , options = typeof option == 'object' && option
            if (!data) $this.data('tooltip', (data = new Tooltip(this, options)))
            if (typeof option == 'string') data[option]()
        })
    }

    $.fn.tooltip.Constructor = Tooltip

    $.fn.tooltip.defaults = {
        animation: true
        , delay: 0
        , selector: false
        , placement: 'top'
        , trigger: 'hover'
        , title: ''
        , template: '<div class="tooltip"><div class="tooltip-arrow"></div><div class="tooltip-inner"></div></div>'
    }

}( window.jQuery );

/* ===========================================================
 * bootstrap-popover.js v2.0.1
 * http://twitter.github.com/bootstrap/javascript.html#popovers
 * ===========================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * =========================================================== */


!function( $ ) {

    "use strict"

    var Popover = function ( element, options ) {
        this.init('popover', element, options)
    }

    /* NOTE: POPOVER EXTENDS BOOTSTRAP-TOOLTIP.js
     ========================================== */

    Popover.prototype = $.extend({}, $.fn.tooltip.Constructor.prototype, {

        constructor: Popover

        , setContent: function () {
            var $tip = this.tip()
                , title = this.getTitle()
                , content = this.getContent()

            $tip.find('.popover-title')[ $.type(title) == 'object' ? 'append' : 'html' ](title)
            $tip.find('.popover-content > *')[ $.type(content) == 'object' ? 'append' : 'html' ](content)

            $tip.removeClass('fade top bottom left right in')
        }

        , hasContent: function () {
            return this.getTitle() || this.getContent()
        }

        , getContent: function () {
            var content
                , $e = this.$element
                , o = this.options

            content = $e.attr('data-content')
                || (typeof o.content == 'function' ? o.content.call($e[0]) :  o.content)

            content = content.toString().replace(/(^\s*|\s*$)/, "")

            return content
        }

        , tip: function() {
            if (!this.$tip) {
                this.$tip = $(this.options.template)
            }
            return this.$tip
        }

    })


    /* POPOVER PLUGIN DEFINITION
     * ======================= */

    $.fn.popover = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('popover')
                , options = typeof option == 'object' && option
            if (!data) $this.data('popover', (data = new Popover(this, options)))
            if (typeof option == 'string') data[option]()
        })
    }

    $.fn.popover.Constructor = Popover

    $.fn.popover.defaults = $.extend({} , $.fn.tooltip.defaults, {
        placement: 'right'
        , content: ''
        , template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>'
    })

}( window.jQuery );

/* ==========================================================
 * bootstrap-alert.js v2.0.1
 * http://twitter.github.com/bootstrap/javascript.html#alerts
 * ==========================================================
 * Copyright 2012 Twitter, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ========================================================== */


!function( $ ){

    "use strict"

    /* ALERT CLASS DEFINITION
     * ====================== */

    var dismiss = '[data-dismiss="alert"]'
        , Alert = function ( el ) {
            $(el).on('click', dismiss, this.close)
        }

    Alert.prototype = {

        constructor: Alert

        , close: function ( e ) {
            var $this = $(this)
                , selector = $this.attr('data-target')
                , $parent

            if (!selector) {
                selector = $this.attr('href')
                selector = selector && selector.replace(/.*(?=#[^\s]*$)/, '') //strip for ie7
            }

            $parent = $(selector)
            $parent.trigger('close')

            e && e.preventDefault()

            $parent.length || ($parent = $this.hasClass('alert') ? $this : $this.parent())

            $parent
                .trigger('close')
                .removeClass('in')

            function removeElement() {
                $parent
                    .trigger('closed')
                    .remove()
            }

            $.support.transition && $parent.hasClass('fade') ?
                $parent.on($.support.transition.end, removeElement) :
                removeElement()
        }

    }


    /* ALERT PLUGIN DEFINITION
     * ======================= */

    $.fn.alert = function ( option ) {
        return this.each(function () {
            var $this = $(this)
                , data = $this.data('alert')
            if (!data) $this.data('alert', (data = new Alert(this)))
            if (typeof option == 'string') data[option].call($this)
        })
    }

    $.fn.alert.Constructor = Alert


    /* ALERT DATA-API
     * ============== */

    $(function () {
        $('body').on('click.alert.data-api', dismiss, Alert.prototype.close)
    })

}( window.jQuery );
