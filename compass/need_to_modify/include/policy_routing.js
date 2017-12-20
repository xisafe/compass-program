$(document).ready(function(){
    
    Appid_panel.render();
    (function (){
        var img = $('<img title="重置" src="/images/reconnect.png">');
        img.css({
            cursor: "pointer",
            position: "relative",
            top: "3px",
            left: "10px"
        });
        img.on("click", function() {
            $("#for_appJstree-policyRouting").jstree().deselect_all();
        })
        $("#list_panel_id_for_Appid_panel .list-panel-title").find("span").after(img);
    })();
    Appid_panel.hide();
    // toggle_policy(document.getElementById("dst_dev"));
});


var Appid_config = {
    url: '/cgi-bin/policy_routing.cgi', // ***必填***，控制数据在哪里加载 
    check_in_id: "Appid_panel",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "Appid_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置应用",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    // render: Appid_render,      //===可选===，渲染每列数据 
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": false,            //用户控制表头是否显示
            "type": "checkbox",           //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox",         //用户装载数据之用
            "class": "",                //元素的class
            "td_class": "",             //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": {              //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": false,
            "type": "name",
            "title": "应用ID号",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [
            {
                enable: true,
                type: "image_button",
                class: "",
                style: "margin-top: 5px;margin-bottom: 5px;",
                button_text: "确定",
                functions: {
                    onclick: "write_app();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "Appid_panel.hide();"
                }
            }
        ]
    }
}
var Appid_panel = new PagingHolder(Appid_config);










function show_error_mesg(mesg) {
    alert(mesg);
}





//获取应用配置面板数据
function load_app() {
    Appid_panel.show();
}
//将用户组配置内容写入文本框
function write_userlist(inputId,jstreeId,panelName) {
    var nodes = $(jstreeId).jstree().get_checked(true);
    console.log( nodes );
    var length = nodes.length;
    var array = new Array();
    var str = "";

    for(var i = 0; i < length; i++) {
        if ( nodes[i].type == "user" ) {
            array.push( nodes[i].text );
        }
    }
    if(array.length == 0) {
        message_manager.show_popup_error_mesg("没有明确的用户！");
        return;
    }
    
    for(var i = 0; i < array.length-1; i++) {
        str += array[i] + "，";
    }
    str += array[array.length-1];
    
    $("#"+inputId).val(str);
    $("#"+inputId+"Id").val(str.replace(/，/g,"&"));
    // writeFrame(document.getElementById("SrcUserlist"), array);
    panelName.hide();
    
}

//将应用配置内容写入文本框
function write_app() {
    

    var nodes = $("#for_appJstree-policyRouting").jstree().get_checked(true);
    var appname = document.getElementById("Appname");
    var length = nodes.length;
    var array = new Array();
    var idArray = new Array();
    var str = "";
    var idStr = "";

    for(var i = 0; i < length; i++) {
        if ( nodes[i].type == "app" ) {
            array.push( nodes[i].text );
            idArray.push( nodes[i].id );
        }
    }
    if(array.length == 0) {
        // message_manager.show_popup_error_mesg("请选择至少一项应用！");
        // return;
        $(appname).val('');
        $("#AppnameList").val('');
        Appid_panel.hide();
        return;
    }
    
    for(var i = 0; i < array.length-1; i++) {
        str += array[i] + ",";
    }
    for(var i = 0; i < idArray.length-1; i++) {
        idStr += idArray[i] + ":";
    } 
    str += array[array.length-1];
    idStr += idArray[idArray.length-1];
    $(appname).val(str);
    $("#AppnameList").val(idStr);
    // writeFrame(appname, array);
    Appid_panel.hide();
    
}