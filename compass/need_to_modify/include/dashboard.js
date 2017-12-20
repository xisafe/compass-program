/**
 * Function Update the HomePage info
 * 
 * Author: Endian
 * History:
 *   ~~ -- 2014 Modified By Unkonwn
 *   2014.12.08 Modified By WangLin
 */


/**
 * Function updateCollectData
 * Performs an AJAX request and calls updateGUI once the request has been completed.
 * 
 * @return void
 */
 
function updateCollectdData() {
    if (!COLLECTD_REQUEST) {
        COLLECTD_REQUEST = true;
        $.getJSON("/manage/status/status.collectd.data/?timeout=2", updateGUI);
        COLLECTD_REQUEST = false;
    }
    //添加系统服务状态
    $.get("/cgi-bin/status.cgi",{  },function(data){
        $("#main_status").html(data);
    })    
}

/**
 * Function updateGUI
 * Gets the JSON response from the updateCollectdData call and updates the dashboard
 * with the new data. Finally updateGraph is called.
 * 
 * @param json
 * 
 * @return void
 */
function updateGUI(json) {
    $.ajaxSetup({ cache: false });
    var memory = 0;
    var memory_used = 0;
    var swap = 0;
    var swap_used = 0;
    var swap_all = 0;
    var oldvalues = false;

    // 原来的代码不够健壮，在某些机器上出错了，修改之 WangLin 2014.12.05
    var memory_free = 0;
    var memory_cached = 0;
    var memory_buffered = 0;
    var memory_used_regx    = /memory\/memory-used/;
    var memory_free_regx    = /memory\/memory-free/;
    var memory_cached_regx  = /memory\/memory-cached/;
    var memory_buffered_regx = /memory\/memory-buffered/;

    var swap_cached = 0;
    var swap_free = 0;
    var swap_used_regx = /swap\/swap-used/;
    var swap_cached_regx = /swap\/swap-cached/;
    var swap_free_regx = /swap\/swap-free/;

    for ( var i in json ) {
        if ( i.match( memory_used_regx ) ) {
            try {
                memory_used = json[i]['value'];
                var ts = json[i]['timestamp'];
                if (cache_timestamp == ts) {
                    // cache is unchanged from last request
                    // so ignore this call in order not to count
                    // things twice
                    oldvalues = true;
                }
                cache_timestamp = ts;
            } catch (e) {} // value not cached, ignore it
        }
        /* 查找内存相关信息 */
        if ( i.match( memory_free_regx ) ) {
            memory_free = json[i]['value'];
        }
        if ( i.match( memory_cached_regx ) ) {
            memory_cached = json[i]['value'];
        }
        if ( i.match( memory_buffered_regx ) ) {
            memory_buffered = json[i]['value'];
        }

        /* 查找交换区相关信息 */
        if ( i.match( swap_used_regx ) ) {
            swap_used = json[i]['value'];
        }
        if ( i.match( swap_cached_regx ) ) {
            swap_cached = json[i]['value'];
        }
        if ( i.match( swap_free_regx ) ) {
            swap_free = json[i]['value'];
        }
    }

    memory += memory_used;
    memory += memory_free;
    memory += memory_cached;
    memory += memory_buffered;
    if (!isNaN(memory_used) && !isNaN(memory)) {
        update_memory(Math.round((memory_used/memory)*100));
    }

    swap += swap_used;
    swap += swap_cached;
    swap += swap_free;
    if (!isNaN(swap_used) && !isNaN(swap)) {
        update_swap(Math.round((swap_used/swap)*100));
    }

    /* try {
        var ts = json['memory/memory-used']['timestamp'];
        if (cache_timestamp == ts) {
        // cache is unchanged from last request
        // so ignore this call in order not to count
        // things twice
        oldvalues = true;
        }
        cache_timestamp = ts;
    } catch (e) {} // value not cached, ignore it

    try {
        memory_used = json['memory/memory-used']['value'];
        memory += json['memory/memory-free']['value'];
        memory += json['memory/memory-cached']['value'];
        memory += json['memory/memory-buffered']['value'];
        memory += memory_used;
        if (!isNaN(memory_used) && !isNaN(memory))
        update_memory(Math.round((memory_used/memory)*100));
    } catch (e) {} // ignore it

    try {
        swap_used += json['swap/swap-used']['value'];
        swap_used += json['swap/swap-cached']['value'];
        swap += json['swap/swap-free']['value'];
        swap += swap_used;
        if (!isNaN(swap_used) && !isNaN(swap))
        update_swap(Math.round((swap_used/swap)*100));
    } catch (e) {} // ignore it */
    // 修改End 2014.12.05 By WangLin

    var cpu_ava = 0;
    var cpu_num = 0;
    for (var j in json) {
        var nic_regex = /interface\/if_octets\-([\.a-z0-9]+)/;

        if (j.match(nic_regex)) { 
            var nic = RegExp.$1;
            nic = nic.replace('.','_');
            if (nic != 'lo') {
            try {
                rx = (parseFloat(json[j]['rx']) / 1000);
                var rxkb = rx;
                rxunit = "KB/s";
                if (rx >= 1000) {
                rx = rx / 1000;
                rxunit = "MB/s";
                }
                if (rx >= 1000) {
                rx = rx / 1000;
                rxunit = "GB/s";
                }

                tx = (parseFloat(json[j]['tx']) / 1000);
                            var txkb = tx;
                txunit = "KB/s";
                if (tx >= 1000) {
                tx = tx / 1000;
                txunit = "MB/s";
                }
                if (tx >= 1000) {
                tx = tx / 1000;
                txunit = "GB/s";
                }
                $('#in-'+nic).text(rx.toFixed(1) + ' ' + rxunit);
                $('#out-'+nic).text(tx.toFixed(1) + ' ' + txunit);
                if ( interfaces[nic]['data']['rx'].length >= MAX_GRAPH_VALUES )
                interfaces[nic]['data']['rx'].shift();
                interfaces[nic]['data']['rx'].push(rxkb); 
                if ( interfaces[nic]['data']['tx'].length >= MAX_GRAPH_VALUES )
                interfaces[nic]['data']['tx'].shift();
                interfaces[nic]['data']['tx'].push(txkb);
                // going here means the nic-zone is unkown
            } catch (e) { }
            }
        }

        if (oldvalues) {
            // don't touch counters if these are old cached values
            continue;
        }

        var cpu_regex = /(cpu\-\d+)\/cpu\-idle/;
        var df_regex = /df\/df\-([a-z]+(?:\-[a-z]+)?)/;
        var smtp_regex = /tail\-smtp\/connections\-([a-z]+)/;
        var pop_regex = /tail\-pop\/connections\-([a-z]+)/;
        var http_regex = /tail\-http\/connections\-([a-z]+)/;
        if (j == "filecount-postfix_queue/files") {
            try {
                var value = Math.round(json[j]['value']);
                $('#task-postfix-queue').text(value);
            } catch (e) {} // ignore it
        } else if (j.match(cpu_regex)) {
            //var cpu = RegExp.$1;
            var per_idle = Math.round(json[j]['value']);
            if (!isNaN(per_idle)) {
                cpu_ava += per_idle;
                cpu_num ++;
                /*
                if(usage>99)
                {
                    usage = 99;
                }
                $('#'+cpu+'-unused').attr('width',usage+'%');
                $('#'+cpu+'-used').attr('width',(100-usage)+'%');
                $('#'+cpu+'-percentage').text(100-usage);
                change_percent_color(cpu,100-usage);
                */
            }
        } else if (j.match(df_regex)) {
            var disk = RegExp.$1;
            var usage = Math.round((json[j]['used']/(json[j]['used']+json[j]['free'])) * 100);
            if ( disk == "var-log" ) {
                update_used_info( "df-log", usage );
            } else if ( disk == "var-efw" ) {
                update_used_info( "df-efw", usage );
            } else {
                update_used_info( "df-" + disk, usage );
            }
        } else if (j.match(smtp_regex)) {
            var type = RegExp.$1;
            try {
                if (!isNaN(json[j]['value'])) {
                    var value = Math.round(json[j]['value']*5);
                    $('#task-postfix-'+type+'-hour').text(
                            Math.round($('#task-postfix-'+type+'-hour').text())+value);
                    $('#task-postfix-'+type+'-day').text(
                            Math.round($('#task-postfix-'+type+'-day').text())+value);
                }
            } catch (e) {} // ignore it
        } else if (j.match(pop_regex)) {
            var type = RegExp.$1;
            try {
                if (!isNaN(json[j]['value'])) {
                    var value = Math.round(json[j]['value']*5);
                    $('#task-p3scan-'+type+'-hour').text(
                            Math.round($('#task-p3scan-'+type+'-hour').text())+value);
                    $('#task-p3scan-'+type+'-day').text(
                            Math.round($('#task-p3scan-'+type+'-day').text())+value);
                }
            } catch (e) {} // ignore it
        } else if (j.match(http_regex)) {
            var type = RegExp.$1;
            try {
                if (!isNaN(json[j]['value'])) {
                    var value = Math.round(json[j]['value']*5);
                    $('#task-squid-'+type+'-hour').text(
                            Math.round($('#task-squid-'+type+'-hour').text())+value);
                    $('#task-squid-'+type+'-day').text(
                            Math.round($('#task-squid-'+type+'-day').text())+value);
                }
            } catch (e) {} // ignore it
        }
    }
    var usage = 0;
    if(cpu_ava){
        usage = 100 - Math.round(cpu_ava/cpu_num);
        if(usage>99){
            usage = 99;
        }
        update_cpu( usage );
    }
    if (! oldvalues) {
        var date = new Date();
        date.setTime(cache_timestamp * 1000);
        $('#timestamp').text(date.toLocaleTimeString());
    }
    updateGraph();
}




