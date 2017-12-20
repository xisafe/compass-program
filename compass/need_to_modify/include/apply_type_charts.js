/*
 * 描述: 应用类型统计图页面
 *
 * 作者: pujiao
 * 公司: Capsheaf
 * 历史：
 *       2016.08.09 创建
 */
$(document).ready(function(){
    list_panel = new PagingHolder( list_panel_config );
    member_panel = new PagingHolder( member_panel_config);
    message_manager = new MessageManager( message_box_config );
    
    // /*统计条件处理*/
    // format_dataobj(data_obj);

    /* 渲染面板 */
    list_panel.render();
    member_panel.render();
    message_manager.render();
    
    apply_flow_chart = echarts.init(document.getElementById('apply_flow_chart')); //生成饼图
    
    list_panel.set_ass_message_manager( message_manager );
    member_panel.set_ass_message_manager( message_manager );
    member_panel.hide();
    data_obj =JSON.parse(localStorage.getItem('flow_charts'));
    if ( data_obj == null || data_obj.apply_charts_obj == null){
       message_manager.show_error_mesg("未设置应用类型统计条件");
    }
    else{
        data_obj = data_obj.apply_charts_obj;
    $.each(data_obj,function(i,v){
        if(v['name'] == "rankby"){
        data_obj.splice(i,1);
        }
        else if (v['name'] == "istrend"){
        data_obj.splice(i,1);
        }
        else if(v['name'] == "top"){
        data_obj.splice(i,1);
        }
        else if(v['name'] == "isurl"){
        if(data_obj[i]['value'] == 0){   /*判断统计数据是否是应用类型*/
            load_chart_data(data_obj,true);
        }
        else{
            load_chart_data([],true);
        } 
        }
    });
    }
    setTimeout(function(){
        $('button[onclick="member_panel.hide()"],#list_panel_close_for_list_panel_for_member,#popup-mesg-border-box-cover-list_panel_for_member').on('click', function() {
               if (data_obj[1].value == 'live') {
                    refresh_status.panel = '';
                }
           });
    },100);
    
});
var apply_flow_chart;
var chart_data = [];
var member_obj = {};
var is_loading_list_data_auto = true;
var member_panel;
var list_panel;
var data_obj;
var data_json;
var refresh_status = {
    select:'',
    panel:'',
    now:''
};
var message_box_config = {
    url: "/cgi-bin/apply_type_charts.cgi",
    check_in_id: "mesg_box_flow",
    panel_name: "my_message_box",
}
var risk_origin_chart = null;
var message_manager;
var tempGlobalObj = {};
var chartGlobalXHR = null;
var list_panel_for_ip_render = {
    'group':{
	render:function(default_data,data_item){
            return data_item.group;
        }    
    },
    'name':{
        render:function(default_data,data_item){
            return data_item.name;
        }
    },
    'host_ip':{
        render:function(default_data,data_item){
            return data_item.ruser;
        }
    },
    'bytes':{
        render:function(default_data,data_item){
            return formatBytes(default_data);
        }
    },
    'member':{
        render:function(default_data,data_item){
          var action_buttons = [
                {
                    enable: true,
                    id: "member_btn",
                    name: "member_btn",
                    class: "",
                    button_icon: "search16x16.png",
                    button_text: "趋势",
                    value: default_data,
                    functions: {
                        onclick: "showMember(this.value);"
                    },
                }
            ];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    },
    'trend':{
            render: function( default_rendered_text, data_item ) {
            var action_buttons = [
                {
                    enable: true,
                    id: "trend_btn",
                    name: "trend_btn",
                    class: "",
                    button_icon: "trend.png",
                    button_text: "趋势",
                    value: data_item.ruser,
                    functions: {
                        onclick: "load_one_trend(this.value);"
                    },
                }
            ];

            return PagingHolder.create_action_buttons( action_buttons );
        }
    }


};

 var panel_header_for_type = [
       {
            "enable": true,
            "type": "text",
            "title": "应用类型",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "10%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "总流量",
            "name": "bytes",
            "width": "10%",
            "td_class":"align-center"

        } , {
            "enable": true,
            "type": "text",
            "title": "流速趋势",
            "name": "trend",
            "width": "10%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "流量构成",
            "name": "member",
            "width": "10%",
            "td_class":"align-center"
        }
    ];


var panel_header_for_ip = [
		{
            "enable": true,
            "type": "text",
            "title": "主机IP",
            "name": "host_ip",
            "width": "20%",
            "td_class":"align-center"

        },
       {
            "enable": false,
            "type": "text",
            "title": "IP",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "20%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "组名",
            "name": "group",
            "width": "20%",
            "td_class":"align-center"

        },  {
            "enable": true,
            "type": "text",
            "title": "总流量",
            "name": "bytes",
            "width": "20%",
            "td_class":"align-center"

        }, {
            "enable": true,
            "type": "text",
            "title": "流速趋势",
            "name": "trend",
            "width": "10%",
            "td_class":"align-center"

        }, {
            "enable": true,
            "type": "text",
            "title": "流量构成",
            "name": "member",
            "width": "10%",
            "td_class":"align-center"

        }
    ];
    var panel_header_for_user = [
       {
            "enable": true,
            "type": "text",
            "title": "用户名",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "20%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "组名",
            "name": "group",
            "width": "20%",
            "td_class":"align-center"
        }, {
            "enable": false,			/*根据用户查询时不显示IP*/
            "type": "text",
            "title": "主机IP",
            "name": "host_ip",
            "width": "20%",
            "td_class":"align-center"
        },  {
            "enable": true,
            "type": "text",
            "title": "总流量",
            "name": "bytes",
            "width": "20%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "流速趋势",
            "name": "trend",
            "width": "10%",
            "td_class":"align-center"
        }, {
            "enable": true,
            "type": "text",
            "title": "流量构成",
            "name": "member",
            "width": "10%",
            "td_class":"align-center"
        }
    ];
   
var toolboxConfig = {
    show : true,
    // color: ["#1e90ff", "#22bb22", "#f009d2", "#d2691e"],
    feature : {
        dataView : {
            show: true,
            readOnly: true,
            y:'40px',
            title: "数据视图",
            lang: ["数据视图", "关闭", "刷新"],
            backgroundColor: "rgb(7, 25, 25)"
        },
        pieButtons:{
                show:true,//是否显示    
                title:'饼图切换', //鼠标移动上去显示的文字    
                icon:'../images/pie.png', //图标    
                option:{},    
                onclick:function(option1) {//点击事件,这里的option1是chart的option信息    
                    showApplyTypeChart();
                }   
            },
        selfButtons:{
                show:true,//是否显示    
                title:'趋势图', //鼠标移动上去显示的文字    
                icon:'../images/trend.png', //图标    
                option:{},    
                onclick:function(option1) {//点击事件,这里的option1是chart的option信息    
                    showApplyTypeTrendChart();
                }   
            }, 
        restore : {show: true},
        saveAsImage : {show: true}
    }
};

var apply_flow_option = {
    title:{
        text:"流量统计(总流量)",
        x:"center",
        y:"20%"
    },
    tooltip : {
        trigger: 'item',
        formatter: function(d){
            var temp = d[1] + ":  ";
            temp += formatBytes(d[2]) + "  ("+ d[3] +"%)";
            return temp;
        }
       
    },
    toolbox: toolboxConfig,
    legend: {
        orient : 'vertical',
        x:"89%",
        y:"13%",
        textStyle: {
            color: 'rgba(119,119,119, 0.8)'
        }
    },
    calculable : false
}
var apply_flow_trend_option = {
    title:{
        text:"流量统计(总流量)",
        x:'center'
    },
     tooltip : {
        trigger: 'axis',
        formatter: function (params,ticket,callback) {
            var res = params[0].name +"时 :";
            for (var i = 0, l = params.length; i < l; i++) {
                if(params[i].seriesName){
                    res += '<br/>' +( params[i].seriesName) + ' : ' + formatBytes(params[i].value);
                }
                else{
                    res += "暂无数据";
                    break;
                }
            }   
           setTimeout(function (){
                // 仅为了模拟异步回调
                callback(ticket, res);
            }, 0);
        }
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    animation:false,
    calculable : true,
    dataZoom : {
        show : true,
        realtime : true
    },
     xAxis : [
        {
            type : 'category',
            boundaryGap : false,
            axisLabel : {
                formatter:function(val){
                    return val + "时";
                }
            }
        }
    ],
    yAxis : [
        {
            type : 'value',
            axisLabel : {
                formatter:function(val){
                    return formatBytes(val);
                }
            }
        }
    ],
    toolbox: toolboxConfig,
    legend: {
        orient : 'vertical',
        x:"right",
        y:"40px",
        textStyle: {
            color: 'rgba(119,119,119, 0.8)'
        }
    },
    calculable : false
}
var member_panel_config = {
    url: "/cgi-bin/apply_type_charts.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_member_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size:10,                           /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel_for_member",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    panel_title: "流量组成",
    is_panel_closable: true, 
    is_modal: true,         
    modal_config: {                
        modal_box_size: "m",       
        modal_level: 10,           
        modal_box_position: "fixed"
    },
    //render: list_panel_for_ip_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj,data_item ) {

        },
        after_load_data: function( list_obj,data_item ) {
           
        },
    },
    panel_header: [
        {
            "enable": true,
            "type": "text",
            "title": "名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "50%"
        },{
           "enable": true,
            "type": "text",
            "title": "流量",        //一般text类型需要title,不然列表没有标题
            "name": "value",
            "width": "50%" 
        }],
    is_default_search: false,        /* ===可选===，默认是true，控制默认的搜索条件 */
    is_paging_tools: false, 
    bottom_extend_widgets: {        /* ===可选===，定义放在底部的按钮 */
        id: "",
        name: "",
        class:"align-center",
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            cls: "",
            style:"margin:4px auto;",
            button_text: "关闭",
            functions: {
                onclick: "member_panel.hide()"
            }
        }]
    }
}
var list_panel_config = {
    url: "/cgi-bin/apply_type_charts.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_flow_list_for_apply",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 3,                           /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel_for_apply",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    // panel_title: "IP/用户",
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    is_paging_tools: false,
    render: list_panel_for_ip_render,      /* ===可选===，渲染每列数据 */
    event_handler: {
        before_load_data: function( list_obj,data_item ) {

        },
        after_load_data: function( list_obj,data_item ) {
          
        },
    },
    panel_header: panel_header_for_type,
    is_default_search: false        /* ===可选===，默认是true，控制默认的搜索条件 */
}
function create_action_buttons( action_buttons ) {
    var buttons = "";

    if( action_buttons === undefined ) {
        return buttons;/*如果没有定义相应的对象，直接返回*/
    }

    for( var i = 0; i< action_buttons.length; i++ ) {
        var item = action_buttons[i];
        if( item.enable === undefined || !item.enable ){
            continue;
        }
        buttons += '<input type="image" ';
        if( item.id !== undefined && item.id ) {
            buttons += 'id="' + item.id + '" ';
        }
        if( item.value !== undefined && item.value ) {
            buttons += 'value="' + item.value + '" ';
        }
        if( item.name !== undefined && item.name ) {
            buttons += 'name="'+ item.name +'" ';
        }
        if( item.class !== undefined && item.class ) {
            buttons += 'class="action-image ' + item.class + '" ';
        } else {
            buttons += 'class="action-image" ';
        }
        if( item.button_text !==undefined && item.button_text ) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if( item.button_icon !== undefined && item.button_icon ) {
            buttons += 'src="../images/' + item.button_icon +'" ';
        }
        if( item.functions !== undefined && item.functions ) {
            var functions = item.functions;
            for ( var key in functions ) {
                buttons += key +'="' + functions[key] + '" ';
            }
        }
        buttons += '/>';
    }
    return buttons;
}

