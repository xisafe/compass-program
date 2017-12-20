/**==============================================================================#
*  * Description:弱口令管理
*  * FileName: weak_pwd_management.js
*  *  CreateDate:2016/12/19
* 
*==============================================================================
*/

$(document).ready(function(){
	
	/* 渲染面板 */
	infoDisplayPanel.render();
	infoDisplayPanel.hide();
    message_manager.render();
    add_panel.render();
    add_panel.hide();
    // tree_panel.render();
    list_panel.render();
   	service_panel.render();
   	service_panel.hide();

   	highSetting_panel.render();
    highSetting_panel.hide();
   	edit_service_panel.render();
    edit_service_panel.hide();
   	showReport.render();
   	showReport.hide();
   	protocolPanel.render();
   	protocolPanel.hide();
    
    strategy_panel.render();
    strategy_panel.hide();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    service_panel.set_ass_add_panel(edit_service_panel)
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
   	// $("#add_panel_body_id_for_tree_panel div.container-main-body").empty().html('<div id="weak_pwd_tree_root" style="height:200px"></div>');
   	init_jstree();
   	$("#add_panel_id_for_highSetting div.container-main-body").empty().html(highSettingHtml);

   	(function(){ /*手动绑定检测*/
   		chinArk_forms = new ChinArk_forms();
   		checkObj = {
   			form_name:"add_panel_body_form_name_for_highSetting",
   			option:{
   				defineName:{
   					type:"textarea",
   					required:1,
   					check:"other",
   					other_reg:"/^[^:/]{0,32}$/",
   					ass_check:function(check){
   						
   					}

   				},
   				definePwd:{
   					type:"textarea",
   					required:1,
   					check:"other",
   					other_reg:"/^[^:/]{0,32}$/",
   					ass_check:function(check){
   						
   					}
   				},
   			}
   		}
   		chinArk_forms._main(checkObj);
   		init_list_panel();
   		$("#info_panel_body_id_for_display_panel div.container-main-body").empty().html($dom);
   		// scanTarget.render();
   	})()


   	/*绑定指定行的点击事件*/

   	
});


var chinArk_forms;
var checkObj;
var paramsObj = {
	title:"",
	assetId:"",
	service:"",
	userNameList:"",
	pwdList:"",
	method:""
};
var services_info;
var arr_new,arr_old;
var ass_url = '/cgi-bin/weak_pwd_management.cgi';

/*管理多个处理程序的中央定时器控制*/
var timeTicket = null;
var	 timers = {
		timerID:0,
		timers:[],
		add:function(fn){
			this.timers.push(fn);
		},
		start:function(){
			if(this.timerID) return;
			(function runNext(){
				if(timers.timers.length > 0){
					for(var i = 0; i < timers.timers.length; i++){
						if(timers.timers[i]() === false){
							timers.timers.splice(i,1);
							i--;
						}
					}
					timers.timerID = setTimeout(runNext,5000);
				}
			})();
		},
		stop:function(){
			clearTimeout(this.timerID);
			this.timerID = 0;
		}
	};


var message_config = {          /* 如果要在页面显示系统消息，需要创建此对象 */
    url: ass_url,                   /* ***必填***，控制应用数据时，向哪个URL提交动作 */
    check_in_id: "mesg_panel",        /* ***必填***，确定面板挂载在哪里 */
    panel_name: "weak_pwd"          /* ==*可选*==，如果页面有多个消息框，此项必填，一般一个消息管理实体就够了 */
}

