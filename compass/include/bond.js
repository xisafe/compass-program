/*
 * 描述:链路聚合配置页面js
 *
 * 作者: xinzhiwei 1002395703@qq.com
 * 历史：
 *       2014.11.7 Created by xinzhiwei
 *       2015.02.11 Modified by WangLin
 */
var ass_url = "/cgi-bin/bond.cgi";
var unoccupied_eths = new Array();

var message_box_config = {
    url: ass_url,
    check_in_id: "mesg_box_test",
    panel_name: "my_message_box"
}

var add_panel_config = {
    url: ass_url,
    check_in_id: "bond_add_panel",
    panel_name: "bond_add_panel",
    rule_title: "新的聚合接口",
    is_panel_closable: true,
    is_panel_stretchable: false,
    is_modal: true,
    modal_config: {
        modal_box_size: "l",
        modal_level: 10
    },
    event_handler: {
        after_cancel_edit:function(add_obj){
            update_eths( unoccupied_eths );
        }
    },
    items_list: [
        {
            title: "聚合接口名称 *",
            sub_items: [
            {
                enable: true,
                type: 'text',
                tip: "(以bond开头, 范围: bond0-bond3)",
                id: "bond_name",
                name: "bond_name",
                placeholder: "请输入接口名称",
                check: {
                    type: 'text',
                    check: 'name|',
                    required: 1,
                    ass_check: function( check ) {
                        var msg = "";
                        var val = $("#bond_name").val();
                        var pattern = /^bond[0-3]$/;

                        if( !pattern.test(val) ){
                            msg = "以bond开头, 范围: bond0-bond3";
                        }
                        return msg;
                    }
                }
            }]
        }, {
            title: "选择成员端口 *",
            sub_items: [
            {
                enable: true,
                type: "select",
                label: "可选的端口",
                id: "left_select",
                name:"left_select",   //此处要改成left_select而非member_port
                style: "height: 120px;",
                item_style: "width: 220px;",
                multiple: true,
                options: [
                ]
            }, {
                enable: true,
                type: "items_group",
                item_style: "width: 150px;line-height: 45px;",
                item_class: "align-center",
                sub_items: [
                {
                    enable: true,
                    type: "button",
                    id: "add",
                    value: ">>",
                    functions: {
                        onclick: "left_to_right();"
                    }
                }, {
                    enable: true,
                    type: "button",
                    id: "del",
                    value: "<<",
                    functions: {
                        onclick: "right_to_left();"
                    }
                }, {
                    enable: true,
                    type: "label",   //为了让上面两个button的高度居中就在它们下面添加一个label并设置高为18px宽为50px
                    value: "",
                    item_style: "height: 18px;width: 50px;"
                }]
            }, {
                enable: true,
                type: "select",
                label: "已选的端口",
                id: "right_select",
                name: "right_select",
                style: "height: 120px;",
                item_style: "width: 220px;",
                multiple: true,
                options: []
            }, {
                enable: true,
                type: 'text',
                id: "selected_member_port",
                name: "selected_member_port",
                value: "",
                item_style: "display:none;"
            }]
        },{
            title: "桥接到区域 *",
            sub_items: [
            {
                enable: true,
                type: "select",
                tip: "",
                id: "bond_area",
                name: "bond_area",
                functions: {  
                    onchange:""
                },
                options: []
            }]
        }
    ]
};

var list_panel_render = {
    bond_area: {
        render: function( default_rendered_text, data_item ) {
            var bond_area = {
                br0: "LAN区",
                br1: "DMZ区",
                br2: "WIFI区",
                none: "无"
            }
            var bond_area_class = {
                br0: "GREEN",
                br1: "ORANGE",
                br2: "BLUE",
                none: "unoccupied"
            }
            return '<span class="' + bond_area_class[default_rendered_text] + '">' + bond_area[default_rendered_text] + '</span>';
        }
    }
};

