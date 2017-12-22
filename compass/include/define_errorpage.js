$(document).ready(function(){
	list_panel.render();
	add_panel.render();
	add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    initOption();
   

	add_panel.hide();
	list_panel.update_info(true);
})

var ass_url = "/cgi-bin/define_errorpage.cgi";
var list_panel_render ={
	'action': {
        render: function( default_rendered_text, data_item ) {
   			var enable_images = ['on.png','off.png'];
   			var button_texts = ['启用','禁用'];
   			var img,btn_text;
   			if(data_item.enable == 'on'){
   				img = enable_images[0];
   				btn_text = button_texts[0]
   			}else{
   				img = enable_images[1];
   				btn_text = button_texts[1];
   			}
            var action_buttons = [{
	                enable: true,
	                id: "enable_btn",
	                name: "enable_btn",
	                class: "action-image",
	                button_icon: img,
	                button_text: btn_text,
	                value: data_item.enable,
            },{
	                enable: true,
	                id: "edit_item",
	                name: "edit_item",
	                class: "action-image",
	                button_icon: "edit.png",
	                button_text: "编辑",
	                value: data_item.id,
	                functions: {
	                    onclick: "list_panel.edit_item(this.value);"
	                }
            },{
	                enable: true,
	                id: "review_button",
	                name: "review_button",
	                class: "action-image",

	                button_icon: "search16x16.png",
	                button_text: "查看详情",
	                value: data_item.content,
	                functions: {
	                    onclick: "openWindow(this.value);"
	                }
            },{
	                enable: true,
	                id: "delete_button",
	                name: "delete_button",
	                class: "action-image",
	                button_icon: "delete.png",
	                button_text: "删除",
	                value: data_item.type,
	                functions: {
	                    onclick: "list_panel.delete_item(this.value);"
	                }
            }];
            var buttons = PagingHolder.create_action_buttons( action_buttons );
            var buttons$ =$(buttons);
            	buttons$[0].onclick =function(){
                    
            		toggle_enable(data_item);
            	}
            
            return buttons$;
        }
    }
}
var list_panel_config ={
	
    url: ass_url, /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",  /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 20,                  /* ===可选===，控制数据项默认加载多少条，默认是15，此处可以在加载数据过程中更改，
                                                   更改方法是从服务器加载数据到浏览器时，传一个page_size字段到浏览器 */
     panel_title: "列表面板",        // ===可选===，面板的标题 
   
    is_panel_closable: false,        /* ===可选===，默认是false，控制面板是否可关闭 */
    is_modal: false,                /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次时创建，并且在is_modal为true时才生效 */
        					       /* ===可选===，默认是l，有l、m、s三种尺寸的模态框 */
        modal_level: 10,            /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
        modal_box_position: "fixed" /* ===可选===，position属性值，目前未使用，未调试成功，建议不使用此字段 */
    },
    is_default_search: false,        /* ===可选===，默认是true，控制搜索框是否展示，
                                                    注意：这里的搜索条件会在用户每次加载数据前提交到服务器，搜索的实现，
                                                要在服务端根据提交上来的条件自行实现，这里并不会提供默认的搜索功能
                                     */
    default_search_config: {        /* ===可选===，只有当is_default_search为true时才生效 */
        input_tip: "输入某字段关键字以查询...",   /* ===可选===，控制搜索输入框内的提示，默认是“输入关键字以查询...” */
        title: "某字段关键字"                     /* ===可选===，控制搜索输入框左边的提示，默认无提示 */
    },
    is_paging_tools: false,          /* ===可选===，默认是true，控制是否需要翻页工具 */
    is_load_all_data: true,         /* ===可选===，默认是true
                                                    目前存在两种情况的数据加载，第一种是从服务器加载全部可显示数据，然后在本地
                                                翻页操作时不再向服务器请求数据；第二种情况是数据太多，没法全部加载在本地，因此
                                                需要一页一页地去服务器请求数据。如果是第二种情况，那么这里要设置成false，每次
                                                翻页时重新向服务器请求数据。
                                                    在第一种情况中，页面的勾选操作是可以记忆的，比如勾选了部分数据，然后翻页，在
                                                翻页回来，是可以保持勾选状态的，但是第二种情况中，勾选功能不能记忆
                                                 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    check_obj: null,                /* ===可选===，当有数据需要检查才刷新时提交此对象 */
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
    panel_header: [{
        enable: true,
        type: "text",
        title: "序号",
        name: "id",
        width: "5%",
        td_class:"align-center"
    },{
        enable: true,
        type: "text",
        title: "错误类型",
        name: "description",
        width: "85%",
        td_class:"align-center"
    }, {
        enable: true,
        type: "text",
        title: "操作",
        name: "action",
        width: "10%",
        td_class:"align-center"
    }],
    top_widgets: [                  /* ===可选=== */
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建",
            functions: {
                onclick: "add_panel.show();"
            }
        },
        {
            "enable": true,
            type: "image_button",
            "id": "delete_selected",
            "name": "delete_selected",
            "class": "",
            "button_icon": "delete.png",
            "button_text": "删除选中",
            "functions": {
                onclick: "check_delete_selected_items()"
            }
        }
    ],
}
var add_panel_config = {
    url: ass_url,
    check_in_id: "add_panel",
    panel_name: "add_panel",
    rule_title: "错误页面配置",
    is_modal: true,
    modal_config: {
        modal_box_size: "m",
        modal_level: 10
    },
    footer_buttons:{
    	add:true,
    	cancel:true,
    	sub_items:[{
    		enable:true,
    		type:'button',
    		id:'review',
    		name:'review',
    		value:'预览',
    		functions:{
    			onclick:"reviewPage();"
    		}
    	}]
    },
    event_handler: {
        before_save_data: function( add_obj,data_item ) {
           	return data_item = data_item + '&description='+$("#type").find("option:selected").text();
        },
        before_load_data: function( add_obj,data_item ) {
            // console.log("加载前");
        },
        after_load_data: function( add_obj,data_item ) {
           // console.log("加载后");
        },
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [
    	{
            title: "是否启用:",
            sub_items: [
                {
                    enable: true,
                    type: "checkbox",
                    id: "enable",
                    name: "enable",
        			
                    functions: {
                    },
                   
                }
            ]
        },
        {
            title: "错误类型:",

            sub_items: [
                {
                    enable: true,
                    type: "select",
                    
                    id: "type",
                    name: "type",
                   	tip:"已配置的类型,将不能配置",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'name',
                        //other_reg:'!/^\$/',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        },
        {
            title: "显示内容(HTML):",
            sub_items: [
                {
                    enable: true,
                    type: "textarea",
                    style: "",
                    id: "content",
                    name: "content",
                    value: "",
                    style:"width:500px;height:200px",
                    functions: {
                    },
                    check: {
                        type: "text",
                        required: 1,
                        check:'note',
                        ass_check: function( check ) {

                        }
                    }
                }
            ]
        }
        
        
    ]
};
var list_panel = new PagingHolder(list_panel_config);
var add_panel = new RuleAddPanel(add_panel_config);
//用于加密解密
var HtmlUtil = {
    /*1.用浏览器内部转换器实现html转码*/
    htmlEncode:function (html){
        //1.首先动态创建一个容器标签元素，如DIV
        var temp = document.createElement ("div");
        //2.然后将要转换的字符串设置为这个元素的innerText(ie支持)或者textContent(火狐，google支持)
        (temp.textContent != undefined ) ? (temp.textContent = html) : (temp.innerText = html);
        //3.最后返回这个元素的innerHTML，即得到经过HTML编码转换的字符串了
        var output = temp.innerHTML;
        temp = null;
        return output;
    },
    /*2.用浏览器内部转换器实现html解码*/
    htmlDecode:function (text){
        //1.首先动态创建一个容器标签元素，如DIV
        var temp = document.createElement("div");
        //2.然后将要转换的字符串设置为这个元素的innerHTML(ie，火狐，google都支持)
        temp.innerHTML = text;
        //3.最后返回这个元素的innerText(ie支持)或者textContent(火狐，google支持)，即得到经过HTML解码的字符串了。
        var output = temp.innerText || temp.textContent;
        temp = null;
        return output;
    }
};

function do_request(sending_data,fn){
     $.ajax({
        type: 'POST',
        url: ass_url,
        data: sending_data,
        dataType: 'json',
        async: true,
        error: function(request){
           console.log("返回数据格式有误,请检查");
        },
        success: fn
    });
}
function creatrOption(data,e){
	var html = "";
		for(var i = 0 ,item;item = data.data[i++]; ){
			html +='<option value="'+item.code+'">'+item.text+'</option>';
		}
		$("#"+e).html("");
		$("#"+e).append(html);
}
function initOption(){
	var sending_data = {
		ACTION:'initOption',
		panel_name:'add_panel'
	}
	do_request(sending_data,function(data){
		creatrOption(data,"type");
	})
}
function openWindow(str){
	OpenWindow=window.open("错误页面预览", "newwin", "height=500, width=1000,top=200, left= 310,toolbar=no ,scrollbars="+scroll+",menubar=no"); 
　　//写成一行 
　　OpenWindow.document.write("<TITLE>实时预览</TITLE>") 
　　OpenWindow.document.write("<BODY BGCOLOR=#ffffff>") 
　　OpenWindow.document.write(str); 
　　OpenWindow.document.write("</BODY>") 
　　OpenWindow.document.write("</HTML>") 
　　OpenWindow.document.close() 
}
function reviewPage(){
	var str = $("#content").val();
	openWindow(str);
}
function toggle_enable(data_item){
	list_panel.request_for_json({
		ACTION:"toggle_enable",
		panel_name:"add_panel",
		id:data_item.type,
		enable:(data_item.enable == "on") ? 'off':'on'
	},function(data){
		if(add_panel.is_operation_succeed(data)){
			list_panel.update_info(true);
		}else{
			add_panel.show_error_mesg(data.mesg);
		}

	})
}