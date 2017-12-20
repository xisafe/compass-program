/*
 * 描述: 测试添加模板和列表模板类
 *          【智能路由页面配置】
 * 作者: 
 * 历史：2014-11-20  xinzhiwei创建
 */

function do_src_type_change(element){
    var value = element.value;

    if(value == "no_type"){
        $("#routing_src_ip_addr_textarea").hide();
        $("#routing_src_left_right_select_box").hide();
        
    }else if(value == "ip_addr_type"){
        $("#routing_src_ip_addr_textarea").show();
        $("#routing_src_left_right_select_box").hide();
        
    }else if(value == "addr_member_type"){
        $("#routing_src_left_right_select_box").show();
        $("#routing_src_ip_addr_textarea").hide();
    }
}
function do_dst_type_change(element){
    var value = element.value;
    if(value == "no_type"){
        $("#isp_name_select_options_item_id").hide();
        $("#routing_dst_ip_addr_textarea").hide();
        
    }else if(value == "isp_addr_type"){
        $("#isp_name_select_options_item_id").show();
        $("#routing_dst_ip_addr_textarea").hide();

    }else if(value == "ip_addr_type"){
        $("#routing_dst_ip_addr_textarea").show();
        $("#isp_name_select_options_item_id").hide();
    }
    var height = $("#modal_border_box_test_add_panel").height();
    $("#TransparentBorder_test_add_panel").css('height',height);
}
function uplinks_box_left_to_right(){
    var selected = $("#uplinks_left_select_box option:selected");
    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var tt = "<option value=" +val+ ">"+txt+"</option>";
            $("#uplinks_right_select_box").append(tt);
        $( option ).remove();
    });
    save_selected_uplinks();
}
function uplinks_box_right_to_left(){
    var selected = $("#uplinks_right_select_box option:selected");
    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var tt = "<option value=" +val+ ">"+txt+"</option>";
            $("#uplinks_left_select_box").append(tt);
        $( option ).remove();
    });
    save_selected_uplinks();
}

function save_selected_uplinks(){
    var options = $("#uplinks_right_select_box option");
    var links_str = "";
    var links_array = new Array();

    options.each(function(){
        var option = this;
        var val  = $( option ).val();
        links_array.push( val );

    });
    links_str = links_array.join( "&" );
    $( "#SELECTED_UPLINKS" ).val( links_str );
    
}

function addr_nodes_box_left_to_right(){

    var selected = $("#routing_src_left_select_box option:selected");

    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var type = $( option ).attr( "class" );

        if ( type == "left_addr_nodes" ) {
            type ="right_addr_nodes";
            var tt = "<option class=" + type + " value=" +val+ ">"+txt+"</option>";
            $("#right_addr_group_tip").before(tt);
        }
        else if( type == "left_addr_groups" ) {
            type ="right_addr_groups";
            var tt = "<option class=" + type + " value=" +val+ ">"+txt+"</option>";
            $("#hidden_right_line").before(tt);
        }
        $( option ).remove();
    });

    save_selected_ip_nodes();

}
function addr_nodes_box_right_to_left(){

    var selected = $("#routing_src_right_select_box option:selected");
    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var type = $( option ).attr( "class" );

        if(type =="right_addr_nodes"){
            type ="left_addr_nodes";
            var tt = "<option class=" + type + " value=" +val+ ">"+txt+"</option>";
            $("#left_addr_group_tip").before(tt);
        }
        else if(type == "right_addr_groups"){
            type ="left_addr_groups";
            var tt = "<option class=" + type + " value=" +val+ ">"+txt+"</option>";
            $("#hidden_left_line").before(tt);
        }
        $( option ).remove();
    });
    save_selected_ip_nodes();
}

function save_selected_ip_nodes() {

    var options = $("#routing_src_right_select_box option");
    var nodes_str = "";
    var nodes_array = new Array();
    var groups_str ="";
    var groups_array = new Array();

    options.each(function(){
        var option = this;
        var val  = $( option ).val();
        var type = $( option ).attr("class");
        if( type == "right_addr_nodes"){
            nodes_array.push( val );
        }else if( type == "right_addr_groups" ){
            groups_array.push( val );
        }

    });

    nodes_str = nodes_array.join( "|" );
    groups_str = groups_array.join("|");
    $( "#SELECTED_IP_NODE" ).val( nodes_str );
    $( "#SELECTED_IP_GROUP" ).val( groups_str );

}

var message_box_config = {
    url: "/cgi-bin/smart_routing.cgi",
    check_in_id: "smart_routing_mesg_box",
    panel_name: "my_message_box"
}