//处理统计条件对象数据
function load_one_trend(data){
    var trend_obj = $.extend(true,[],data_obj);
    var flag = 1;
    $.each(data_obj,function(i,v){
        if(v['name']=='istrend'){
         data_obj.splice(i,1);
        }
        if(v['name'] == "time_range" && v['value'] == "live"){
            message_manager.show_error_mesg("实时条件下，无法查看趋势图");
            flag = 0;
        }
    });
    trend_obj.push({"name":"istrend","value":1});
    trend_obj.push({"name":"ruser","value":data});
    if(flag){
        load_chart_data(trend_obj,false);
    }
       
}
//统计条件改变事件
function chang_statistical_method(){
    var statistical_method = $("#statistical_method").val();
    var header_list = [panel_header_for_type,panel_header_for_ip,panel_header_for_user];
    list_panel_config.panel_header = header_list[statistical_method];
    list_panel.display_list_panel();
    
    $.each(data_obj,function(i,v){
        if(v['name'] == "rankby"){
            data_obj[i][value] = statistical_method;
        }
    })
    // if (data_obj[1].value === 'live') {
    //     apply_flow_chart.clear()
    // }
    refresh_status.now = 'refresh';
    load_chart_data(data_obj,true);
}
//排名显示改变事件
function chang_top_method(){
    var top = $("top_num").val();
    // data_obj = top.frames.mainFrame.GetObj();
     $.each(data_obj,function(i,v){
        if(v['name'] == "top"){
            data_obj[i][value] = top;
        }
    })
    //  if (data_obj[1].value === 'live') {
    //     apply_flow_chart.clear()
    // }
     refresh_status.now = 'refresh';
    load_chart_data(data_obj,true);

}
//流量降序处理
function sortBytesDesc(item1, item2) {
    var sortResult = item2.bytes - item1.bytes;
    return sortResult;
}
//时间降序处理
function sortTimeDesc(item1, item2) {
    if(typeof(item1)=="object"){
        return item2[0] - item1[0]
    }else{
        return item2 - item1;
    }
}