var highSetting_config = {
	url:ass_url,
	url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "highSetting",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "highSetting",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "高级选项",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 11             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add_btn: false,
        cancel_btn: false,
        sub_items:[{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "确定",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "save_highSetting();"
            }
        },{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "取消",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "cancel_highSetting();"
            }
        }]
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function( add_obj, data_item ) {
          
        },
        before_cancel_edit: function( add_obj ) {
            
        },
        after_cancel_edit: function( add_obj ) {
            
        },
        before_save_data: function( add_obj, sending_data ) {
            
        },
        after_save_data: function( add_obj, received_data ) {
           
        }
    },
    items_list:[{
        title: "自定义用户名",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "defineName",
            name: "defineName",
            functions: {
            	
            },
            check: {
                type: "textarea",
                required: 1,
                check: 'note|',
                ass_check: function( check ) {

                }
            }
        }]
    },{
        title: "自定义密码字典列表",
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "definePwd",
            name: "definePwd",
            functions: {
            	
            },
            check: {
                type: "textarea",
                required: 1,
                check: 'note|',
                ass_check: function( check ) {

                }
            }
        }]
    }]

}
var edit_service_panel_config ={
	url:ass_url,
	url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "edit_service_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "edit_service_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "服务应用",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 12,             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    	self_class:"edit_service_panel-class"
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add_btn: false,
        cancel_btn: false,
        sub_items:[{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "确定",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "save_paramsSettig();"
            }
        },{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "取消",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "edit_service_panel.hide();"
            }
        }]
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function( add_obj, data_item ) {
          
        },
        before_cancel_edit: function( add_obj ) {
            
        },
        after_cancel_edit: function( add_obj ) {
            
        },
        before_save_data: function( add_obj, sending_data ) {
            
        },
        after_save_data: function( add_obj, received_data ) {
           
        }
    },
    items_list:[{
        title: "扫描应用名称:",
        sub_items: [{
            enable: true,
            type: "text",
            id: "editName",
            name: "name",
            readonly: true,
            disabled: true,
            functions: {
            	
            },
            check: {
                type: "name",
                required: 1,
                check: 'name|',
                ass_check: function( check ) {

                }
            }
        }]
    },{
        title: "端口号:",
        sub_items: [{
            enable: true,
            type: "text",
            id: "editPort",
            name: "port",
            functions: {
            	
            },
            check: {
                type: "text",
                required: 1,
                check: 'port|',
                ass_check: function( check ) {

                }
            }
        }]
    },{
        title: "首页地址:",
        enable:true,
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "defineUrl",
            name: "defineUrl",
            functions: {
            	
            },
            check: {
                type: "textarea",
                required: 1,
                check: 'other|',
                other_reg:'/^http[s]?:[/][/][^\\s]+$/',
                ass_check: function( check ) {

                }
            }
        }]
    },{
        title: "邮箱地址",
        enable:true,
        sub_items: [{
            enable: true,
            type: "textarea",
            id: "defineEmail",
            name: "defineEmail",
            functions: {
            	
            },
            check: {
                type: "textarea",
                required: 1,
                check: 'mail|',
                ass_check: function( check ) {

                }
            }
        }]
    }]

}
var add_panel_config = {
   	url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "add_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "weak_pwd",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "配置",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add_btn: false,
        cls:"weak_pwd-footer",
        cancel_btn: false,
        import_btn: false,
        sub_items: [{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "配置扫描任务",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "saveTask();"
            }
        }]
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        before_load_data: function( add_obj, data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载时，数据还“未”装载入面板时调用，
             *    一般是点击编辑后数据项才会向添加面板加载
             *
             * 参数：-- add_obj   ==可选==，添加面板实例
             *        -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        after_load_data: function( add_obj, data_item ) {
            /*
             * ===可选事件函数===，在数据项往添加面板加载后，数据“已”装载入面板时调用
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *         -- data_item ==可选，要加载进添加面板的整个数据项
             *
             * 返回：无
             */
        },
        before_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“前”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        after_cancel_edit: function( add_obj ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的撤销按钮时，系统会做一些默认操作，
             *    在做这些默认的操作之“后”调用此函数
             *
             * 参数： -- add_obj   ==可选==，添加面板实例
             *
             * 返回：无
             */
        },
        before_save_data: function( add_obj, sending_data ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“前”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例
             *        -- sending_data  ==可选==, 要向服务器提交的数据，
             *           用户可以通过 sending_data.xxx = xxx 添加向服务器提交的数据
             * 返回：true/false
             *       -- 返回true，或者不返回数据，数据会如实提交
             *       -- 返回false，会阻止数据向服务器其提交
             */
        },
        after_save_data: function( add_obj, received_data ) {
            /*
             * ===可选事件函数===，在用户点击面板默认渲染的添加按钮时，系统向服务器提交添加面板的所有数据，
             *    在做提交数据之“后”并且服务器响应之“后”会调用此函数
             *
             * 参数： -- add_obj       ==可选==，添加面板实例，可以调用add_obj.show_error_mesg( mesg )
             *           或者add_obj.show_note_mesg( mesg )等函数反馈信息给用户
             *        -- received_data ==可选==, 服务器响应的数据，
             *           可以在后台配置要传递的数据，并在此处访问
             * 返回：无
             */
        }
    },
    items_list: [{              /* ***必填***，确定面板中有哪些规则，不填什么都没有 */
        title: "任务名称",          /* **必填**，每一行前面的提示文字，不填没有提示，影响用户体验 */
        id: "name_tr",          /* ==可选==，整行的id */
        name: "",               /* ==可选==，整行的name */
        cls: "",                /* ==可选==，整行的class */
        functions: {            /* ==可选==，整行相应事件的回调函数，DOM标准事件都可生效 */
            // onmouseover: "alert('hover on name line');",
            // onclick: "alert('click on name line');",
        },
        sub_items: [{           /* **必填**，确定此行有哪些字段，不填什么都没有 */
            enable: true,       /* **必填**，如果为不填或者为false,就不创建 */
            type: "text",       /* ==可选==，默认是text类型，支持text,password,button,file,select,checkbox,
                                             radio,textarea,label,items_group
                                */
           	id:"taskName",
            name: "name",       /* **必填**，字段的名字 */
            value: "",          /* ==可选==，字段默认值 */
            functions: {        /* ==可选==，DOM标准事件都可生效 */
            },
            check: {            /* ==可选==，如果要对字段进行检查，填写此字段 */
                type: "text",   /* **必填**，支持text,textarea,password,file,select-one,select-multiple,checkbox,radio */
                required: 1,    /* **必填**，1表示必填，0表示字段可为空 */
                check: 'name|', /* **必填**，检测类型，具体支持哪些种类型参见ChinArk_form.js文件源码 */
                ass_check: function( check ) {
                    /*
                     * ===可选检测函数===，如果用户输入的内容满足了上面的name类型和必填两个条件，才会调用这里的检测函数
                     *
                     * 参数： -- check ChinArk_form实体具体使用参见ChinArk_form.js文件源码
                     *
                     * 返回：如果有错，返回非空字串的错误消息，没有则返回空串或者不写返回语句，返回的消息将会用户提示用户
                     */
                }
            }
        }]
    }, {
        title: "扫描目标IP范围",
        enable:false,
        sub_items: [{
            enable: false,
            type: "button",
            id: "setIP",
            name: "setIP",
            value: "配置",
            functions: {
            	onclick:"tree_panel.show();"
            }
        }]
    }, 
    {
        title: "扫描服务应用",
        sub_items: [{
            enable: true,
            type: "button",
            id: "setRange",
            name: "setRange",
            value: "配置",
            functions: {
            	onclick:"service_panel.show();"
            }
            
        }]
    },{
        title: "扫描方式",
        sub_items: [{
            enable: true,
            type: "select",
            id: "method",
            name: "method",
            options:[{
            	value:1,
            	text:'常规扫描'
            },{
            	value:2,
            	text:'完整扫描'
            }]
        },{
        	enable:true,
        	type:"button",
        	id:'high_setting',
        	name:'high_setting',
        	value:'高级选项',
        	functions:{
        		onclick:"highSetting_panel.show();"
        	}
        }]
    }]

};
var tree_root_id                 = '1';
var tree_panel_config = {
   	url: ass_url,                   /* ***必填***，点击添加或者导入，或者其他自定义动作时，控制数据向哪里提交 */
    check_in_id: "tree_panel",       /* ***必填***，确定面板挂载在哪里 */
    panel_name: "tree_panel",        /* ==*可选*==，默认名字my_add_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    rule_title: "选择目标IP范围",         /* ==*可选*==，默认是"规则" */
    is_panel_closable: true,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_panel_stretchable: false,    /* ===可选===，默认是true，控制面板是否可伸缩 */
    is_modal: true,                 /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 13             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    footer_buttons: {               /* ===可选===，默认是add和cancel按钮，如果想创建import,要在此控制 */
        add_btn: false,
        cancel_btn: false,
        sub_items: [{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "添加",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "save_treePanel();"
            }
        },{               /* ===可选===，想要添加当前没有考虑到的按钮，通过此选项 */
            enable: true,
            type: "button",
            value: "取消",
            functions: {            /* ===可选===，定义对按钮进行相应操作时应当做的事，比如onclick、onmousehover */
                onclick: "cancel_treePanel();"
            }
        }]
    },
    event_handler: {                /* ===可选===，如果要在一些节点做事情，可以在此定义如下一些函数 */
        
    },
    items_list:[{
        title: "扫描服务应用",
        sub_items: [{
            enable: true,
            type: "button",
            id: "setRange",
            name: "setRange",
            value: "配置",

    	}]
    }]
};
var list_panel_render = {
	'beginTime':{
		render:function(item,data,dom){

			if(item == "0"){
				return "未扫描";
			}else{
				return item;
			}
		}
	},
	'endTime':{
		render:function(item,data,dom){
			if(item == "0"){
				return "未扫描";
			}
			else if(item == "1"){
				return "未完成";
			}
			else{
				return item;
			}
		}
	},
	'processBar':{
		render: function(item, data,dom) {
			var progress;
			
			progress = parseInt(item * 100);
			var html = 
			'<div class="progress progress-striped active" style="margin: auto;">' +
				'<div class="progress-bar progress-bar-info" role="progressbar"' +
					 'aria-valuenow="60" aria-valuemin="0" aria-valuemax="100"' +
					 'style="width: ' + progress + '%;">' +
					 progress + '%' + 
				'</div>' +
			'</div>';
			return html;
		}
	},
	'action': {
        render: function( default_rendered_text, data_item,dom ) {
            // console.log(data_item.runToggle);
        	var runBtn_icon = (data_item.runToggle == 'yes') ? "stop.png" : "start.png";
        	var runBtn_text= (data_item.runToggle == 'yes') ? "结束" : "开始";
        	var reportBtn_icon = (data_item.reportToggle == 'yes') ? "report16x16.png" : "report_disabled.png";
        	var reportBtn_text = (data_item.reportToggle == 'yes') ? "查看报表" : "暂无报表";
        	var delBtn_icon = (data_item.runToggle == 'yes') ? "delete_disabled.png" : "delete.png";
        	var delBtn_text = (data_item.runToggle == 'yes') ? "不能删除" : "删除";
            var action_buttons = [{
                enable: true,
                id: "toggle_on_off",
                name: "toggle_on_off",
                cls: "",
                button_icon: runBtn_icon,
                button_text: runBtn_text,
                value: data_item.name
            },
            // {
            //     enable: true,
            //     id: "showInfo",
            //     name: "showInfo",
            //     cls: "",
            //     button_icon: "view_details.png",
            //     button_text: "查看详情",
            //     value: data_item.name,
            //     functions: {
            //         onclick: "showScanInfo(this.value);"
            //     }
            // }
            // ,
            {
                enable: true,
                id: "viewReport",
                name: "viewReport",
                cls: "",
                button_icon: reportBtn_icon,
                button_text: reportBtn_text,
                value: data_item.name,
                // functions: {
                //     onclick: "viewReport()"
                // }
            }
            ,{
                enable: true,
                id: "deleteBtn",
                name: "deleteBtn",
                cls: "",
                button_icon: delBtn_icon,
                button_text: delBtn_text,
                value: data_item.name,
                // functions: {
                //     onclick: "deleteTaskList();"
                // }
            },{
                enable: true,
                id: "apply-btn",
                name: "aply-btn",
                clas: "",
                button_icon: "add.png",
                button_text: "应用策略",
                value: data_item.name
            }];

            var btn$ = $(PagingHolder.create_action_buttons( action_buttons ));
            btn$.eq(0).on("click", function(){startScan(data_item)});
            btn$.eq(1).on("click", function(){
            	if(data_item.reportToggle == 'yes'){
            		viewReport(data_item);
            	}
            	else{
            		return false;
            	}
        	});
            btn$.eq(2).on("click", function(){
            	if(data_item.runToggle == 'no'){
            		deleteTaskList(data_item);
            	}
            	else{
            		message_manager.show_popup_error_mesg("扫描中不能删除");
            	}
        	});
            btn$.eq(3).on("click", function() {
                applyStrategy(data_item.name);
            });
            return btn$;
        }
    }
};
var $dom ='<div class="infoPanel">';
            $dom += '<ul>';
                $dom +='<li><fieldset><legend>扫描目标:</legend><div id="scan_obj"></div></fieldset></li>';
                $dom +='<li><fieldset><legend>扫描服务:</legend><div id="scan_service"></div></fieldset></li>';
                $dom +='<li><fieldset><legend>扫描方式:</legend><div id="scan_mode"></div></fieldset></li>';
            $dom +='</ul>';
            $dom +='<div class="toolbar align-center"><button class="imaged-button report-btn" onclick="infoDisplayPanel.hide();"><span class="button-text ">关闭</span></button></div>'
       $dom +='</div>';