var add_panel_config = {
    url: "/cgi-bin/smart_routing.cgi",
    check_in_id: "smart_routing_add_panel",
    panel_name: "test_add_panel",
    rule_title: "智能路由",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_cancel_edit:function(add_obj){
        },
        after_cancel_edit:function(add_obj){
            resume_left_select_data();

            $( "#routing_name" ).attr( "readonly", false );
            $( "#routing_name" ).val("");

            $("#routing_src_ip_addr_textarea").hide();
            $("#routing_src_ip_addr_textarea").val("");

            $("#routing_src_left_right_select_box").hide();  //2015.03.05 将源地址节点和地址组选项框隐藏

			$( "#routing_src_right_select_box option:enabled" ).remove();
            $( "#SELECTED_IP_NODE" ).val("");
            $( "#SELECTED_IP_GROUP" ).val("");

            $("#isp_name_select_options_item_id").hide();  //2015.03.05 将ISP选项列表隐藏
            $("#routing_dst_ip_addr_textarea").hide();
            $("#routing_dst_ip_addr_textarea").val("");

            
            $("#uplinks_right_select_box").empty();
            $("#SELECTED_UPLINKS").val("");

            do_uplinks_change();
        },
        before_load_data: function( add_obj, data_item ) {
            resume_left_select_data();
        },
        after_load_data: function ( add_obj, data_item ) {
            save_selected_uplinks();   // 2015.03.05 辛志薇添加
            save_selected_ip_nodes();  // 2015.03.05 辛志薇添加
            var src = data_item.routing_src;
            if(src == ""){
                $("#src_type").val("no_type");  //首先必须要把源类型的值改成"no_type"
                $("#routing_src_ip_addr_textarea").hide();
                $("#routing_src_left_right_select_box").hide();
            }else if( /IP:/.test(src) ){
                $("#src_type").val("ip_addr_type");  //首先必须要把源类型的值改成‘网络/IP’
                $("#routing_src_ip_addr_textarea").show();
                $("#routing_src_left_right_select_box").hide();

                var pos = src.search(/:/);
                // $("#routing_src_ip").val( src.substring(pos+1) );
                var text = src.substring(pos+1);
                var v = text.replace(/\|/,'\n');
                $("#routing_src_ip").val( v );

            }else if( /IP_NODE:/.test(src) || /IP_GROUP:/.test(src) ){
                $("#src_type").val("addr_member_type");   //首先必须要把源类型的值改成‘地址成员’
                $("#routing_src_ip_addr_textarea").hide();
                $("#routing_src_left_right_select_box").show();

                var _pos1    = src.indexOf(':');
                var _pos_bwn = src.search(/\|IP_GROUP/);
                var _pos2    = src.indexOf(':', _pos1+1);

                var selected_nodes = src.substring( _pos1+1, _pos_bwn );
                var selected_groups = src.substring( _pos2+1 );
                
                
                var nodes_arr = selected_nodes.split( "|" );
                if ( selected_nodes == "" ) {   nodes_arr = [];  }
                var options = "";
                for ( var i = 0; i < nodes_arr.length; i++ ) {
                    var item = nodes_arr[i];
                    var type ="right_addr_nodes";
                    $("#routing_src_left_select_box option[value="+item+"]").remove();
                    options += '<option class="' + type + '" value="' + item + '">' + item + '</option>';
                }
                $( "#routing_src_right_select_box option:enabled" ).remove();
                $( "#right_addr_group_tip" ).before( options );
                
                var groups_arr = selected_groups.split( "|" );
                if ( selected_groups == "" ) {   groups_arr = [];  }
                var options = "";
                for ( var i = 0; i < groups_arr.length; i++ ) {
                    var item = groups_arr[i];
                    var type ="right_addr_groups";
                    $("#routing_src_left_select_box option[value="+item+"]").remove();
                    options += '<option class="' + type + '" value="' + item + '">' + item + '</option>';
                }

                $( "#hidden_right_line" ).before( options );

                $("#SELECTED_IP_NODE").val( selected_nodes );
                $("#SELECTED_IP_GROUP").val( selected_groups );

            }

            var dst = data_item.routing_dst;
            if(dst ==""){
                $("#dst_type").val("no_type");   //首先必须要把目的类型的值改成"no_type"
                $("#isp_name_select_options_item_id").hide();
                $("#routing_dst_ip_addr_textarea").hide();
        
            }else if( /ISP:/.test(dst) ){
                $("#dst_type").val("isp_addr_type");   //首先必须要把目的类型的值改成"isp_addr_type"
                $("#isp_name_select_options_item_id").show();
                $("#routing_dst_ip_addr_textarea").hide();

                var pos1 = dst.search(/:/);
                $("#isp_name_select_options").val( dst.substring(pos1+1) );

            }else if( /IP:/.test(dst) ){
                $("#dst_type").val("ip_addr_type");   //首先必须要把目的类型的值改成"ip_addr_type"
                $("#isp_name_select_options_item_id").hide();
                $("#routing_dst_ip_addr_textarea").show();

                var pos2 = dst.search(/:/);
                // $("#routing_dst_ip").val( dst.substring(pos2+1) );
                var text = dst.substring(pos2+1);
                var v = text.replace(/\|/,'\n');
                $("#routing_dst_ip").val( v );
            }
            
            var links = data_item["links"];
            $( "#SELECTED_UPLINKS" ).val(links);
            var arr = links.split("&");
            if ( links == "" ) {   arr = [];  }
            var options = "";

            for ( var i = 0; i < arr.length; i++ ) {
                var item = arr[i];
                var item_val = UPL_HASH[item];
                $("#uplinks_left_select_box option[value="+item+"]").remove();
                options += '<option value="' + item + '">' + item_val + '</option>';
            }
			$( "#uplinks_right_select_box" ).empty();
            $( "#uplinks_right_select_box" ).append( options );
            save_selected_uplinks();
            do_uplinks_change();
            var sch = data_item["scheduler"];
            $("#scheduler option[value="+sch+"]").attr("selected","selected");

            if ( data_item.id != "" ) {
                $( "#routing_name" ).attr( "readonly", true );
            }
            
            var id = data_item["id"];
            $("#position_list option:eq("+id+")").attr("selected", "selected");

            var enabled = data_item["enabled"];
            if(enabled == "on"){  $("#enabled_id").attr("checked", "checked");  }
            else{  $("#enabled_id").attr("checked", "");  }

            var height = $("#modal_border_box_test_add_panel").height();
            $("#TransparentBorder_test_add_panel").css('height',height);
        },
        before_save_data: function ( add_obj, sending_data ) {
            var s = typeof(sending_data); //s="object" 说明sending_data是object类型而非string类型
            // 所以下面要做的就是先把sending_data转换成为string类型
            var data = "";
            for(item in sending_data){
                data += item + "=" + sending_data[item];   // 要用中括号运算符[]！
                  // 注意sending_data.item是不好使的!!!导致每一项的值都是undefined，即ACTION=undefined&
                  // panel_name=undefined&id=undefined...可能就是因为.运算符的优先级和+号优先级的问题，
                  // 也可能就是.运算符不能被正确解析从而无法求值[测试结果证明就是.运算符不能被正确解析]
                data += "&";
            }
            var pos = data.search(/&scheduler/);  // bug修复：data必须是string类型，方法才能执行成功
            var pos_1 = data.indexOf('=', pos);              // bug修复：同上
            var pos_2 = data.indexOf('&', pos_1);            // bug修复：同上
            var scheduler = data.substring(pos_1+1, pos_2);  // bug修复：同上
            var uplinks = $( "#SELECTED_UPLINKS" ).val();
            if(uplinks == "")   {
                list_panel.show_error_mesg('请配置使用至少一条链路！');
                return false;
            }
            if( scheduler == "wlb" ){
                var total_num = list_panel.total_num;
                var count = 0;
                var data_item = null;
                for(var i=0; i<total_num-1; i++){
                    data_item = list_panel.get_item(i);
                    if(data_item['scheduler'] == "wlb"){
                        count = count +1;
                    }
                }
                if(parseInt(count) == 4){
                    list_panel.show_error_mesg('对不起，调度策略为加权最小带宽的路由规则最多允许建立4条！');
                    return false;
                }
                
            }

                return sending_data;
        },
        after_save_data: function ( add_obj, received_data ) {
            if ( received_data.status == 0 ) {
                $("#routing_src_right_select_box option:enabled").remove();
                $( "#uplinks_right_select_box option" ).remove();
                $( "#routing_name" ).attr( "readonly", false );
                $( "#routing_name" ).val("");
                list_panel.show_apply_mesg("路由规则已改变，需要重新应用以使规则生效");
                init_position_list();
                do_uplinks_change();
            }else{
                resume_left_select_data();  // 最新修改：添加失败时要把用户上次从左边选到右边的项还原回去！
            }
        }
    },
    items_list: [
    {
        title: "名称 *",
        sub_items: [
            {
                enable: true,
                type: "text",
                id  : "routing_name",
                name: "routing_name",
                tip: "",
                placeholder: "请输入规则名称",
                functions: {
                },
                check: {                /* ==可选==，如果要对字段进行检查，填写此字段 */
                    type: "text",       /* **必填** */
                    required: 1,        /* **必填** */
                    check: 'name|',     /* **必填** */
                    ass_check: function( check ) {
                    }
                }
            }
         ]
    }, {
        title: "目标 *",
        sub_items: [
        {
            enable: true,
            type: "select",
            id:"dst_type",
            name: "dst_type",
            label:"类型",
            style: "height: 20px; width: 169px;",
            options: [
                {
                    value :"no_type",
                    text :"<任意>",
                    selected :true
                },{
                    value : "isp_addr_type",
                    text : "ISP地址段"
                },{
                    value : "ip_addr_type",
                    text : "指定IP"
                }
            ],
            functions:{
                onchange: "do_dst_type_change(this);"
            }
        }, {
            enable: true,
            type: "select",
            id:"isp_name_select_options",
            name: "isp_name_select_options",
            label:"ISP地址段",
            item_id:"isp_name_select_options_item_id",
            style: "height:20px; width:100px;",
            options:[]
        }, {
            enable: true,
            type: "textarea",
            id:"routing_dst_ip",
            name: "routing_dst_ip_addr_textarea",
            label: "请输入网络/IP(一行一条)",
            item_id:"routing_dst_ip_addr_textarea",
            item_style: "display:inline-block;",
            check: {
                type:"textarea",
                required:0,
                check: 'ip|ip_mask',     /* **必填** */
                ass_check: function( check ) {
                }
            }
        }]
    }, /*{
        title: "服务/端口",
        sub_items: [{
            enable: true,
            type: "select",
            name: "protocal",
            label:"协议",
            style: "height: 20px; width: 100px;",
            options:[{
                value:"TCP",
                text:"TCP"
            }]
        }]
    },*/ {
        title: "使用链路*",
        id:"uplinks_left_right_select_box",
        name:"uplinks_left_right_select_box",
        sub_items:[
        {
            enable: true,
            type: "select",
            label: "可选的链路",
            id: "uplinks_left_select_box",
            name:"uplinks_left_select_box",
            style: "height: 100px;",
            item_style: "width: 200px;",
            multiple: true,
            options: []
        },{
            enable: true,
            type: "items_group",
            item_style: "width: 60px;",
            item_class: "align-center",
            sub_items: [
                {
                    enable: true,
                    type: "button",
                    id: "add",
                    value: ">>",
                    functions: {
                        onclick: "uplinks_box_left_to_right(); do_uplinks_change();"
                    }
                },{
                    enable: true,
                    type: "button",
                    id: "del",
                    value: "<<",
                    functions: {
                        onclick: "uplinks_box_right_to_left(); do_uplinks_change();"
                    }
                },{
                    enable: true,
                    type: "label",   //为了让上面两个button的高度居中就在它们下面添加一个label并设置高为18px宽为50px
                    value: "",
                    item_style: "height: 3px;width: 43px;"
                },{
                    enable: true,
                    type: "text",
                    id: "SELECTED_UPLINKS",
                    name: "SELECTED_UPLINKS",
                    item_style:"width:6px; display:none;"
                }
            ]
        },{
            enable: true,
            type: "select",
            label: "已选的链路",
            id: "uplinks_right_select_box",
            name: "uplinks_right_select_box",
            style: "height: 100px;",
            item_style: "width: 200px;",
            multiple: true,
            options: []
        }]
    }, /*{
        title: "生效时间",
        sub_items: [{
            enable: true,
            name: "time",
            type: "select",
            options:[]
        }]
    },*/ {
        title: "调度策略",
        sub_items: [{
            enable: true,
            type: "select",
            id:"scheduler",
            name: "scheduler",
            style:"height:20px; width:200px;",
            disabled:true,
            options:[
            {
                value:"none",
                text:"无"
            },{
                value:"rr",
                text:"轮询"
            },{
                value:"wrr",
                text:"加权轮询"
            },{
                value:"br",
                text:"带宽比例"
            },{
                value:"wlb",
                text:"加权最小流量"
            }]
        }]
    },{
        title:"其他",
        type:"items_group",
        sub_items: [
        {
            enable: true,
            type:"select",
            name:"position",
            id:"position_list",
            label:"位置",
            style:"height:20px; width:169px;",
            options:[
            {
                value:"first_line",
                text:"第一条"
            },{
                id:"last_line_position",
                value:"last_line",
                text:"最后一条",
                selected:true
            }]
        }, {
            enable:true,
            type: "checkbox",
            id:"enabled_id",
            checked: true,
            name:"enabled",
            label:"启用"
        }]
    }]
}
function do_uplinks_change(){

    var options_arr = $("#uplinks_right_select_box  option");
    if(options_arr.length > 1){
        $("#scheduler").attr("disabled", false );
        $("#scheduler option:eq(0)").attr("disabled", true );
        $("#scheduler option:eq(1)").attr("selected", true );
        $("#scheduler option:gt(0)").attr("disabled", false );
    }
    else if(options_arr.length == 1){
        $("#scheduler").attr("disabled", false );
        $("#scheduler option:eq(0)").attr("disabled", false );
        $("#scheduler option:eq(0)").attr("selected", true );
        $("#scheduler option:gt(0)").attr("disabled", true );
    }
    else if(options_arr.length == 0){
        $("#scheduler").attr("disabled", true );
    }
}
var list_panel_actions_render = {
    'checkbox': {
        render: function( default_rendered_text, data_item ) {
            if ( data_item.IS_DEFAULT_ROUTING == "true" ) {
                return "";
            } else {
                return default_rendered_text;
            }
        }
    },
    'routing_src':{
        render: function( default_rendered_text, data_item ){

            var text = default_rendered_text;
            if( text == "" ) {
                text = "全部";
            }else if( /IP:/.test(text) ){
                text = text.replace('IP:', 'IP地址:');
                // text = text.replace('\|','\n');   不好的一点就是只能替换一个！要用全局替换模式
                // text = text.replace(/\|/g, "\n");  全局替换哦
                var replace_str = '<ul>';
                var arr = text.split("|");  // var arr = text.split(/\|/);也是对的
                for(var i=0; i<arr.length; i++){
                    replace_str += '<li>'+ arr[i] +'</li>';
                }
                replace_str += '</ul>';
                text = replace_str;
            }else if(/IP_NODE:/.test(text) || /IP_GROUP:/.test(text) ){
                text = text.replace(/IP_NODE:/, "地址节点:");
                text = text.replace(/IP_GROUP:/, "地址组:");
                var replace_str = '<ul>';
                var arr = text.split("|");  // var arr = text.split(/\|/);也是对的
                for(var i=0; i<arr.length; i++){
                    replace_str += '<li>'+ arr[i] +'</li>';
                }
                replace_str += '</ul>';
                text = replace_str;
            }
            return text;
        }
    },
    'routing_dst':{
        render: function( default_rendered_text, data_item ){
            var text = default_rendered_text;
            if( text == "" ) {
                text = "全部";
            }else if( /IP:/.test(text) ){
                text = text.replace('IP:', 'IP地址:');
                var replace_str = '<ul>';
                var arr = text.split("|");  // var arr = text.split(/\|/);也是对的
                for(var i=0; i<arr.length; i++){
                    replace_str += '<li>'+ arr[i] +'</li>';
                }
                replace_str += '</ul>';
                text = replace_str;
            }
            else if( /ISP:/.test(text) ){
            }
            return text;
        }
    },
    'links':{
        render: function( default_rendered_text, data_item ){
            var text = default_rendered_text;
            if(text ==""){  return text;  }
            var links = text.split(/&/);
            var len = links.length;
            var uplink = "";

            for(var i=0; i<len; i++){
                uplink = links[i];
                var reg = new RegExp( uplink );   // 技巧：因为这里的uplink是个变量，故得用new的方法创建变量式的正则表达式
                /*if(reg.test(text) && REV_HASH[uplink] != undefined){  // 出错啦: 因为/uplink/.test(text)里的'uplink'被认为是个字符串常量而非一个变量名！
                    // 替换的前提还要有判断REV_HASH哈希里是否存在键为uplink值的项，如果不存在就不能做替换，
                    // 否则最后一行默认路由的链路字符串‘全部’就会被替换为‘undefined’啦 
                    // text = text.replace( uplink, UPL_HASH[uplink] ); 致命错误：不要用UPL_HASH，因为它实际是个空的哈希！
                    text = text.replace( uplink, REV_HASH[uplink] );
                }*/
                if(reg.test(text) && UPL_HASH[uplink] != undefined){
                    text = text.replace( uplink, UPL_HASH[uplink] );
                }
            }
            if(/&/.test(text)){
                // text = text.replace('&',',');
                var replace_str = '<ul>';
                var arr = text.split("&");  // var arr = text.split(/&/);也是对的
                for(var i=0; i<arr.length; i++){
                    replace_str += '<li>'+ arr[i] +'</li>';
                }
                replace_str += '</ul>';
                text = replace_str;
            }
            return text;
        }
    },
    'time':{
        render:function( default_rendered_text, data_item ){
            var text = default_rendered_text;
            if(text == "" || !text){
                text = "全部";
            }return text;
        }
    },
    'scheduler':{
        render:function( default_rendered_text, data_item ){
            var text = default_rendered_text;
            if(!text){
                text = "无";
            }else if(text == "rr"){
                text = "轮询";
            }else if(text == "wrr"){
                text = "加权轮询";
            }else if(text == "br"){
                text = "带宽比例";
            }else if(text == "wlb"){
                text = "加权最小流量";
            }
            return text;
        }
    },
    'action': {
        render: function( default_rendered_text, data_item ) {
            var enabled = data_item.enabled;
            var toggle_class, button_text, button_icon, onclick;
            
            if(enabled == "off"){
                button_icon = "off.png";
                onclick = "enable_item(this.value);";
            }
            else{
                button_icon = "on.png";
                onclick = "disable_item(this.value);";
            }
            var toggle_enable_button = {
                enable: true,
                cls:toggle_class,
                button_text: button_text,
                button_icon: button_icon,
                value: data_item.id,
                functions: { 
                    onclick: onclick
                },
                class:"action-image"
            };
            // var move_up_button = {
            //     enable: true,
            //     button_icon: ( data_item.IS_FIRST_LINE == 1 ? "clear.gif":"stock_up-16.png" ),
            //     button_text: "上移",
            //     value: data_item.id,
            //     functions: {
            //         onclick: ( data_item.IS_FIRST_LINE == 1 ? null:"handle_move_up_operation(this.value);" )
            //     },
            //     class:"action-image"
            // };
            // var move_down_button = {
            //     enable: true,
            //     button_icon: ( data_item.IS_LAST_LINE == 1 ? "clear.gif":"stock_down-16.png" ),
            //     button_text: "下移",
            //     value: data_item.id,
            //     functions: {
            //         onclick: ( data_item.IS_LAST_LINE == 1 ? null:"handle_move_down_operation(this.value);" )
            //     },
            //     class:"action-image"
            // };

            var edit_button = {
                enable: true,
                id: "edit_edit",
                name: "edit_edit",
                button_icon: "edit.png",
                button_text: "编辑",
                value: data_item.id,
                functions: {
                    onclick: "handle_edit_operation(this);"
                },
                class:"action-image"
            };
            var del_button = {
                enable: true,
                id: "delete_delete",
                name: "delete_delete",
                button_icon: "delete.png",
                button_text: "删除",
                value: data_item.id,
                functions: {
                    onclick: "handle_delete_operation(this);"
                },
                class:"action-image"
            };
            var action_buttons = [ /*move_up_button, move_down_button,*/ toggle_enable_button, edit_button, del_button ];

            var rendered_text =  PagingHolder.create_action_buttons( action_buttons );

            if ( data_item.id == 0 ) {
                
            }
            if ( data_item.IS_DEFAULT_ROUTING == "true" ) {
                return "";
            }

            return rendered_text;
        }
    }
};
var list_panel_config = {
    url: "/cgi-bin/smart_routing.cgi",
    check_in_id: "smart_routing_list_panel",
    panel_name: "test_list_panel",
    render: list_panel_actions_render,
    default_search_config: {
        input_tip: "支持名称查询",
        title: ""
    },
    event_handler: {
        before_load_data: function( add_obj, data_item ) {
        },
        after_load_data: function ( add_obj, data_item ) {
        },
        before_save_data: function ( add_obj, sending_data ) {

        },
        after_save_data: function ( add_obj, received_data ) {

        }
    },

    panel_header: [
        {
            enable: true,
            type: "checkbox",
            name: "checkbox",
            width: "5%",
            td_class: "align-center"
        }, {
            enable: true,
             type: "text",
             title: "名称",
             name: "routing_name",
             width: "20%"
        }, /*{
            enable: true,
            type: "text",
            title: "源",
            name: "routing_src",
            width: "15%"
        },*/ {
            enable: true,
             type: "text",
             title: "目标",
             name: "routing_dst",
             width: "20%"
        }, {
            enable: true,
            type: "text",
            title: "使用链路",
            name: "links",
            width: "20%"
        }, /*{
            enable: true,
            type: "text",
            title: "生效时间",
            name: "time",
            width: "10%"
        },*/ {
            enable: true,
            type: "text",
            title: "调度策略",
            name: "scheduler",
            width: "20%"
        },{
            enable: true,
            type: "action",
            name: "action",
            width: "10%",
            td_class: "align-center"
        }
    ],
    top_widgets: [
        {
            enable: true,
            type: "image_button",
            button_icon: "add16x16.png",
            button_text: "新建智能路由",
            // style: "padding:3px 4px",
            functions: {
                onclick: "show_add_panel(this);"
            }
        }, {
            enable: true,
            type: "image_button",
            button_icon: "delete.png",
            button_text: "删除选中",
            style: "",
            functions: {
                onclick: "delete_selected_items(this);"
            }
        }
    ]
};

