/**
 * Subscriber part for the Service Notification API.
 *
 * This class implements the client for the service notifications.
 * Using the ServiceNotification class (defined in python), services can post
 * updates of there status, which are displayed to the user on the web 
 * interface.
 *
 * An instance of this class subscribes to one or more services, and is
 * then informed about each update of the status the service pushes.
 *
 * The status updates are contained within a JSON file, hence can be directly
 * used in JavaScript.
 *
 * Problems:
 
 * In case the service is killed the JSON file is not removed. 
 * The ServiceSubscrption would then assume, the service is posting
 * notifications, and would try to display them.
 * To solve this problem the status file is checked for it's Last-Modified
 * time. A very old file can't be a new status file, hence ServiceSubscription
 * knows, that the service is not running. 
 *
 * Example:
 * var status = new ServiceSubscription("snort");
 * status.registerCallback(function(evt, data) {
 *     enconsole.log("Status change occured");
 *     enconsole.log(data);
 * }
 * status.poll();
 *
 */

/**
 * Service notifications break in IE7, since indexOf is not supported.
 * Adding it to the Array prototype for Internet Explorer
 */
if (!Array.prototype.indexOf) {
    Array.prototype.indexOf = function(elt /*, from*/) {
        var len = this.length;
        
        var from = Number(arguments[1]) || 0;
        from = (from < 0) ? Math.ceil(from) : Math.floor(from);
        if (from < 0)
            from += len;
        for (; from < len; from++) {
            if (from in this && this[from] === elt)
                return from;
        }
        return -1;
    };
}

/* Location to the service status file */
//var SERVICE_STATUSLOCATION = "/notifications/%(service)%.status";
var SERVICE_STATUSLOCATION = "/notifications/%(service)%.status"
/* Location to the service status history file */
var SERVICE_HISTORYLOCATION = "/notifications/%(service)%.history.status";
/* Location to the service error file */
var SERVICE_ERRORLOCATION = "/notifications/%(service)%.error";
/* Display debug messages? */
var DEBUG = false;

/* Extending jQueries getJSON to support error callback, since the notification
 * queries could fail.
 */
var originalGetJSON = jQuery.getJSON;
jQuery.extend({
    getJSON: function(url, data, callback, error_cb) {
        // shift arguments if data argument was ommited
        if ( jQuery.isFunction( data ) ) {
            error_cb = callback;
            callback = data;
            data = null;
        }
        
        return jQuery.ajax({
           type: "GET",
           url: url,
           data: data,
           success: callback,
           error: typeof(error_cb) != 'undefined' ? error_cb : undefined,
           dataType: "json"
        });
    }
});

/* Log lastModified for each request */
var __lastModified = {};
/* This is NOT SAFE for concurrent requests */
var __lastXHR = null;
/* Hold all subscribers, to eventually stop them */
var __subscribers = {};

/* The constructor for the service subscriber class. Only calls the init
 * method of the classes, which performs the actual initialization
 */
var ServiceSubscriber = function(services, options) {
    this.init(services, options || {});
}

