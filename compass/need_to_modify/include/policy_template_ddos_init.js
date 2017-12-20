$(document).ready(function(){
    add_panel = new RuleAddPanel( add_panel_config );
    scan_panel = new RuleAddPanel( scan_panel_config );
    list_panel = new PagingHolder( list_panel_config );
    scan_panel = new PagingHolder( scan_panel_config );
    transport_panel = new PagingHolder( transport_panel_config );
    apply_panel = new PagingHolder( apply_panel_config );
    strange_panel = new PagingHolder( strange_panel_config );
    ip_panel = new PagingHolder( ip_panel_config );
    tcp_panel = new PagingHolder( tcp_panel_config );
    message_manager = new MessageManager( message_box_config );
    
    /* 渲染面板 */
    add_panel.render();
    list_panel.render();
    scan_panel.render();
    transport_panel.render();
    apply_panel.render();
    strange_panel.render();
    ip_panel.render();
    tcp_panel.render();
    message_manager.render();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );
    
    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );
    
    add_panel.hide();
    scan_panel.hide();
    transport_panel.hide();
    apply_panel.hide();
    strange_panel.hide();
    ip_panel.hide();
    tcp_panel.hide();
    
    list_panel.update_info(true);
    scan_panel.update_info(true);
    transport_panel.update_info(true);
    apply_panel.update_info(true);
    strange_panel.update_info(true);
    ip_panel.update_info(true);
    tcp_panel.update_info(true);
    
    $(".ctr_inpt").css("width","50px");
});
var list_panel;
var add_panel;
var scan_panel;
var transport_panel;
var apply_panel;
var strange_panel;
var ip_panel;
var tcp_panel;
var message_box_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "mesg_box_tmp",
    panel_name: "my_message_box"
}
var message_manager;

var scan_panel_render = {
    'checkbox':{
        listeners:{
            click: function(element, data_item){
                var input_id = "#";
                if(element.value == "0"){
                    input_id += "max_val_ipaddr_input";
                }else{
                    input_id += "max_val_port_input";
                }
                if(element.checked){
                    $(input_id).removeAttr("disabled");
                }else{
                    $(input_id).attr("disabled","disabled");
                }
            }
        }
    },
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "ipaddr_scan"){
                result_render = "IP地址扫描防护";
            }else if(data_item.policy_name == "port_scan"){
                result_render = "端口扫描防护";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'config_policy_param': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var val_scan = "2000";
            if(data_item.config_policy_param){
                val_scan = data_item.config_policy_param;
            }
            if(val_scan == null){
                val_scan = "";
            }
            var is_disabled = "disabled='disabled'";
            if(data_item.enable == "on"){
                is_disabled = "";
            }
            if(data_item.policy_name == "ipaddr_scan"){
                result_render = "同一源IP的IP地址扫描报文阈值"+"<input class='ctr_inpt' "+is_disabled+" id='max_val_ipaddr_input' type ='text' value='"+val_scan+"' /></br>";
            }else if(data_item.policy_name == "port_scan"){
                result_render = "同一源IP的端口扫描报文阈值"+"<input style='margin-left:8px;' "+is_disabled+" class='ctr_inpt' id='max_val_port_input' type ='text' value='"+val_scan+"' /></br>";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var scan_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_scan",
    panel_name: "scan_panel",
    page_size: 2,
    panel_title: "扫描防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: scan_panel_render,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    scan_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
        }
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        td_class:"align-center",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "防护策略",
        name: "policy_name",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "策略参数配置",
        name: "config_policy_param",
        width: "60%"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_scan();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "scan_panel.hide();"
            }
        }]
    }
};
//传输层风暴型攻击面板配置
var transport_panel_render = {
    'checkbox':{
        listeners:{
            click: function(element, data_item){
                var input_s_id = "#";
                var input_d_id = "#";
                if(element.value == "0"){
                    input_s_id += "num_syn_source_input";
                    input_d_id += "num_syn_dest_input";
                }else if(element.value == "1"){
                    input_s_id += "num_ack_source_input";
                    input_d_id += "num_ack_dest_input";
                }else if(element.value == "2"){
                    input_s_id += "num_udp_source_input";
                    input_d_id += "num_udp_dest_input";
                }else{
                    input_s_id += "num_icmp_source_input";
                    input_d_id += "num_icmp_dest_input";
                }
                if(element.checked){
                    $(input_s_id).removeAttr("disabled");
                    $(input_d_id).removeAttr("disabled");
                }else{
                    $(input_s_id).attr("disabled","disabled");
                    $(input_d_id).attr("disabled","disabled");
                }
            }
        }
    },
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "syn"){
                result_render = "SYN洪泛攻击防护";
            }else if(data_item.policy_name == "ack"){
                result_render = "ACK洪泛攻击防护";
            }else if(data_item.policy_name == "udp"){
                result_render = "UDP洪泛攻击防护";
            }else if(data_item.policy_name == "icmp"){
                result_render = "ICMP洪泛攻击防护";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'config_policy_param': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var is_disabled = "disabled='disabled'";
            if(data_item.enable == "on"){
                is_disabled = "";
            }
            if(data_item.policy_name == "syn"){
                var num_syn_source = "2000";
                var num_syn_dest = "2000";
                if(data_item.num_syn_source){
                    num_syn_source = data_item.num_syn_source;
                }
                if(data_item.num_syn_dest){
                    num_syn_dest = data_item.num_syn_dest;
                }
                result_render = "同一源IP的SYN报文数"+"<input style='margin-left:10px;' "+is_disabled+" class='ctr_inpt' id='num_syn_source_input' type ='text' value='"+num_syn_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px;'>同一目的IP的SYN报文数"+"<input "+is_disabled+" class='ctr_inpt' id='num_syn_dest_input' type ='text' value='"+num_syn_dest+"' />/秒</span></br>";
            }else if(data_item.policy_name == "ack"){
                var num_ack_source = "2000";
                var num_ack_dest = "2000";
                if(data_item.num_ack_source){
                    num_ack_source = data_item.num_ack_source;
                }
                if(data_item.num_ack_dest){
                    num_ack_dest = data_item.num_ack_dest;
                }
                result_render = "同一源IP的ACK报文数"+"<input "+is_disabled+" style='margin-left:10px;' class='ctr_inpt' id='num_ack_source_input' type ='text' value='"+num_ack_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px;'>同一目的IP的ACK报文数"+"<input "+is_disabled+" class='ctr_inpt' id='num_ack_dest_input' type ='text' value='"+num_ack_dest+"' />/秒</span></br>";
            }else if(data_item.policy_name == "udp"){
                var num_udp_source = "2000";
                var num_udp_dest = "2000";
                if(data_item.num_udp_source){
                    num_udp_source = data_item.num_udp_source;
                }
                if(data_item.num_udp_dest){
                    num_udp_dest = data_item.num_udp_dest;
                }
                result_render = "同一源IP的UDP报文数"+"<input "+is_disabled+" style='margin-left:12px;' class='ctr_inpt' id='num_udp_source_input' type ='text' value='"+num_udp_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px;'>同一目的IP的UDP报文数"+"<input "+is_disabled+" style='margin-left:2px;' class='ctr_inpt' id='num_udp_dest_input' type ='text' value='"+num_udp_dest+"' />/秒</span></br>";
            }else if(data_item.policy_name == "icmp"){
                var num_icmp_source = "2000";
                var num_icmp_dest = "2000";
                if(data_item.num_icmp_source){
                    num_icmp_source = data_item.num_icmp_source;
                }
                if(data_item.num_icmp_dest){
                    num_icmp_dest = data_item.num_icmp_dest;
                }
                result_render = "同一源IP的ICMP报文数"+"<input "+is_disabled+" style='margin-left:10px;' class='ctr_inpt' id='num_icmp_source_input' type ='text' value='"+num_icmp_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px;'>同一目的IP的ICMP报文数"+"<input "+is_disabled+" class='ctr_inpt' id='num_icmp_dest_input' type ='text' value='"+num_icmp_dest+"' />/秒</span></br>";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var transport_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_transport",
    panel_name: "transport_panel",
    page_size: 4,
    panel_title: "传输层风暴型攻击防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: transport_panel_render,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    transport_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
            //checkon_selected_items();
        }
    },
    panel_header: [{
        enable: true,
        type: "checkbox",
        name: "checkbox",
        td_class:"align-center",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "防护策略",
        name: "policy_name",
        width: "30%"
    }, {
        enable: true,
        type: "text",
        title: "策略参数配置",
        name: "config_policy_param",
        width: "60%"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_transport();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "transport_panel.hide();"
            }
        }]
    }
};