/**
 * Function cloneObject
 * Makes a copy of an object instead of referencing it.
 * 
 * @param what
 * 
 * @return clone
 */
function cloneObject(what) {
    var clone = [];
    for (i in what) {
        clone[i] = what[i];
    }
    return clone;
}

/**
 * Function updateGraph
 * Is called by updateGUI and refreshes the charts with the new data. 
 * 
 * @return void
 */
function updateGraph() {
    var width_style = ((document.documentElement.clientWidth||Width.innerWidth)-150)*0.65;
    $("#live-traffic-graph-rx").css("width",width_style);
    $("#live-traffic-graph-tx").css("width",width_style);
    
    
    var rxlist = [];
    var txlist = [];

    var options = {
        'series': { shadowSize: 0 ,lines:{lineWidth: 1}},
        'yaxis': {'showLabels': true, 'label': Y_AXIS_TITLE},
        'xaxis': {'ticks': new Array()},
        'legend':{
                  'noColumns':1,
                  container:$(".rx-text")
         }
    };
    
    for (nic in interfaces) {
        // if ($('#if-checkbox-'+nic).attr('checked') == true) { 
        // jquery从11.3.2低版本升级到1.7以后此属性如此访问存在问题，首页的曲线没法显示
        // 2014.12.05 WangLin 修改
        if ($('#if-checkbox-'+nic)[0].checked == true) {
            if (interfaces[nic]['data']['rx'].length > 0) {
                data = cloneObject(interfaces[nic]['data']['rx']);
                rxlist.push({'label':nic,
                             'color':interfaces[nic]['color'],
                             'data':data});
            }
            if (interfaces[nic]['data']['tx'].length > 0) {
                data = cloneObject(interfaces[nic]['data']['tx']);
                txlist.push({'label':nic,
                             'color':interfaces[nic]['color'],
                             'data':data});
            }
        }
    }
    if (rxlist.length > 0) {
        for (rx = 0; rx < rxlist.length; rx++) {
            try {
                for (i = 0; i < rxlist[rx]['data'].length; i++) {
                    rxlist[rx]['data'][i] = [i,rxlist[rx]['data'][i]]; 
                }
            }
            catch(e) { }
        }
    }
    if (txlist.length > 0) {
        for (tx = 0; tx < txlist.length; tx++) {
            try {
                for (i = 0; i < txlist[tx]['data'].length; i++) {
                    txlist[tx]['data'][i] = [i,txlist[tx]['data'][i]]; 
                }
            }
            catch(e) { }
        }
    }
    
    $.plot($("#live-traffic-graph-rx"), rxlist, options);
    $.plot($("#live-traffic-graph-tx"), txlist, options);
}