ServiceSubscriber.prototype = {
    /* Subscriptions which are polled for notications */
    subscriptions: [],
    /* Notifications received from the the polled services */
    notifications: [],
    /* Callback to notify the developer on new notifications */
    callback: null,
    /* Determine if the subscriber already received one or more 
     * notifications
     */
    receiving: false,
    /* Contains the error notification which was last posted by one of the
     * subscribed services.
     */
    error: null,
    /* The master subscription. As soon as the master subscription is no longer
     * active, the subscriber triggers the subscribe.stop event.
     *
     * The master is the first service being subscribed to.
     */
    master: null,
    /**
     * The constructor. Initializes subscriptions for the services, if passed.
     */
    init: function(services, options) {
        options = typeof options != 'undefined' ? options : {};
        options.type = typeof options.type != 'undefined' ? options.type : 
                                                            'observe'
        if(typeof(services) != 'undefined') {
            for(var i = 0; i < services.length; i++) {
                this.subscribe(services[i], isMaster=(i == 0) ? true : false,
                               options.type);
            }
        }
    },
    
    /* Subscribe to a single service */
    subscribe: function(name, isMaster, type) {
        var isMaster = typeof isMaster != 'undefined' ? isMaster : false;
        var subscription = new ServiceSubscription(name, type);
        if(isMaster)
            this.master = subscription;
        /* Each notitification arriving is added to an internal list,
         * since different services might run at the same time,
         * but notifications should still be displayed sequentially.
         *
         * After adding a new notification to the list, the callback
         * defined by the user, is executed, passing the latest notification.
         *
         * The latest notification is service independent and is determined,
         * by the timestamp of the notification.
         *
         * The callback is only executed if a new notification is detected,
         * comparing the time of the latest notification with the new one.
         */
        var __subscriber = this;
        subscription.registerCallback(lazy_apply(
            function(evt, data) {
                var subscription = data.subscription;
                var data = data.notification;
                
                var latest = this.notifications[this.notifications.length - 1];
                if(latest != null && latest.time == data.time) return;
                
                this.notifications.push(data);
                /* Sorting the notifications by time */
                this.notifications.sort(function(a, b) {
                    return a.time - b.time;
                });
                
                /* Executing the callback passing the newest status as 
                 * argument.
                 */
                var newest = this.notifications[this.notifications.length - 1];
                if($.isFunction(this.callback)) {
                    this.callback(newest, subscription);
                }
            }, __subscriber));
        /* The subscription must alert the subscriber as soon as the service
         * posts no more notifications.
         *
         * The service subscription is then removed from the list of
         * subscriptions.
         *
         * As soon as there master (first service in the list of subscriptions)
         * is no longer active, the onStop
         * callback is triggered.
         *
         * All child services must finish (by protocol) before the master,
         * hence the master stop triggers the subscriber.stop event.
         */
        $(document).bind('subscription.endReceiving', 
                         function(e, data) {
                             var service = data.subscription.service;
                             __subscriber.removeService(service);
                             
                             /* Trigger subscriber.stop if the master is 
                              * sending the endReceiving event
                              */ 
                             if(__subscriber.isMaster(data.subscription) &&
                                !__subscriber.masterRunning()) {
                                    $(document).trigger('subscriber.stop');
                                    __subscriber.stop();
                             }
                         });
        /**
         * Listen for errors on the subscription. After each subscription
         * finished posting the error message is displayed if one was posted.
         */
        trackErrors = lazy_apply(function(evt, data) {
            this.error = data.subscription.error;
            
            /* Manipulate data.subscription active flag. */
            if(!this.masterRunning()) {
                enconsole.log("Trigger subscriber.failure!");
                $(document).trigger('subscriber.failure', 
                                    [this.error, data.subscription]);
            }
            /* If the master fails, all children must be stopped */
            if(this.isMaster(data.subscription) && !this.masterRunning()) {
                this.stop();
            }
        }, this);
        $(document).unbind('subscription.failure', trackErrors)
                   .bind('subscription.failure', trackErrors);
        
        /**
         * Trigger subscriber.success if no service posted an error and the
         * master finished posting.
         */
        onSuccess = lazy_apply(function(evt, data) {
            enconsole.log("onSuccess#error");
            enconsole.log(this.master.error);
            if(!this.masterRunning() && !this.master.error) {
                enconsole.log('Trigger subscriber.success');
                $(document).trigger('subscriber.success', [data.subscription])
            }
        }, this);
        $(document).unbind('subscription.success')
                   .bind('subscription.success', onSuccess);
            
        this.subscriptions.push(subscription);
        return subscription;
    },
    
    /**
     * Return if the master is still running.
     *
     * The master service is the first one in the list of the ones 
     * to be polled.
     *
     * If the master dies, all other services must have ended as well, since
     * they are started within the master.
     */
    masterRunning: function() {
        if(this.master == null) {
            enconsole.log("no master found!");
            return false;
        }
        enconsole.log("masterRunning#master");
        enconsole.log(this.master);
        enconsole.log("Master active? " + this.master.active());
        return this.master.active();
    },
    
    /**
     * Return whether the given subscription is the master.
     *
     * The master is the first service in the subscription list.
     */
    isMaster: function(subscription) {
        return subscription == this.master ? true : false;
    },
    
    /* Poll the notification system for new notifications.
     *
     * Query the notification system helper using an AJAX-Request.
     * The response is a JSON-list containing a status entry in each
     * element.
     *
     */
    poll: function(interval) {
        /* Add a delay, so not all requests are started at once. BAD for
         * scalability.
         */
        var delay = 400;
        var i = 0;
        /* Trigger onStart event as soon as subscription is receiving 
         * notification
         */
        var __subscriber = this;
        var startReceiving = function(e, data) {
            /* Only trigger on first notification */
            if(!e.data.subscriber.receiving) {
                $(document).trigger("subscriber.start");
                e.data.subscriber.receiving = true;
            }
        }
        $(document).unbind('subscription.startReceiving', startReceiving)
                   .bind('subscription.startReceiving', 
                         {subscriber: __subscriber},
                         startReceiving);
        
        $.each(this.subscriptions, function() {
            this.poll(interval, delay * i);
            i++;
        })
    },
    
    /**
     * Stop the polling for new notifications
     */
    stop: function() {
        /* Clear event subscriptions and stop subscription polling */
        $.each(this.subscriptions, function() {
            enconsole.log('Stopping subscription: ');
            enconsole.log(this);
            this.stop();
        })
    },
    
    /**
     * Aborts the polling, not changing the state
     */
    abort: function() {
        /* Clear event subscriptions and stop subscription polling */
        $.each(this.subscriptions, function() {
            enconsole.log('Stopping subscription: ');
            enconsole.log(this);
            this.stop(true, false);
        })
    },
    
    /**
     * Register the callback which is fired as soon as new notifications
     * are detected.
     */
    registerCallback: function(cb) {
        if(!$.isFunction(cb))
            throw "Callback must be a either a function or method";
        this.callback = cb;
    },
    
    /**
     * Add a service at runtime.
     *
     * If poll is set, the subscriber immediately starts to poll the service,
     * else the user might use .poll to start the subscription.
     *
     * Returns the subscription, which can be started by invoking
     * poll on it.
     */
    addService: function(service, poll_itv) {
        var subscription = this.subscribe(service);
        if(typeof poll_itv != 'undefined')
            subscription.poll(poll_itv);
        return subscription;
    },
    
    /**
     * Remove a service from the subscriber list.
     *
     * JAVASCRIPT TIP:
     * Removing an item from a list with delete, doesn't actually remove it
     * from the list, but replaces its value with undefined.
     *
     * E.g.: >>> var a = [1,2,3]
     *       >>> delete a[0]
     *       true
     *       >>> [undefined, 2, 3]
     *
     * Correct this behavior by using splice and indexOf.
     *
     * E.g.: >>> var a = [1,2,3]
     *       >>> a.splice(a.indexOf(1),1)
     *       [1]
     *       >>> a
     *       [2,3]
     *
     */
    removeService: function(service) {
        for(var i = 0; i < this.subscriptions.length; i++) {
            var subscription = this.subscriptions[i];
            if(subscription.service == service) {
                subscription.stop(imminent = false);
                this.subscriptions.splice(
                    this.subscriptions.indexOf(subscription), 1);
            }
        }
    }
};