function sortTimeAsc(item1,item2){
    return item1 - item2;
}
//数组求和
function sum(arr){
    return arr.reduce(function(a, b){ return a + b; });
}

//对象深拷贝
function deep_copy(t){
    return JSON.parse(JSON.stringify(t))
}
//将变量中的未定义赋值
function convertUndefToOther(obj,rep){
    if(rep === undefined || rep === null){
        rep = 0
    }
    if($.type(obj) === "object"){
        for(key in obj){
            obj[key] = convertUndefToOther(obj[key],rep);    
        }
        return obj;
    }else if($.type(obj) === "array"){
        $.each(obj,function(i,v){
            if(v === undefined || v === null){
                obj[i] = rep;
            }else{
                obj[i] = convertUndefToOther(obj[i],rep);
            }
        })
        return obj
    }else {
        //ignore function and others
         if(obj === undefined || obj === null){
                obj = rep;
            }
            return obj
    }
}
//对象转换为数组
function objectToArray(object){
    var array = [];
    for(var key in object){
        var arr =[];
        arr.push(key);
        arr.push(object[key]);
        array.push(arr);
    }
    return array;
}
/*
    * arr = [[1,2],[2,3]];
    *  arrayTobject(arr);
    * 返回： {1: 2, 2: 3}
    *
*/