/**
 * Function updateUplinks
 * Is called periodically and refreshes the uplinks-view.
 * 
 * @return void
 */
function updateUplinks() {
    if (!UPLINK_REQUEST) {
        UPLINK_REQUEST = true;
        $.getJSON("/manage/status/status.uplinksdaemon.data/?timeout=2",
        function (json) {
            var uplinks = json['uplinks']
            for (var uplink in uplinks) {
                var name = uplinks[uplink]['name'];
                var ip = "";
                var iface = "";
                try {
                    ip = uplinks[uplink]['data']['ip'];
                    iface = uplinks[uplink]['data']['interface'];
                } catch (e) {}
                var managed = uplinks[uplink]['managed'];
                var islinkactive = uplinks[uplink]['isLinkActive'];
                var uptime = uplinks[uplink]['uptime'];
                var status = uplinks[uplink]['status'];
                if (status == "ACTIVE")
                    $('#uplink-'+name+'-status').text('已连接');
                else if(status == "INACTIVE")
                    $('#uplink-'+name+'-status').text('未连接');
                else if(status == "DEAD")
                    $('#uplink-'+name+'-status').text('无效');
                else if(status == "connecting")
                    $('#uplink-'+name+'-status').text('正在连接');
                else if(status == "inactive")
                    $('#uplink-'+name+'-status').text('未激活');
                else if(status == "falure")
                    $('#uplink-'+name+'-status').text('连接失败');

                $('#uplink-'+name+'-status').css({'color':status_color[status]});
                $('#uplink-'+name+'-ip').text(ip);
                $('#uplink-'+name+'-interface').text(iface);
                if (managed == 'on') {
                    if (!MANAGE_REQUEST)
                        $('#uplink-'+name+'-managed').html('<a href="javascript: void(0);" '+
                                                       'onclick="setManaged(\''+name+'\',false);">'+
                                                       '<img src="/images/on.png" border="0" /></a>');
                    if (!UPLINK_HANDLE_REQUEST) {
                        if (islinkactive) {
                            $('#uplink-'+name+'-active').html('<a href="javascript: void(0);"> '+
                                                        '<img src="/images/on.png" border="0" /></a>');
                        } else {
                            $('#uplink-'+name+'-active').html('<a href="javascript: void(0);"> '+
                                                        '<img src="/images/off.png" border="0" /></a>');
                        }
                    }
                } else {
                    if (!MANAGE_REQUEST)
                        $('#uplink-'+name+'-managed').html('<a href="javascript: void(0);" '+
                                                       'onclick="setManaged(\''+name+'\',true);">'+
                                                       '<img src="/images/off.png" border="0" /></a>');
                    if (!UPLINK_HANDLE_REQUEST) {
                        if (islinkactive) {
                            $('#uplink-'+name+'-active').html('<a href="javascript: void(0);" '+
                                                              'onclick="changeUplink(\''+name+'\',\'stop\');">' +
                                                              '<img src="/images/on.png" border="0" /></a>');
                        } else {
                            $('#uplink-'+name+'-active').html('<a href="javascript: void(0);" '+
                                                              'onclick="changeUplink(\''+name+'\',\'start\');">' +
                                                              '<img src="/images/off.png" border="0" /></a>');
                        }
                    }
                }
            }
            UPLINK_REQUEST = false;
        });
    }
}