/* The constructor for the service subscription class. Only calls the init
 * method of the classes, which performs the actual initialization
 */
 
var ServiceSubscription = function(service, type) {
    this.init(service, type || 'observe');
}

/**
 * The Service Subscription can be in 3 different states:
 * INITIATING -- Wait for the first notification
 * RECEVEING -- Receive ongoing notifications
 * STOPPED -- No longer receiving notifications
 * ERROR -- Service stopped and error notification detected
 * SUCCESS -- Service stopped and no error notification.
 *
 * Status Diagram
 * 1.) Set Status INITIATING
 * 2.) Check if service is posting (location exists.)
 * 2.1) Location exists
 * 2.1.1) Last-Modified > 10 minutes ago -> File outdated, error in the 
 *                                          service, no status change
 * 2.1.1.1) State change => STOPPED
 * 2.1.2) Last-Modified < 10 minutes ago -> Switch to status RECEIVING
 * 2.2) Location does not exist
 * 2.2.1) Wait for service to start posting (poll continously)
 * 3.) Poll for notifications
 * 3.1) Notification received
 * 3.1.1) State set to RECEIVING -> Display the notification
 * 3.1.2) State set to INITIATING -> Do nothing
 * 3.2) Location disappeared
 * 3.2.1) If State set to RECEIVING -> State switch to STOPPED
 * 3.2.1.1) Check for ERROR_LOCATION
 * 3.2.1.1.1) Location exists -> State change => ERROR
 * 3.2.1.1.1.1) Fire error event
 * 3.2.1.1.2) Location doesn't exist -> Switch state to SUCCESS
 * 3.2.1.1.2.1) Fire success event
 *
 */

