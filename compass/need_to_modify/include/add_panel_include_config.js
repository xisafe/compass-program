// 用于含有'配置'面板的页面
// author：chenshisong
// data: 2017.9.6


//点击按钮弹出jstree面板（基于list_panel）
//panel：面板名字
//action：得到jstree_tree发送的请求
//input_id ；jstree勾选后填入数据后写进input框的id
//img ：第三层图片的地址{有三个默认值：user,app,file}
//type:如果需要自定义图片，并给条目设置type，则需要重新定义
//例：load_jstree_panel(SrcUserlist_panel,'load_userlist','SrcUserlist','user')
//例：load_jstree_panel(SrcUserlist_panel,'load_userlist','SrcUserlist','aaa.png','aaa') 自定义图片
function load_jstree_panel(panel,action,input_id,img,type){

    var sending_data = {
        ACTION: action
    };

    function ondatareceived(data) {
        data = change_jstree_data(input_id,data);
        jstree_render(panel,data,img,type);
        panel.show();
    }
    do_request(sending_data, ondatareceived);
}

//点击配置按钮弹出配置面板（list_panel）
//panel:面板的名字
//id:需要写进面板中的text框的id
function show_config_panel(panel,id) {
    //修改部分
    panel.update_info(true);
    var text_val = $('#'+id).val();
    if (text_val != '') {
        var text_arr = /\,/.test(text_val) ? text_val.split(',') : text_val.split('，');
        text_arr = text_arr.map(function(ele, index) {
            return ele.trim();
        });
        $('#'+panel.panel_body_id+' tr').each(function(index, el) {
        if ($.inArray($(this).children('td').eq(1).text(),text_arr) != -1) {
            $(this).children('td').eq(0).children('input').attr('checked',true);
            if ($(this).children('td').eq(1).text() == 'any') {
                $(this).siblings().each(function(index, el) {
                    $(this).children('td').eq(0).children('input').attr('disabled',true);  
                })
            }
            for (var i = 0; i < panel.detail_data.length; i++) {
                    panel.detail_data[index].checked = true;
                }
            } 
        });
    }
    panel.show();
}

function show_config_panel_area(panel,id) {
    //修改部分
    panel.update_info(true);
    var text_val = $('#'+id).val();
    if (text_val != '') {
        var text_arr = text_val.split('\n');
        text_arr = text_arr.map(function(ele, index) {
            return ele.trim();
        });
        $('#'+panel.panel_body_id+' tr').each(function(index, el) {
        if ($.inArray($(this).children('td').eq(1).text(),text_arr) != -1) {
            $(this).children('td').eq(0).children('input').attr('checked',true);
            if ($(this).children('td').eq(1).text() == 'any') {
                $(this).siblings().each(function(index, el) {
                    $(this).children('td').eq(0).children('input').attr('disabled',true);  
                })
            }
            for (var i = 0; i < panel.detail_data.length; i++) {
                    panel.detail_data[index].checked = true;
                }
            } 
        });
    }
    panel.show();
}
// 用于将jstree选中的项目写进input框中
// panel:放jstree的面板
// input_id：数据写入的input的id
// type：jstree中要选择的类型，同load_jstree_panel中的img参数
// id_id: 如果需要将选择项的id传入，则传入该值，隐藏的用来放置id的input的id
// 例：write_checked_for_jstree(Appid_panel,'Appname','app','Appid')
function write_checked_for_jstree(panel,input_id,type,id_id){
    var jstree_id = 'jstree_' + panel.panel_name ;
    var checked_nodes = $('#'+jstree_id).jstree().get_checked(true);
    var checked_str = '',checked_id_str = '',temp = 0;
    for (var i = 0; i < checked_nodes.length; i++) {
        if (checked_nodes[i].type == type) {
            var separator = temp == 0 ? '' : ', ';
            temp++ ;
            checked_str += separator ;
            checked_str += checked_nodes[i].text.replace(/\n/,'') ;
            if (id_id) {
                // var id_separator = i == 0 ? '':',';
                // checked_id_str += id_separator ;
                checked_id_str += separator;
                checked_id_str += checked_nodes[i].id ;
            }
        }
    }
    if (checked_str == '') {
        message_manager.show_popup_error_mesg("没有明确的选项！");
        return;
    }
    $('#'+input_id).val(checked_str).attr('title',checked_str);
    id_id ? $('#'+id_id).val(checked_id_str) : true;
    panel.hide();
}
// 用于将list_panel选中的项目写进input框中
// panel:放jstree的面板
// input_id：数据写入的input的id
// id_id: 如果需要将选择项的id传入，则传入该值，隐藏的用来放置id的input的id
// 例：write_checked_for_list(SrcIPGroup_panel,'SrcIPGroup')
function write_checked_for_list(panel, textId,id_id,idReal) {
    var checked_items = panel.get_checked_items();
    var checked_str = "",checked_id_str='';
    if (checked_items.length == 0) {
        message_manager.show_popup_error_mesg('请至少选择其中一项！');
        return;
    } else {
        for (var i = 0; i < checked_items.length; i++) {
            var separator = i == 0 ? '' : ', ';
            checked_str += separator ;
            checked_str += checked_items[i].name ;
            if (id_id) {
                checked_id_str += separator ;
                if (idReal) {
                    checked_id_str += checked_items[i].idReal ;
                }else{
                    checked_id_str += checked_items[i].id ;
                }
            }
        }
    }
    $("#" + textId).val(checked_str).attr('title',checked_str);
    id_id ? $('#'+id_id).val(checked_id_str) : true;
    panel.hide();
}
// 根据select的选择显示不同的选填项
// val:选择的select的value
// id:select的id
// select_obj：所有需要操控显示隐藏的对象
// select_obj={
// 	select的id：{
// 		选择的select的value：'当选择该value时需要显示的组件的id'
// 	},
// 	...
// }
// 例：
// var select_obj = {
//         'ip_or_user': {
//             'sour_ip': '#SrcIPGroup,#SrcIPGroup_btn',
//             'sour_user': '#SrcUserlist,#SrcUserlist_btn',
//             'sour_netip': '#sour_netip_text',
//             'sour_mac': '#sour_mac_text'
//         },
//         'dest_ipgroup': {
//             'dest_ip': '#DestIPGroup,#ipGroup',
//             'dest_group': '#dest_ip_text'
//         }
//     }