/**
 * Function setManaged
 * Sets a specified uplink to managed or unmanaged and refreshes the uplinks GUI.
 * 
 * @param name
 * @param value
 * 
 * @return void
 */
function setManaged(name, value) {
    var name = name;
    var value = value;
    if (!MANAGE_REQUEST) {
        MANAGE_REQUEST = true;
        $('#uplink-'+name+'-managed').html('<img src="/images/indicator.gif" />');
        $.getJSON("/cgi-bin/uplinks-status.cgi?uplink="+name+"&action="+(value==true?'manage':'unmanage'),
                  manageUplink);
    }
    function manageUplink(json) {
        $('#uplink-'+name+'-managed').html('<a href="javascript: void(0);" '+
                   'onclick="setManaged(\''+name+'\','+(value==true?'false':'true')+');">'+
                      '<img src="/images/'+(value==true?'on':'off')+'.png" border="0" /></a>');
        if (value == true) {
            if (json['isLinkActive']) {
                $('#uplink-'+name+'-active').html('<a href="javascript: void(0);"> '+
                                                    '<img src="/images/on.png" border="0" /></a>');
            } else {
                $('#uplink-'+name+'-active').html('<a href="javascript: void(0);"> '+
                                                    '<img src="/images/off.png" border="0" /></a>');
            }
            //$('#uplink-'+name+'-reconnect a').each(function() {console.log($(this).val())});
            $('#uplink-'+name+'-reconnect').html($('#uplink-'+name+'-reconnect').html().replace("restart", "stop"));
        }
        else {
            if (json['isLinkActive']) {
                $('#uplink-'+name+'-active').html('<a href="javascript: void(0);" '+
                                                    'onclick="changeUplink(\''+name+'\',\'stop\');">' +
                                                    '<img src="/images/on.png" border="0" /></a>');
            } else {
                $('#uplink-'+name+'-active').html('<a href="javascript: void(0);" '+
                                                    'onclick="changeUplink(\''+name+'\',\'start\');">' +
                                                    '<img src="/images/off.png" border="0" /></a>');
            }
            //$('#uplink-'+name+'-reconnect a').each(function() {console.log($(this).val())});
            $('#uplink-'+name+'-reconnect').html($('#uplink-'+name+'-reconnect').html().replace("stop", "restart"));

        }
        MANAGE_REQUEST = false;
    }
}