function enable_item(data_item_id){
    list_panel.operate_item( data_item_id, "enable_data", "确认启用？", false );
}
function disable_item(data_item_id){
    list_panel.operate_item( data_item_id, "disable_data", "确认禁用？", false );
}
function handle_move_operation( type, line_id ) {
    var url = "/cgi-bin/smart_routing.cgi";
    var total_num = list_panel.total_num;
    var action = "";
    if(type == "up"){
        action = "MOVE_UP";
    }else if(type == "down"){
        action = "MOVE_DOWN";
    }
    var sending_data = {
       ACTION: action,
       LINE_ID: line_id,
       MAX_LINE_NUM:total_num
    };
    function onreceived(response){
        if ( list_panel.is_operation_succeed(response) ) {
            list_panel.update_info( true );
            if ( response.mesg !== undefined && response.mesg != "" ) {
                list_panel.show_note_mesg( response.mesg );
            }
            if ( list_panel.is_need_reload(response) ) {
                list_panel.show_apply_mesg();
            }
        } else {
            if ( response.mesg !== undefined && response.mesg != "" ) {
                list_panel.show_error_mesg( response.mesg );
            }
        }
    }
    
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            alert("handle_move_operation返回数据格式有误,请检查");
        },
        success: onreceived
    });
}
function handle_move_up_operation( data_item_id ){

    var data_item = list_panel.get_item( data_item_id );
    var line_id = data_item.id;
    var IS_FIRST_LINE = data_item.IS_FIRST_LINE;
    var IS_LAST_LINE = data_item.IS_LAST_LINE;
    var IS_DEFAULT_ROUTING = data_item.IS_DEFAULT_ROUTING;
    if( IS_FIRST_LINE ==1 ){
        list_panel.show_error_mesg("第一行的规则不能再上移！");
        return;
    }if( IS_DEFAULT_ROUTING == "true" ){
        list_panel.show_error_mesg("默认路由不能上移！");
        return;
    }
    handle_move_operation("up",line_id);
    return;
}