function select_and_show(val,id,select_obj){
    for (var k in select_obj[id]) {
        if (k == val) {
            $(select_obj[id][k]).show().removeAttr('disabled').parent().show();
        } else {
            $(select_obj[id][k]).hide().attr('disabled', 'disabled').parent().hide();
        }
    }
}
// 用于处理jstree的数据，读取input框中内容，在jstree中显示
// 仅支持{chilren:[children:{text:'aa'}]}和[children:{text:'aa'}];
// input_id ：input的id
// data ： 后台传回来的jstree
function change_jstree_data(input_id,data){
    var input_val = $('#'+input_id).val();
    if (input_val != '') {
        var input_arr = /\,/.test(input_val) ? input_val.split(',') : input_val.split('，');
        input_arr = input_arr.map(function(ele, index) {
            return ele.trim();
        });
        Array.isArray(data) ? change_arr() : change_obj() ;

        function change_obj(){
            data.state = {opened : true} ;
            for (var i = 0; i < data.children.length; i++) {
                for (var j = 0; j < data.children[i].children.length; j++) {
                    var data_text = data.children[i].children[j].text.replace(/\n/,'');
                    if ($.inArray(data_text,input_arr) != -1) {
                        data.children[i].children[j].state = { 'selected' : true} ;
                    }
                }
            }
        }
        function change_arr(){
            for (var i = 0; i < data.length; i++) {
                for (var j = 0; j < data[i].children.length; j++) {
                    var data_text = data[i].children[j].text.replace(/\n|\ /,'');
                    if ($.inArray(data_text,input_arr) != -1) {
                        data[i].children[j].state = { 'selected' : true} 
                    }
                }
            }
        }
    }
    Array.isArray(data) ? true : data.state.opened=true ;
    return data;
}



//AJAX异步请求数据
function do_request(sending_data, ondatareceived, error) {
    if (error && typeof error === "function") {
        var errorFun = error;
    } else {
        errorFun = function(request) {
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        };
    }
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: true,
        error: errorFun,
        success: ondatareceived
    });
}

//渲染JS树
function jstree_render(panel,data,img,type) {
    var jstree_id = 'jstree_' + panel.panel_name ;
    if ($('#'+jstree_id)) {$('#'+jstree_id).remove()};
    var jstree_div = '<div id="'+jstree_id+'"></div>';
    var panel_id = panel.panel_id;
    $('#'+panel_id + ' .container-main-body').append(jstree_div).css('min-height', '200px').children('.rule-list').remove();
    data = Array.isArray(data) ? data : [data] ;
    var i_d_a = "../images/";
    icon = {'user':i_d_a+"login_user.png",'app':i_d_a+'application.png','file':i_d_a+'applications-blue.png'}[img] || i_d_a+img;
    var jstree_obj = {
        "plugins": [
            "checkbox","types", "wholerow"
        ],
        "core": {
            "themes": {
                "stripes": true
            },
            "data": data
        },
        "types":{},
        "checkbox": {
            "keep_selected_style": false
        },
    }
    type ? jstree_obj.types[type] = {'icon':icon} : jstree_obj.types[img] = {'icon':icon}
    $('#'+jstree_id).jstree(jstree_obj);
}