var protocolConfig ={
	url: ass_url,                   
    check_in_id: "protocolPanel",      
    panel_name: "protocolPanel",       
    page_size:10,
    is_modal:true,
    panel_title:'详情:',
    is_panel_title_icon:true,
    is_panel_closable:true,
    is_paging_tools:false,
    is_default_search:false,
    modal_config: {                 /* ===可选===，当想控制模块框大小层次时创建，并且在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 14,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
        // modal_box_position: "fixed" /* ===可选===，position属性值，目前未使用，未调试成功，建议不使用此字段 */
    },        
    panel_header: [{
        enable: true,
        type: "text",
        title: "开放端口",
        name: "port",
        width: "30%"
    },{
        enable: true,
        type: "text",
        title: "协议",
        name: "protocol",
        width: "30%"
    }],
    bottom_extend_widgets: {        /* ===可选===，定义放在底部的按钮 */
        id: "",
        name: "",
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            cls: "protocolPanel-btn",
            button_text: "关闭",
            functions: {
                onclick: "protocolPanel.hide();"
            }
        }]
    }
}
// var scanTarget = new PagingHolder(scanTarget_config);

var showReport_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "showReport",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "showReport",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，*/
    page_size:10,
    is_modal:true,
    modal_config:{
    	modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 11,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
        self_class:"showReport-content"
    },
    is_panel_closable:true,
    is_paging_tools:false,
    panel_title:"扫描结果:",
    is_panel_title_icon:true,
    // panel_title_icon:'scan16x16.png',
   	bottom_extend_widgets: {        /* ===可选===，定义放在底部的按钮 */
        id: "",
        name: "",
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            cls: "report-btn",
            button_text: "关闭",
            functions: {
                onclick: "showReport.hide();"
            }
        }]
    },
    is_default_search:false,
    render:{
	    	'isExists':{
				render:function(item,data,dom){
						if(item == "no"){
							return "不存在";
						}else{
							// ;
							var span = '<span style="cursor:pointer;">存在</span>';
							var span$ = $(span);
							span$.on('click',function(){
								showProtocol(data);
							});
							
				            return span$;
							

						}
					}
				}
    },                                              /*以区别不同面板 */
    event_handler: {
       
    },
    panel_header: [{            
            enable: false,          
            type: "checkbox",       
            title: "",              
            name: "checkbox",       
            cls: "",                
            column_cls: "",         
            width: "5%",            
            functions: {            
            	
                    }
    }, {
        enable: false,
        type: "text",
        title: "服务器名称",
        name: "name",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "服务器IP地址",
        name: "ip",
        width: "50%"
    },
  	{
        enable: true,
        type: "action",
        name: "isExists",
        title:"是否存在弱口令",
        width: "20%"
    }]
   
};        
var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，*/
    page_size:20,
    is_default_search:false,
    render:list_panel_render,                                              /*以区别不同面板 */
    event_handler: {
        before_load_data: function( list_obj ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 时，系统向服务器重新加载数据之前调用此函数
             *
             * 参数： -- list_obj      ==可选==，列表面板实例
             * 返回：无
             */
        },
        after_load_data: function ( list_obj, response ) {
            /*
             * ===可选事件函数===，在用户调用update_info( true ) 后，并且服务器响应后调用此函数
             *
                                    
             * 参数： -- add_obj    ==可选==，添加面板实例，用户可以通过add_obj.show_
             *        -- response   ==可选==, 服务器响应的数据
             * 返回：无
             */
        }
    },
    panel_header: [{            /* ***必填***，控制数据的加载以及表头显示 */
        enable: true,           /* ==可选==，作用于整列，如果为不填或者为false，那么定义的这一列都不会显示 */
        type: "checkbox",       /* ==可选==，作用于整列，type目前有checkbox/text/radio/action，分别对应不同类型的表头，
                                            默认是text类型，表示显示加载的数据，如果是checkbox，表示整列都显示checkbox框，
                                            如果是radio，表示整列都显示radio按钮，如果是action，表示这一列是操作列，可以自
                                            行定义要显示哪些操作按钮，也可以使用默认渲染的操作按钮，见“配置对象”（注释<1>）
                                            的render属性中的action属性
                                                type为checkbox类型和radio类型在一个列表面板中一般不能一起使用，到目前为止，
                                            也没有遇到这种需求，并且一起使用会有BUG。
                                                type为action的列，默认会渲染启用/禁用按钮（如果本行数据中包含enable字段的
                                            话会渲染）、编辑、删除，并且点击这三种类型按钮会有默认动作，点击启用/禁用按钮
                                            会自动向服务器发起启用/禁用相关规则的请求，具体能否启用/禁用相关规则，还要靠后
                                            台 的相关处理是否起作用；点击编辑时，会向添加面板加载数据并将添加面板切换为编
                                            辑状态（前提是“列表面板”设置了关联的“添加面板”具体使用方法见add_list_demo.js中
                                            set_ass_add_panel）；点击删除按钮时，会向服务器发起删除相关规则的请求，具体能
                                            否删除相关规则，也要靠后台处理结果
                                 */
        title: "",              /* =*可选*=，作用于标题头单元格，不同type，title需要的情况不同，
                                                一般type为text需要文字title，提示这一列数据表示什么意义，不填不显示标题
                                                当type为checkbox时，会默认渲染‘全选checkbox框’，填了title也将不起作用，
                                            当type为radio类型时，title变为‘请选择’，填了title也不起作用，当type为action时，
                                            默认标题是“活动/动作”，如果在action配置项填了title属性，会覆盖默认标题，示例见
                                            下文
                                 */
        name: "checkbox",       /* **必填**，作用于整列，控制整列要显示的数据项
                                                ****当type为checkbox、radio、action之一时，name也必须对应为三项中的一项
                                                如果要渲染每列数据，到“配置对象”（注释<1>）的render属性中去配置与当前name值
                                            一样的属性，比如要渲染checkbox列，就去render中配置checkbox，见list_panel_extend.js
                                            第20行，再比如要渲染下文中classification列，见list_panel_extend.js的42行。
                                 */
        cls: "",                /* ==可选==，作用于标题头单元格，标题的class，比如要标题加粗、斜体等 */
        column_cls: "",         /* ==可选==，作用于整列，控制单元格中内容显示样式，比如要求内容居中显示，首行缩进两字符等
                                             当type为checkbox、radio类型时，默认居中显示，其他左对齐显示，并且首行缩进5px，
                                             在此处有一个align-center的样式可以直接使用，控制内容居中显示
                                 */
        width: "5%",            /* ==可选==，作用于整列，控制每列的显示宽度，所有表头（除去enable为false的）加起来应该等于100%，
                                             以精确控制你想要的宽度
                                 */
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    }, {
        enable: true,
        type: "text",
        title: "扫描任务名称",
        name: "name",
        width: "25%"
    }, {
        enable: true,
        type: "text",
        title: "扫描进度",
        name: "processBar",
        width: "25%"
    }, 
     {
        enable: true,
        type: "text",
        title: "扫描开始时间",
        name: "beginTime",
        width: "20%"
    },{
        enable: true,
        type: "text",
        title: "扫描完成时间",
        name: "endTime",
        width: "20%"
    },
  	{
        enable: true,
        type: "action",
        name: "action",
        width: "15%"
    }],
    top_widgets: [{                     /* ===可选===，在面板左上角的操作控件，目前按钮位置不能调整 */
        enable: true,                   /* =*可选*=，如果为不填或者为false,就不创建 */
        type: "image_button",           /* =*可选*=，目前支持类型有text,password,file,select,checkbox,radio,textarea,
                                                    label,button和image_button,最常用的是image_button，并且目前考虑得
                                                    比较多其他组件比较弱，但能勉强使用，如果其他需求很强，需要进一步
                                                    扩展
                                         */
        button_icon: "add16x16.png",    /* ==可选==，image_button的图标，如果没有设置，就没有图标，image_button独有字段 */
        button_text: "配置",        /* **必填**，image_button的文字，这个必须设置,建议在五个字以内，image_button独有字段 */
        functions: {                    /* ==可选==，回调函数，没有的话就只是一个按钮，什么也不做 */
            onclick: "add_panel.show()"
        }
    }, {
        enable: true,
        type: "image_button",
        button_icon: "on.png",
        button_text: "防护风险",
        functions: {
            onclick: "defendRisk();"
        }},
        {
            enable: true,
            type: "image_button",
            button_icon: "view_details.png",
            button_text: "查看已添加策略",
            functions: {
                onclick: "strategy_panel_show()"
            }
    }]
};
var service_panel_config = {
	url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "servicePanel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "servicePanel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，*/
    is_panel_closable:true,
    panel_title: "选择扫描服务应用",
    is_panel_title_icon:true,
    page_size:10,
    is_modal:true,
    modal_config: {                 /* ===可选===，当想控制模块框大小层次时创建，并且在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
        // modal_box_position: "fixed" /* ===可选===，position属性值，目前未使用，未调试成功，建议不使用此字段 */
    	self_class:"service_panel-class"
    },

    is_default_search:false,                                              /*以区别不同面板 */
    is_paging_tools:false,
    event_handler: {
        before_load_data: function( list_obj ) {
           
        },
        after_load_data: function ( list_obj, response ) {
        }
    },
    render:{
    	'checkbox': {
	
	    },
	    'action':{
	    	render: function( default_rendered_text, data_item ) {
            var action_buttons = [{
                enable: true,
                id: "editBtn",
                name: "editBtn",
                cls: "",
                button_icon: "edit.png",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "show_edit_service_panel(this.value);"
                }
            }];
            return PagingHolder.create_action_buttons( action_buttons );
        
	    	}
		}
    },
    panel_header: [{            
        enable: true,          
        type: "checkbox",                   
        title: "",                            
        name: "checkbox",                     
        cls: "",                
        column_cls: "",                       
        width: "5%",                            
        functions: {            /* ==可选==，作用于标题头单元格，只有checkbox的这个字段会生效，也就是说这个只会传给‘全选checkbox框’ */
            // onclick: "alert(this.value);"
        }
    }, {
        enable: true,
        type: "text",
        title: "扫描应用名称",
        name: "name",
        width: "20%"
    },{
    	enable:true,
    	type:"text",
    	title:"端口",
    	name:"port",
    	width:"20%"
    },{
        enable: true,
        type: "action",
        name: "action",
        width: "20%"
    }],
    
    bottom_extend_widgets: {        /* ===可选===，定义放在底部的按钮 */
        id: "",
        name: "",
        cls: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            cls: "servicePanel-btn",
            button_text: "确定",
            functions: {
                onclick: "save_servicePanel();"
            }
        }, {
            enable: true,
            type: "image_button",
            cls: "servicePanel-btn",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "cancel_servicePanel();"
            }
        }]
    }
}

