/*
 * 描述: 类型统计页面
 *
 * 作者: pujiao
 * 公司: Capsheaf
 * 历史：
 *       2016.08.08  pujiao创建
 */
$(document).ready(function(){
	add_panel = new RuleAddPanel( add_panel_config );
	message_manager = new MessageManager( message_box_config );
	
	/* 渲染面板 */
	add_panel.render();
	message_manager.render();
	/* 设置面板关联 */
	add_panel.set_ass_message_manager( message_manager );

	read_data();
	data_obj = JSON.parse(localStorage.getItem('flow_charts'));
	$("#start_time").datepicker({
	 		
			dateFormat:"yy-mm-dd",
			yearSuffix: '年', 
			monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
			dayNamesMin: ['日','一','二','三','四','五','六'],
			onClose: function( selectedDate,obj) {
				$( "#end_time" ).datepicker( "option", "minDate", selectedDate );
				$("#start_time").change();
			}
		});
	$("#end_time").datepicker({
			dateFormat:"yy-mm-dd",
			yearSuffix: '年', 
			monthNames: ['一月','二月','三月','四月','五月','六月','七月','八月','九月','十月','十一月','十二月'],
			dayNamesMin: ['日','一','二','三','四','五','六'],
			onClose: function( selectedDate ) {
				$( "#start_time" ).datepicker( "option", "maxDate", selectedDate );
				$("#end_time").change();
			}
		}); 
		$("#ip_or_user_name").hide();
		$("#website_value").attr("disabled",true);
	!function() {
		$("#add_panel_title_for_add_panel").css("cursor", "default");
	}();
	
});
var message_manager;
var add_panel;
var message_box_config = {
	url: "/cgi-bin/type_statistics.cgi",
	check_in_id: "mesg_box_tmp",
	panel_name: "my_message_box",
};
var add_panel_config = {
	url: "/cgi-bin/type_statistics.cgi",
	check_in_id: "panel_flow_list",
	panel_name: "add_panel",
	rule_title: "统计条件",
	is_popup_tip:false,
	is_follow_tip:true,
	is_modal: false,
	modal_config: {
		modal_box_size: "m",
		modal_level: 10
	},
	footer_buttons: {              
		add: false,
		cancel: false,
		import: false,
		sub_items: [               
			{
				enable: true,
				type: "button",
				value: "统计",
				functions: {       
					onclick: "statistics()"
				}
			}
		]
	},
	event_handler: {
		before_save_data: function( add_obj,data_item ) {


		},
		after_save_data:function( add_obj,data_item ) {
	   
		},
		before_load_data: function( add_obj,data_item ) {
		
		},
		after_load_data: function( add_obj,data_item ) {
		   
		  
		},
		after_cancel_edit: function( add_obj ) {
			
		}

		
	},
	is_panel_stretchable: false,
	is_panel_closable: false,
	items_list: [
	   
		{
			title: "时间范围",
			sub_items: [
				{
					enable: true,
					type: "select",
					id: "time_range",
					name: "time_range",
					value: "",
					style: "width:100px",
					functions: {
						onchange:"time_change(this.value);"
					},
					options:
					[
							{
								text:"自定义",
								value:"custom"
							},
							{
								text:"实时",
								value:"live"
							},
							{
								text:"最近一小时",
								value:"hour"
							},
							{
								text:"最近一天",
								value:"day"
							},
							{
								text:"最近一周",
								value:"week"
							},
							{
								text:"最近一个月",
								value:"month"
							}

					],
					check: {
						type: "select-one",
						required: 1,
						check:'name|',
						// other_reg:'//',
						ass_check: function( check ) {
			
						}
					}
				},
				{
					enable: true,
					type: "text",
					id: "start_time",
					name: "start_time",
					class:"calendar",
					check:{
						type: "date",
						required: 1,
						check:'other',
						other_reg:'/^\\d{4}-\\d{2}-\\d{2}$/',
						ass_check:function(eve){
							// console.log(eve);
                            var date = $("#start_time").val();
                            if(date.length<0){
                                return "日期必填！";
                            }
                        }
					}
				  	
				},
				{
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "start_time_hour",
                    name: "start_time_hour",
                    options: select_options(24),
                    tip:"时",
                    functions:{
						"onchange": "chooice_right_time()"
					},
                    check:{
                        type:"select-one",
                        required:1,
                        ass_check: function( check ) {
                            // console.log(check);
                        }
                    }
                  
                },{
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "start_time_min",
                    name: "start_time_min",
                    options: select_options(60),
                    tip:"分  至",
                    functions:{
						"onchange": "chooice_right_time()"
					},
                    check:{
                        type:"select-one",
                        required:1,
                        ass_check: function( check ) {
                            // console.log(check);
                        }
                    }
                  
                },
				{
					enable: true,
					type: "text",
					// style: "width:81px", 
					id: "end_time",
					name: "end_time",
					class:"calendar",	
					check:{
						type: "date",
						required: 1,
						check:'other',
						other_reg:'/^\\d{4}-\\d{2}-\\d{2}$/',
						ass_check:function(eve){
                            var date = $("#end_time").val();
                            if(date.length<0){
                                return "日期必填！";
                            }
                        }
					}

				},{
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "end_time_hour",
                    name: "end_time_hour",
                    options: select_options(24),
                    tip:"时",
                    functions:{
						"onchange": "chooice_right_time()"
					},
                    check:{
                        type:"select-one",
                        required:1,
                        ass_check: function( check ) {
                            // console.log(check);
                        }
                    }
                  
                },{
                    enable: true,
                    type:"select",
                    style: "width:50px;",
                    id: "end_time_min",
                    name: "end_time_min",
                    options: select_options(60),
                    tip:"分",
                    functions:{
						"onchange": "chooice_right_time()"
					},
                    check:{
                        type:"select-one",
                        required:1,
                        ass_check: function( check ) {
                            // console.log(check);
                        }
                    }
                  
                }
			]
		},
		{
			title: "IP/用户",
			sub_items: [
				{
					enable: true,
					type: "radio",
					style: "", 
					id: "all",
					label:"所有",
					checked: true,
					name: "ip_or_user",
					value:"0",
					functions:{
						"onclick": "select_ip_or_user(this.value)"
					}
				},
				{
					enable: true,
					type: "radio",
					style: "", 
					id: "ip",
					label:"IP",
					name: "ip_or_user",
					value:"1",
					functions:{
						"onclick": "select_ip_or_user(this.value)"
					}
				},
				{
					enable: true,
					type: "radio",
					style: "", 
					label:"用户",
					id: "user",
					name: "ip_or_user",
					value:"2",
					functions:{
						"onclick": "select_ip_or_user(this.value)"
					}
				},
				{
					enable: true,
					type: "text",
					id: "ip_or_user_name",
					name:"tvalue"

				}
			]
		},
		{
			title: "应用分类/网站分类*",
			sub_items: [
				{
					enable: true,
					type: "items_group",
					style: "height:30px;line-height:20px;width:1000px;margin:-5px;", 
					sub_items:[{
						enable:true,
						id:"apply",
						name:"isurl",
						label:"应用分类",
						type:"radio",
						checked:true,
						value:"0",
						functions:{
								onclick: "select_isurl(this.value)"
							}
						},
						{
						enable:true,
						id:"apply_value",
						name:"avalue",
						type:"select",
						style:"width:150px",
						check:{
						  
						},
						options:[]
					}]
					

				},{
					enable: true,
					type: "items_group",
					style: "height:30px;line-height:20px;width:1000px;margin:-5px",
					sub_items:[{
						enable:true,
						id:"website",
						name:"isurl",
						label:"网站分类",
						type:"radio",
						value:"1",
						functions:{
							 onclick: "select_isurl(this.value)"
						},
						
					},
					{
						enable:true,
						id:"website_value",
						name:"uvalue",
						style:"width:150px",
						type:"select",
						check:{
						  
						},
						options:[{
								text:"所有网站分类",
								value:"1"
							}]
						

		   
					}]
				  

				}
			]
		}
		]
};

