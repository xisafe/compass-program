/***author:刘炬隆(Liu Julong)
    createDate:2014.9.2
***/
var paging_holder = {
    url:"/cgi-bin/chart_linkage.cgi",
    data_content:{
        total: 0,
        sessioninfo_hour: [],
        sessioninfo_day: [],
        sessioninfo_week: [],
        sessioninfo_month: [],
        sessioninfo_history: []
    },
    data_hour_x:[],
    data_hour_y:[],
    data_day_x:[],
    data_day_y:[],
    data_week_x:[],
    data_week_y:[],
    data_month_x:[],
    data_month_y:[],
    
    data_history_x:[],
    data_history_y_day:[],
    data_history_y_aven:[],
    is_load_hour: true,
    is_load_another: false,
    load_hour_num: 0
};

var myChart;
var jat_Lag = 0;
var hour_option;
//初始化页面
$(document).ready(function(){
    load_data();
    //init();
});

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: paging_holder.url,
        data: sending_data,
        async: true,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//加载数据
function load_data(){
    
    var sending_data = {
        ACTION: "load_data"
    };

    function ondatareceived(data) {
        //var data_content = JSON.parse(data);
        var data_content = eval("("+data+")");
        paging_holder.data_content.sessioninfo_hour = preprocess(60,data_content.sessioninfo_hour);
        paging_holder.data_content.sessioninfo_day = preprocess(1440,data_content.sessioninfo_day);
        paging_holder.data_content.sessioninfo_week = preprocess(10080,data_content.sessioninfo_week);
        paging_holder.data_content.sessioninfo_month = preprocess(43200,data_content.sessioninfo_month);
        paging_holder.data_content.sessioninfo_history = data_content.sessioninfo_history;
        //初始化一小时会话数据
        
        paging_holder.data_hour_x = [];
        paging_holder.data_hour_y = [];
        var last_item = "first";
        var hour_last = 99;
        var minutes_last = 99;
        for(var i=0;i<paging_holder.data_content.sessioninfo_hour.length;i++){
            
            //获取60个点
            var seconds = paging_holder.data_content.sessioninfo_hour[i].time;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var hour = parseInt(mydate.getHours());
            var val_hour = hour;
            if(hour < 10){
                hour = "0"+hour;
            }
            var minutes = parseInt(mydate.getMinutes());
            var val_minutes = minutes;
            if(minutes < 10){
                minutes = "0"+minutes;
            }
            
            var item = hour+":"+minutes;
            paging_holder.data_hour_y.unshift(paging_holder.data_content.sessioninfo_hour[i].value);
            paging_holder.data_hour_x.unshift(item);
            
            
        }
        //paging_holder.data_hour_x = line_x;
        //初始化一天会话数据
        paging_holder.data_day_x = [];
        paging_holder.data_day_y = [];
        for(var i=0;i<paging_holder.data_content.sessioninfo_day.length;i++){
            var seconds = paging_holder.data_content.sessioninfo_day[i].time;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var hour = parseInt(mydate.getHours());
            if(hour < 10){
                hour = "0"+hour;
            }
            if(i == 0){
                paging_holder.data_day_x.unshift(hour);
                paging_holder.data_day_y.unshift(paging_holder.data_content.sessioninfo_day[i].value);
                lastHour = hour;
            }
            if(i>0 && (i+1)%10 == 0){
                paging_holder.data_day_x.unshift(hour);
                paging_holder.data_day_y.unshift(paging_holder.data_content.sessioninfo_day[i].value);
            }
        }
        
        
        //初始化一周会话数据
        paging_holder.data_week_x = [];
        paging_holder.data_week_y = [];
        
        for(var i = 0; i < paging_holder.data_content.sessioninfo_week.length;i++){
            var seconds = paging_holder.data_content.sessioninfo_week[i].time;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var month = parseInt(mydate.getMonth()+1);
            var day = parseInt(mydate.getDate());
            
            if(month < 10){
                month = "0"+month;
            }
            if(day < 10){
                day = "0"+day;
            }
            
            if(i == 0){
                paging_holder.data_week_x.unshift(month+"-"+day);
                paging_holder.data_week_y.unshift(paging_holder.data_content.sessioninfo_week[i].value);
            }
            
            if(i>0 && (i+1)%10 == 0){
                paging_holder.data_week_x.unshift(month+"-"+day);
                paging_holder.data_week_y.unshift(paging_holder.data_content.sessioninfo_week[i].value);
            }
            
        }    
        //初始化一月会话数据
        paging_holder.data_month_x = [];
        paging_holder.data_month_y = [];
        
        for(var i=0;i<paging_holder.data_content.sessioninfo_month.length;i++){
            var seconds = paging_holder.data_content.sessioninfo_month[i].time;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var month = parseInt(mydate.getMonth()+1);
            var day = parseInt(mydate.getDate());
            
            if(month < 10){
                month = "0"+month;
            }
            if(day < 10){
                day = "0"+day;
            }
            
            if(i == 0){
                paging_holder.data_month_x.unshift(month+"-"+day);
                paging_holder.data_month_y.unshift(paging_holder.data_content.sessioninfo_month[i].value);
            }
            if(i>0 && (i+1)%10 == 0){
                paging_holder.data_month_x.unshift(month+"-"+day);
                paging_holder.data_month_y.unshift(paging_holder.data_content.sessioninfo_month[i].value);
            }
            
        }
        
        //初始化历史平均会话数据
        paging_holder.data_history_x = [];
        var last_hour_history = "00";
        for(var i=0;i<paging_holder.data_content.sessioninfo_history.length;i++){
            var seconds = paging_holder.data_content.sessioninfo_history[i].time.split(".")[0]*1000 - jat_Lag;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var hour = parseInt(mydate.getHours());
            last_hour_history = hour;
            if(hour < 10){
                hour = "0"+hour;
            }
            var minutes = parseInt(mydate.getMinutes());
            if(minutes < 10){
                minutes = "0"+minutes;
            }
            paging_holder.data_history_x.unshift(hour);
            /* paging_holder.data_history_x.unshift(mydate.getFullYear()+"-"+(mydate.getMonth()+1)+"-"
            +mydate.getDate()+" "+hour+":"+minutes); */
        }
        paging_holder.data_history_y_day = [];
        paging_holder.data_history_y_aven = [];
        for(var i=0;i<paging_holder.data_content.sessioninfo_history.length;i++){
            paging_holder.data_history_y_day.unshift(paging_holder.data_content.sessioninfo_history[i].value[0]);
            paging_holder.data_history_y_aven.unshift(paging_holder.data_content.sessioninfo_history[i].value[1]);
        }
        //如果不够1440个点，前面的点置空
        var length_history = paging_holder.data_history_x.length;
        if(paging_holder.data_history_x.length < 1440){
            var time_add = last_hour_history;
            if(time_add > 0){
                time_add--;
            }else{
                time_add = "23";
            }
            for(var i=length_history;i<1440;i++){
                if( i % 60 == 0){
                    if(time_add > 0){
                        time_add--;
                    }else{
                        time_add = "23";
                    }
                }
                var time_del = time_add;
                if(time_del < 10 ){
                    time_del = "0"+time_del;
                }
                paging_holder.data_history_x.unshift(time_del);
                paging_holder.data_history_y_day.unshift("0");
                paging_holder.data_history_y_aven.unshift("0");
            }
        }
        var selected_style = $("#style_count").val();
        init();
        if(selected_style == "hour"){
            setChartForHour();
            load_data_hour();
        }else{
            window.setTimeout("load_data()",600000);
        }
    }
    do_request(sending_data, ondatareceived);
}
//实时请求一小时内的数据
function load_data_hour(){
    paging_holder.load_hour_num++;
    var sending_data = {
        ACTION: "load_data_hour"
    };

    function ondatareceived(data) {
        //var data_content = JSON.parse(data);
        var data_content = eval("("+data+")");
        paging_holder.data_content.sessioninfo_hour = preprocess(60,data_content.sessioninfo_hour);
        //初始化一小时会话数据
        paging_holder.data_hour_x = [];
        paging_holder.data_hour_y = [];
        var last_item = "first";
        var hour_last = 99;
        var minutes_last = 99;
        for(var i=0;i<paging_holder.data_content.sessioninfo_hour.length;i++){
            
            //获取60个点
            var seconds = paging_holder.data_content.sessioninfo_hour[i].time;
            var mydate = new Date(seconds);
            mydate.setTime(seconds);
            var hour = parseInt(mydate.getHours());
            var val_hour = hour;
            if(hour < 10){
                hour = "0"+hour;
            }
            var minutes = parseInt(mydate.getMinutes());
            var val_minutes = minutes;
            if(minutes < 10){
                minutes = "0"+minutes;
            }
            
            var item = hour+":"+minutes;
            paging_holder.data_hour_y.unshift(paging_holder.data_content.sessioninfo_hour[i].value);
            paging_holder.data_hour_x.unshift(item);
            
            
        }
        
        if(paging_holder.is_load_hour == true){
            var lastData = paging_holder.data_hour_y[paging_holder.data_hour_y.length - 1];
            var axisData = paging_holder.data_hour_x[paging_holder.data_hour_x.length - 1];
            myChart.addData([
                [
                    0,        // 系列索引
                    lastData, // 新增数据
                    false,    // 新增数据是否从队列头部插入
                    false,    // 是否增加队列长度，false则自定删除原有数据，队头插入删队尾，队尾插入删队头
                    axisData  // 坐标轴标签
                ],
            ]);
            window.setTimeout("load_data_hour()",60000);
        }
    }
    do_request(sending_data, ondatareceived);
}
function init(){
    /* var myChart = echarts.init(document.getElementById('chart_recent'));
    myChart.setOption({
        tooltip : {
            trigger: 'axis'
        },
        legend: {
            data:['总连接数'],
            orient:'vertical',
            x:'right'
        },
        toolbox: {
            show : false,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        calculable : true,
        xAxis : [{
            name: '时间',
            type : 'category',
            data: paging_holder.data_hour_x
        }],
        yAxis : [{
            name: '总连接数',
            type : 'value',
            splitArea : {show : true}
        }],
        series : [{
            name:'总连接数',
            type:'line',
            symbol:'none',
            data:paging_holder.data_hour_y
        }]
    }); */
    
    //历史会话对比
    var myChart_history = echarts.init(document.getElementById('chart_history'));
    myChart_history.setOption({
        tooltip : {
            show:false,
            trigger: 'axis'
        },
        legend: {
            data:['当前一天连接数','历史日均连接数'],
            orient:'vertical',
            x:'right'
        },
        toolbox: {
            show : false,
            feature : {
                mark : {show: true},
                dataView : {show: true, readOnly: false},
                magicType : {show: true, type: ['line', 'bar']},
                restore : {show: true},
                saveAsImage : {show: true}
            }
        },
        calculable : true,
        xAxis : [{
            name: '时间',
            type : 'category',
            axisTick: {
                show: false,
                interval : 59
            },
            axisLabel: {
                show: true,
                interval : 59
            },
            data: paging_holder.data_history_x
        }],
        yAxis : [{
            name: '总连接数',
            type : 'value',
            splitArea : {show : true}
        }],
        series : [{
            name:'当前一天连接数',
            type:'line',
            symbol:'none',
            data:paging_holder.data_history_y_day
        }, {
            name:'历史日均连接数',
            type:'line',
            symbol:'none',
            data:paging_holder.data_history_y_aven
        }]
    });
};

