$(document).ready(function(){
    message_manager.render();

    init_page_size();
   
    
    // logs_rt_events.update_info( true ); //在init_page_size请求回来之后调用
    update_info_handler = window.setInterval( "logs_rt_events.update_info( true )", update_info_interval );
});


var ass_url = "/cgi-bin/logs_real_time_events.cgi";
var update_info_interval = 10000;
var message_box_config = {
    url: ass_url,
    check_in_id: "logs_event_mesg_box",
    self_class:"logs_event_mesg_box-class"
}
var message_manager = new MessageManager( message_box_config );

var logs_rt_events_render = {
    result:{
        render:function(default_rendered_text,data_item){
            return "成功";
        }
    },
    event_name: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;
            if ( !default_rendered_text ) {
                return "";
            }
            if ( default_rendered_text.split( "" ).length > 15 ) {
                rendered_text = '<span class="short-mesg" title="' + default_rendered_text + '">' + 
                                default_rendered_text.substring( 0, 15 ) + '...</span>';
            }
            return rendered_text;
        }
    },
    chinese_classification: {
        render: function( default_rendered_text, data_item ) {
            var level = "";
            if( data_item.priority == "高" || data_item.priority == "1" ) {
                level = "h-level";
            } else if ( data_item.priority == "中" || data_item.priority == "2" ) {
                level = "m-level";
            }
            else if ( data_item.priority == "低" || data_item.priority == "3" ) {
                level = "l-level";
            }

            return '<span class="classification-text ' + level + '" onclick="show_suggestion(\'' + data_item.sid+ '\')">' + default_rendered_text + '<img src="/images/suggestion.png" class="suggestion-img" alt="点击查看建议" title="点击查看建议"/></span>';
           
        }
    },
    priority: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( default_rendered_text == 1 ) {
                rendered_text = '<span class="h-level">高</span>';
            } else if ( default_rendered_text == 2 ) {
                rendered_text = '<span class="m-level">中</span>';
            } else if ( default_rendered_text == 3 ) {
                rendered_text = '<span class="l-level">低</span>';
            } else if ( default_rendered_text == 4 ) {
                rendered_text = '<span class="l-level">信息</span>';
            } else {
                rendered_text = "未知";
            }

            return rendered_text;
        }
    },
    // time_start: {
    //     render: function( default_rendered_text, data_item ) {
    //         var day_time_regx = /(\d{2}:\d{2}:\d{2})/;
    //         var time_start = data_item.time_start;
    //         var time_end = data_item.time_end;
    //         if ( data_item.time_start.match( day_time_regx) ) {
    //             time_start = RegExp.$1;
    //         }
    //         if ( data_item.time_end.match( day_time_regx) ) {
    //             time_end = RegExp.$1;
    //         }
    //         if( data_item.merge_type == 1 || data_item.merge_type == 2 || data_item.merge_type == 3 ) {
    //             // 进行时间提取
    //             return time_start + " - " + time_end;
    //         } else {
    //             return time_start;
    //         }
    //     }
    // },
    sip: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( data_item.merge_type == 1 ) {
                var merged_count =  '<span class="merged_count" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">(' + data_item.merge_count +
                                    ')</span>';
                rendered_text = '<span class="dip-merged">已合并 ' + merged_count +  '</span>';
                // rendered_text = '<span class="sip-merged" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">已合并</span>';
            }
            else if(data_item.merge_type == 3 ){
                var merged_count =  '<span class="merged_count" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">(' + data_item.merge_count +
                                    ')</span>';
                rendered_text = '<span class="dip-merged">已合并 ' + merged_count +  '</span>';
            }
             else {
                 if ( data_item.sport > 0 ) {
                    if(data_item.src_user == ""){
                         rendered_text = '<span class="sip">' + default_rendered_text + '</span>: '+ data_item.sport;
                    }else{
                         rendered_text = '<span class="sip">' + default_rendered_text + '</span>: ' + data_item.sport +"("+data_item.src_user +")";
                    }
                }
                 else if(data_item.sport == 0){
            		if(data_item.src_user !== ""){
                          rendered_text = '<span class="sip">' + default_rendered_text + '</span> '  +"("+data_item.src_user +")";
                    }
            }
            }

            return rendered_text;
        }
    },
    dip: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( data_item.merge_type == 2 ) {
                var merged_count =  '<span class="merged_count" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">(' + data_item.merge_count +
                                    ')</span>';
                rendered_text = '<span class="dip-merged">已合并 ' + merged_count +  '</span>';
                // rendered_text = '<span class="dip-merged" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">已合并</span>';
            } 
             else if(data_item.merge_type == 3 ){
                var merged_count =  '<span class="merged_count" onclick="show_ip_details(\'' + data_item.merge_eid + '\',\''+data_item.sid+'\')">(' + data_item.merge_count +
                                    ')</span>';
                rendered_text = '<span class="dip-merged">已合并 ' + merged_count +  '</span>';
            }

            else {
                if ( data_item.dport > 0 ) {
                    if(data_item.dst_user == ""){
                         rendered_text = '<span class="dip">' + default_rendered_text + '</span>: '+data_item.dport;
                    }else{
                         rendered_text = '<span class="dip">' + default_rendered_text + '</span>: ' + data_item.dport +"("+data_item.dst_user +")";
                    }
            }
            else if(data_item.dport == 0){
            	if(data_item.dst_user !== ""){
                          rendered_text = '<span class="dip">' + default_rendered_text + '</span> '  +"("+data_item.dst_user +")";
                    }
            }
            }

            return rendered_text;
        }
    },
    merge_eid: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( default_rendered_text == "1" ) { // 按sip合并
                rendered_text = "源IP合并";
            } else if ( default_rendered_text == "2" ) { // 按dip合并
                rendered_text = "目标IP合并";
            } else if ( default_rendered_text == "3" ) { // 按sid、dip合并
                rendered_text = "源、目标IP合并";
            } else {
                rendered_text = "不合并";
            }

            return rendered_text;
        }
    },
    response_type: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = default_rendered_text;

            if ( default_rendered_text == "log" ) {
                rendered_text = "默认(日志记录)";
            } else {
                rendered_text = "未知";
            }

            return rendered_text;
        }
    },
    r_action: {
        render: function( default_rendered_text, data_item ) {
            var rendered_text = "允许";
            if ( /drop|reject/.test(default_rendered_text) ) {
                rendered_text = "阻断";
            }
            return rendered_text;
        }
    }
};
var logs_rt_events_config_render = {
	result: {
		render: function(item,data) {
            console.log(data);
			if(data) {
				return "成功";
			}
		}
	}
}