//存储统计条件，并为页面上赋值
function recoverSetting(){
	
	var obj = {};
	if(data_obj != null){
		var flow_type = data_obj.flow_type == 'apply_charts' ? 'apply_charts_obj':'net_charts_obj';
		var data_array = data_obj[flow_type];
		$.each(data_array,function(i,v){
            var name = v.name;
            var value = v.value;
            obj[name]= value;
        });
		for(var k in obj){
			if(k == "time_range"){
				$("#"+k).val(obj[k]);
				if(obj[k] == "live"){
					$("#time_range").parent().siblings().hide();

				}
				else{
					$("#time_range").parent().siblings().show();

				}
			}
			else if(k == "ip_or_user" || k == "isurl" ){
				$('input[name="'+k+'"][value="'+obj[k]+'"]').attr("checked",true);
				if(k == "ip_or_user" ){
					if(obj[k] == 0){
						$("#ip_or_user_name").val("");
						$("#ip_or_user_name").hide();
					}
					else{
						$("#ip_or_user_name").val(obj['tvalue']);
						$("#ip_or_user_name").show();
					}
					
				}
				
			}
			else if(k == "avalue"){
				$("#apply_value").val(obj[k]);
				$("#apply_value").removeAttr("disabled");

				$("#website_value").val("");
				$("#website_value").attr("disabled",true);
			}
			else if(k == "uvalue"){
				$("#website_value").val(obj[k]);
				$("#website_value").removeAttr("disabled");
				$("#apply_value").val("");
				$("#apply_value").attr("disabled",true);


			}
			else{
				$("#"+k).val(obj[k]);
			}
		}

	}
	
	
}
//将小时转换为两位数
function convertTime(hour){
	hour = ( (hour+"").length > 1 ) ? hour : "0" + hour;
	return hour;
}

