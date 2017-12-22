$(document).ready(function(){
    paging_holder = new PagingHolder("/cgi-bin/logs_event_search.cgi", "logs_event_search", logs_event_search_render, check_obj );

    /*绑定时间输入*/
    ESONCalendar.bind("time_start");
    ESONCalendar.bind("time_end");

    $( "#PAGESIZE" ).keydown(function( event ){
        page_size_input_control( document.getElementById("PAGESIZE"), event );
    });

});

var paging_holder;

var logs_event_search_render = {
    'classification':{
        render: function( text, data_item ) {
            var level = "low-risk";
            if( data_item.priority == "高" || data_item.priority == "1" ) {
                level = "high-risk";
            } else if ( data_item.priority == "中" || data_item.priority == "2" || data_item.priority == "3" ) {
                level = "medium-risk"
            }
            return '<span class="classification-text ' + level + '" onclick="show_suggestion(\'' + text + '\')">' + text + '<img src="/images/suggestion.png" class="suggestion-img" alt="点击查看建议" title="点击查看建议"/></span>';
        }
    },
    'priority': {
        render: function( text, data_item ) {
            var level = "low-risk";
            if( data_item.priority == "高" || data_item.priority == "1" ) {
                level = "high-risk";
            } else if ( data_item.priority == "中" || data_item.priority == "2" || data_item.priority == "3"  ) {
                level = "medium-risk"
            }
            return '<span class="' + level + '">' + text + '</span>';
        }
    },
    'time_start': {
        render: function( text, data_item ) {
            var rendered_text = text;
            var time_start = data_item.time_start.split( " " );
            var time_end = data_item.time_end.split( " " );
            if( data_item.time_start == data_item.time_end ) {
                rendered_text = time_start[0] + "&nbsp;&nbsp;&nbsp;" + time_start[1];
            } else {
                rendered_text = time_start[0] + "&nbsp;&nbsp;&nbsp;" + time_start[1] + "-" + time_end[1];
            }
            return rendered_text;
        }
    },
    'sip': {
        render: function( text, data_item ) {
            var rendered_text = text;
            if ( data_item.merge_type == "2" && ( text === null || text === undefined || text === '' ) ) {
                rendered_text = '<span class="sip-merged">已合并</span>';
            }
            return rendered_text;
        }
    },
    'dip': {
        render: function( text, data_item ) {
            var rendered_text = text;
            if( data_item.merge_type == "1" && ( text === null || text === undefined || text === '' ) ) {
                rendered_text = '<span class="dip-merged">已合并</span>';
            } 
            return rendered_text;
        }
    }
};

var check_obj = {
   'form_name':'LOGS_EVENT_SEARCH_FORM',
   'option':{
        'PAGESIZE':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var PAGESIZE = eve._getCURElementsByName("PAGESIZE","input","LOGS_EVENT_SEARCH_FORM")[0].value;
                if (PAGESIZE < 15 || PAGESIZE > 100 ){
                    msg = "请填写15-100的整数";
                }
                return msg;
            }
        }
    }
}

function page_size_input_control(element,event) {
    /*8：退格键、46：delete、37-40： 方向键
    **48-57：主键盘区的数字、96-105：小键盘区的数字
    **110、190：小键盘区和主键盘区的小数
    **189、109：小键盘区和主键盘区的负号
    **enter:13
    **/
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode||event.keyCode; //IE、FF下获取键盘码
    if (cod == 13){
        //do nothing
    } else {
        if(cod!=8 && cod != 46 && !((cod >= 48 && cod <= 57) || (cod >= 96 && cod <= 105) || (cod >= 37 && cod <= 40))){
            notValue(event);
        } 
    }
    function notValue(event){
        event.preventDefault ? event.preventDefault() : event.returnValue=false;
    }
}

function show_suggestion( type ) {
    var sending_data = {
        ACTION: 'query_suggestion',
        type: type
    }

    function ondatareceived(data) {
        show_popup_mesg( data.mesg )
    }

    paging_holder.request_for_json(sending_data, ondatareceived);

}

function save_parameter_config () {
    if( !paging_holder.check_input_data() ) {
        show_popup_alert_mesg("请正确填写表单");
        return;
    }
    var sending_data = {
        ACTION: 'save_data'
    };
    var values = $( ".parameter_config_commit" );
    values.each(function() {
        var values_handle = this;
        sending_data[$(values_handle).attr("name")] = $(values_handle).val();
    });

    function ondatareceived(data) {
        if( opt_is_succeeded( data.status ) ) {
            show_popup_mesg("保存成功");
            paging_holder.update_info();
        }
    }

    paging_holder.request_for_json(sending_data, ondatareceived);
}

function delete_all_logs( element ) {
    var sending_data = {
        ACTION: 'delete_all'
    };

    function ondatareceived(data) {
        if( opt_is_succeeded( data.status ) ) {
            alert("删除成功");
            paging_holder.update_info();
        } else {
            alert("操作失败，请重试")
        }
    }

    paging_holder.request_for_json(sending_data, ondatareceived);
}

function opt_is_succeeded( status ) {
    if( status == '0' ) {
        return true;
    } else {
        return false;
    }
}