ServiceSubscription.prototype = {
    /* Name of the service this subscription is listening to. */
    service: "",
    /* Type of the subscription. observe or commit allowed. 
     * observe doesn't check for history files, to determine
     * whether a service has already ended
     */
    type: "observe",
    /* Status file for this subscription. */
    status_location: "",
    /* History file for the subscription. */
    history_location: "",
    /* Data of previous notification. */
    previousNotification: null,
    /* Callback used to inform on new notifications. */
    callback: null,
    /* Interval object to start and stop polling. */
    _interval_obj: null,
    /* Intervall to poll for updates. */
    poll_interval: 500,
    /* Flag to signal that a request is running. */
    requestInProgress: false,
    /* Parameters which can be configured from the outside, else use
     * defaults.
     */
    options: {},
    /* Determine whether or not the service is sending notifications.
     * Set to true on first notification, set to false, on missing location.
     */
    receiving: false,
    /* The status of the subscription. One of INITIATING, RECEIVING, ERROR,
     * ABORT, STOPPED.
     */
    state: 'INITIATING',
    /* The number of requests performed in one of the possible states */
    stateRequestCount: {
        'INITIATING': 0,
        'RECEIVING': 0,
        'ERROR': 0,
        'ABORT': 0,
        'STOPPED': 0
    },
    /* Max requests triggered, if the location is not found */
    maxNotFound: 100,
    /* The max age of the status location in seconds. If this value is exceeded
     * the location is treated as if it doesn't exist.
     */
    maxStatusAge: 5*60,
    /* The max age of the error location in seconds. If this value is exceeded
     * the location is treated as if it doesn't exist.
     */
    maxErrorAge: 5*60,
    /* Use to determine if an error notification was sent. */
    errorOccured: false,
    /* Last notification of type error */
    error: null,
    /* Previous state */
    previousState: null,
    
    /* The constructor. Only setting the service name */
    init: function(service, type, options) {
        if(typeof(service) == 'undefined')
            throw "Name of the service is required";
        this.service = service;
        if(typeof(callback) != 'undefined')
            this.callback = callback;
        this.type = typeof type != 'undefined' ? type : this.type;
        
        this.status_location = SERVICE_STATUSLOCATION.replace('%(service)%',
                                                              this.service);
        this.history_location = SERVICE_HISTORYLOCATION.replace('%(service)%',
                                                                this.service);
        this.error_location = SERVICE_ERRORLOCATION.replace('%(service)%',
                                                             this.service);
        /* Trigger onStop as soon as service starts posting notifications */ 
        this.options = {
            onStop: null
        }
        
        $.extend(this.options, options || {});
        
        /* The location queried for notifications doesn't exist. */
        $(document).bind('subscription.locationNotFound', 
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.locationNotFound, this)));
        /* Receive a notification and handle it */
        $(document).bind('notification.received', 
                          ServiceSubscription.prototype.routeEvent(this, 
                              lazy_apply(this.notificationReceived, this)));
        /* The first notification was received. Switch status to receiving */
        $(document).bind('subscription.startReceiving', 
                         ServiceSubscription.prototype.routeEvent(this,
                            lazy_apply(this.startReceiving, this)));
        /* The received notification has the type error */
        $(document).bind('notification.error', 
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.notificationError, this)));
        /* The service stopped posting notifications. */
        $(document).bind('subscription.endReceiving', 
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.endReceiving, this)));
        /* The service stopped but posted an error along the way */
        $(document).bind('subscription.failure', 
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.endedWithFailure, this)));
        /* The service stopped and no error was posted */
        $(document).bind('subscription.success',
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.endedWithSuccess, this)));
        /* Handle the notification. Should be overwritten */
        $(document).bind('notification.dispatch', 
                         ServiceSubscription.prototype.routeEvent(this,
                             lazy_apply(this.dispatch, this)));
        
        
        return this;
    },
    routeEvent: function(subscription, fn) {
        return lazy_apply(function(evt, data) {
            if(data.subscription != this) {
                return;
            }
            fn(evt, data);
        }, subscription);
    },
    endedWithSuccess: function(evt) {
        enconsole.info("Service succeeded! No errors reported.")
    },
    endedWithFailure: function(evt) {
        enconsole.error("Error: " + this.error.msg);
    },
    dispatch: function(evt, notification) {
    },
    /**
     * Triggers if the location to poll is no longer available.
     *
     * Depending on the actual state the following actions are taken:
     * INITIATING -> wait for maxLocationNotFound more requests, then conclude
     *               that an error occured and stop polling.
     *
     * RECEIVING -> it's assumed that the service stopped pasting (or died),
     *              hence stop polling.
     */
    locationNotFound: function(evt, data) {
        if(this.state == 'INITIATING') {
            if(this.stateRequestCount[this.state] >= this.maxNotFound) {
                this.switchState("STOPPED");
                return;
            }
            /* If the subscription should only be obversing and not committing,
             * it can be stopped, since no notifications are posted from the
             * service.
             */
            if(this.type == 'observe') {
                this.stop(imminent = true, switch_state = false);
                return;
            }
            this.stateRequestCount[this.state] += 1;
            enconsole.log("Waiting " + (this.maxNotFound - 
                                      this.stateRequestCount[this.state] || 0)
                                   + " more requests...");
        }
        if(this.state == 'RECEIVING') {
            enconsole.log("locationNotFound() -> No more notification, stop!")
            this.switchState("STOPPED");
        }
    },
    startReceiving: function() {},
    notificationError: function(evt, notification, service) {
        this.errorOccured = true;
        this.error = notification;
    },
    /**
     * Call when the service posts no more notifications.
     *
     * If an error occured, switch into the ERROR state.
     * If no notification was received simply stop polling.
     */
    endReceiving: function() {
        /* Stop polling */
        clearInterval(this._interval_obj);
        if(this.stateRequestCount['INITIATING'] >= this.maxNotFound)
            return;
        this.checkForErrors();
    },
    
    /**
     * Check if the service posted an error.
     *
     * If an error occured, the error location should exist. A single
     * notification is found at that location, explaining the error that
     * occured. 
     *
     * If for whatever reason that file doesn't exist, but error
     * is referencing a valid error notification (happens when an error 
     * notification is received), assume that there's a bug in the notification
     * system and use that error to be displayed after switching state.
     *
     * If an error is detected in one the checks described above, switch
     * to the error state.
     */
    checkForErrors: function() {
        var errorXHR = null;
        /* Execute when the error location exists */ 
        error_location_found = function(notification) {
            /* Check if the notification is not too old. If so, dismiss it and
             * check if this.error is already referencing an error notification
             *
             * SHOULD ONLY HAPPEN IF THE NOTIFICATION SERVICE IS BUGGY!
             */
            if(this._locationAge(errorXHR) >= this.maxErrorAge &&
              !this.error) {
                enconsole.log("OUTAGED: Error message to old");
                this.switchState("SUCCESS");
                return;
            }
            this.error = notification;
            enconsole.log("ERRORLOCATION: Error found");
            this.switchState("ERROR");
        }
        /* Execute if the error location doesn't exist */
        error_location_not_found = function(xhr, status, e) {
            if(this.errorOccured && this.error) {
                enconsole.log("ERRORLOCATION NOT FOUND: Error found");
                this.switchState("ERROR");
                return;
            }
            enconsole.log("NO ERROR FOUND, switching to success");
            this.switchState("SUCCESS");
        }
        errorXHR = $.getJSON(this.error_location + '?' + rand(),
                             lazy_apply(error_location_found, this),
                             lazy_apply(error_location_not_found, this));

    },
    
    /* Poll the notification system for new notifications from a service.
     *
     * If a new notification (status change of the service) is detected, 
     * the registered callback is fired.
     *
     * Query the notification json files for updates using an AJAX-Request.
     * The response is a JSON-list containing a status entry in each
     * element.
     *
     * If the location is not found, fire the subscription.locationNotFound
     * event.
     *
     * Give a delay, to delay the time of the first poll.
     */
    poll: function(interval, delay) {
        this.poll_interval = typeof(interval) == 'undefined' ? 
                                this.poll_interval : interval; 
        var delay = typeof delay != "undefined" ? delay : 0;
        var __poller = this;
        
        /* Define the poll function */
        pollfn = lazy_apply(function() {
            /* Only allow one request at a time */
            if(this.requestInProgress) {
                return;
            }
            this.requestInProgress = true;
            
            /* Fire a new request to the notification location */
            __lastXHR = $.getJSON(this.status_location + '?' + rand(), 
                                  lazy_apply(this.onSuccess, this), 
                                  lazy_apply(this.onError, this))
        }, this);
        
        /* Call pollfn using interval as interval */
        var starter = lazy_apply(function() {
            /* A state different from initiating implies, that the subscription
             * was aborted already. This might happen, if a subscription is
             * controlled by a master.
             */
            if(this.state != 'INITIATING') return;
            /* Check if the service has already died with an error */
            if(this.type != 'observe')
                this.serviceEndedAlready();
            /* Call once immediately, then after the defined interval */
            pollfn();
            this._interval_obj = setInterval(pollfn, interval);
        }, this);
        /* Delay the polling start if delay is defined */
        if(delay > 0) {
            setTimeout(starter, delay);
        }
        else {
            starter();
        }
    },
    /* Check if the service has already ended, before
     * the subscription started listening.
     */
    serviceEndedAlready: function() {
        var errorXHR = null;
        error_location_found = function(notification) {
            /* Check if the notification is not too old. If so, dismiss it and
             * check if this.error is already referencing an error notification
             *
             * SHOULD ONLY HAPPEN IF THE NOTIFICATION SERVICE IS BUGGY!
             */
            if(this._locationAge(errorXHR) >= this.maxErrorAge && 
               !this.error) {
                enconsole.log("OUTAGED: Ignore error message");
                return;
            }
            this.error = notification;
            enconsole.log("ERRORLOCATION: Error found");
            this.switchState("ERROR");
        }
        
        errorXHR = $.getJSON(this.error_location + '?' + rand(),
                             lazy_apply(error_location_found, this));
        
        var historyXHR = null;
        history_location_found = function(notification) {
            /* Check if the notification is not too old. If so, dismiss it and
             * check if this.error is already referencing an error notification
             *
             * SHOULD ONLY HAPPEN IF THE NOTIFICATION SERVICE IS BUGGY!
             */
            if(this._locationAge(historyXHR) >= this.maxHistoryAge || 
               this.state != 'INITIATING') {
                enconsole.log("OUTAGED: Ignore history message");
                return;
            }
            enconsole.log("HISTORY: Success!");
            this.switchState("RECEIVING");
        }
        
        historyXHR = $.getJSON(this.history_location + '?' + rand(),
                               lazy_apply(history_location_found, this));
    },
    /* Trigger everytime a notification is received */
    onSuccess: function(notification) {
        $(document).trigger('notification.received', 
                            {subscription: this, 
                             notification: notification})
        
        this.requestInProgress = false;
    },
    /**
     * A Ajax error is triggered in two cases:
     * 1. HTTP 404 - Location is not found
     * 2. Invalid JSON - No valid json object found under the given
                         location
     *
     * Case one triggers the subscription.locationNotFound event.
     * The second is handled by notificationReceived, since invalid
     * json object simply means, that the service started running
     * but no notifications have been posted yet.
     */
    onError: function(xhr, status, e) {
        /* Allow starting the next request */
        this.requestInProgress = false;
        
        /* Trigger respective event */
        if(xhr.status == 404) {
            enconsole.log("Triggering subscription.locationNotFound");
            $(document).trigger('subscription.locationNotFound', 
                                {'subscription': this,
                                 'error': [xhr, status, e]});

            
        }
        else if(status == 'parsererror') 
            $(document).trigger('notification.received', {subscription: this})
    },
    /**
     * Register the callback which is fired as soon as new notifications
     * are detected.
     */
    registerCallback: function(cb) {
        if(!$.isFunction(cb))
            throw "Callback must be a either a function or method";
        this.callback = cb;
        $(document).bind('notification.dispatch', 
                         ServiceSubscription.prototype.routeEvent(
                            this, this.callback));
    },
    /**
      * Stop the polling for new notifications
      */
    stop: function(imminent, switch_state) {
        var imminent = typeof imminent != 'undefined' ? imminent : true;
        var switch_state = typeof switch_state != 'undefined' ? switch_state :
                                                                true;
        this.receiving = false;
        
        if(imminent) {
            clearInterval(this._interval_obj);
            if(this.state == 'INITIATING' && switch_state)
                this.switchState("STOPPED");
        }
    },
    /**
     * Receive notification.
     */
    notificationReceived: function(evt, data) {
        var notification = data.notification;
        if(this.state == 'INITIATING') {
            /* Reset stateRequestCount for INITIATING */
            this.stateRequestCount['INITIATING'] = 0;
            /* Only switch state, if the location is not too old.
             * else, stop polling.
             */
            if(this._locationAge() <= this.maxStatusAge)
                this.switchState('RECEIVING');
            else {
                this.stop();
                return;
            }
        }
        /* Dispatch the notification´unless the same was
         * already receveived.
         */
        if(typeof notification == 'undefined') return;
        
        var dispatch = false;
        if(this.previousNotification == null)
            dispatch = true;
        else if(notification.time != this.previousNotification.time)
            dispatch = true;
        
        if(dispatch)
            this.previousNotification = notification
        $(document).trigger('notification.dispatch', 
                            {subscription: this,
                             notification: notification});
        
        if(dispatch && notification.type == 'error')
            $(document).trigger('notification.error', 
                                {subscription: this,
                                 notification: notification});
            
        
        return;
    },
    switchState: function(state) {
        enconsole.log("Switching state of " + this.service + "..." + 
                      this.state + " -> " + state);
        this.previousState = this.state
        this.state = state
        if(state == 'STOPPED' || state == 'ERROR' || state == 'SUCCESS') {
            this.stop();
        }
        
        if(state == 'RECEIVING')
            $(document).trigger('subscription.startReceiving', 
                                {subscription: this});
        else if(state == 'STOPPED')
            $(document).trigger('subscription.endReceiving', 
                                {subscription: this});
        else if(state == 'ERROR')
            $(document).trigger('subscription.failure', 
                                {subscription: this});
        else if(state == 'SUCCESS')
            $(document).trigger('subscription.success', 
                                {subscription: this});
    },
    /**
     * Return the age of the location in seconds.
     *
     * Check the Last-Modified header of the request to determine, when
     * the location was last changed and compare it with the current time.
     */
    _locationAge: function(xhr) {
        if(typeof(xhr) == 'undefined' && !__lastXHR) return 0;
        
        var xhr = typeof(xhr) != 'undefined' ? xhr : __lastXHR;
        
        date = xhr.getResponseHeader("Last-Modified")
        enconsole.log("date: " + date);
        try {
            time1 = Date.parse(date);
            time2 = Date.parse((new Date()).toUTCString());
            
            return (time2 - time1) / 1000;
        }
        catch(e) {
            enconsole.log(e);
            return 0;
        }
    },
    /**
     * Return the state of the subscription.
     *
     * Returns true if the state of the subscription differs from STOPPED,
     * ERROR or SUCCESS
     */
    active: function() {
        return (this.state != 'STOPPED' && this.state != 'ERROR' &&
                this.state != 'SUCCESS');
    }
}