//传输层风暴型攻击面板配置
var apply_panel_render = {
    'checkbox':{
        listeners:{
            click: function(element, data_item){
                var input_s_id = "#";
                var input_d_id = "#";
                if(element.value == "0"){
                    input_s_id += "num_http_source_input";
                    input_d_id += "num_http_dest_input";
                }else{
                    input_s_id += "num_dns_source_input";
                    input_d_id += "num_dns_dest_input";
                }
                if(element.checked){
                    $(input_s_id).removeAttr("disabled");
                    $(input_d_id).removeAttr("disabled");
                }else{
                    $(input_s_id).attr("disabled","disabled");
                    $(input_d_id).attr("disabled","disabled");
                }
            }
        }
    },
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "http"){
                result_render = "HTTP GET/PUT洪泛攻击防护";
            }else if(data_item.policy_name == "dns"){
                result_render = "DNS洪泛攻击防护";
            }
            return '<span>' + result_render + '</span>';
        }
    },
    'config_policy_param': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            var is_disabled = "disabled='disabled'";
            if(data_item.enable == "on"){
                is_disabled = "";
            }
            if(data_item.policy_name == "http"){
                var num_http_source = "2000";
                var num_http_dest = "2000";
                if(data_item.num_http_source){
                    num_http_source = data_item.num_http_source;
                }
                if(data_item.num_http_dest){
                    num_http_dest = data_item.num_http_dest;
                }
                result_render = "同一源IP的GET/PUT报文数"+"<input "+is_disabled+" style='margin-left:10px;' class='ctr_inpt' id='num_http_source_input' type ='text' value='"+num_http_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px;'>同一目的IP的GET/PUT报文数"+"<input "+is_disabled+" class='ctr_inpt' id='num_http_dest_input' type ='text' value='"+num_http_dest+"' /></span>/秒</br>";
            }else if(data_item.policy_name == "dns"){
                var num_dns_source = "2000";
                var num_dns_dest = "2000";
                if(data_item.num_dns_source){
                    num_dns_source = data_item.num_dns_source;
                }
                if(data_item.num_dns_dest){
                    num_dns_dest = data_item.num_dns_dest;
                }
                result_render = "同一源IP的DNS报文数"+"<input "+is_disabled+" style='margin-left:32px;' class='ctr_inpt' id='num_dns_source_input' type ='text' value='"+num_dns_source+"' />/秒</br>";
                result_render += "<span style='margin-left:5px'>同一目的IP的DNS报文数"+"<input "+is_disabled+" style='margin-left:21px;' class='ctr_inpt' id='num_dns_dest_input' type ='text' value='"+num_dns_dest+"' />/秒</span></br>";
                var types = ["query","respond"];
                var types_text = ["查询报文","响应报文"];
                var query_styles = ["recursive","iterative","any"];
                var query_styles_text = ["递归查询","迭代查询","递归和迭代查询"];
                var html_types = "<select id='dns_type_input'>";
                var html_query_styles = "<select id='dns_query_style_input'>";
                for(var i=0;i<types.length;i++){
                    if(data_item.dns_type == types[i]){
                        html_types += "<option selected value='"+types[i]+"'>"+types_text[i]+"</option>";
                    }else{
                        html_types += "<option value='"+types[i]+"'>"+types_text[i]+"</option>";
                    }
                }
                html_types += "</select>";
                for(var j=0;j<query_styles.length;j++){
                    if(data_item.dns_query_style == query_styles[j]){
                        html_query_styles += "<option selected value='"+query_styles[j]+"'>"+query_styles_text[j]+"</option>";
                    }else{
                        html_query_styles += "<option value='"+query_styles[j]+"'>"+query_styles_text[j]+"</option>";
                    }
                }
                html_query_styles += "</select>";
                result_render += "<span style='margin-left:5px'>DNS报文类型"+html_types+"</span></br>";
                result_render += "<span style='margin-left:5px'>DNS查询方式"+html_query_styles+"</span></br>";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var apply_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_apply",
    panel_name: "apply_panel",
    page_size: 2,
    panel_title: "应用层风暴型攻击防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: apply_panel_render,
    modal_config: {
        modal_box_size: "m",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    apply_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
            //checkon_selected_items();
        }
    },
    panel_header: [
        {
            enable: true,
            td_class:"align-center",
            type: "checkbox",
            name: "checkbox",
            width: "10%"
        }, {
            enable: true,
            type: "text",
            title: "防护策略",
            name: "policy_name",
            width: "30%"
        }, {
            enable: true,
            type: "text",
            title: "策略参数配置",
            name: "config_policy_param",
            width: "60%"
        }
    ],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_apply();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "apply_panel.hide();"
            }
        }]
    }
};
var strange_panel_render = {
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "land"){
                result_render = "Land攻击防护";
            }else if(data_item.policy_name == "smurf"){
                result_render = "Smurf攻击防护";
            }else if(data_item.policy_name == "winnuke"){
                result_render = "Winnuke攻击防护";
            }else if(data_item.policy_name == "teardrop"){
                result_render = "Teardrop攻击防护";
            }else if(data_item.policy_name == "targa3"){
                result_render = "Targa3攻击防护";
            }else if(data_item.policy_name == "fraggle"){
                result_render = "Fraggle攻击防护";
            }else if(data_item.policy_name == "largest_icmp"){
                result_render = "超大ICMP数据攻击防护（数据尺寸>1500）(Ping of death)";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var strange_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_strange",
    panel_name: "strange_panel",
    page_size: 7,
    panel_title: "畸形数据包攻击防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: strange_panel_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    strange_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
            //checkon_selected_items();
        }
    },
    panel_header: [{
        enable: true,
        td_class:"align-center",
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "策略名称",
        name: "policy_name"
    }],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_strange();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "strange_panel.hide();"
            }
        }]
    }
};