/**
 * Function changeUplink
 * Activates or deactivates the specified uplink and refreshes the uplinks GUI.
 * 
 * @param name
 * @param action
 * 
 * @return void
 */
function changeUplink(name,action) {
    var name = name;
    // if action is not start or restart set it to stop
    var action = (action == 'start' ? 'start' : (action == 'restart' ? 'restart' : 'stop'));
    
    if (!UPLINK_HANDLE_REQUEST) {
        UPLINK_HANDLE_REQUEST = true;
        $('#uplink-'+name+'-active').html('<img src="/images/indicator.gif" />');
        $.getJSON("/cgi-bin/uplinks-status.cgi?uplink="+name+"&action="+action,change);
    }
    
    function change(json) {
        var status = json['status'];
        var pic = (status == 'ACTIVE' ? 'off' : 'on');
        var act = (status == 'ACTIVE' ? 'stop' : 'start');
        $('#uplink-'+name+'-active').html('<a href="javascript: void(0);" '+
                                          'onclick="changeUplink(\''+name+'\',\''+act+'\');">' +
                                          '<img src="/images/'+pic+'.png" border="0" /></a>');
        UPLINK_HANDLE_REQUEST = false;
    }
}


//author：zhouyuan
//date:2011-07-11
function change_percent_color(id,percent)
{
    if(percent<30)
    {
        $('#'+id+"-used").css("background-image","url(/images/percent_bg_low.jpg)");
        //$('#'+id+"-percentage").css("color","green").css("font-weight","bold");
    }else if(percent>70)
    {
        $('#'+id+"-used").css("background-image","url(/images/percent_bg_high.jpg)");
        //$('#'+id+"-percentage").css("color","red").css("font-weight","bold");
    }else{
        $('#'+id+"-used").css("background-image","url(/images/percent_bg_middle.jpg)");
        //$('#'+id+"-percentage").css("color","orange").css("font-weight","bold");
    }
}


/**
 * Function update_memory
 * Updates the memory graph and sets the bar to the specified percentage.
 * 
 * @param mpercentage
 * 
 * @return void
 */