/**
 * Returns a random number 
 */
function rand() {
    var chars = "0123456789";
    var string_length = 10;
    var randomstring = '';
    for (var i=0; i<string_length; i++) {
        var rnum = Math.floor(Math.random() * chars.length);
        randomstring += chars.substring(rnum,rnum+1);
    }
    return randomstring;
}

/**
 * jQuery Plugin for Service Notifications.
 *
 * Display the notifications received in the given element.
 *
 * Arguments:
 *     services -- list of services to watch for notifications
 *     custom_options --  dictionary of possible options to modify
 *                        the behaviour of how the notifications are
 *                        displayed
 *
 * Possible options:
 *     startMessage -- message to be displayed as soon as polling is started.
 *     endMessage -- message which is displayed as soon as the service sends no
 *                  more notifications
 *     onStart -- callback which is triggered IMMEDIATELY AFTER polling starts
 *     onEnd -- callback which is triggered when the service sends no more
 *              notifications.
 *     onNotification -- trigger callback on new notification
 *     interval -- interval for polling
 */
jQuery.fn.extend({
    notification: function(services, custom_options) {
        var __element = this;
        /* Defaul options which are overridden */
        this.options = {
            startMessage: "Notification listener is started",
            endMessage: "Notification listener is stopped",
            onStart: lazy_apply(function() {
                enconsole.log("Started notifications logging");
                __element.find('.content').html(this.options.startMessage)
                $('#notification-overlay').show().fadeTo(500, 0.66, 
                    function() {
                        $('#notification-container').show()
                        $('#notification-view').show();
                    });
            }, this),
            onEnd: lazy_apply(function() {
                /* Hide the Notification Display */
                $('#notification-view').fadeTo(500, 0.0, function() {
                    $('#notification-container').hide()
                    $('#notification-overlay').fadeTo(500, 0.0, function() {
                        $('#notification-overlay').hide();
                    });
					$('.temp_div').fadeTo(1500, 0.0, function() {
                        $('#notification-overlay').hide();
						$('.temp_div').hide();
                    });
					window.location.href = window.location.href;
                });
                /* Display the actual content */
                $('#module-content').css('visibility', 'visible');
				
            }, this),
            onFailure: lazy_apply(function(evt, notification, subscription) {
                $(document).trigger('subscriber.end');
                /* If the timeout for the error view kicks in, abort */
                if(typeof error_view != 'undefined')
                    clearTimeout(error_view);
                //$error_view.find('.text').html(notification.msg);
			    $error_view.find('.text').html("服务重启时发生错误，请关闭服务后再重新启动！");
                $error_view.fadeIn(500);
            }, this),
            onSuccess: lazy_apply(function(evt) {
                $(document).trigger('subscriber.end');
                /* If the timeout for the success view kicks in, abort */
                if(typeof notification_view != 'undefined')
                    clearTimeout(notification_view);
                $success_view.find('.text').html(this.options.endMessage);
                $success_view.fadeIn(500);
            }, this),
            onNotification: lazy_apply(function(notification, subscription) {
				if(notification.msg == "Initializing notification for service 'snort'"){
					notification.msg = "入侵防御服务正在重启...";
				}
                __element.find('.content').html(notification.msg)
				//__element.find('.content').html("正在重启...")returnDic
				//if(services[0] != "backup")
				//	__element.find('.content').html("正在重启...");
				//else
                //    __element.find('.content').html("正在备份...");
					
            }, this),
            interval: 1500,
            type: 'observer'
        }
        var $container = $overlay = $content = null;
        var createNotificationView = function() {
            var viewport_width = $(window).width();
            var viewport_height = $(window).height();
            var document_width = $(document).width();
            var document_height = $(document).height();
            $overlay = $('<div></div>').attr('id', 'notification-overlay')
                         .css('width', document_width + 'px')
                         .css('height', document_height + 'px')
                         .css('opacity','0.0')
            $container = $('<div></div>').attr('id', 'notification-container')
            var left = Math.round((viewport_width - 516) / 2);
            var top = Math.round((viewport_height - 86) / 2);
            /* Centering the container */
            $container.css('top', top).css('left', left)
            $content = $('<div></div>').addClass("content");
            /* Inserting the content view into the container */
            $container.append($content)
            enconsole.log($container);
            enconsole.log($content);
            /* Inserting the container view into the body */
            $('body').append($overlay)
            this.append($container);
        }
        
        var createStatusView = function(type) {
            var $status_view = $('<div style="display:none;width:100%;margin:0px"></div>');
           
            var class_name = type == 'error' ? "border:3px solid #f8622e;" : 
                                             "border:3px solid #fcb214;";
            var $layout = $('<div   class= "temp_div"  style="width:50%;margin:5px auto;padding:10px;min-height:60px;background-color:#FFF;'+class_name+'"><table  style="color:#666768;font-weight:bold;font-size:13px;"><tbody><tr></td></tbody></table></div>')
            $layout.attr('cellpadding', '0')
                   .attr('cellspacing', '0')
                   .attr('border', '0')
            var sign_img = type == 'error' ? '/images/pop_error.png' : 
                                             '/images/Emoticon.png';
            var $sign_img = $('<img alt="" src="' + sign_img + '"/>');
            var $sign = $('<td></td>').attr('align', 'right')
									  .attr('width', '35%')
									  .attr('height', '70px;')
                                      .attr('class','sign');
            $sign.append($sign_img);
            var $text = $('<td></td>').attr('align','left')
									  .attr('width', '65%')
									  .attr('height', '70px;')
                                      .attr('class','text')
            
            $layout.find('tr').append($sign);
            $layout.find('tr').append($text);
            $status_view.append($layout);

            return $status_view;
        }
      
        var $error_view = createStatusView.apply(this, ['error']);
        var $success_view = createStatusView.apply(this, ['notification']);
        
        $('#module-content').prepend($error_view);
        $('#module-content').prepend($success_view);
        
        createNotificationView.apply(this);
		
        /* Override default options with custom ones */
        jQuery.extend(this.options, custom_options || {});
        
        var beforeStop = lazy_apply(function() {
            if(typeof this.options.updateContent != 'undefined') {
                enconsole.log('beforeStop#reload_content -> this.options.onEnd');
                reload_content(lazy_apply(function() {
                    enconsole.log('#reload_content -> this.options.onEnd');
                    this.options.onEnd();
                }, this))
            }
            else {
                enconsole.log('beforeStop#onEnd');
                this.options.onEnd();
            }
        }, this);
        
        $(document).unbind('subscriber.start', this.options.onStart)
                   .bind('subscriber.start', this.options.onStart);
        $(document).unbind('subscriber.stop', beforeStop)
                   .bind('subscriber.stop', beforeStop);
        $(document).unbind('subscriber.failure', this.options.onFailure)
                   .bind('subscriber.failure', this.options.onFailure);
        $(document).unbind('subscriber.success', this.options.onSuccess)
                   .bind('subscriber.success', this.options.onSuccess);
        var reload_content = lazy_apply(function(callback) {
            var klass = typeof this.options.updateContent != 'undefined' ?
                        this.options.updateContent : null;
            if(klass == null) {
                enconsole.log("No class given!");
                return;
            }
            enconsole.log('Reloading content from ' + document.location.href 
                          + ' ' + klass);
            $.get(document.location.pathname, function(content) {
                $html = $(content);
                try {
                    $(document).find(klass).html($html.find(klass).html());
                }
                catch(e) {
                    enconsole.error(e);
                }
                try {
                    callback();
                }
                catch(e) {
                    enconsole.log(e);
                }
                
            });
        }, this);
        // $(document).unbind('subscriber.end', reload_content)
        //                    .bind('subscriber.end', reload_content);
        var subscriber = new ServiceSubscriber(services, 
                                               {type: this.options.type});
        subscriber.registerCallback(this.options.onNotification);
        subscriber.poll(this.options.interval);
        
        /* Push to global subscribers */
        __subscribers[this] = subscriber;
        

    },
    end_notifications: function() {
        if(typeof __subscribers[this] == 'undefined') return;
        __subscribers[this].abort();
		$(".temp_div").fadeOut("slow");
    }
	
});