var list_panel_config = {
    url: ass_url,
    check_in_id: "bond_list_panel",
    panel_name: "bond_list_panel",
    is_default_search: false,
    event_handler: {
        before_load_data: function( list_obj ) {
            
        },
        after_load_data: function ( list_obj, response ) {
            unoccupied_eths = response.eths;
            update_eths( response.eths );
        }
    },
    render: list_panel_render,
    panel_header: [
        {
            enable: true,
            type: 'text',
            title: "聚合接口名称",
            name: "bond_name",
            width: "20%"
        }, {
            enable: true,
            type: 'text',
            title: "成员端口",
            name: "selected_member_port",
            width: "30%"
        }, {
            enable: true,
            type: 'text',
            title: "桥接区域",
            name: "bond_area",
            column_cls: "align-center",
            "td_class": "align-center",
            width: "30%"
        }, {
            enable: true,
            type: "action",
            name: "action",
            "td_class": "align-center",
            width: "20%"
        }
    ],
    top_widgets: [
    {
        enable: true,
        type: "image_button",
        button_icon: "add16x16.png",
        button_text: "新建",
        functions: {
            onclick: "add_bond();"
        }
    }]
};

var add_panel = new RuleAddPanel( add_panel_config );
var list_panel = new PagingHolder( list_panel_config );
var message_manager = new MessageManager( message_box_config );

$( document ).ready(function() {

    /* 渲染面板 */
    message_manager.render();
    list_panel.render();

    // add_panel.hide();

    /* 设置面板关联 */
    add_panel.set_ass_list_panel( list_panel );
    list_panel.set_ass_add_panel( add_panel );

    add_panel.set_ass_message_manager( message_manager );
    list_panel.set_ass_message_manager( message_manager );

    init_used_area();

});

function init_used_area(){
    var sending_data = {
        ACTION: "load_used_area"
    }

    function ondatareceived( response ) {
        var used_area = response.used_area;
        var options = new Array();
        for ( var i = 0; i < used_area.length; i++ ) {
            var item = used_area[i];
            var option = {
                enable: true,
                value: item.text_value,
                text: item.text,
                cls: item["class"]
            }
            options.push( option );
        }
        add_panel_config.items_list[2].sub_items[0].options = options;
        add_panel.render();
        add_panel.hide();

        list_panel.update_info( true );
    }

    add_panel.request_for_json( sending_data, ondatareceived );
}

function update_eths( eths ) { //每次编辑完后都要更新左框里的选项
    var options = "";
    for ( var i = 0; i < eths.length; i++ ) {
        var item = eths[i];
        var eth_name = item.eth_name;
        var eth_color = item.eth_color;  // color的值就是GREEN,RED,ORANGE !
        var class_str = eth_color;  // 把color 的值直接赋值给 class_str

        options += '<option class="' + class_str + '"value="' + eth_name + '">' + eth_name + '</option>';
    }
    $( "#left_select" ).empty();
    $( "#right_select" ).empty();
    $( "#left_select" ).append( options );
}


function left_to_right(){   // 思路：把被选中的option元素从左边的select对象里删除或隐藏并且添加到右边的select对象里!

    var selected = $("#left_select option:selected");
    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var class_str = $( option ).attr("class");
        // var tt = "<option class=" +class_str+ " value=" +val+ ">"+txt+"</option>";
        var tt = '<option class="' + class_str + '"value="' + val + '">' + txt + '</option>';
        $( option ).remove();   //注意要把option变量用$()包装为jQuery对象用remove方法才能起作用！
        $( "#right_select" ).append(tt);
    });
    save_selected_ports();

}

function right_to_left(){

    var selected = $("#right_select option:selected");
    selected.each(function(){
        var option = this;
        var val = $( option ).val();
        var txt = $( option ).text();
        var class_str = $( option ).attr("class");
        // var tt = "<option class=" +class_str+ " value=" +val+ ">"+txt+"</option>";
        var tt = '<option class="' + class_str + '"value="' + val + '">' + txt + '</option>';
        $( option ).remove();
        $( "#left_select" ).append(tt);
    });
    save_selected_ports();
}

function save_selected_ports() {
    var options = $("#right_select option");
    var selected_val = "";
    var selected_vals = new Array();

    options.each(function(){
        var option = this;
        var val = $( option ).val();
        selected_vals.push( val );
    });

    selected_val = selected_vals.join( "," );

    $( "#selected_member_port" ).val( selected_val );

}

function add_bond() {
    add_panel.show();
}