function time_change(val){
	var now = new Date();  //获取当前
	if (val == 'live') {
		$("#time_range").parent().siblings().hide();
	}else{
		$("#time_range").parent().siblings().show();
		if (val != 'custom') {
			var end_min = convertTime(now.getMinutes());
			$('#end_time_min,#start_time_min').val(end_min);
			var end_hour = convertTime(now.getHours());
			$("#start_time_hour,#end_time_hour").val(end_hour);
			$("#start_time,#end_time").datepicker("setDate",now);
			switch (true){
				case (val == 'hour'):
					$('#start_time_hour').val(convertTime(Number(end_hour)-1));break;
				case (val == 'day'):
					var start_time = now.subductionDays(1);break;
				case (val == 'week'):
					var start_time = now.subductionWeeks(1);break;
				case (val == 'month'):
					var start_time = now.subductionMonths(1);break;
			}
			val == 'hour'? true:$("#start_time").datepicker("setDate",start_time.Format("yyyy-MM-dd"));
		}
		$("#start_time,#end_time").change();
	}
}
//初始化小时和分钟的选项值
function select_options(val){
    var options = [];
    for(var i = 0; i<val; i++){
       var  option ={};
        i = i + "";
        if(i.length<2){
        i = "0"+i;
        }
        else{
        }
        option.value = i;
        option.text = i;
        options.push(option);
    }
    return options;
}
function select_isurl(val){
	if(val == 0){
		$("#apply_value").removeAttr("disabled");
		$("#website_value").attr("disabled",true);
		$("website_value").val("");
	}
	else{
		$("#website_value").removeAttr("disabled");
		$("#apply_value").attr("disabled",true);
		$("#apply_value").val("");
	}

}

function select_ip_or_user(val){
	if(val == 0){
		$("#ip_or_user_name").hide();
	}else if(val == 1){
		$("#ip_or_user_name").attr("placeholder","请输入IP地址/网段");
		$("#ip_or_user_name").val("");
		$("#ip_or_user_name").show();
	}else{
		$("#ip_or_user_name").attr("placeholder","请输入用户名");
		$("#ip_or_user_name").val("");
		$("#ip_or_user_name").show();
	}

}