//查看策略面板 
var strategy_panel_render = {
    action: {
        render: function(a, b) {
            var png, text, func;
            if(b["status"] == "1") {
                png = "on.png";
                text = "禁用";
                func = "actionStrategy('off', " + b['idView'] + ");";
            }else {
                png = "off.png";
                text = "启用";
                func = "actionStrategy('on', " + b['idView'] + ");";
            }
            action_buttons = [
                {
                    "enable": true,
                    "id": "enable_item",
                    "name": "enable_item",
                    "button_icon": png,
                    "button_text": text,
                    "style": "margin-left: 50px;",
                    "functions": {
                        onclick: func
                    },
                    "class": ""
                },
                {
                    "enable": true,
                    "id": "delete_item",
                    "name": "delete_item",
                    "button_icon": "delete.png",
                    "button_text": "删除",
                    "style": "margin-left: 35px;",
                    "functions": {
                        onclick: "actionStrategy('delete', " + b['idView'] + ");"
                    },
                    "class": ""
                }
            ];
        
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};
var strategy_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "strategy_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "strategy_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，*/
    panel_title: "查看已添加策略",
    //panel_title_class: "glyphicon glyphicon-list-alt",
    is_panel_closable: true,
    is_modal: true,
    page_size: 10,
    render : strategy_panel_render,
    
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",        /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 11             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },                                            
    panel_header: [           /* ***必填***，控制数据的加载以及表头显示 */
        {
            enable: true,
            type: "checkbox",
            name: "checkbox",
            width: "5%"
        },
        {
            enable: true,
            type: "text",
            title: "目标服务IP",
            name: "ips",
            width: "20%"
        },
        {
            enable: true,
            type: "text",
            title: "策略号",
            name: "idView",
            width: "20%"
        },
        {
            enable: true,
            type: "text",
            title: "添加时间",
            name: "time",
            width: "20%"
        },
        {
            enable: true,
            type: "action",
            title: "操作",
            name: "action",
            width: "20%"
        }
    ],
    top_widgets: [
    {                     
        enable: true,                   
        type: "image_button",
        button_icon: "delete.png",    
        button_text: "删除",        
        functions: {                   
            onclick: "actionStrategy('delete');"
        }
    },
    {                     
        enable: true,                   
        type: "image_button",
        button_icon: "on.png",    
        button_text: "启用",        
        functions: {                   
            onclick: "actionStrategy('on');"
        }
    },
    {                     
        enable: true,                   
        type: "image_button",
        button_icon: "off.png",    
        button_text: "禁用",        
        functions: {                   
            onclick: "actionStrategy('off');"
        }
    }]
};
var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_config );
var tree_panel = new RuleAddPanel( tree_panel_config );
var service_panel = new PagingHolder(service_panel_config);
var highSetting_panel = new RuleAddPanel(highSetting_config);
var showReport = new PagingHolder(showReport_config);
var edit_service_panel = new RuleAddPanel(edit_service_panel_config);
var protocolPanel = new PagingHolder(protocolConfig);
var strategy_panel = new PagingHolder(strategy_panel_config);
/* 树形数据配置 */
var zone_tree_config = {
    core: {
        data: {},
        check_callback: function(o, n, p, i, m) {
            if (m && m.dnd && m.pos !== 'i') { return false; }
            if (o === "move_node" || o === "copy_node") {
                if (this.get_node(n).parent === this.get_node(p).id) { return false; }
            }
            return true;
        },
        multiple: true,
        force_text: true,
        themes: {
            responsive: false,
            variant: 'large',
            stripes: true
        }
    },
    types: {
        "#" : {
            max_children: 1, 
            max_depth: 4, 
            valid_children: ["root"]
        },
        root: {
            icon: "glyphicon glyphicon-map-marker",
            valid_children: ["default"]
        },
        default: {
            icon: "../images/service-icon.png",
            valid_children: ["default","file"]
        },
        asset:{
        	icon:"../images/area-icon.png",
        	valid_children:["asset"]
        },
        file: {
            icon: "file",
            valid_children: []
        }
    },
    plugins : [
        //"contextmenu",
        "state",
        "types",
        "wholerow",
        "checkbox"
    ]
};
var infoDisplayPanelConf = {
    check_in_id: "display_panel",   /* ***必填***，确定面板挂载在哪里 */
    panel_name: "display_panel",    /* ==*可选*==，默认名字my_add_panel，当一个页面存在多个信息展示面板用于区分不同面板 */
    panel_title: "配置信息",    /* ===可选===，默认是“信息”，表示显示前面的 */
    is_panel_title_icon: true,      /* ===可选===，默认是“true”，表示标题前面的图标是否显示 */
    panel_title_icon: "info.png",   /* ===可选===，默认是“info.png”，is_panel_title_icon为true才有效 */
    is_panel_closable: true,       /* ===可选===，默认是false，控制面板是否可关闭，跟点击撤销按钮是一个效果 */
    is_modal: true,                /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "s",        /* ===可选===，默认是l,有l、m、s三种尺寸的模态框 */
        modal_level: 11             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    columns: 1,                     /* ===可选===，默认是2，表示信息展示的列数 */
    label_width: 1,                 /* ===可选===，默认是3，填写的是比例，必须是数字(整数类型和浮点类型) */
    value_width: 3,                 /* ===可选===，默认是7，填写的是比例，必须是数字(整数类型和浮点类型)，此处是1:3的比例 */
    items_list: [
    ] 
}
var infoDisplayPanel = new InfoDisplayPanel( infoDisplayPanelConf )