function handle_move_down_operation( data_item_id ){

    var data_item = list_panel.get_item( data_item_id );
    var line_id = data_item.id;
    var IS_FIRST_LINE = data_item.IS_FIRST_LINE;
    var IS_LAST_LINE = data_item.IS_LAST_LINE;
    var IS_DEFAULT_ROUTING = data_item.IS_DEFAULT_ROUTING;

    if( IS_LAST_LINE ==1 ){
        list_panel.show_error_mesg("最后一行的规则不能再下移！");
        return;
    }if( IS_DEFAULT_ROUTING == "true" ){
        list_panel.show_error_mesg("默认路由不能下移！");
        return;
    }
    handle_move_operation("down",line_id);
    return;
}
function resume_left_select_data(){
    $( "#routing_src_left_select_box option:enabled" ).remove();
    var len = addr_nodes_arr.length;   var options = "";
    for(var j=0; j<len; j++){
        var item = addr_nodes_arr[j];
        options += '<option class="left_addr_nodes" value="' + item + '">' + item + '</option>';
    }
    $( "#left_addr_group_tip" ).before( options );

    len = addr_groups_arr.length;   options = "";
    for(j=0; j<len; j++){
        var item = addr_groups_arr[j];
        options += '<option class="left_addr_groups" value="' + item + '">' + item + '</option>';
    }
    $( "#hidden_left_line" ).before( options );

    options = "";   // 少了这句！！options你没有清空啊啊！所以总是出现多出my_group,group这两个行！
    for(var item in UPL_HASH){
        var item_val = UPL_HASH[item];
        options += '<option value="' + item + '">' + item_val + '</option>';
    }
    $( "#uplinks_left_select_box" ).empty();
    $( "#uplinks_left_select_box" ).append( options );
}
function save_received_data_to_local(response){
        var i=0;
        var len = response.isp_name_list.length;
        for(i=0; i<len; i++) {
            isp_name_arr.push(response.isp_name_list[i]);
        }
        len = response.addr_nodes.length;
        for(i=0; i<len; i++){
            addr_nodes_arr.push(response.addr_nodes[i]);
        }
        len = response.addr_groups.length;
        for(i=0; i<len; i++){
            addr_groups_arr.push(response.addr_groups[i]);
        }

}