//点击统计按钮触发事件
function statistics(){
	// before_statistics();//统计之前检查合法性
	if( add_panel.is_input_data_correct() ){
		data_obj = data_obj == null ? {} : data_obj ;
		var list= $('input:radio[name="isurl"]:checked').val();
		var obj = $("#add_panel_body_form_id_for_add_panel").serializeArray();
	
		if(list == 0){
			var avalue = $("#apply_value").val();
			if(!avalue){
				message_manager.show_popup_error_mesg("请选择应用分类！");
				
			}else{
				var atext= $("#apply_value").find("option:selected").text();
				obj.push({"name":"atext","value":atext});
				data_obj.flow_type = 'apply_charts';
				data_obj.apply_charts_obj = obj ;
				localStorage.setItem('flow_charts',JSON.stringify(data_obj));
	  			window.location=('/cgi-bin/apply_type_charts.cgi');
			}
		}
		else{
			var tvalue = $("#website_value").val();
			if(!tvalue){
				message_manager.show_popup_error_mesg("请选择网站分类！");
				
			}
			else{
				var utext= $("#website_value").find("option:selected").text();
				obj.push({"name":"utext","value":utext});
				data_obj.flow_type = 'net_charts';
				data_obj.net_charts_obj = obj ;
				localStorage.setItem('flow_charts',JSON.stringify(data_obj));
				// top.frames.mainFrame.AsyncModify(obj);
				window.location =('/cgi-bin/net_classify_flow_charts.cgi');
			}
		}
	}else{
		message_manager.show_popup_error_mesg( "请正确填写各字段" );
		return;
	}


}

//初始化应用分类和网站分类选项
function read_data(){
    // 获取数据
   
    var sending_data = {
        ACTION: "read_data"
    }

    function ondatareceived( data ) {
        // console.log(data);
        var apply_option_str = '<option value="" disabled selected>请选择应用分类</option>';
        var website_option_str = '<option value="" disabled selected>请选择网站分类</option>';
       
        for(var i = 0; i < data.url_classify_data.length; i++ ){
        	var id = data.url_classify_data[i].split(',')[0];
         	var value = data.url_classify_data[i].split(',')[1];
            website_option_str += '<option value="'+id +'">'+value+'</option>';    
        }
         for(var i = 0; i < data.apply_classify_data.length; i++ ){
         	var id = data.apply_classify_data[i].split(',')[0];
         	var value = data.apply_classify_data[i].split(',')[1];
           apply_option_str += '<option value="'+id +'">'+value+'</option>';    
        }
        $("#apply_value").html('');
        $("#website_value").html('');
        $("#apply_value").append(apply_option_str);
        $("#website_value").append(website_option_str);
        recoverSetting();
    }

   do_request( sending_data, ondatareceived );
}


function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: "/cgi-bin/type_statistics.cgi",
        dataType: "json",
        data: sending_data,
        async: true,
        error: function(request){
            message_manager.show_popup_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function chooice_right_time(){
	var st = $('#start_time').val();
	var et = $('#end_time').val();
	var sth = $('#start_time_hour').val();
	var eth = $('#end_time_hour').val();
	var stm = $('#start_time_min').val();
	var etm = $('#end_time_min').val();
	$('#start_time_hour,#end_time_hour,#start_time_min,#end_time_min')
	.children('option').removeAttr('disabled');
	if (st == et) {
			for (var i = 0; i < (Number(sth)+1); i++) {
				$('#end_time_hour option').eq(i-1).attr('disabled', 'disabled');
			}
			for (var i = Number(eth); i < 24; i++) {
				$("#start_time_hour option").eq(i+1).attr('disabled', 'disabled');
			}

		if (sth == eth) {
				for (var i = 0; i < (Number(stm)+1); i++) {
					$('#end_time_min option').eq(i).attr('disabled', 'disabled');
				}
				for (var i = Number(etm); i < 60; i++) {
					$('#start_time_min option').eq(i).attr('disabled', 'disabled');
				}
		}

	}
}