var highSettingHtml = '<fieldset class="high_setting-field"><legend>自定义字典</legend><div class="highSetting-cls"><label>自定义用户名:</label><textarea id="defineName" name="defineName"></textarea></div><div class="highSetting-cls"><label>自定义密码字典列表:</label><textarea id="definePwd" name="definePwd"></textarea></div></fieldset>'
function startScan(obj){
	// var toggle = (obj.runToggle == "no") ? "yes" : "no";
	do_request({ACTION:"startScan",taskName:obj.name,operate:obj.runToggle},function(item){
		if(item.status == "1"){
			message_manager.show_popup_error_mesg("执行失败,请稍后再试!");
		}
		else{
			if(obj.runToggle == "yes"){
				message_manager.show_popup_note_mesg('停止扫描!');
			}else{
				message_manager.show_popup_note_mesg('正在扫描...');
			}

			list_panel.detail_data = item.detail_data;
			list_panel.total_num = item.detail_data.length;
			list_panel.update_info();
		}
		// clearTimeout(timeTicket);
		// if(item.flush_flag == '0'){
			timeTicket = setTimeout(init_list_panel,5000);
		// }else{

		// }
	})
}

function defendRisk(){
    var check_items = list_panel.get_checked_items();
    if(check_items.length < 1){
        message_manager.show_error_mesg("请选择需要任务！");
    }else{
        var nameArr = [];
        for(var i = 0; i < check_items.length;i++){
            nameArr.push(check_items[i].name);
        }
        list_panel.request_for_json({"ACTION":"apply_strategy","name":nameArr.join("&")},function(data){
            alert(data["mesg"]);
        })
    }
}