var ip_panel_render = {
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "ip_record"){
                result_render = "IP记录路径选项报文防护";
            }else if(data_item.policy_name == "ip_time"){
                result_render = "IP时间戳选项报文防护";
            }else if(data_item.policy_name == "ip_district"){
                result_render = "IP宽松源路由选项报文防护";
            }else if(data_item.policy_name == "ip_strict"){
                result_render = "IP严格源路由选项报文防护";
            }else if(data_item.policy_name == "ip_safe"){
                result_render = "IP安全和处理限制选项报文防护";
            }/* else if(data_item.policy_name == "ip_unlaw"){
                result_render = "非法IP选项报文防护";
            } */
            return '<span>' + result_render + '</span>';
        }
    }
};
var ip_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_ip",
    panel_name: "ip_panel",
    page_size: 5,
    panel_title: "IP协议报文选项防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: ip_panel_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    ip_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
            //checkon_selected_items();
        }
    },
    panel_header: [{
        enable: true,
        td_class:"align-center",
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "策略名称",
        name: "policy_name"
    }],
    bottom_extend_widgets: {
        class: "align-center",
        sub_items: [{
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_ip();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "ip_panel.hide();"
            }
        }]
    }
};

var tcp_panel_render = {
    'policy_name': {
        render: function( default_rendered_text, data_item ) {
            var result_render = "";
            if(data_item.policy_name == "tcp_head0"){
                result_render = "TCP报头标志全为0防护";
            }else if(data_item.policy_name == "tcp_head1"){
                result_render = "TCP报头标志全为1防护";
            }else if(data_item.policy_name == "syn_fin"){
                result_render = "SYN和FIN标志位同时为1防护";
            }else if(data_item.policy_name == "fin"){
                result_render = "仅FIN标志位为1防护";
            }
            return '<span>' + result_render + '</span>';
        }
    }
};
var tcp_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_tcp",
    panel_name: "tcp_panel",
    page_size: 4,
    panel_title: "TCP协议报文选项防护策略",
    is_panel_closable: true,
    is_default_search: false,
    is_paging_tools: false,
    is_modal: true,
    render: tcp_panel_render,
    modal_config: {
        modal_box_size: "s",
        modal_level: 20
    },
    event_handler: {
        before_load_data: function( list_obj,data_item ) {
            
        },
        after_load_data: function( list_obj,data_item ) {
            for(var i=0;i<data_item.detail_data.length;i++){
                if(data_item.detail_data[i].enable == "on"){
                    tcp_panel.set_check( data_item.detail_data[i].id, true );
                }
            }
            //checkon_selected_items();
        }
    },
    panel_header: [{
        td_class:"align-center",
        enable: true,
        type: "checkbox",
        name: "checkbox",
        width: "10%"
    }, {
        enable: true,
        type: "text",
        title: "策略名称",
        name: "policy_name"
    }],
    bottom_extend_widgets: {
        id: "",
        name: "",
        class: "align-center",
        sub_items: [
        {
            enable: true,
            type: "image_button",
            style: "margin-top: 5px;margin-bottom: 5px;",
            button_text: "确定",
            functions: {
                onclick: "change_conf_tcp();"
            }
        }, {
            enable: true,
            type: "image_button",
            button_text: "取消",
            style: "margin-top: 5px;margin-bottom: 5px;",
            functions: {
                onclick: "tcp_panel.hide();"
            }
        }]
    }
};