var logs_rt_events_config = {
    url: ass_url,
    check_in_id: "logs_rt_events",
    panel_name: "logs_rt_events",
    page_size: 15,
    is_default_search: true,
	render: logs_rt_events_config_render,
    default_search_config: {
        input_tip: "输入入侵事件关键字以查询...",
        title: "入侵事件关键字"
    },
    is_paging_tools: false,
    is_load_all_data: true,
    render: logs_rt_events_render,
     event_handler: {
        before_load_data: function(list_obj) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
           
        },
        after_load_data: function(list_obj, response) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        },
    },
    panel_header: [{
        enable: true,
        type: "text",
        title: "发生时间",
        name: "time_start",
        column_cls: "align-center",
        td_class: "align-center",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "入侵事件名称",
        name: "event_name",
        column_cls: "align-center",
        width: "15%"
    }, {
        enable: true,
        type: "text",
        title: "入侵类型",
        column_cls: "align-center",
        name: "chinese_classification",
        td_class: "align-center",
        width: "12%"
    }, {
        enable: true,
        type: "text",
        title: "危险级别",
        column_cls: "align-center",
        name: "priority",
        td_class: "align-center",
        width: "6%"
    }, {
        enable: true,
        type: "text",
        title: "源",
        name: "sip",
        column_cls: "align-center",
        //td_class: "align-center",
        width: "14%"
    }, {
        enable: true,
        type: "text",
        title: "目标",
        name: "dip",
        column_cls: "align-center",
        //td_class: "align-center",
        width: "14%"
    }, {
        enable: true,
        type: "text",
        title: "合并类型",
        name: "merge_eid",
        column_cls: "align-center",
        td_class: "align-center",
        width: "8%"
    }, {
        enable: true,
        type: "text",
        title: "处理动作",
        name: "r_action",
        column_cls: "align-center",
        td_class: "align-center",
        width: "8%"
    }, {
		enable: true,
		type: "text",
		title: "结果",
		name: "result",
		width: "8%",
        td_class: "align-center",
		column_cls: "align-center"	
	}],
    top_widgets: [{
        enable: true,
        type: "checkbox",
        id: "stop_refresh_data",
        name: "stop_refresh_data",
        "label": "停止刷新",
        functions: {
            onclick: "stop_refresh_data(this)"
        }
    }],
    extend_search: [{
        enable: true,
        type: "text",
        id: "page_size",
        name: "page_size",
        title: "最大事件显示条数",
        value: 15,
        check: {
            type: 'text',
            required: '1',
            check: 'int|',
            ass_check: function( check ){
                var val = $( "#page_size" ).val();
                if( val > 1000 || val < 10 ) {
                    return "输入10-1000之间的整数";
                }
            }
        }
    }, {
        enable: true,
        type: "image_button",
        id: "save_parameter",
        name: "save_parameter",
        button_text: "保存参数",
        functions: {
            onclick: "save_parameter_func(this);"
        }
    }, {
        enable: true,
        type: "select",
        id: "event_level",
        name: "event_level",
        title: "窗口",
        multiple: false,
        options: [{
            value: "1",
            text: "高"
        }, {
            value: "2",
            text: "中"
        }, {
            value: "3",
            text: "低"
        }, {
            value: "4",
            text: "信息"
        }, {
            value: "all",
            text: "全部事件",
            selected: true
        }]
    }]
};