//统计图切换状态
function changeChart(e){
    var myChart = echarts.init(document.getElementById('chart_recent'));
    //var Chart_history = echarts.init(document.getElementById('chart_history'));
    var data_line_x = [];
    var data_line_y = [];
    var intervals = 5;
    var width_line = 1;
    var color_line = 'red';
    var fontSize = 12;
    
    var style_count = e.value;
    
    if(style_count == "hour"){
        paging_holder.load_hour_num = 0;
        data_line_x = paging_holder.data_hour_x;
        data_line_y = paging_holder.data_hour_y;
        paging_holder.is_load_hour = true;
        paging_holder.is_load_another = false;
        setChartForHour();
        //load_data_hour();
    }else if(style_count == "day"){
        data_line_x = paging_holder.data_day_x;
        data_line_y = paging_holder.data_day_y;
        paging_holder.is_load_hour = false;
        paging_holder.is_load_another = true;
        intervals = 5;
        width_line = 2;
        color_line = '#ff7f50';
        fontSize = 12;
    }else if(style_count == "week"){
        data_line_x = paging_holder.data_week_x;
        data_line_y = paging_holder.data_week_y;
        paging_holder.is_load_hour = false;
        paging_holder.is_load_another = true;
        intervals = 143;
        width_line = 0.5;
        color_line = 'red';
        fontSize = 12;
        //load_data();
    }else if(style_count == "month"){
        data_line_x = paging_holder.data_month_x;
        data_line_y = paging_holder.data_month_y;
        paging_holder.is_load_hour = false;
        paging_holder.is_load_another = true;
        intervals = 143;
        width_line = 0.5;
        color_line = 'red';
        fontSize = 9;
        //load_data();
    }
    if(style_count != "hour"){
        myChart.setOption({
            tooltip : {
                show:false,
                trigger: 'axis'
            },
            legend: {
                data:['总连接数'],
                orient:'vertical',
                x:'right'
            },
            
            toolbox: {
                show : false,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar']},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            calculable : true,
            xAxis : [{
                name: '时间',
                type : 'category',
                axisTick: {
                    show: false,
                    interval : intervals
                },
                axisLabel: {
                    show: true,
                    interval : intervals,
                    textStyle: {
                        fontSize: fontSize
                    }
                },
                data: data_line_x
            }],
            yAxis : [{
                name: '总连接数',
                type : 'value',
                splitArea : {show : true}
            }],
            series : [{
                name:'总连接数',
                type:'line',
                symbol:'none',
                itemStyle: {
                    normal: {
                        lineStyle: {
                            width:width_line,
                            color: color_line
                        }
                    }
                },
                data:data_line_y
            }]
        });
    } 
}

//仅加载最近一小时会话连接曲线
function setChartForHour(){
    // if(paging_holder.load_hour_num == 1){
        myChart = echarts.init(document.getElementById('chart_recent'));
    
        hour_option = {
            tooltip : {
                show:false,
                trigger: 'axis'
            },
            legend: {
                data:['总连接数'],
                orient:'vertical',
                x:'right'
            },
            toolbox: {
                show : false,
                feature : {
                    mark : {show: true},
                    dataView : {show: true, readOnly: false},
                    magicType : {show: true, type: ['line', 'bar']},
                    restore : {show: true},
                    saveAsImage : {show: true}
                }
            },
            calculable : true,
            xAxis : [{
                name: '时间',
                type : 'category',
                axisTick: {
                    show: false,
                    interval : 4
                },
                axisLabel: {
                    show: true,
                    interval : 4
                },
                data: paging_holder.data_hour_x
                
            }],
            yAxis : [{
                name: '总连接数',
                type : 'value',
                splitArea : {show : true}
            }],
            series : [{
                name:'总连接数',
                type:'line',
                symbol:'none',
                //xAxisIndex: 1,
                //yAxisIndex: 1,
                data:paging_holder.data_hour_y
            }]
        };
        myChart.setOption(hour_option,true);
    // }
}

//判断请求的数据的每个点的时间是否在当前一个小时以内
function is_include_recentHour(item,recent_hour){
    var result = false;
    for(var i=0;i<recent_hour.length;i++){
        if(item == recent_hour[i]){
            result = true;
        }
    }
    return result;
}