var add_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi",
    check_in_id: "panel_tmp_add",
    panel_name: "add_panel",
    rule_title: "策略模板",
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        before_save_data: function( add_obj ) {
            var arr_defend = [];
            arr_defend = scan_panel.get_checked_items();
            arr_defend = arr_defend.concat(transport_panel.get_checked_items());
            arr_defend = arr_defend.concat(apply_panel.get_checked_items());
            arr_defend = arr_defend.concat(strange_panel.get_checked_items());
            arr_defend = arr_defend.concat(ip_panel.get_checked_items());
            arr_defend = arr_defend.concat(tcp_panel.get_checked_items());
            if(arr_defend.length < 1){
                message_manager.show_popup_error_mesg("至少选择一种防护策略！");
                return false;
            }
        },
        before_load_data: function( add_obj,data_item ) {
            
        },
        after_load_data: function( add_obj,data_item ) {
            scan_panel.extend_sending_data = {
                line_num: data_item.id
            };
            scan_panel.update_info(true);
            change_conf_scan();
            
            transport_panel.extend_sending_data = {
                line_num: data_item.id
            };
            transport_panel.update_info(true);
            change_conf_transport();
            //刷新数据
            apply_panel.extend_sending_data = {
                line_num: data_item.id
            };
            apply_panel.update_info(true);
            change_conf_apply();
            
            strange_panel.extend_sending_data = {
                line_num: data_item.id
            };
            strange_panel.update_info(true);
            change_conf_strange();
            
            ip_panel.extend_sending_data = {
                line_num: data_item.id
            };
            ip_panel.update_info(true);
            change_conf_ip();
            
            tcp_panel.extend_sending_data = {
                line_num: data_item.id
            };
            tcp_panel.update_info(true);
            change_conf_tcp();
            
            $(".ctr_inpt").css("width","50px");
            //改变添加面板
        }
    },
    is_panel_stretchable: false,
    is_panel_closable: true,
    items_list: [{
        title: "名称*",
        sub_items: [{
            enable: true,
            type: "text",
            id: "name",
            name: "name",
            value: "",
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
        }]
    }, {
        title: "说明",
        sub_items: [{
            enable: true,
            type: "text",
            // style: "width:300px",
            id: "description",
            name: "description",
            value: "",
            functions: {
            },
            check: {
                type: "text",
                required: 0,
                check:'note',
                ass_check: function( check ) {

                }
            }
        }]
    }, {
        title: "扫描防护",
        sub_items: [{
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[{
                enable: true,
                type: "label",
                id: "link_scan",
                name: "link_scan",
                label: "扫描防护类型：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_scan'>请选择防护类型</a>",
                functions: {
                    onclick: "scan_panel.show();"
                }
            },
            {
                enable: true,
                type: "text",
                cls: "ctr_scan",
                id: "enable_ipaddr",
                name: "enable_ipaddr",
                label: "",
                value: "",
                item_style: "display:none;"
            },
            {
                enable: true,
                type: "text",
                cls: "ctr_scan",
                id: "max_val_ipaddr",
                name: "max_val_ipaddr",
                label: "",
                value: "",
                item_style: "display:none;"
            },
            {
                enable: true,
                type: "text",
                cls: "ctr_scan",
                id: "enable_port",
                name: "enable_port",
                label: "",
                value: "",
                item_style: "display:none;"
            },
            {
                enable: true,
                type: "text",
                cls: "ctr_scan",
                id: "max_val_port",
                name: "max_val_port",
                label: "",
                value: "",
                item_style: "display:none;"
            }]
        }]
    }, {
        title: "风暴型攻击",
        sub_items: [{
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[{
                enable: true,
                type: "label",
                id: "link_transport",
                name: "link_transport",
                label: "传输层风暴型攻击类型：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_transport'>请选择防护类型</a>",
                functions: {
                    onclick: "transport_panel.show();"
                }
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "enable_syn",
                name: "enable_syn",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_syn_source",
                name: "num_syn_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_syn_dest",
                name: "num_syn_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "enable_ack",
                name: "enable_ack",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_ack_source",
                name: "num_ack_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_ack_dest",
                name: "num_ack_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "enable_udp",
                name: "enable_udp",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_udp_source",
                name: "num_udp_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_udp_dest",
                name: "num_udp_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "enable_icmp",
                name: "enable_icmp",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_icmp_source",
                name: "num_icmp_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_transport",
                id: "num_icmp_dest",
                name: "num_icmp_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }]
        }, {
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[ {
                enable: true,
                type: "label",
                id: "link_apply",
                name: "link_apply",
                label: "应用层风暴型攻击类型：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_apply'>请选择防护类型</a>",
                functions: {
                    onclick: "apply_panel.show();"
                }
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "enable_http",
                name: "enable_http",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "num_http_source",
                name: "num_http_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "num_http_dest",
                name: "num_http_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "enable_dns",
                name: "enable_dns",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "num_dns_source",
                name: "num_dns_source",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "num_dns_dest",
                name: "num_dns_dest",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "dns_type",
                name: "dns_type",
                label: "",
                value: "",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_apply",
                id: "dns_query_style",
                name: "dns_query_style",
                label: "",
                value: "",
                item_style: "display:none;"
            }]
        }]
    }, {
        title: "畸形数据包攻击",
        sub_items: [{
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[{
                enable: true,
                type: "label",
                id: "link_abnormal",
                name: "link_abnormal",
                label: "畸形数据包攻击类型：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_strange'>请选择防护类型</a>",
                functions: {
                    onclick: "strange_panel.show();"
                }
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_land",
                name: "enable_land",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_smurf",
                name: "enable_smurf",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_winnuke",
                name: "enable_winnuke",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_teardrop",
                name: "enable_teardrop",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_targa3",
                name: "enable_targa3",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_fraggle",
                name: "enable_fraggle",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_abnormal",
                id: "enable_largest_icmp",
                name: "enable_largest_icmp",
                item_style: "display:none;"
            }]
        }]
    }, {
        title: "异常报文侦测",
        sub_items: [{
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[{
                enable: true,
                type: "label",
                id: "link_ip",
                name: "link_ip",
                label: "IP协议报文选项：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_ip'>请选择防护类型</a>",
                functions: {
                    onclick: "ip_panel.show();"
                }
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_record",
                name: "enable_ip_record",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_time",
                name: "enable_ip_time",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_district",
                name: "enable_ip_district",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_strict",
                name: "enable_ip_strict",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_safe",
                name: "enable_ip_safe",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_ip",
                id: "enable_ip_unlaw",
                name: "enable_ip_unlaw",
                
                item_style: "display:none;"
            }]
        }, {
            enable:true,
            type:"items_group",
            item_style:"width:100%",
            sub_items:[{
                enable: true,
                type: "label",
                id: "link_tcp",
                name: "link_tcp",
                label: "TCP协议报文选项：",
                value: "<a style='text-decoration:underline;cursor:pointer;' id='defend_tcp'>请选择防护类型</a>",
                functions: {
                    onclick: "tcp_panel.show();"
                }
            }, {
                enable: true,
                type: "text",
                cls: "ctr_tcp",
                id: "enable_tcp_head0",
                name: "enable_tcp_head0",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_tcp",
                id: "enable_tcp_head1",
                name: "enable_tcp_head1",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_tcp",
                id: "enable_syn_fin",
                name: "enable_syn_fin",
                item_style: "display:none;"
            }, {
                enable: true,
                type: "text",
                cls: "ctr_tcp",
                id: "enable_fin",
                name: "enable_fin",
                item_style: "display:none;"
            }]
        }]
    }]
};

var list_panel_render = {
    'action': {
        render: function( default_rendered_text, data_item ) {
        var action_buttons = [{
                "enable": true,
                "id": "edit_item",
                "name": "edit_item",
                "button_icon": "edit.png",
                "button_text": "编辑",
                "value": data_item.id,
                "functions": {
                    onclick: "list_panel.edit_item(this.value);"
                },
                 "class": "action-image",
            },
            {
                "enable": true,
                "id": "delete_item",
                "name": "delete_item",
                "button_icon": "delete.png",
                "button_text": "删除",
                "value": data_item.id,
                "functions": {
                    onclick: "check_delete_rule(this.value);"
                },
                 "class": "action-image",
            }];
            return PagingHolder.create_action_buttons( action_buttons );
        }
    }
};


var list_panel_config = {
    url: "/cgi-bin/policy_template_ddos.cgi", /* ***必填***，控制数据在哪里加载 */
    check_in_id: "panel_tmp_list",         /* ***必填***，确定面板挂载在哪里 */
    page_size: 20,                  /* ===可选===，定义页大小，默认是15 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一二个页面存在多个相同的面板，此字段必填，以区别不同面板 */
    is_load_all_data: true,         /* ===可选===，默认是true,如果设置成false，翻页回重新加载数据，并且记忆功能不能使用 */
    render: list_panel_render,      /* ===可选===，渲染每列数据 */
    default_search_config: {
        input_tip: "支持名称、说明关键字查询",
        title: ""
    },
    panel_header: [{
        "enable": true,            //用户控制表头是否显示
        "type": "checkbox",         //type目前有checkbox/text/radio/action，分别对应不同类型的表头，最一般的还是text
        "title": "",                //不同类型的，title需要的情况不同，一般text类型需要title
        "name": "checkbox",         //用户装载数据之用
        "td_class": "align-center",  //这一列td的class，主要用于控制列和列内元素,此处checkbox的column_cls是固定的
        "width": "5%",              //所有表头加起来应该等于100%,以精确控制你想要的宽度
        "functions": {              //一般只有checkbox才会有这个字段
        }
    }, {
        "enable": false,
        "type": "radio",
        "name": "radio",
        "column_cls": "rule-listbc",
        "width": "5%"
    }, {
        "enable": true,
        "type": "text",
        "title": "名称",        //一般text类型需要title,不然列表没有标题
        "name": "name",
        "width": "40%"
    }, {
        "enable": true,
        "type": "text",
        "title": "说明",
        "name": "description",
        "width": "40%"
    }, {
        "enable": true,
        "type": "action",
        "title": "活动/动作",
        "name": "action",
        "td_class":"align-center",
        "width": "10%"
    }],
    top_widgets: [{
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建",
        functions: {
            onclick: "add_rule(this);"
        }
    }, {
        "enable": true,
        type: "image_button",
        "id": "delete_selected",
        "name": "delete_selected",
        "button_icon": "delete.png",
        "button_text": "删除选中",
        "functions": {
            onclick: "check_delete_selected_items()"
        }
    }],
    bottom_widgets: [{
        "enable": false,
        "id": "export_selected",
        "name": "export_selected",
        "button_icon": "download.png",
        "button_text": "导出选中",
        "functions": {
            onclick: "export_selected_items(this)"
        }
    }, {
        "enable": false,
        "id": "delete_all_logs",
        "name": "delete_all_logs",
        "button_icon": "delete.png",
        "button_text": "清空日志",
        "functions": {
            onclick: "delete_all_logs(this)"
        }
    }],
    is_default_search: true
    
}

function enable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.enable_item( ids );
}