var logs_rt_details_config = {
    url: ass_url,
    check_in_id: "logs_rt_details",
    panel_name: "logs_rt_details",
    page_size: 10,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    is_default_search: false,
    is_load_all_data: true,
    is_panel_closable: true,
    panel_header: [{
        enable: true,
        type: "text",
        title: "发生时间",
        name: "datetime",
        column_cls: "align-center",
        width: "20%"
    },{
        enable: true,
        type: "text",
        title: "入侵类型",
        name: "chinese_classification",
        column_cls: "align-center",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "源IP地址",
        name: "sip",
        column_cls: "align-center",
        width: "28%"
    }, {
        enable: true,
        type: "text",
        title: "源端口",
        name: "sport",
        column_cls: "align-center",
        width: "12%"
    }, {
        enable: true,
        type: "text",
        title: "目标IP地址",
        name: "dip",
        column_cls: "align-center",
        width: "28%"
    }, {
        enable: true,
        type: "text",
        title: "目的端口",
        name: "dport",
        column_cls: "align-center",
        width: "12%"
    }]
}

var logs_rt_events = new PagingHolder( logs_rt_events_config );
var logs_rt_details = new PagingHolder( logs_rt_details_config );

function init_page_size() {
    var sending_data = {
        ACTION: "load_page_size"
    };
    function ondatareceived( response ) {
        logs_rt_events_config.page_size = response.page_size;
        logs_rt_events_config.extend_search[0].value = response.page_size;

        logs_rt_events.render();
        logs_rt_events.set_ass_message_manager( message_manager );
        
        logs_rt_details.render();
        logs_rt_details.hide();
        $( "#page_size" ).val( response.page_size );
        logs_rt_events.update_info( true );
        window.setInterval( logs_rt_events.update_info( true ) );
    }
    logs_rt_events.request_for_json( sending_data, ondatareceived );
}

function save_parameter_func( element ) {
    logs_rt_events.update_info( true );
}

var update_info_handler; 


function stop_refresh_data( element ) {
    if ( !element.checked ) {
        update_info_handler = window.setInterval( "logs_rt_events.update_info( true )", update_info_interval );
    } else {
        window.clearInterval( update_info_handler );
    }
}

function show_ip_details( eid,sid ) {
    logs_rt_details.extend_sending_data = {
        eid: eid,
        sid:sid
    }
    logs_rt_details.update_info( true );
    logs_rt_details.show();
}

function show_suggestion( type ) {
    var sending_data = {
        ACTION: 'query_suggestion',
        type: type
    }

    function ondatareceived(data) {

        if (data == null ) {
            code = '没有具体的详细信息';
        }else{
            var suggestionArray = data.mesg;
            var code = '<TABLE>';
            for(var i = 0; i<suggestionArray.length; i++){
            	
                var suggestionList = (suggestionArray[i]); 
                code = code + ('<tr class="tr_css"><td class="td_css" style="width:100px;">'+suggestionList[0]+'</td> <td class="td_css" style="">'+suggestionList[1]+'</td></tr>');
            }         
            code = code + '</TABLE>';
            
        }

        message_manager.show_details_message( code , true);
        $("#details_message_box_title_for_my_message_box").text("入侵类型详细信息");
        $("#details_message_box_button_for_my_message_box").parent().attr("id","my_button");
    }

    logs_rt_events.request_for_json(sending_data, ondatareceived);

}