function load_other_data() {

    function onreceived( response ) {

        save_received_data_to_local(response);

        var is_need_reload = response['need_reload'];
        if( is_need_reload == 1 ){
            list_panel.show_apply_mesg(response['mesg']);
        }
        var options = "";
        var len = response.isp_name_list.length;
        for ( var i = 0; i < len; i++ ) {
            var item = response.isp_name_list[i];
            options += '<option value="' + item + '">' + item + '</option>';
        }
        $( "#isp_name_select_options" ).empty();
        $( "#isp_name_select_options" ).append( options );
        
        options = "";
        len = response.addr_nodes.length;
        for ( var i = 0; i < len; i++ ) {
            var item = response.addr_nodes[i];
            options += '<option class="left_addr_nodes" value="' + item + '">' + item + '</option>';
        }
        $( "#left_addr_group_tip" ).before( options );
        
        options = "";
        len = response.addr_groups.length;
        for ( var i = 0; i < len; i++ ) {
            var item = response.addr_groups[i];
            options += '<option class="left_addr_groups" value="' + item + '">' + item + '</option>';
        }
        $( "#hidden_left_line" ).before( options );

        options = "";
        UPL_HASH = response.uplinks_hash;

        for(var item in UPL_HASH){
            var item_val = UPL_HASH[item];
            options += '<option value="' + item + '">' + item_val + '</option>';
        }
        $( "#uplinks_left_select_box" ).empty();
        $( "#uplinks_left_select_box" ).append( options );
    }

    send_request( 'load_other_data', onreceived );
}