function disable_selected_items() {
    var checked_items = list_panel.get_checked_items();
    var checked_items_id = new Array();
    for( var i = 0; i < checked_items.length; i++ ) {
        checked_items_id.push( checked_items[i].id );
    }

    var ids = checked_items_id.join( "&" );

    list_panel.disable_item( ids );
}

function delete_selected_items(e) {
    var ids = "";
    if(e.id == "delete_selected"){
        var checked_items = list_panel.get_checked_items();
        var checked_items_id = new Array();
        for( var i = 0; i < checked_items.length; i++ ) {
            checked_items_id.push( checked_items[i].id );
        }
        ids = checked_items_id.join( "&" );
    }else{
        ids = e.value;
    }
    
    list_panel.delete_item( ids );
}

function extend_search_function( element ) {
    list_panel.update_info( true );
}

function add_rule( element ) {
    add_panel.show();
    recovery_text_a();
}
//显示扫描面板并查询数据
/* function display_scan_panel(n){
    scan_panel.show();
    scan_panel.extend_sending_data = {
        line_num = 
    };
} */
//将扫描面板的数据写入添加面板
function change_conf_scan(){
    var checked_items = scan_panel.get_checked_items();
    var selected_protect = [];
    var text_a = "已选防护：";
    var is_null = false;
    var msg =''
    $(".ctr_scan,#enable_ipaddr,#enable_port").val("");
    if(checked_items.length > 0){
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "ipaddr_scan"){
                $("#enable_ipaddr").val("on");
                var max_val_ipaddr = $("#max_val_ipaddr_input").val();
                $("#max_val_ipaddr").val(max_val_ipaddr);
                if(max_val_ipaddr == "" || max_val_ipaddr == null){
                    is_null = true;
                }else{
                    if (max_val_ipaddr<2 || max_val_ipaddr >4294836224) {
                        msg='同一源IP的IP地址扫描报文阈值输入错误'
                    }
                }
                selected_protect.push("IP地址扫描防护");
                //text_a += "IP地址扫描防护";
            }else if(checked_items[i].policy_name == "port_scan"){
                $("#enable_port").val("on");
                var max_val_port = $("#max_val_port_input").val()
                $("#max_val_port").val(max_val_port);
                if(max_val_port == "" || max_val_port == null){
                    is_null = true;
                }else{
                    if (max_val_port<2 || max_val_port >4294836224) {
                        msg='同一源IP的端口扫描报文阈值输入错误'
                    }
                }
                selected_protect.push("端口扫描防护");
                //text_a += "端口扫描防护";
            }
        }
        text_a += selected_protect.join("、");
    }else{
        text_a = "请选择防护类型";
    }
    if(is_null){
        message_manager.show_popup_error_mesg("选中的防护策略的阀值不能为空！");
    }else if(msg !== ''){
        message_manager.show_popup_error_mesg(msg);

    }
    else{
        $("#defend_scan").html(text_a);
        scan_panel.hide();
    }
}
//将传输风暴面板的数据写入添加面板
function change_conf_transport(){
    var checked_items = transport_panel.get_checked_items();
    var selected_protect = [];
    var text_a = "已选防护：";
    var is_null = false;
    // $(".ctr_transport").val("");
    $('#link_transport').parent().siblings().find('input').val('')
    if(checked_items.length > 0){
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "syn"){
                $("#enable_syn").val("on");
                var num_syn_source = $("#num_syn_source_input").val();
                var num_syn_dest = $("#num_syn_dest_input").val();
                $("#num_syn_source").val(num_syn_source);
                $("#num_syn_dest").val(num_syn_dest);
                if(num_syn_source == "" || num_syn_dest == ""){
                    is_null = true;
                }
                selected_protect.push("SYN洪泛攻击防护");
                //text_a += "SYN洪泛攻击防护、";
            }else if(checked_items[i].policy_name == "ack"){
                $("#enable_ack").val("on");
                var num_ack_source = $("#num_ack_source_input").val();
                var num_ack_dest = $("#num_ack_dest_input").val();
                $("#num_ack_source").val(num_ack_source);
                $("#num_ack_dest").val(num_ack_dest);
                if(num_ack_source == "" || num_ack_dest == ""){
                    is_null = true;
                }
                selected_protect.push("ACK洪泛攻击防护");
                //text_a += "ACK洪泛攻击防护、";
            }else if(checked_items[i].policy_name == "udp"){
                $("#enable_udp").val("on");
                var num_udp_source = $("#num_udp_source_input").val();
                var num_udp_dest = $("#num_udp_dest_input").val();
                $("#num_udp_source").val(num_udp_source);
                $("#num_udp_dest").val(num_udp_dest);
                if(num_udp_source == "" || num_udp_dest == ""){
                    is_null = true;
                }
                selected_protect.push("UDP洪泛攻击防护");
                //text_a += "UDP洪泛攻击防护、";
            }else if(checked_items[i].policy_name == "icmp"){
                $("#enable_icmp").val("on");
                var num_icmp_source = $("#num_icmp_source_input").val();
                var num_icmp_dest = $("#num_icmp_dest_input").val();
                $("#num_icmp_source").val(num_icmp_source);
                $("#num_icmp_dest").val(num_icmp_dest);
                if(num_icmp_source == "" || num_icmp_dest == ""){
                    is_null = true;
                }
                selected_protect.push("ICMP洪泛攻击防护");
                //text_a += "ICMP洪泛攻击防护";
            }
        }
        text_a += selected_protect.join("、");
    }else{
        text_a = "请选择防护类型";
    }
    if(is_null){
        message_manager.show_popup_error_mesg("选中的防护策略的阀值不能为空！");
    }else{
        $("#defend_transport").html(text_a);
        transport_panel.hide();
    }
}
//将应用层风暴面板的数据写入添加面板
function change_conf_apply(){
    var checked_items = apply_panel.get_checked_items();
    var selected_protect = [];
    var text_a = "已选防护：";
    var is_null = false;
    // $(".ctr_apply").val("");
    $('#link_apply').parent().siblings().find('input').val('')
    if(checked_items.length > 0){
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "http"){
                $("#enable_http").val("on");
                var num_http_source = $("#num_http_source_input").val();
                var num_http_dest = $("#num_http_dest_input").val();
                $("#num_http_source").val(num_http_source);
                $("#num_http_dest").val(num_http_dest);
                if(num_http_source == "" || num_http_dest == ""){
                    is_null = true;
                }
                selected_protect.push("HTTP GET/PUT洪泛攻击防护");
                //text_a += "HTTP GET/PUT洪泛攻击防护、";
            }else if(checked_items[i].policy_name == "dns"){
                $("#enable_dns").val("on");
                var num_dns_source = $("#num_dns_source_input").val();
                var num_dns_dest = $("#num_dns_dest_input").val();
                $("#num_dns_source").val(num_dns_source);
                $("#num_dns_dest").val(num_dns_dest);
                if(num_dns_source == "" || num_dns_dest == ""){
                    is_null = true;
                }
                $("#dns_type").val($("#dns_type_input").val());
                $("#dns_query_style").val($("#dns_query_style_input").val());
                selected_protect.push("DNS洪泛攻击防护");
                //text_a += "DNS洪泛攻击防护";
            }
        }
        text_a += selected_protect.join("、");
    }else{
        text_a = "请选择防护类型";
    }
    if(is_null){
        message_manager.show_popup_error_mesg("选中的防护策略的阀值不能为空！");
    }else{
        $("#defend_apply").html(text_a);
        apply_panel.hide();
    }
}
//将畸形数据包攻击防护面板的数据写入添加面板
function change_conf_strange(){
    var checked_items = strange_panel.get_checked_items();
    var selected_protect = [];
    // $(".ctr_abnormal").val("");
    $('#link_abnormal').parent().siblings().find('input').val('')
    if(checked_items.length > 0){
        var text_a = "已选防护：";
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "land"){
                $("#enable_land").val("on");
                selected_protect.push("Land攻击防护");
                //text_a += "Land攻击防护、";
            }else if(checked_items[i].policy_name == "smurf"){
                $("#enable_smurf").val("on");
                selected_protect.push("Smurf攻击防护");
                //text_a += "Smurf攻击防护、";
            }else if(checked_items[i].policy_name == "winnuke"){
                $("#enable_winnuke").val("on");
                selected_protect.push("Winnuke攻击防护");
                //text_a += "Winnuke攻击防护、";
            }else if(checked_items[i].policy_name == "teardrop"){
                $("#enable_teardrop").val("on");
                selected_protect.push("Teardrop攻击防护");
                //text_a += "Teardrop攻击防护、";
            }else if(checked_items[i].policy_name == "targa3"){
                $("#enable_targa3").val("on");
                selected_protect.push("Targa3攻击防护");
                //text_a += "Targa3攻击防护、";
            }else if(checked_items[i].policy_name == "fraggle"){
                $("#enable_fraggle").val("on");
                selected_protect.push("Fraggle攻击防护");
                //text_a += "Fraggle攻击防护、";
            }else if(checked_items[i].policy_name == "largest_icmp"){
                $("#enable_largest_icmp").val("on");
                selected_protect.push("超大ICMP数据攻击防护");
                //text_a += "超大ICMP数据攻击防护";
            }
        }
        text_a += selected_protect.join("、");
        $("#defend_strange").html(text_a);
    }else{
        $("#defend_strange").html("请选择防护类型");
    }
    strange_panel.hide();
}
//将IP协议报文选项面板的数据写入添加面板
function change_conf_ip(){
    var checked_items = ip_panel.get_checked_items();
    var selected_protect = [];
    // $(".ctr_ip").val("");
    $('#link_ip').parent().siblings().find('input').val('')
    if(checked_items.length > 0){
        var text_a = "已选防护：";
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "ip_record"){
                $("#enable_ip_record").val("on");
                selected_protect.push("IP记录路径选项报文防护");
                //text_a += "IP记录路径选项报文防护、";
            }else if(checked_items[i].policy_name == "ip_time"){
                $("#enable_ip_time").val("on");
                selected_protect.push("IP时间戳选项报文防护");
                //text_a += "IP时间戳选项报文防护、";
            }else if(checked_items[i].policy_name == "ip_district"){
                $("#enable_ip_district").val("on");
                selected_protect.push("IP宽松源路由选项报文防护");
                //text_a += "IP宽松源路由选项报文防护、";
            }else if(checked_items[i].policy_name == "ip_strict"){
                $("#enable_ip_strict").val("on");
                selected_protect.push("IP严格源路由选项报文防护");
                //text_a += "IP严格源路由选项报文防护、";
            }else if(checked_items[i].policy_name == "ip_safe"){
                $("#enable_ip_safe").val("on");
                selected_protect.push("IP安全和处理限制选项报文防护");
                //text_a += "IP安全和处理限制选项报文防护";
            }else if(checked_items[i].policy_name == "ip_unlaw"){
                $("#enable_ip_unlaw").val("on");
                selected_protect.push("非法IP选项报文防护");
                //text_a += "非法IP选项报文防护";
            }
        }
        text_a += selected_protect.join("、");
        $("#defend_ip").html(text_a);
    }else{
        $("#defend_ip").html("请选择防护类型");
    }
    
    ip_panel.hide();
}
//将TCP协议报文选项面板的数据写入添加面板
function change_conf_tcp(){
    var checked_items = tcp_panel.get_checked_items();
    var selected_protect = [];
    // $(".ctr_tcp").val("");
    $('#link_tcp').parent().siblings().find('input').val('')
    if(checked_items.length > 0){
        var text_a = "已选防护：";
        for(var i = 0;i < checked_items.length; i++){
            if(checked_items[i].policy_name == "tcp_head0"){
                $("#enable_tcp_head0").val("on");
                selected_protect.push("TCP报头标志全为0防护");
                //text_a += "TCP报头标志全为0防护、";
            }else if(checked_items[i].policy_name == "tcp_head1"){
                $("#enable_tcp_head1").val("on");
                selected_protect.push("TCP报头标志全为1防护");
                //text_a += "TCP报头标志全为1防护、";
            }else if(checked_items[i].policy_name == "syn_fin"){
                $("#enable_syn_fin").val("on");
                selected_protect.push("SYN和FIN标志位同时为1防护");
                //text_a += "SYN和FIN标志位同时为1防护、";
            }else if(checked_items[i].policy_name == "fin"){
                $("#enable_fin").val("on");
                selected_protect.push("仅FIN标志位为1防护");
                //text_a += "仅FIN标志位为1防护";
            }
        }
        text_a += selected_protect.join("、");
        $("#defend_tcp").html(text_a);
    }else{
        $("#defend_tcp").html("请选择防护类型");
    }
    
    tcp_panel.hide();
}
//重置添加面板超链接文字
function recovery_text_a(){
    $("#defend_tcp").html("请选择防护类型");
    $("#defend_ip").html("请选择防护类型");
    $("#defend_strange").html("请选择防护类型");
    $("#defend_scan").html("请选择防护类型");
    $("#defend_apply").html("请选择防护类型");
    $("#defend_transport").html("请选择防护类型");
    
    scan_panel.uncheck_current_page();
    scan_panel.update_info();
    transport_panel.uncheck_current_page();
    transport_panel.update_info();
    apply_panel.uncheck_current_page();
    apply_panel.update_info();
    strange_panel.uncheck_current_page();
    strange_panel.update_info();
    ip_panel.uncheck_current_page();
    ip_panel.update_info();
    tcp_panel.uncheck_current_page();
    tcp_panel.update_info();
    
    $(".ctr_inpt").val("2000");
    $(".ctr_inpt").attr("disabled","disabled");
    //$("#max_val_ipaddr_input").val("200");
    //$("#max_val_port_input").val("2000");
    $(".ctr_inpt").css("width","50px");
}
//删除规则函数，包含规则引用检查
function check_delete_rule(item_id){
    //var length_used_rule = [];
    var data_item = list_panel.get_item(item_id);
    //length_used_rule = data_item.rules_for_policy.split("&");
    if( data_item.rules_for_policy != "" ){
        list_panel.operate_item( data_item.id, 'delete_data',
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(data_item.id);
    }
}
//删除选中规则，包含规则引用检查
function check_delete_selected_items(){
    var checked_items = list_panel.get_checked_items();
    if(checked_items.length < 1){
        message_manager.show_popup_note_mesg("请先选中策略项");
        return;
    }
    var checked_items_id = new Array();
    var ids = "";
    var is_used = "no";
    var used_policy = new Array();
    for(var i=0;i<checked_items.length;i++){
        checked_items_id.push(checked_items[i].id);
        if(checked_items[i].rules_for_policy != ""){
            is_used = "yes";
            used_policy.push(checked_items[i].name);
        }
    }
    ids = checked_items_id.join("&");
    if(is_used == "yes"){
        list_panel.operate_item( ids, 'delete_data',used_policy.join("、")+
        '策略模板正在被使用。删除该策略模板，也将删除使用该策略模板的规则', true );
    }else{
        list_panel.delete_item(ids);
    }
}