function showProtocol(data){
	
	protocolPanel.detail_data = data.detail_info;
	protocolPanel.total_num = data.detail_info.length;
	protocolConfig.page_size = data.detail_info.length;
	protocolPanel.refresh_list_panel(protocolConfig);
	protocolPanel.update_info();
	protocolPanel.show();


}
function showScanInfo(name){
	do_request({ACTION:"showScanInfo",taskName:name},function(item){
		// console.log(item);
		var status = item.err_msg;
		if(status == "0"){
			var data = item.detail_data;
			var thArrList = {
					scan_obj:[
						{
							name:"asset_name",
							value:"目标名称"
						},
						{
							name:"asset_ips",
							value:"目标IP地址"
						}],
					scan_service:[
						{
							name:"service",
							value:"服务名称"
						},
						{
							name:"port",
							value:"端口号"
						}
						]
				};

			for(var key in data){
				if(typeof data[key] === "object"){
					if(data[key].length > 0){
						$("#"+key).html('');
						$("#"+key).html(createTable(key,thArrList[key],data[key]));
					}
					else{

					}
					
				}else{
					$("#"+key).text(data[key]);
				}
			}
		}else{
			$("#scan_obj,#scan_service").text("暂无数据");

		}
		
	});
    infoDisplayPanel.show();
}
/*
	创建table;
	thArr:[{name:key1,value:},{name:key2,value:}....],
	data:[{key1:,key2:}...]

*/
function createTable(tId,thArr,data){
	var table = '<table class="rule-list">';
			table		+='<thead id="panel_header_id_for_'+ tId + '" class="rule-listbh">';
			table			+='<tr>';
						for(var i = 0;i < thArr.length; i++){
								var w = (i == 0)? "width=30%" : ""; 
			table				+='<td '+ w +'>';
			table					+='<span name="'+thArr[i].name+'">'+thArr[i].value+'</span>';
			table				+='</td>';
						}
			table			+='</tr>';
			table		+='</thead>';
			table		+='<tbody id="panel_header_id_for_'+ tId + '" class="rule-listb">';
						for(var m = 0; m < data.length; m++){
			table			+='<tr>';

							for(var n = 0 ; n < thArr.length; n++){
								var name = thArr[n]['name'];
			table					+='<td>'+data[m][name] +'</td>';
							}
			table				+='<tr>';
						}
						
			table		+='</tbody>';
			table		+='</table>';
	return table;
}
function viewReport(obj){
	do_request({ACTION:"viewReport",taskName:obj.name},function(item){
		if(item.status == "1"){
			message_manager.show_popup_error_mesg("获取报表失败!");
		}
		else{
			
			showReport.detail_data = item.detail_info;
			showReport.total_num = item.detail_info.length;
			showReport_config.page_size = item.detail_info.length;
			showReport.refresh_list_panel(showReport_config);

			showReport.update_info();
            showReport.show();
		}
	})
}
function deleteTaskList(obj){
	do_request({ACTION:"deleteTaskList",taskName:obj.name},function(item){
		if(item.status == "1"){
			message_manager.show_popup_error_mesg("删除失败!");
		}
		else{
			message_manager.show_popup_note_mesg("删除成功!");
			list_panel.detail_data = item.detail_data;
			list_panel.total_num = item.detail_data.length;
			list_panel.update_info();
		}
	})
}
function init_list_panel(){
	do_request({
		ACTION:"init_list_panel"
	},function(items){
	
		if(items.flush_flag == '0'){
			
			timeTicket = setTimeout(init_list_panel,5000);
		}else{
			clearTimeout(timeTicket);
		}
		list_panel.detail_data = items.taskList;
		list_panel.total_num = items.taskList.length;
		list_panel.update_info();

	})
}
function refreshListPanel(data){
	
}
function saveTask(){
	if(add_panel.is_input_data_correct()){
		paramsObj.method = $("#method").val();
		paramsObj.title = $("#taskName").val();
		if(paramsObj.assetId == ""){
			message_manager.show_popup_error_mesg("请配置目标IP范围!");
			return
		}
		else if(paramsObj.service.length == 0){
			message_manager.show_popup_error_mesg("请配置服务应用");
		}
		else{
			//发送请求
			var temp = [];
			$.each(paramsObj.service,function(i,v){
				if(v.hasOwnProperty('defineUrl')){
					paramsObj.urlList = v.defineUrl; 
				}
				else if(v.hasOwnProperty('defineEmail') && v.name == "SMTP"){
					paramsObj.emailList_stmp = v.defineEmail.split("\n").join("&");
				}
				else if(v.hasOwnProperty('defineEmail') && v.name == "POP3"){
					paramsObj.emailList_pop3 = v.defineEmail.split("\n").join("&");
				}
				else if(v.hasOwnProperty('defineEmail') && v.name == "IMAP"){
					paramsObj.emailList_imap = v.defineEmail.split("\n").join("&");
				}
				temp.push(v.name + "/" +v.port);
			})
			paramsObj.serviceStr = temp.join("&");
			var sending_data = {
				ACTION:"saveTask",
				title: paramsObj.title,
				assetId:paramsObj.assetId,
				service:paramsObj.serviceStr,
				method:paramsObj.method,
				userNameList:paramsObj.userNameList,
				pwdList:paramsObj.pwdList,
				urlList:paramsObj.urlList,
				emailList_stmp:paramsObj.emailList_stmp,
				emailList_pop3:paramsObj.emailList_pop3,
				emailList_imap:paramsObj.emailList_imap
			}
			function ondatareceived(data){
				if(data.status == '2'){
					message_manager.show_popup_error_mesg("任务名称已存在，请重新配置");
				}else if(data.status == '0'){
					add_panel.hide();
					list_panel.detail_data = data.taskList;
					list_panel.total_num = data.taskList.length;
					list_panel.update_info();
				}else{
					message_manager.show_popup_error_mesg('配置失败');
					add_panel.hide();
				}
				
			}
			function err(error){
		        
		    }
		    do_request(sending_data, ondatareceived);
				
		}
	}
}
function show_edit_service_panel(val){
	
	var arr = [9,10,11,12,13];
    var index = $.inArray(parseInt(val),arr);
    if(index > -1){
    	if(index < 2){
    		edit_service_panel_config.items_list[2].enable = true;
    		edit_service_panel_config.items_list[3].enable = false;
    	}else{
    		edit_service_panel_config.items_list[2].enable = false;
    		edit_service_panel_config.items_list[3].enable = true;
    	}
    		
    }else{
     edit_service_panel_config.items_list[2].enable = false;
     edit_service_panel_config.items_list[3].enable = false;
    }
    edit_service_panel.render();
    	// edit_service_panel.show(); 
    service_panel.edit_item(val);
}
function save_paramsSettig(){

	if(edit_service_panel.is_input_data_correct()){
		var name = $("#editName").val();
		var port = $("#editPort").val();
		var defineUrl = $("#defineUrl").val();
		var defineEmail = $("#defineEmail").val();
		$.each(services_info,function(i,n){
			if(n.name == name){
				n.port = port;
				if(defineUrl !== undefined){n.defineUrl = defineUrl;service_panel.set_check(n.id,"checked");} 
				if(defineEmail !== undefined){n.defineEmail = defineEmail;service_panel.set_check(n.id,"checked");}

			}
		})
		edit_service_panel.hide();
		service_panel.detail_data = services_info;
		service_panel.total_num = services_info.length;

		service_panel.update_info();

	}
	else{
		message_manager.show_popup_error_mesg("请输入合法字符！");
		return;
	}
	
}
function cancel_paramsSetting(){
	paramsPanel.hide();
}
function save_treePanel(){
	arr_old = arr_new;
	paramsObj.assetId = arr_new.join("&");
	tree_panel.hide();
	$('#weak_pwd_tree_root').jstree(true).deselect_all();
	$('#weak_pwd_tree_root').jstree(true).select_node(arr_new);
}
function cancel_treePanel(){
	arr_new  = arr_old;
	paramsObj.assetId = arr_new.join("&");
	tree_panel.hide();
	$('#weak_pwd_tree_root').jstree(true).deselect_all();
	$('#weak_pwd_tree_root').jstree(true).select_node(arr_new);
}
function save_servicePanel(){
	paramsObj.service = service_panel.get_checked_items();
	service_panel.hide();
}
function cancel_servicePanel(){
	// paramsObj.service = "";
	service_panel.uncheck_current_page();
	if(!!paramsObj.service){
		var arr = paramsObj.service;
		$.each(arr,function(i,v){
			service_panel.set_check(v['id'],"checked");
		})
		service_panel.update_info();
	}
	service_panel.hide();
}
function save_highSetting(){
	if(!chinArk_forms._submit_check(checkObj,chinArk_forms)){
		var defineName = $("#defineName").val().split("\n");
		var definePwd  = $("#definePwd").val().split("\n"); 
		paramsObj.userNameList = defineName.join(":");
		paramsObj.pwdList = definePwd.join(":");
		highSetting_panel.hide();
	}
	else{
		message_manager.show_popup_error_mesg("请输入合法字符！");
		return;
	}

}
function cancel_highSetting(){
	highSetting_panel.cancel_edit_box();
	$("#defineName").val(paramsObj.userNameList.replace(":","\n"));
	$("#definePwd").val(paramsObj.pwdList.replace(":","\n"));
	highSetting_panel.hide();

}



