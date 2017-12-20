function submitForm(formclass) {
       var fields = Array('input','textarea', 'select');
       var urldata = {};
       $.each(fields, function(i, o) {
           $("form." + formclass + " " + o).each(function(i, o) {
               $o = $(o);
               if($o.is("select") && typeof $o.attr("id") != "undefined" && $o.attr("id") == "") {
                   return;
	           } else if ($o.is("input") && $o.attr("type") == "checkbox") {
	               urldata[encodeURIComponent($o.attr("name"))] = $o.attr("checked") ? 'on' : "";
	           } else if ($o.is("input") && $o.attr("type") == "radio") {
                    if ( $o.attr("checked") ) {
                        urldata[encodeURIComponent($o.attr("name"))] = $o.attr("value");
                    }
               } else {
	               urldata[encodeURIComponent($o.attr("name"))] = $o.attr("value");
	           }
           });
       });
       
       urldata['perform_switch'] = '1';
       return urldata;
}

function sToD(string) {
    var arr = string.split('&');
    var d = {};
    for(var i = 0; i < arr.length; i++) {
        var arr2 = arr[i].split('=');
        d[arr2[0]] = arr2[1];
    }
    return d;
}

function sget(dict, key, alternative) {
    if(typeof dict[key] == "undefined") return alternative;
    return dict[key];
}

var REQUEST_RUNNING = false;

var ServiceSwitch = function(url, status_description, ajaxian_save, partial_reload, validate_enable) {
    var klass = {
        url: url,
        statusDescriptions: status_description,
        statusBeforeSwitch: "", 
        ajaxianSave: typeof(ajaxian_save) != "undefined" ? ajaxian_save : true,
        partialReload: typeof(partial_reload) != "undefined" ? partial_reload : false,
        validateEnable: typeof(validate_enable) != "undefined" ? validate_enable : null,
        action: "",
        switchForm: $('.service-switch-form'),
        control: $('.service-switch .image img'),
        /* installs the onclick functions in for the
         * switch image 
         */
        init: function() {
            var x = this;
            /* Beware current status */
            this.control.click(function() {
                /* Disable notification listeners */
                $('#notification').end_notifications();
                var run = true;
                if(x.validateEnable != null && !x.validateEnable(x.status())) run = false;
                if(run)
                    x.run();
            });
            
            if(this.ajaxianSave) {
                this.switchForm.submit(function() {
                    x.action = "restart";
                    x.run(x.action);
                    x.action = "";
                    return false;
                });
            }
        },
        /* Is triggered when the control is clicked */
        run: function(restart) {
            var restart = typeof(restart) == "undefined" ? false : true;
            this.save(restart);
        },
        status: function(status) {
            if(typeof(status) == "undefined") {
                if(this.action != "") return this.action;
                return this.control.hasClass("on") ? "on" : "off";
            }
            if(status == "on") {
                if(this.control.hasClass("off")) 
                    this.control.removeClass("off");
                this.control.addClass("on");
            }
            else {
                this.control.removeClass("on");
                this.control.addClass("off");
            }
        },
        installerSaver: function(save) {
            this.save = save;
        },
        spinner: function(spinner) {
            this.spinner = spinner;
        },
        save: function(no_state_change) {
            if(REQUEST_RUNNING) return false;
            /* Change the status of the service accordingly */
            /* Perform state change, only if no restart is supposed to be triggered */
            if(!no_state_change) {
                this.switchStatus();
                $('.service-status').val(this.status());
            }
            else {
                this.action = "restart";
            }
            $('.service-switch .options-container').hide();
            $('.service-switch .description').hide();
            
            /* Display working spinner */
            this.displaySpinner(this.status());
            var x = this;
            REQUEST_RUNNING = true;
            
            $('.notification-fancy').hide();
            $('.error-fancy').hide();
            $.post(this.url, submitForm('service-switch-form'), function(content) {
                REQUEST_RUNNING = false;
                $('.service-switch .working').hide();
                x.changeSwitch();
                if(x.status() == "on")
                    $('.service-switch .options-container').show();
                else
                    $('.service-switch .description').show();
            });
        },
        changeSwitch: function() {
            $('.service-switch .image img').attr('src', '/images/switch-' + this.status() + '.png');
        },
        switchStatus: function(status) {
            if(typeof(status) == "undefined")
                this.status(this.status() == "on" ? "off" : "on");
            this.status(status);
        },
        displaySpinner: function(status) {
            $('.service-switch .working').html(this.statusDescription());
            $('.service-switch .working').show();
        },
        statusDescription: function() {
            var status = this.action != "" ? this.action : this.status()
            return sget(this.statusDescriptions, status, "Status info N/A. Please hold...");
        },
        restoreStatus: function() {
            this.status(this.statusBeforeSwitch);
        }
    };
    klass.init();
    return klass;
}

function cleanHTML(content) {
    var lines = content.split('\n')
    var new_content = []
    var track = false
    for(var i = 0; i < lines.length; i++) {
        var line = lines[i]
        if(line.search(/<html/) > -1) track = true;
        if(track) new_content.push(line)
        
    }
    return new_content.join('\n')
}