// function update_memory(mpercentage) {
//     $('#memory-unused').attr('width',(100-mpercentage)+'%');
//     $('#memory-used').attr('width',mpercentage+'%');
//     $('#memory-percentage').text(mpercentage);
//     change_percent_color("memory",mpercentage);
// }

/**
 * Function update_swap
 * Updates the swap graph and sets the bar to the specified percentage.
 * 
 * @param per
 * 
 * @return void
 */
// function update_swap(per) {
//     try {
//         $('#swap-unused').attr('width',(100-per)+'%');
//         $('#swap-used').attr('width',per+'%');
//         $('#swap-percentage').text(per);
//         change_percent_color("swap",per);
//     }
//     catch(e) {}
// }

// function update_cpu( per ) {
//         $('#cpu-unused').attr('width',usage+'%');
//         $('#cpu-used').attr('width',(100-usage)+'%');
//         $('#cpu-percentage').text(100-usage);
//         change_percent_color("cpu",100-usage);
// }

/**
 * Function update_used_info
 * Updates the specific graph and sets the bar to the specified percentage.
 * @Author: WangLin
 * @History 2014.12.08 WangLin Created
 * 
 * @param id -- the specific graph id
 *        per -- used percentage
 * 
 * @return void
 */
function update_used_info( id, per ) {
    try {
        $('#' + id + '-unused').attr('width',(100-per)+'%');
        $('#' + id + '-used').attr('width',per+'%');
        $('#' + id + '-percentage').text(per);
        change_percent_color( id , per);
    }
    catch(e) {}
}

function update_cpu( per ) {
    update_used_info( "cpu", per );
}

function update_swap( per ) {
    update_used_info( "swap", per );
}

function update_memory( per ) {
    update_used_info( "memory", per );
}
/**
 * Function getDashboard
 * This function is called once the document is loaded. It will load the
 * dashboard in the background and then show it on the page.
 * 
 * @param data
 * 
 * @return void
 */
function getDashboard(data) {
    updateCollectdData();
    updateUplinks();
    $('#module-content').html(data);
    $('#dashboard').show('1000');
    add_help();
    //window.setInterval("add_help()",2500);
    window.setInterval("updateCollectdData()",2500);
    window.setInterval("updateUplinks()",2500);    
    $(".dashboard-service").eq(2).css("display","none");
    //2013-7-22屏蔽入侵防御显示
    $(".dashboard-service").eq(3).css("display","none");
    //
    //$(".dashboard-service").eq(1).css("display","none");
    //$(".dashboard-service").eq(0).css("display","none");
}

/**
 * Function checkCheckboxes
 * Makes sure that not more than MAX_GRAPH_CHECKED checkboxes are checked.
 * If MAX_GRAPH_CHECKED checkboxes have been checked the others will be disabled
 * until one is unchecked.
 * 
 * @param id
 * 
 * @return void
 */
function checkCheckboxes(id) {
    try {
        var el = document.getElementById(id);
        if (el.checked && !el.disabled) {
            currently_checked++;
            if (currently_checked >= MAX_GRAPH_CHECKED) { 
                var boxes = $('input.graph_checkbox').get();
                for (var box in boxes) {
                    if (!boxes[box].checked) {
                        boxes[box].disabled = true;
                    }
                }
            }
        } else if (!el.checked) {
            currently_checked--;
            currently_checked = Math.max(0,currently_checked);
            if (currently_checked < MAX_GRAPH_CHECKED) { 
                var boxes = $('input.graph_checkbox').get();
                for (var box in boxes) {
                    if (boxes[box].disabled) {
                        boxes[box].disabled = false;
                    }
                }
            }
        }
    } catch(e) {}
}


/*
    作者:周圆
    功能:显示帮助悬浮层信息
    修改时间：2011-09-23
*/
function show_help(id)
{
    $("#"+id).find(".help_div").stop()
    .animate({left: "150", opacity:1}, "fast")
    .css("display","block")
}