function init_jstree(){
    do_request({ACTION: "load_zoneData"},
        function(data) {
           
            // var length = Object.keys(data.object_info).length;
            // if(length){
            //     zone_tree_config.core.data = data.object_info;
            // }else {
            //     zone_tree_config.core.data = "";
            // }
            // if(!$("#weak_pwd_tree_root").jstree(true)) {
            //     $("#weak_pwd_tree_root").jstree(zone_tree_config);
            // }else {
            //     $("#weak_pwd_tree_root").jstree(true).settings.core.data = zone_tree_config.core.data;
            //     $("#weak_pwd_tree_root").jstree(true).refresh();
            // }
            // tree_root_id = data.object_info.children.id;
            // addEventToZoneTree($("#weak_pwd_tree_root"));

            /**/
            services_info =  data.services_info;
            service_panel.detail_data = services_info;
            service_panel.total_num = services_info.length;
            service_panel_config.page_size = services_info.length;
            service_panel.refresh_list_panel(service_panel_config);
            service_panel.update_info();
        }
    );

}
function addEventToZoneTree($zone_tree) {
    $zone_tree
    .on('changed.jstree', function (e, data) {
        var $zone_tree = $('#weak_pwd_tree_root').jstree(true);
        var selected_node = $zone_tree.get_selected();
        if ( selected_node.length ) {
           arr_new = selected_node;
            if ( !$zone_tree.is_open(selected_node) && selected_node.id == tree_root_id ) {
                /* 如果是整棵树的根节点，使其保持打开状态 */
                $zone_tree.open_node(tree_root_id);
            }
        }
    })
    .on('state_ready.jstree', function (e, data) {
        var $zone_tree = $('#weak_pwd_tree_root').jstree(true);
        $zone_tree.deselect_all();
        $zone_tree.open_node(tree_root_id);
        arr_old = [];
        arr_new = [];
        var selected_node = $zone_tree.get_selected(true)[0];
        if ( !selected_node ) {
            $zone_tree.select_node(tree_root_id);
            $zone_tree.open_node(tree_root_id);
        } else {
            !$zone_tree._open_to( selected_node);
        }
    });
};


function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: ass_url,
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//应用策略
function applyStrategy(n) {
    var obj = {
        ACTION: "apply_strategy",
        name: n
    }
    var fun = function(data) {
        alert(data["mesg"]);
    }
    do_request(obj, fun);
}
//操作策略
function actionStrategy(str, id) {
    var ids;
    var arr = strategy_panel.get_checked_items();
    var error = (str == "delete" && "请选择需要删除的策略") || (str == "on" && "请选择需要启用的策略") || (str == "off" && "请选择需要禁用的策略");
    if(id) {
        ids = id;
    }else if(arr["length"]) {
        var idArr = new Array();
        for(var k in arr) {
            idArr.push(arr[k]["idView"]);
        }
        ids = idArr.join("&");
    }else {
        alert(error);
        return false;
    }

    var obj = {
        ACTION: str + "_strategy",
        ids: ids 
    };
    var fun = function(data) {
        alert(data["mesg"]);
        strategy_panel.update_info(true);
    }
    do_request(obj, fun);
}
function strategy_panel_show() {
    strategy_panel.update_info(true);
    strategy_panel.show();
}