function send_request( action, onreceived ) {
    var url = "/cgi-bin/smart_routing.cgi";
    var sending_data = {
        ACTION: action
    };
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            list_panel.show_error_mesg("返回数据格式有误,请检查");
        },
        success: onreceived
    });
}

function handle_edit_operation( element ) {
    var data_item_id = element.value;
    var data_item = list_panel.get_item(data_item_id);
    var IS_DEFAULT_ROUTING = data_item.IS_DEFAULT_ROUTING;
    if( IS_DEFAULT_ROUTING == "true"){
        list_panel.show_error_mesg("对不起，默认路由不可以编辑！");
        return;
    }
    list_panel.edit_item( element.value );
}
function handle_delete_operation( element ) {
    var data_item_id = element.value;
    var data_item = list_panel.get_item(data_item_id);
    var IS_DEFAULT_ROUTING = data_item.IS_DEFAULT_ROUTING;
    if( IS_DEFAULT_ROUTING == "true"){
        list_panel.show_error_mesg("对不起，默认路由不可以删除！");
        return;
    }
    list_panel.delete_item( element.value );
    init_position_list();
    do_uplinks_change();

}
var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );
var isp_name_arr = new Array();
var uplinks_arr = new Array();
var addr_nodes_arr = new Array();
var addr_groups_arr = new Array();
var UPL_HASH = null;
var REV_HASH = null;

$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    add_panel.render();
    add_panel.hide();
    list_panel.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );

    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

    var obj ={
        value:"no_type"
    };
    do_src_type_change(obj);
    
    do_dst_type_change(obj);

    load_other_data();  // 放在list_panel.update_info();的前面！
    list_panel.update_info( true );
    // load_other_data();
    init_position_list();
    do_uplinks_change();

});
function init_position_list(){
    
    $("#position_list").empty();
    var first_line_option = '<option value="first_line" >第一条</option>';
    var last_line_option = '<option id="last_line_position" value="last_line" selected="selected" >最后一条</option>';
    $("#position_list").append(first_line_option);
    $("#position_list").append(last_line_option);

    for(var id=1; id<=list_panel.total_num-2; id++){
        var text = "在第"+id+"行规则之后";
        var option = '<option value="' + id + '">' + text + '</option>';
        $("#last_line_position").before(option);
    }
}

function delete_selected_items( element ) {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }
    var ids = checked_items_id.join( "&" );
    if( ids == ""){
        list_panel.show_error_mesg( "未检测到删除项" );
        return;
    }
    list_panel.delete_item( ids );
    update_uplinks();
    init_position_list();
    do_uplinks_change();

}

function show_add_panel( element ) {
    add_panel.show();
}