/*
 * 描述: 测试添加模板和列表模板类
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.09.23 WangLin创建
 */

/*
 * 注释<1>：此文档的“配置对象”指new PagingHolder时传入的对象
 */

$( document ).ready(function() {


	
    /* 渲染面板 */
     message_manager.render();
     lib_panel.render();
     lib_panel.hide();
     lib_panel.update_info(true);
     

    DestIPGroup_panel.render();
    DestIPGroup_panel.hide();
    DestIPGroup_panel.update_info(true);

    (function() {
        //控制应用面板是否显示
        var control = parseInt( $("#apply-control").val() );
        if(control) {
            message_manager.show_apply_mesg();
        }
        
        //为form表单绑定检测方法
        var object = {
            "form_name": "setbotnet-form",
            option: {
                'name': {
                    'type': 'text',
                    'required': '1',
                    'check': 'name|',
                    'ass_check': function(eve){                        
                    }
                },
                'description': {
                    'type': 'textarea',
                    'required': '0',
                    'check': 'note|',
                    'ass_check': function(eve){                       
                    }
                },
                'ipGroup': {
                    'type': 'select-one',
                    'required': '1',
                    'check': 'other|',
                    'other_reg': '/.*/'
                },
                'webRule': {
                    'type': 'textarea',
                    'required': '1',
                    'check': 'other|',
                    'other_reg': '/.*/'
                }
            }
        }
        var check = new ChinArk_forms();
        check._main(object);
     })();
 

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/set_botnet.cgi";

var message_box_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_box",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "mesg_box",         /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

// var add_panel_config = {
//     url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
//     check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
//     panel_name: "add_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
//     rule_title: "WEB应用防护",         /* ==*可选*==，默认是"规则" */
//     is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
//     is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
//     is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
//     modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
//         modal_box_size: "m",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
//         modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
//     },
//     event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
//         before_load_data: function( add_obj, data_item ) {
                     
// 					   read_data();
//         },
//         after_load_data: function( add_obj, data_item ) {
//             /*
//              * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
//              *
//              * 参数： -- add_obj   ==可选==，添加面板实例
//              *         -- data_item ==可选，要加载进添加面板的整个数据项
//              *
//              * 返回：无
//              */
//         },
//         before_cancel_edit: function( add_obj ) {
//             /*
//              * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
//              *    在做这些默认的操作之“前”调用此函数
//              *
//              * 参数： -- add_obj   ==可选==，添加面板实例
//              *
//              * 返回：无
//              */
//         },
//         after_cancel_edit: function( add_obj ) {
//             /*
//              * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
//              *    在做这些默认的操作之“后”调用此函数
//              *
//              * 参数： -- add_obj   ==可选==，添加面板实例
//              *
//              * 返回：无
//              */
//         },
//         before_save_data: function( add_obj, sending_data ) {
//             /*
//              * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
//              *    在做提交数据之“前”会调用此函数
//              *
//              * 参数： -- add_obj       ==可选==，添加面板实例
//              *        -- sending_data  ==可选==, 要向服务器提交的数据，
//              *           用户可以通过 sending_data.xxx = xxx 添加向服务器提交的数据
//              * 返回：true/false
//              *       -- 返回true，或者不返回数据，数据会如实提交
//              *       -- 返回false，会阻止数据向服务器其提交
//              */
//         },
//         after_save_data: function( add_obj, received_data ) {
//             /*
//              * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
//              *    在做提交数据之“后”并且服务器响应之“后”会调用此函数
//              *
//              * 参数： -- add_obj       ==可选==，添加面板实例，可以调用add_obj.show_error_mesg( mesg )
//              *           或者add_obj.show_note_mesg( mesg )等函数反馈信息给用户
//              *        -- received_data ==可选==, 服务器响应的数据，
//              *           可以在后台配置要传递的数据，并在此处访问
//              * 返回：无
//              */
//         }
//     },
//     items_list: [                   /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
//         {
//             title: "名称：",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
//             id: "name_tr",          /* ==可选==，整行的id */
//             name: "",               /* ==可选==，整行的name */
//             class: "",              /* ==可选==，整行的class */
//             functions: {            /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
//                 // onmouseover: "alert('hover on name line');",
//                 // onclick: "alert('click on name line');",
//             },
//             sub_items: [            /* **必填**，确定此行有哪些字段，不填什么都没有 */
//                 {
//                     enable: true,           /* **必填**，如果为不填或者为false,就不创建 */
//                     type: "text",           /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
//                                                          radio,textarea,label,items_group
//                                              */
//                     name: "name",           /* **必填**，字段的名字 */
//                     value: "",              /* ==可选==，字段默认值 */
//                     functions: {            /* ==可选==，DOM标准事件都可生效 */
//                     },
//                     check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
//                         type: "text",       /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
//                         required: 1,        /* **必填**，1表示必填，0表示字段可为空 */
//                         check: 'name|',     /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
//                         ass_check: function( check ) {
//                             /*
//                              * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
//                              *
//                              * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
//                              *
//                              * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
//                              */
//                         }
//                     }
//                 }
//             ]
//         }, {
//             title: "描述：",
//             sub_items: [
//                 {
//                     enable: true,
//                     type: "text",
//                     name: "description",
//                     value: "",
//                     functions: {
//                     },
//                     check: {
//                         type: "text",
//                         required: 1,
//                         check: 'note|',
//                         ass_check: function( check ) {

//                         }
//                     }
//                 }
//             ]
//         }, {
//             title: "IP组：",
//             sub_items: [
//                 {
//                     enable: true,
//                     type: "select",
// 					id:"ipGroup",
//                     name: "ipGroup",
// 					check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
//                         type:'select-one',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
//                         required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
//                         check:'note|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
//                         ass_check:function( check ){
//                             /*
//                              * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
//                              *
//                              * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
//                              *
//                              * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
//                              */
//                         }
//                     }
//                 }
//             ]
//         }, {
//             title: "端口：",
//             sub_items: [
//                 {
//                     enable: true,
//                     type: "textarea",
//                     name: "ipPort",
// 					id: "ipPort",
//                     value: "",
// 					tip: "请输入端口号，可多个，每行一个",
//                     functions: {
//                     },
// 					check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
// 						type:'textarea',        /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
// 						required:'1',       /* **必填**，1表示必填，0表示字段可为空 */
// 						check:'port|',      /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
// 						ass_check:function( check ) {
// 							var str = $("#ipPort").val();
// 							console.log(str);
// 							if( str == "") {
// 								return "该项不能为空";
// 							}
// 							var strs = new Array();
// 							strs = str.split("\n");
// 							for( var i=0; i<strs.length-1; i++) {
// 								if (strs[i] == "") {
// 									return "请不要输入空的端口号";
// 								}
// 							}
// 							if( !judgePort(strs) ) {
// 								return "请不要输入重复的端口号";
// 							} 
// 							/*
// 							 * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
// 							 *
// 							 * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
// 							 *
// 							 * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
// 							 */
// 						}
// 					}
//                 }
//             ]
//         }, {
//             title: "WEB防护规则",
//             sub_items: [
// 				{
//                     enable: true,
//                     type: "textarea",
// 					id:"webRule",
//                     name: "webRule",
// 					readonly:true,
//                     value: "",
//                     functions: {
//                     },
//                     check: {
//                         type: "textarea",
//                         required: 1,
//                         check: 'note|',
//                         ass_check: function( check ) {

//                         }
//                     }
//                 },
// 				{
//                     enable: true,
//                     type: "button",
//                     id: "setting",
//                     name: "setting",
//                     value: "配置",
// 					functions: {
// 						onclick: "lib_panel.show();"
// 				}
					
                    
                    
//                 }
//             ]
//         },{
//             title: "动作",
//             id: "webAction_line", //整行的id
//             sub_items: [
//                 {
//                     enable: true,
//                     type: "items_group",
//                     id: "webAction",
//                     item_style: "width: 100%;",
//                     sub_items: [
//                         {
//                             enable: true,
//                             type: "radio",
//                             id: "merge_type_none",
//                             name: "webAction",
//                             value: "0",
//                             label: "允许",
//                             checked: true
                         
//                         }, {
//                             enable: true,
//                             type: "radio",
//                             id: "merge_type_s_ip",
//                             name: "webAction",
//                             value: "1",
//                             label: "拒绝"
                            
//                         }
//                     ]
//                 }
//             ]
//         },{
//             title: "启用",
//             sub_items: [
//                 {
//                     enable: true,
//                     type: "checkbox",
//                     id: "enable",
//                     name: "enable",
//                     text: "启用",
//                     checked: true
//                 }
//             ]
//         }
//     ]
// };

var lib_panel_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "panel_rule_lib",         // ***必填***，确定面板挂载在哪里 
    page_size: 10,                  //===可选===，定义页大小，默认是15 
    panel_name: "lib_panel",       // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true,         // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置僵尸网络",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    panel_header: [                 // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true,            //用户控制表头是否显示
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
            "enable": true,
            "type": "text",
            "title": "BOTNET规则名称",        //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }, {
            "enable": true,
            "type": "text",
            "title": "描述",
            "name": "description",
            "width": "60%"
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
                    onclick: "write_lib_data();"
                }
            }, {
                enable: true,
                type: "image_button",
                class: "",
                button_text: "取消",
                style: "margin-top: 5px;margin-bottom: 5px;",
                functions: {
                    onclick: "lib_panel.HideForBorder();"
                }
            }
        ]
    }
}