/**
 * Helper for ease of use in Endian Firewall Modules
 */
function display_notifications(service, options) {
    services = []
    if(typeof service == 'string')
        services.push(service)
    else
        services = service;
    $('#notification-view').notification(services, options || {});
	
}

/**
 * Set the context of the function to the given context
 */
function lazy_apply(fn, context, args) {
    return function() {
        context.func_args = typeof args != 'undefined' ? args : undefined;
        return fn.apply(context, arguments);
    }
}

/**
 * ENConsole - Browser safe logging engine
 *
 * ENConsole allows you to debug your scripts using ERROR, INFO, or LOG 
 * messages via the console interface of browsers.
 *
 * If a browser doesn't provide the console interface, no log messages will
 * be printed (using console directly would lead to code breachs).
 *
 * Use the .off method to disable logging, and .on to enable logging.
 * By default, logging is ENABLED!
 *
 */
var ENConsole = function() {
    this.init();
}
ENConsole.prototype = {
    init: function() {
        this.state = 'on';
    },
    _log: function(obj) {
        console.log(obj);
    },
    _error: function(obj) {
        console.log(obj);
    },
    _info: function(obj) {
        console.log(obj)
    },
    log: function(obj) {
        if(!this.enabled()) return;
        this._log(obj);
    },
    info: function(obj) {
        if(!this.enabled()) return;
        this._info(obj);
    },
    error: function(obj) {
        if(!this.enabled()) return;
        this._error(obj);
    },
    enabled: function() {
        if(this.state == 'off') return false;
        if(typeof console == 'undefined') return false;
        if(typeof console.log == 'undefined' || 
           typeof console.error == 'undefined' ||
           typeof console.info == 'undefined') return false;
        
        return true;
    },
    on: function() {
        this.state = 'on';
    },
    off: function() {
        this.state = 'off';
    }
}

var enconsole = new ENConsole();
if(!DEBUG) {
    enconsole.off();
}