/*
    作者:周圆
    功能:隐藏帮助悬浮层信息
    修改时间：2011-09-23
*/
function hide_help(id)
{
    $("#"+id).find(".help_div").stop()
    .animate({left: "130", opacity:0}, "10")
    .css("display","none")
}

/*
    作者:周圆
    功能:添加帮助悬浮层信息
    修改时间：2011-09-23
*/
function add_help()
{
    $.get('/cgi-bin/main_help_back.cgi', {}, function(data){    
        var temp = data.split("&&&&&&&&&&");
        $(".help_div_box").remove();
        if(temp[0] == "on")
        {
            $(temp[1]).appendTo("#main_disk");
            $(temp[2]).appendTo("#main_eth");
            $(temp[3]).appendTo("#squid");
            $(temp[4]).appendTo("#postfix");
            $(temp[5]).appendTo("#main_pop3");
            $(temp[6]).appendTo("#snort");
            $(temp[7]).appendTo("#main_state");
        }
    });
}

/*
    Author:zhouyuan
    Function: 点击主面板上的日志记录时，左边menu显示正确
*/
function link_to_log()
{
    parent.window.document.getElementById('rightFrame').src='logs_live.cgi';
    var inner_html = self.parent.frames[0].document.getElementById('menu-content').innerHTML;
    var dd_object = self.parent.frames[0].document.getElementsByTagName('dd');
    var dt_object = self.parent.frames[0].document.getElementsByTagName('dt');
    for(var i= 0;i<dd_object.length;i++)
    {
        dd_object[i].style.display = "none";
    }
    var dt_length = dt_object.length;
    for(var i= 0;i<dt_object.length;i++)
    {
        dt_object[i].firstChild.style.background = "#c7eaf9";
        dt_object[i].firstChild.style.fontWeight = "normal";
    }
    self.parent.frames[0].document.getElementById('is_logs_live').parentNode.parentNode.style.display="block";
    var object = self.parent.frames[0].document.getElementById('is_logs_live');
    object.style.backgroundColor= "#fef2e7";
    object.style.fontWeight= "bold";
    dt_object[dt_length-1].firstChild.style.background = "url(/images/menu-bg-hover.jpg)";
    dt_object[dt_length-1].firstChild.style.fontWeight = "bold";
}


var uplink_colors = {'offline' : '#993333',
        'online' : '#339933',
        'pending' : '#FF9933',
        'unmanaged' : '#666666'};

/* mapping status to color */
var status_color = {'DEAD' : uplink_colors['pending'],
        'INACTIVE' : uplink_colors['offline'],
        'ACTIVE' : uplink_colors['online'],
        'CONNECTING' : uplink_colors['pending'],
        'DISCONNECTING' : uplink_colors['pending'],
        'FAILURE' : uplink_colors['pending']};

var COLLECTD_REQUEST = false;
var UPLINK_REQUEST = false;
var MANAGE_REQUEST = false;
var UPLINK_HANDLE_REQUEST = false;
var MAX_GRAPH_VALUES = 30;
var MAX_GRAPH_CHECKED = 6; // this value is overwritten in the dashboard template
var Y_AXIS_TITLE = 'KB/s'; // this value is overwritten in the dashboard template
var interfaces = {};
var green_colors = ['#00C618','#39E24D','#66E275','#008110','#259433'];
var red_colors = ['#A60800','#BF3730','#FF0D00','#FF4940','#FF7A73'];
var orange_colors = ['#FFC773','#A66300','#BF8630','#FF9900','#FFB240'];
var blue_colors = ['#0C5DA5','#408DD2','#679FD2','#043A6B','#26537C'];
var purple_colors = ['#660BAB','#9440D5','#A668D5','#41046F','#592680'];
var unknown_colors = ['#222222','#555555','#888888','#AAAAAA','#CCCCCC'];
var unknown_count = 0;
var green_count = 0;
var red_count = 0;
var orange_count = 0;
var blue_count = 0;
var purple_count = 0;
var currently_checked = 0;
var cache_timestamp = 0;


$(document).ready( function() {
    $.get('/cgi-bin/dashboard.cgi',getDashboard);
});