var DestIPGroup_config = {
    url: ass_url, // ***必填***，控制数据在哪里加载 
    check_in_id: "DestIPGroup_panel", // ***必填***，确定面板挂载在哪里 
    page_size: 10, //===可选===，定义页大小，默认是15 
    panel_name: "DestIPGroup_panel", // ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 
    is_load_all_data: true, // ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 
    panel_title: "配置目标IP",
    is_panel_closable: true,
    is_paging_tools: false,
    is_default_search: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "s",
        modal_level: 11
    },
    panel_header: [ // ***必填***，控制数据的加载以及表头显示 
        {
            "enable": true, //用户控制表头是否显示
            "type": "checkbox", //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
            "title": "", //不同类型的，title需要的情况不同，一般text类型需要title
            "name": "checkbox", //用户装载数据之用
            "class": "", //元素的class
            "td_class": "align-center", //这一列td的class，主要用于控制列和列内元素,此处checkbox的td_class是固定的
            "width": "5%", //所有表头加起来应该等于100%,以精确控制你想要的宽度
            "functions": { //一般只有checkbox才会有这个字段
            }
        }, {
            "enable": false,
            "type": "radio",
            "name": "radio",
            "td_class": "rule-listbc",
            "width": "5%"
        }, {
            "enable": true,
            "type": "name",
            "title": "目标IP名称", //一般text类型需要title,不然列表没有标题
            "name": "name",
            "width": "30%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            class: "",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "write_lib_data_other(DestIPGroup_panel,'DestIPGroup');"
            }
        }, {
            enable: true,
            type: "image_button",
            class: "",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "DestIPGroup_panel.HideForBorder();"
            }
        }]
    }
}