function arrayToObject(arr){
    var o = {};
    for(var i = 0; i < arr.length; i++){
        o[arr[i][0]] =arr[i][1];
    }
    return o;
}
//字节单位转换
function formatBytes(bytes){
    if (bytes == 0) {return '0'};
    var type = 'B' ;
    var B = 1.0 ; 
    var K = 1024 * B ;
    var M = K * K ;
    var G = M * K ;
    var T = G * K ;
    var obj = {
        "B" : [B , "B"],
        "K" : [K , "KB"],
        "M" : [M , "MB"],
        "G" : [G , "GB"],
        "T" : [T , "TB"],
    }
    var fix = 3 ;
    if(bytes > T){
        type = 'T' ;
    }else if(bytes > G){
        type = 'G' ;
    }else if(bytes > M){
        type = 'M' ;
    }else if(bytes > K){
        type = 'K' ;
    }else{
        type = 'B' ;
    }
    return  (bytes/obj[type][0]).toFixed(fix).toString() + obj[type][1]
}
//加载图表数据
function load_chart_data(obj,updateListPanel){
    var send_obj = {};
    if(obj.length == 0){
        var nodata = [];
	message_manager.show_error_mesg("未设置应用统计条件");
        // apply_flow_option.noDataLoadingOption.text = "未设置统计条件";
        renderApplyTypeChart(nodata);
    }
    else{
         $.each(obj,function(i,item){
            var name = item.name;
            var value = item.value;
            send_obj[name]= value;
        });
        var lowtime = Math.round(new Date(send_obj.start_time +' '+ send_obj.start_time_hour+':'+send_obj.start_time_min).getTime()/1000);
        var hightime = Math.round(new Date(send_obj.end_time +' '+ send_obj.end_time_hour+':'+send_obj.end_time_min).getTime()/1000)+59;
        var ttag = send_obj.ip_or_user;
        var isurl =send_obj.isurl;
        var islive = (send_obj.time_range == "live") ? 1:0;
        
        var rankby = $("#statistical_method").val();
        var top =$("#top_num").val();
        var istrend;
        var tvalue = 0;
        if(!send_obj.hasOwnProperty("istrend")){
            istrend = 0;
        }
        else{
            istrend = send_obj['istrend'];
        }
        var sending_data = {
                ACTION: "load_data",
                rankby: rankby,
                top:top,
                islive:islive,
                ldate: lowtime,
                hdate: hightime,
                ttag: ttag,
                isurl: isurl,
                avalue: 0,
                tvalue:tvalue,
                istrend:istrend
        };
        if(isurl == "0"){
            sending_data['avalue'] = send_obj.avalue;
        }else{
            sending_data['uvalue'] = send_obj.uvalue;
        }
        if(send_obj.hasOwnProperty("tvalue")){
            tvalue = sending_data['tvalue'] = send_obj.tvalue;
        }
        if(send_obj.hasOwnProperty("ruser")){
            sending_data['ruser'] = send_obj.ruser;
        }
            var time_text = '(实时)';
            if (!islive){
                time_text = "("+send_obj.start_time+" "+send_obj.start_time_hour+":"+send_obj.start_time_min+" ~ "+send_obj.end_time+" "+send_obj.end_time_hour+":"+send_obj.end_time_min+")";
                $("#is_refresh_wrap").hide();
            }else{
                $("#is_refresh_wrap").show();

            }
            $("#s_time").html(time_text);
            var t_name ="";
            if(ttag == "0"){
                t_name = "所有";
            }
            else if(ttag == "1"){
                t_name = "IP";

            }
            else{
                t_name ="用户";
            }
            var t_text = '';
            if (!!tvalue){
                t_text = ": "+ tvalue;
            }
            $("#user_type").html("("+t_name+ t_text + ")");
            var classify_value = send_obj.atext;

            $("#app_type").html("("+classify_value+")");
	    
	    
        apply_flow_chart.showLoading({
            text:"加载中",
            effect:"whirling",
            textStyle : {
                fontSize : 20
            }
        });
        function ondatareceived(data){
            // console.log('ondatareceived start');
            // apply_flow_chart.clear()
            var _data = [];
            if (data!=null) {
                for (var i = 0; i < data.detail_data.length; i++) {
                    _data.push(data.detail_data[i][1]) ;
                }
                _data= _data[0];
            }
            if (data == null && _data == '') {
                apply_flow_chart.hideLoading();
                apply_flow_chart.showLoading({
                    text: '暂无数据',
                    effect: 'bubble',
                    effectOption: {
                        effect: {
                            n: 10
                        }
                    }                  
                })
                return;
            }
            if( istrend == 0){
                if (data_obj[1].value == 'live') {
                    renderApplyTypeChart(_data,'live');
                }else{
                    renderApplyTypeChart(_data);
                }
            }
            else{

                renderApplyTypeTrendChart(data.detail_data,top);
            }
            if(updateListPanel){
                if(_data.length > 0){
                    $("#no_data_box").hide();
               }
               else{
                    $("#no_data_box").show();
               }
                list_panel.detail_data = _data.sort(sortBytesDesc) ;
                list_panel.total_num = _data.length;
                list_panel.page_size = _data.length >= 3 ? _data.length : 3;
                list_panel.refresh_list_panel_body();
                list_panel.update_info();
            }
            // console.log('ondatareceived end');
            
        }

        var live_time = 5000;
        function live_charts(){
            refresh_status.panel == '' && do_request(sending_data, ondatareceived);
        }
        if (islive) {
            if (typeof(live_timer) != 'undefined') {
                window.clearInterval(live_timer);
            }

            if (refresh_status.select != 'refresh_no') {
                do_request(sending_data, ondatareceived);
                live_timer = window.setInterval(live_charts,live_time);
                
            }else{
                if (refresh_status.now != '') {
                    do_request(sending_data, ondatareceived);
                    refresh_status.now = '' ;   
                }else{
                    apply_flow_chart.hideLoading();
                    
                }
            }
            
        }else{
            do_request(sending_data, ondatareceived);
            
        }
    }

}
function renderApplyTypeChart(detail_data,status){
    detail_data = detail_data.sort(sortBytesDesc);
    var series_data = [], legend_data = [];
    if(detail_data.length == 0){
        series_data.push([0]);
    }else{
            for( var i = 0; i < detail_data.length; i++){
             var data_item = {
                 value: detail_data[i].bytes,
                 name: detail_data[i].name

             };
             series_data.push(data_item);
             legend_data.push(detail_data[i].name);
        } 
    }
    
    apply_flow_option.legend.data = legend_data;
    apply_flow_option.series =[ {
        name:'总流量',
        type:'pie',
        radius : '50%',
        startAngle:  0 ,
        center: ['50%', '60%'],
        data: series_data,
    }];
    if (!status) {
        apply_flow_chart.clear();

    }
    apply_flow_chart.hideLoading();
    apply_flow_chart.setOption(apply_flow_option,true);
}
function getDefaultArray(len, default_data){
    var arr=[];
    for(var i = 0 ; i < len ; i++){
        arr.push(default_data);
    }
    return arr;
}
function renderApplyTypeTrendChart(detail_data,top){
    var series_data = [], legend_data = [], xaxis_data = [];
    var o = {};
    var objLen = Object.keys(detail_data).length;
    for (var i = 0; i < detail_data.length; i++) {
        xaxis_data.push(detail_data[i][0].split(',')[1]);
        var items = detail_data[i][1];
        var len = items.length;
        // var data_arr = [];
        for(var j = 0; j < len; j++){
            var o_name = items[j].name;
            if(!o.hasOwnProperty(o_name)){
                o[o_name] = getDefaultArray(objLen, 0);
            }
            o[o_name][xaxis_data.length-1]= items[j].bytes;
        } 
    }
   o = convertUndefToOther(o,0);
    /*根据总流量排序取top*/
   var array = objectToArray(o);
    array = array.sort(function(item1, item2){
        return sum(item2[1]) - sum(item1[1]);
    }).splice(0,top);
    o = arrayToObject(array);

    xaxis_data.sort(sortTimeAsc);
    for(var i = 0 ; i < xaxis_data.length; i++){
        var d = new Date(parseInt(xaxis_data[i])*1000);
        xaxis_data[i] = d.Format("yyyy-MM-dd hh");
    }
    var s_len = Object.keys(o).length;
    if(s_len == 0){
        series_data.push({'name':"",'data':[0],'type':"line"});
    }else{
        for(var name in o){
            series_data.push({'name':name, 'type':'line','smooth':true,'data':o[name]});
            legend_data.push(name);  
        }
    }
    apply_flow_trend_option.xAxis[0].data = xaxis_data;
    apply_flow_trend_option.legend.data = legend_data;
    apply_flow_trend_option.series =series_data;
    apply_flow_chart.clear();
    apply_flow_chart.hideLoading();
    apply_flow_chart.setOption(apply_flow_trend_option,true);
    
}