var lib_panel = new PagingHolder( lib_panel_config );
var message_manager = new MessageManager( message_box_config );
var DestIPGroup_panel = new PagingHolder(DestIPGroup_config);

//将特征库数据写入配置输入框
function write_lib_data(){
    var checked_items = lib_panel.get_checked_items();
	var str = "";
	var length = checked_items.length;
	if(!checked_items[0]) {
		alert("请选择一种防护规则");
	}else{
    	for(var i = 0; i < length-1; i++) {
    		str += checked_items[i].name + "\n";
    	}
    	str += checked_items[length-1].name;
        $("#setbotnet-webrule").val(str);
        lib_panel.hide();
	}
}
//判定端口号是否重复
function judgePort (e) {
	var array = e;
	array.sort(function(a,b){
		return a - b;
	});
	console.log(array);
	for ( var i = 0; i < array.length; i++ ) {
		if( array[i] == array[i+1] ) {

			return false;
			}
	}
	return true;
}

function write_lib_data_other(panel, textId) {
    var checked_items = panel.get_checked_items();
    var dataText = new Object();
    dataText.SrcIPGroup = "请选择至少一组源IP组！";
    dataText.DestIPGroup = "请选择至少一组目标IP组！";
    dataText.ServiceName = "请选择至少一种服务";
    var str = "";
    var array = new Array();
    var length = checked_items.length;
    if (checked_items.length == 0) {
        message_manager.show_popup_error_mesg(dataText[textId]);
        return;
    } else {
        for (var i = 0; i < length - 1; i++) {
            str += checked_items[i].name + "，";
            array.push(checked_items[i].name);
        }
        str += checked_items[length - 1].name;
        array.push(checked_items[length - 1].name);
        $("#" + textId).val(str);
        writeFrame(document.getElementById(textId), array);
        panel.hide();
    }
}

//将input内容写进提示框
function writeFrame(e, array) {

    if (array.length < 4) {
        clearFrame(e);
        return;
    }
    var ul$ = $(e).next().children("ul");
    ul$.html("");
    for (var i = 0; i < array.length && i < 15; i++) {
        ul$.append("<li>" + array[i] + "</li>");
    }
    if (array.length > 15) {
        ul$.append("<li>...</li>");
    }
    susFrame(e);
}

function clearFrame(e) {

    $(e).removeClass("displayPro");

}
function susFrame(e) {

    $(e).addClass("displayPro");

}