//显示饼图
function showApplyTypeChart(){
    // $.each(data_obj,function(i,item){
    //     if(item['name']=='istrend'){
    //      data_obj.splice(i,1);
    //      return false;
    //     }
    // });
    for (var i = 0; i < data_obj.length; i++) {
        if (data_obj[i].name == 'istrend') {
            data_obj[i].value = 0 ;
        }
    }
    load_chart_data(data_obj,true);
}

// 显示趋势图
function showApplyTypeTrendChart(){
    
     var flag = 1;
     $.each(data_obj,function(i,v){
        if(v['name'] == "time_range" && v['value'] == "live"){
            message_manager.show_error_mesg("实时条件下，无法查看趋势图");
            flag = 0;
        }
     });
     if(flag){
        var flag_trend = true;
        for (var i = 0; i < data_obj.length; i++) {
            if (data_obj[i].name == 'istrend') {
                data_obj[i].value = 1 ;
                flag_trend = false;
            }
        }
        if (flag_trend) {
            data_obj.push({"name":"istrend","value":1});
        }
         load_chart_data(data_obj,false);
     }
}
function showMember(data_str){
    if (data_obj[1].value == 'live') {
        refresh_status.panel = 'refresh_no';
    }
    var arr1 =[],arr2=[];
    var arr = [];
    var b=data_str.split(',');
    for(var i=0;i<b.length;i+=2){
        arr1.push(b[i]);
        arr2.push(b[i+1]);
    }
    for(var i = 0; i < arr1.length; i++){
        var obj = {};
        obj['name'] = arr1[i];
        obj['value'] =formatBytes(arr2[i]);
        arr.push(obj);
    }
    member_panel.detail_data = arr;
    member_panel.total_num =arr.length;
    member_panel.page_size = arr.length;
    member_panel.refresh_list_panel_body();
    member_panel.update_info();
    member_panel.show();
}
//AJAX异步请求数据
function do_request(sending_data, ondatareceived) {
 
    try{
        if (chartGlobalXHR){
            chartGlobalXHR.abort();
            // isForcedAbort = true
            chartGlobalXHR = null
            // TODO: 如果请求时间过长，就不应该abort，否则永远无数据
            // console.log('abort ok..new ajax start');
        }
    }catch(e){
        // console.log('abort fail..new ajax start');
    }
    chartGlobalXHR = $.ajax({
        type: 'POST',
        url: "/cgi-bin/apply_type_charts.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            // if (!isForcedAbort){
            //     message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
            // }else{
            //     isForcedAbort = false;
            // }
        },
        success: ondatareceived
    });
}

function PreferSpeed1024(value, ps, fixed, extStr){
        var _value = parseFloat(value);
    var lst = ['T','G','M','K',''];
    var delta = 0;
    if (fixed === undefined) fixed = 0;
    if (extStr === undefined) extStr = '';
    else{ delta = 1/(fixed*100); }
        for(var i=0;  i < lst.length; i++){
        var unit = lst[i];
                if (_value > SCALE_INT1024[unit]){
                        return String((_value/SCALE_INT1024[unit]+delta).toFixed(fixed)).replace(/\.?0*$/,'')+unit+ps+extStr;   
        }
    }
    return value+ps+extStr;
}

function change_refresh() {
    refresh_status.select = $("#is_refresh").val();
    load_chart_data(data_obj,true);
}

