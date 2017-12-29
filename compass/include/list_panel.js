/*
 * 描述: 用于创建可翻页的列表面板
 * 参数：panel_config -- 翻页面板所需的所有配置，具体使用见list_panel_extend.js文件
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2014.08.01 WangLin创建
 */
 function PagingHolder( panel_config ) {
    /* 第一步，初始化本panel_config */
    this.init_panel_config( panel_config );
    /* 第二步，创建面板相关变量 */
    this.init_paging_tools_variable();
    /* 第三步，创建面板 */
    // this.render();//留给用户去渲染
}

PagingHolder.prototype.render = function() {
    var paging_holder = this;

    /* 第一步，创建面板 */
    paging_holder.display_list_panel();
    /* 第二步，给面板上的控件加载默认动作 */
    paging_holder.init_paging_tools();
    /* 第三步，加载数据前初始化表单检查 */
    paging_holder.init_check_input_data();
    /* 第四步，加载数据 */
    // paging_holder.update_info( true );

}

PagingHolder.prototype.init_panel_config = function( panel_config ) {
    var paging_holder = this;
    paging_holder.panel_config = panel_config;

    paging_holder.url        = panel_config.url;
    paging_holder.panel_name = panel_config.panel_name !== undefined ? panel_config.panel_name : "my_list_panel"; /*默认的面板名字*/
    paging_holder.title_icon = panel_config.title_icon !== undefined ? panel_config.title_icon  : "";/*配置面板图标*/
    /*默认渲染类型*/
    paging_holder.panel_config.default_render = {
        'checkbox': true,
        'radio': true,
        'action': true,
        'move':true
    };
    paging_holder.paging_action = {
        first_page: "first_page",
        last_page: "last_page",
        go_to_page: "go_to_page",
        next_page: "next_page",
        end_page: "end_page",
        refresh: "refresh",
        search: "search",
    }
    paging_holder.panel_config.is_panel_closable = panel_config.is_panel_closable !== undefined ? panel_config.is_panel_closable : false;
    /*默认搜索*/
    paging_holder.panel_config.is_default_search = panel_config.is_default_search !== undefined ? panel_config.is_default_search : true;
    paging_holder.panel_config.is_paging_tools = panel_config.is_paging_tools !== undefined ? panel_config.is_paging_tools : true;

    paging_holder.panel_config.is_modal = panel_config.is_modal !== undefined ? panel_config.is_modal : false;
    // 输出到面板中字符是否进行转义，false不转义，true转义
    paging_holder.panel_config.render_to_text = panel_config.render_to_text !== undefined ? panel_config.render_to_text : true;
    /* 定义面板是否可拖拽 */
    paging_holder.panel_config.is_panel_draggable = panel_config.is_panel_draggable !== undefined ? panel_config.is_panel_draggable : true;

    paging_holder.panel_config.border_transparent = panel_config.border_transparent !== undefined ? panel_config.border_transparent : false;
    if ( paging_holder.panel_config.is_modal ) {
        if ( panel_config.modal_config !== undefined ) {
            if ( panel_config.modal_config.modal_box_size === undefined ) {
                panel_config.modal_config.modal_box_size = "l"; // 默认值为large
            }
            if ( panel_config.modal_config.modal_level === undefined ) {
                panel_config.modal_config.modal_level = 10;     // 默认值为10
            }
        } else {
            panel_config.modal_config = {
                modal_box_size: "l",    // 默认值为large
                modal_level: 10,        // 默认值为10
            }
        }
    }

    paging_holder.panel_config.ass_add_panel = panel_config.ass_add_panel !== undefined ? panel_config.ass_add_panel : null;
    paging_holder.panel_config.ass_message_manager = panel_config.ass_message_manager !== undefined ? panel_config.ass_message_manager : null;
    paging_holder.panel_config.actions = panel_config.actions !== undefined ? panel_config.actions : new Object();
    /* 外接事件处理函数 */
    paging_holder.panel_config.event_handler = panel_config.event_handler !== undefined ? panel_config.event_handler : null;
    /*检查输入正确与否的工具*/
    paging_holder.check_tool = new ChinArk_forms();
    paging_holder.search_check_tool = new ChinArk_forms();
}

PagingHolder.prototype.set_ass_add_panel = function( add_panel ) {
    var paging_holder = this;

    paging_holder.panel_config.ass_add_panel = add_panel;
}

PagingHolder.prototype.set_ass_message_manager = function( message_manager ) {
    var paging_holder = this;

    paging_holder.panel_config.ass_message_manager = message_manager;
}

PagingHolder.prototype.get_search_input_check_obj = function() {
    var paging_holder = this;

    var extend_search = paging_holder.panel_config.extend_search;

    if( extend_search === undefined || extend_search === null ) {
        return null;
    }

    var check_count = 0;
    var check_option = new Object();
    for ( var i = 0; i < extend_search.length; i++ ) {
        var item = extend_search[i];
        if ( item.check !== undefined ) {
            if ( item.name === undefined ) {
                paging_holder.show_error_mesg( "初始化查询表单检查失败，请检查name属性是否填写");
                return null;
            } else {
                check_option[item.name] = item.check;
                check_count++;
            }
        }
    }

    var search_check = null;
    if ( check_count > 0 ) {
        search_check = new Object();
        search_check.form_name = paging_holder.search_form_name;
        search_check.option = check_option;
    }

    return search_check;
}

PagingHolder.prototype.init_paging_tools = function() {
    var paging_holder = this;
    var panel_close_selector = "#" + paging_holder.panel_close_id;
    var first_page_icon_selector = "#" + paging_holder.first_page_icon_id;
    var last_page_icon_selector = "#" + paging_holder.last_page_icon_id;
    var current_page_selector   = "#" + paging_holder.current_page_id;
    var next_page_icon_selector = "#" + paging_holder.next_page_icon_id;
    var end_page_icon_selector = "#" + paging_holder.end_page_icon_id;
    var refresh_icon_selector = "#" + paging_holder.refresh_icon_id;
    var search_key_selector = "#" + paging_holder.search_key_id;
    var search_button_selector = "#" + paging_holder.search_button_id;
    var is_paging_tools = paging_holder.panel_config.is_paging_tools;
    /*点击关闭按钮*/
    $( panel_close_selector ).click(function(){
        paging_holder.HideForBorder();
    });
    if( is_paging_tools === true ) {
        /*初始化翻页按钮的各个状态*/
        paging_holder.update_paging_tools_info();
        /*点击第一页按钮*/
        $( first_page_icon_selector ).click(function(){
            paging_holder.first_page_op();
        });
        /*点击上一页按钮*/
        $( last_page_icon_selector ).click(function(){
            paging_holder.last_page_op();
        });
        /*输入页码,或者按enter键按钮*/
        $( current_page_selector ).keydown(function( event ){
            paging_holder.current_page_input_control( event );
        });
        /*点击下一页按钮*/
        $( next_page_icon_selector ).click(function(){
            paging_holder.next_page_op();
        });
        /*点击最后一页按钮*/
        $( end_page_icon_selector ).click(function(){
            paging_holder.end_page_op();
        });
        /*点击刷新按钮*/
        $( refresh_icon_selector ).click(function(){
            paging_holder.update_info( true, paging_holder.paging_action.refresh );
        });
    }
    /*在搜索框中输入关键字或者按enter键*/
    $( search_key_selector ).keydown(function( event ){
        paging_holder.search_input_control( event );
    });
    /*点击搜索按钮*/
    $( search_button_selector ).click(function(){
        paging_holder.update_info( true );
    });
    /*点击全选按钮*/
    paging_holder.init_control_checkbox();
}

PagingHolder.prototype.init_control_checkbox = function() {
    var paging_holder = this;

    var control_checkbox_selector = "#" + paging_holder.control_checkbox_id;
    if( $( control_checkbox_selector ).length > 0 ) {
        /*如果存在全选按钮，初始化*/

        $( control_checkbox_selector ).click(function(){
            paging_holder.toggle_check_current_page( $( control_checkbox_selector )[0] );
        });
    }
}

PagingHolder.prototype.add_listener_to_control_items = function() {
    var paging_holder = this;

    paging_holder.add_listener_to_checkboxs();
    paging_holder.add_listener_to_radios();
    paging_holder.add_listener_to_up_button();
    paging_holder.add_listener_to_down_button();
    paging_holder.add_listener_to_top_button();
    paging_holder.add_listener_to_bottom_button();
    paging_holder.add_listener_to_toggle_enable();
    paging_holder.add_listener_to_edit_buttons();
    paging_holder.add_listener_to_delete_buttons();
    paging_holder.add_listener_to_default_search();
    if (paging_holder.panel_config.is_panel_draggable && paging_holder.panel_config.is_modal) {
        paging_holder.add_listener_to_panel_header();
    }
    paging_holder.add_listener_to_hover_tr();
}
PagingHolder.prototype.add_listener_to_hover_tr = function() {
    var paging_holder = this;
    $("#"+paging_holder.panel_body_id).on('mouseenter', 'tr', function(event) {
        if ($(this).children('td').eq(0).html() != "&nbsp;") {
            $(this).addClass('background-hovered');
        }
    }).on('mouseleave', 'tr', function(event) {
        $(this).removeClass('background-hovered');
    });

}
PagingHolder.prototype.add_listener_to_panel_header = function() {
    var paging_holder = this;

    var panel_container = paging_holder.panel_id;
    var panel_header = document.querySelector('#'+paging_holder.panel_id).children[0];
    var panel_container_father;
    if (paging_holder.panel_config.border_transparent) {
        var panel_TB_id = 'TransparentBorder_' + paging_holder.panel_name;
        panel_container_father = document.querySelector('#' + panel_TB_id);
    } else {
        panel_container_father = document.querySelector('#' + panel_container).parentElement;
    }

        panel_header.className += ' add_panel_header_move';

        panel_header.onmousedown = function(ev) {　　　　
            var oevent = ev || event;

            　　　　
            var distanceX = oevent.clientX - panel_container_father.offsetLeft;　　　　
            var distanceY = oevent.clientY - panel_container_father.offsetTop;

            　　　　
            document.onmousemove = function(ev) {　　　　
                var oevent = ev || event;
                
                var marginLeft = Number( panel_container_father.style.marginLeft.replace('px',''));
                var marginTop = Number( panel_container_father.style.marginTop.replace('px',''));

                var ele_left = oevent.clientX - distanceX -marginLeft;
                var ele_left_down = document.body.scrollWidth - panel_container_father.offsetWidth - 20- marginLeft;
                var ele_top = oevent.clientY - distanceY -marginTop;
                var ele_top_down = document.body.scrollHeight - panel_container_father.offsetHeight - 40 - marginTop;

                if (ele_left < -marginLeft) {
                    ele_left = -marginLeft;
                } else if (ele_left > ele_left_down) {
                    ele_left = ele_left_down;
                }
                if (ele_top < -marginTop) {
                    ele_top = -marginTop
                } else if (ele_top > ele_top_down) {
                    ele_top = ele_top_down;
                }

                　　　　
                panel_container_father.style.left = ele_left + 'px';　　　　
                panel_container_father.style.top = ele_top + 'px';　　　　
            };　　　　
            document.onmouseup = function() {　　　　　　
                document.onmousemove = null;　　　　　　
                document.onmouseup = null;　　　　
            };　　
        };
    // }
    
}
// 添加搜素框的监听事件
PagingHolder.prototype.add_listener_to_default_search = function(){
    // var paging_holder = this;
    // var panel_config = paging_holder.panel_config;
    // var search_selector = "#" + paging_holder.search_key_id;
    // var default_search = null;
    // var search_box = $( search_selector);
    // search_box.addEventListener("onchange",function(){
    //     paging_holder.update_info( true, paging_holder.paging_action.search );
    // })
}
PagingHolder.prototype.add_listener_to_checkboxs = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    var checkbox_selector = "." + paging_holder.checkbox_class;

    var checkbox_listeners = null;
    if ( panel_config.render !== undefined ) {
        var render = panel_config.render;
        if ( render.checkbox !== undefined ) {
            var checkbox = render.checkbox;
            if ( checkbox.listeners !== undefined ) {
                checkbox_listeners = checkbox.listeners;
            }
        }
    }
    
    var checkboxs = $( checkbox_selector );
    checkboxs.each( function() {
        $( this ).click(function(){
            paging_holder.set_check( this.value, this.checked,this.attributes.index.value );
        });

        /* 注入外界定义的函数 */
        if ( checkbox_listeners ) {
            for ( var listener in checkbox_listeners ) {
                $( this ).bind( listener, function( event ){
                    var data_item = paging_holder.get_item( $( this ).val() );
                    checkbox_listeners[listener]( this, data_item, paging_holder );
                });
            }
        }
    });
}

PagingHolder.prototype.add_listener_to_radios = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    var radio_selector = "input[name='" + paging_holder.radio_name + "']";

    var radio_listeners = null;
    if ( panel_config.render !== undefined ) {
        var render = panel_config.render;
        if ( render.radio !== undefined ) {
            var radio = render.radio;
            if ( radio.listeners !== undefined ) {
                radio_listeners = radio.listeners;
            }
        }
    }

    var radios = $( radio_selector );
    radios.each( function() {
        var radio_handle = this;
        $( radio_handle ).click(function(){
            paging_holder.set_check_single( this.value, this.checked );
        });

        /* 注入外界定义的函数 */
        if ( radio_listeners ) {
            for ( var listener in radio_listeners ) {
                $( radio_handle ).bind( listener, function( event ){
                    var data_item = paging_holder.get_item( $( radio_handle ).val() );
                    radio_listeners[listener]( radio_handle, data_item, event, paging_holder );
                });
            }
        }
    });
}
PagingHolder.prototype.add_listener_to_up_button = function(){
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var up_selector = "." + paging_holder.up_class;
    var up_buttons = $( up_selector);
        up_buttons.each( function(){
            var up_button = this;
            $(up_button).click(function(){
                var element = this;
               if( panel_config.actions.up_button !== undefined ) {
                panel_config.actions.up_button( paging_holder.get_item(element.value) );
                } else {
                    paging_holder.up_item( element.value );
                }
            });
        })
}
PagingHolder.prototype.add_listener_to_down_button = function(){
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var down_selector = "." + paging_holder.down_class;
    var down_buttons = $( down_selector);
        down_buttons.each( function(){
            var down_button = this;
            $(down_button).click(function(){
                var element = this;
               if( panel_config.actions.down_button !== undefined ) {
                panel_config.actions.down_button( paging_holder.get_item(element.value) );
                } else {
                    paging_holder.down_item( element.value );
                }
            });
        })
}
PagingHolder.prototype.add_listener_to_top_button = function(){
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var top_selector = "." + paging_holder.top_class;
    var top_buttons = $( top_selector);
        top_buttons.each( function(){
            var top_button = this;
            $(top_button).click(function(){
                var element = this;
               if( panel_config.actions.top_button !== undefined ) {
                panel_config.actions.top_button( paging_holder.get_item(element.value) );
                } else {
                    paging_holder.top_item( element.value );
                }
            });
        })
}
PagingHolder.prototype.add_listener_to_bottom_button = function(){
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var bottom_selector = "." + paging_holder.bottom_class;
    var bottom_buttons = $( bottom_selector);
        bottom_buttons.each( function(){
            var bottom_button = this;
            $(bottom_button).click(function(){
                var element = this;
               if( panel_config.actions.bottom_button !== undefined ) {
                panel_config.actions.bottom_button( paging_holder.get_item(element.value) );
                } else {
                    paging_holder.bottom_item( element.value );
                }
            });
        })
}
PagingHolder.prototype.add_listener_to_toggle_enable = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    var enable_selector = "." + paging_holder.enable_class;
    var disable_selector = "." + paging_holder.disable_class;

    var enable_buttons = $( enable_selector );
    var disable_buttons = $( disable_selector );
    enable_buttons.each( function() {
        var enable_button = this;
        $( enable_button ).click(function(){
            var element = this;
            if( panel_config.actions.enable_button !== undefined ) {
                panel_config.actions.enable_button( paging_holder.get_item(element.value) );
            } else {
                paging_holder.enable_item( element.value );
            }
        });
    });
    disable_buttons.each( function() {
        var disable_button = this;
        $( disable_button ).click(function(){
            var element = this;
            if( panel_config.actions.disable_button !== undefined ) {
                panel_config.actions.disable_button( paging_holder.get_item(element.value) );
            } else {
                paging_holder.disable_item( element.value );
            }
        });
    })
}

PagingHolder.prototype.add_listener_to_edit_buttons = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    var edit_selector = "." + paging_holder.edit_class;

    var edit_buttons = $( edit_selector );
    edit_buttons.each( function() {
        var edit_button = this;
        $( edit_button ).click(function(){
            var element = this;
            if( paging_holder.panel_config.actions.eidt_button !== undefined ) {
                paging_holder.panel_config.actions.eidt_button( paging_holder.get_item(element.value) );
            } else {
                paging_holder.edit_item( element.value );
            }
        });
    })
}

PagingHolder.prototype.add_listener_to_delete_buttons = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    var delete_selector = "." + paging_holder.delete_class;

    var delete_buttons = $( delete_selector );
    delete_buttons.each( function() {
        var delete_button = this;
        $( delete_button ).click(function(){
            var element = this;
            if( panel_config.actions.delete_button !== undefined ) {
                panel_config.actions.delete_button( paging_holder.get_item(element.value) );
            } else {
                paging_holder.delete_item( element.value );
            }
        });
    })
}
PagingHolder.prototype.up_item = function(item_id){
    var paging_holder = this;
    paging_holder.operate_item( item_id, "up", "上移", false);
}
PagingHolder.prototype.down_item = function( item_id){
    var paging_holder = this;
    paging_holder.operate_item( item_id, "down","下移",false);
}
PagingHolder.prototype.top_item = function(item_id){
    var paging_holder = this;
    paging_holder.operate_item( item_id, "top", "置顶", false);
}
PagingHolder.prototype.bottom_item = function( item_id){
    var paging_holder = this;
    paging_holder.operate_item( item_id, "bottom","置底",false);
}
PagingHolder.prototype.enable_item = function( item_id ) {
    var paging_holder = this;

    paging_holder.operate_item( item_id, "enable_data", "确认启用?", false );
}

PagingHolder.prototype.disable_item = function( item_id ) {
    var paging_holder = this;

    paging_holder.operate_item( item_id, "disable_data", "确认禁用?", true );
}

PagingHolder.prototype.edit_item = function( item_id ) {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    /*第一步，设置行被选中状态*/
    paging_holder.select_edit_item( item_id );

    /*第二步,定义编辑完成后执行的动作(更新信息)*/
    function on_finished() {
        // paging_holder.deselect_edit_item();
        // paging_holder.update_info( true );
    }

    /*第三步，调用外部函数执行编辑动作*/
    if( panel_config.actions.edit_item !== undefined ) {
        panel_config.actions.edit_item( paging_holder.get_item(item_id), on_finished );
    } else {
        var ass_add_panel = panel_config.ass_add_panel;
        if ( ass_add_panel !== undefined && ass_add_panel !== null ) {
            ass_add_panel.load_data_into_add_panel( paging_holder.get_item( item_id ) );
        }
        on_finished();
    }

}

PagingHolder.prototype.delete_item = function( item_id ) {
    var paging_holder = this;

    paging_holder.operate_item( item_id, "delete_data", "确认删除?", true );
}

PagingHolder.prototype.operate_item = function( item_id, operation, operation_tip, inquiry ) {
    var paging_holder = this;

    var sending_data = {
        ACTION: operation,
        id: item_id,
        panel_name: paging_holder.panel_name
    }

    function ondatareceived( data ) {
        if ( paging_holder.is_operation_succeed(data) ) {
            paging_holder.update_info( true );
            if ( data.mesg !== undefined && data.mesg != "" ) {
                if ( message_manager !== undefined && message_manager !== null ) {
                    message_manager.show_note_mesg( data.mesg  );
                }else{
                    paging_holder.show_note_mesg( data.mesg );
                }
            }
            if ( paging_holder.is_need_reload(data) ) {
                paging_holder.show_apply_mesg();
            }
        } else {
            if ( data.mesg !== undefined && data.mesg != "" ) {
                paging_holder.show_error_mesg( data.mesg );
            }
        }
    }

    if( inquiry !== undefined && inquiry ) {
        if( confirm( operation_tip) ) {
            paging_holder.request_for_json( sending_data, ondatareceived );
        }
    } else {
        paging_holder.request_for_json( sending_data, ondatareceived );
    }
}

PagingHolder.prototype.first_page_op = function() {
    var paging_holder = this;
    var control_checkbox_id = paging_holder.control_checkbox_id;
    if(paging_holder.current_page > paging_holder.first_page) {
        paging_holder.current_page = paging_holder.first_page;
        paging_holder.update_info( false, paging_holder.paging_action.first_page );
        $("#"+control_checkbox_id).attr("checked",paging_holder.is_selected_checkbox());
        
    }

}

PagingHolder.prototype.last_page_op = function() {
    var paging_holder = this;
    var control_checkbox_id = paging_holder.control_checkbox_id;
    

    if(paging_holder.current_page > paging_holder.first_page) {
        paging_holder.current_page = paging_holder.current_page - 1;
        paging_holder.update_info( false, paging_holder.paging_action.last_page );
        $("#"+control_checkbox_id).attr("checked",paging_holder.is_selected_checkbox());

    }
}

PagingHolder.prototype.current_page_input_control = function( event ) {
    var paging_holder = this;
    var current_page_selector   = "#" + paging_holder.current_page_id;
    /*8：退格键、46：delete、37-40： 方向键
    **48-57：主键盘区的数字、96-105：小键盘区的数字
    **110、190：小键盘区和主键盘区的小数
    **189、109：小键盘区和主键盘区的负号
    **enter:13
    **/
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode||event.keyCode; //IE、FF下获取键盘码
    if (cod == 13){
        /*按enter键*/
        paging_holder.current_page = Number( $( current_page_selector ).val() );
        paging_holder.update_info( false, paging_holder.paging_action.go_to_page );
    } else {
        if(cod!=8 && cod != 46 && !((cod >= 48 && cod <= 57) || (cod >= 96 && cod <= 105) || (cod >= 37 && cod <= 40))){
            notValue(event);
        }
    }
    function notValue(event){
        event.preventDefault ? event.preventDefault() : event.returnValue=false;
    }
}

PagingHolder.prototype.search_input_control = function( event ){
    var paging_holder = this;
    var event = event || window.event; //IE、FF下获取事件对象
    var cod = event.charCode || event.keyCode; //IE、FF下获取键盘码
    if(cod == 13) {
        paging_holder.update_info( true, paging_holder.paging_action.search );
    }
}

PagingHolder.prototype.next_page_op = function() {
    var paging_holder = this;
    var control_checkbox_id = paging_holder.control_checkbox_id;
    if(paging_holder.current_page < paging_holder.total_page) {
        paging_holder.current_page = paging_holder.current_page + 1;
        paging_holder.update_info( false, paging_holder.paging_action.next_page );
        $("#"+control_checkbox_id).attr("checked",paging_holder.is_selected_checkbox());

    }
}

PagingHolder.prototype.end_page_op = function() {
    var paging_holder = this;
    var control_checkbox_id = paging_holder.control_checkbox_id;

    if(paging_holder.current_page < paging_holder.total_page) {
        paging_holder.current_page = paging_holder.total_page;
        paging_holder.update_info();
        paging_holder.disable_next_end_page_op( false, paging_holder.paging_action.end_page );
        $("#"+control_checkbox_id).attr("checked",paging_holder.is_selected_checkbox());

    }
}

PagingHolder.prototype.enable_first_last_page_op = function() {
    var paging_holder = this;
    

    var first_page_icon_selector = "#" + paging_holder.first_page_icon_id;
    var last_page_icon_selector = "#" + paging_holder.last_page_icon_id;
    $( first_page_icon_selector ).attr("src", "../images/first-page.gif").removeClass('disabled');
    $( last_page_icon_selector ).attr("src", "../images/last-page.gif").removeClass('disabled');
}

PagingHolder.prototype.enable_next_end_page_op = function() {
    var paging_holder = this;
    var next_page_icon_selector = "#" + paging_holder.next_page_icon_id;
    var end_page_icon_selector = "#" + paging_holder.end_page_icon_id;
    $( next_page_icon_selector ).attr("src", "../images/next-page.gif").removeClass('disabled');
    $( end_page_icon_selector ).attr("src", "../images/end-page.gif").removeClass('disabled');

}

PagingHolder.prototype.disable_first_last_page_op = function() {
    var paging_holder = this;
    var first_page_icon_selector = "#" + paging_holder.first_page_icon_id;
    var last_page_icon_selector = "#" + paging_holder.last_page_icon_id;
    $( first_page_icon_selector ).attr("src", "../images/first-page-off.png").addClass('disabled');
    $( last_page_icon_selector ).attr("src", "../images/last-page-off.png").addClass('disabled');
}

PagingHolder.prototype.disable_next_end_page_op = function() {
    var paging_holder = this;
    var next_page_icon_selector = "#" + paging_holder.next_page_icon_id;
    var end_page_icon_selector = "#" + paging_holder.end_page_icon_id;
    $( next_page_icon_selector ).attr("src", "../images/next-page-off.png").addClass('disabled');
    $( end_page_icon_selector ).attr("src", "../images/end-page-off.png").addClass('disabled');
}
/*A Function to juduge  checkbox button of select all is should keep checked*/
PagingHolder.prototype.is_selected_checkbox = function(){
    var paging_holder = this;
    var panel_name = paging_holder.panel_name;
    var current_page = paging_holder.current_page;
    var page_size = paging_holder.page_size;
    var detail_data = paging_holder.detail_data;
    var data_item_length = detail_data.length;
    for(var i = current_page * page_size - page_size ; i <Math.min( current_page * page_size, data_item_length)   ; i++){
        if(!detail_data[i].checked){
            return false;
        }
    }
    return true;

}
/*A function to refresh the page info*/
PagingHolder.prototype.update_info = function( refresh, paging_action ) {
    var paging_holder = this;
    /*第一步,根据配置，判断是否重新加载数据*/
    if( (!paging_holder.is_load_all_data || refresh) && typeof paging_holder.is_log_search =='undefined') {
        /***************首先判断能否进行刷新******************/
        if( !paging_holder.is_input_data_correct() ) {
            paging_holder.show_error_mesg( "请正确输入各字段" );
            return;
        }
        /***************能进行刷新****************************/
        if( paging_holder.is_editing_item() ) {
            if( confirm("您正在编辑数据，确认刷新?") ) {
                paging_holder.reset_selected_item();
                paging_holder.load_data( paging_action );
                paging_holder.reset_control_checkbox();

                var ass_add_panel = paging_holder.panel_config.ass_add_panel;
                if( ass_add_panel !== undefined && ass_add_panel !== null ) {
                    ass_add_panel.cancel_edit_box();
                }
            }
        } else {
            /*根据现在定位的页数，加载一页的数据*/
            paging_holder.load_data( paging_action );
            paging_holder.reset_control_checkbox();
        }
    }
    /*第二步,更新paging_holder的数据*/
    paging_holder.update_paging_holder();
    /*第三步,更新页面主体的数据*/
    paging_holder.load_data_into_main_body();
    /*第四步,更新翻页工具的数据*/
    paging_holder.update_paging_tools_info();
    /*第五步,给页面上的控制按钮注册监听*/
    paging_holder.add_listener_to_control_items();

    paging_holder.text_hidden();
}

PagingHolder.prototype.init_check_input_data = function() {
    var paging_holder = this;

    var check_obj = paging_holder.panel_config.check_obj;
    var search_check_obj = paging_holder.get_search_input_check_obj();
    var search_check_tool = paging_holder.search_check_tool;
    var check_tool = paging_holder.check_tool;

    if( check_obj !== null && check_obj !== undefined ) {
        check_tool._main( check_obj );
    }

    if( search_check_obj !== null && search_check_obj !== undefined ) {
        search_check_tool._main( search_check_obj );
    }
}

PagingHolder.prototype.is_input_data_correct = function() {
    var paging_holder = this;

    /*默认没有要检查的数据，给予通过*/
    var check_result = true;
    var check_obj = paging_holder.panel_config.check_obj;
    var search_check_obj = paging_holder.get_search_input_check_obj();
    var search_check_tool = paging_holder.search_check_tool;
    var check_tool = paging_holder.check_tool;

    if( check_obj !== null && check_obj !== undefined ) {
        if( check_tool._submit_check( check_obj, check_tool ) ){
            check_result = false;
        }
    }

    if ( search_check_obj !== null && search_check_obj !== undefined ) {
        if( search_check_tool._submit_check( search_check_obj, search_check_tool ) ){
            check_result = false;
        }
    }

    return check_result;
}

PagingHolder.prototype.load_data = function( paging_action ){
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var event_handler = panel_config.event_handler;

    /* 第零步，调用可能的外接函数 */
    if( event_handler !== null && event_handler.before_load_data !== undefined ) {
        event_handler.before_load_data( paging_holder );
    }

    var sending_data = {
        ACTION: "load_data",
        current_page: paging_holder.current_page,
        page_size: paging_holder.page_size,
        panel_name: paging_holder.panel_name
    };

    if ( paging_action !== undefined ) {
        sending_data.paging_action = paging_action;
    } else {
        sending_data.paging_action = "none";
    }

    var searching_data = paging_holder.get_search_keys();
    for( var element in searching_data ) {
        sending_data[element] = searching_data[element];
    }

    /*加入要传输的扩展数据*/
    var extend_sending_data = paging_holder.extend_sending_data;
    for( var element in extend_sending_data ) {
        sending_data[element] = extend_sending_data[element];
    }
    function ondatareceived(data) {
        paging_holder.detail_data   = data.detail_data;
        paging_holder.total_num     = Number( data.total_num );
        paging_holder.refresh_list_panel( data );

        if ( paging_holder.is_need_reload( data ) ) {
            paging_holder.show_apply_mesg();
        }
        /* 最后一步，调用可能的外接函数 */
        if( event_handler !== null && event_handler.after_load_data !== undefined ) {

            event_handler.after_load_data( paging_holder, data );
        }
    }

    paging_holder.request_for_json(sending_data, ondatareceived);
}

PagingHolder.prototype.get_search_keys = function() {
    var paging_holder = this;
    var searching_data = {};

    /*加入普通查询条件*/
    var search_key_selector = "#" + paging_holder.search_key_id;
    if( $( search_key_selector ).length > 0 ) {
        var search = $( search_key_selector ).val();
        searching_data.search = search;
    }

    /*加入扩展插叙条件*/
    var extend_search_selector = "." + paging_holder.extend_search_class;
    var extend_search = $( extend_search_selector );
    extend_search.each( function() {
        var extend_search_handle = this;
        searching_data[$(extend_search_handle).attr("name")] = $(extend_search_handle).val();
    });

    return searching_data;
}

PagingHolder.prototype.request_for_json = function( sending_data, ondatareceived ) {
    var paging_holder = this;
    var url = paging_holder.url;
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            paging_holder.show_error_mesg("返回数据格式有误,请检查");
        },
        success: ondatareceived
    });
}

PagingHolder.prototype.update_paging_holder = function() {
    var paging_holder   = this;
    var total_num       = paging_holder.total_num;
    var page_size       = paging_holder.page_size;

    var total_page = 1;

    if( total_num % page_size == 0 && total_num > 0 ) {
        total_page = Math.floor( ( total_num / page_size ) );
    } else {
        total_page = Math.floor( ( total_num / page_size ) ) + 1;
    }
    var current_page = paging_holder.current_page;
    if (current_page <= 0){
        current_page = 1;
    }else if (current_page > total_page) {
        current_page = total_page;
    }

    var from_num = (current_page - 1) > 0 ? (current_page - 1) * page_size : 0;
    if (from_num > total_num) {
        from_num = total_num;
    }

    var to_num = current_page * page_size;
    if (to_num > total_num) {
        to_num = total_num;
    }

    /*Update paging_holder*/
    paging_holder.total_page    = total_page;
    paging_holder.current_page  = current_page;
    paging_holder.from_num      = from_num;
    paging_holder.to_num        = to_num;
}

PagingHolder.prototype.refresh_list_panel = function( data ) {
    var paging_holder = this;

    /* 第一步，查看是否需要重新渲染主体 */
    if( data.panel_header !== undefined ) {
        paging_holder.panel_config.panel_header = data.panel_header;
        /* 第二步，查看是否需要渲染页数 */
        if( data.page_size !== undefined ) {
            var page_size = Number( data.page_size );
            if( paging_holder.page_size != page_size ) {
                /*如果请求数据回来pageSize发生了变化，要重新生成页面主体 */
                paging_holder.page_size = page_size;
            }
        }
        paging_holder.refresh_list_panel_header();
        paging_holder.refresh_list_panel_body();
        
    } else {
        /* 第二步，查看是否需要渲染页数 */
        if( data.page_size !== undefined ) {
            var page_size = Number( data.page_size );
            if( paging_holder.page_size != page_size ) {
                /*如果请求数据回来pageSize发生了变化，要重新生成页面主体 */
                paging_holder.page_size = page_size;
                paging_holder.refresh_list_panel_body();
            }
        }
    }
}

PagingHolder.prototype.refresh_list_panel_header = function() {
    var paging_holder = this;

    var panel_header_selector = "#" + paging_holder.panel_header_id;
    var panel_header = paging_holder.create_list_panel_header();
    $( panel_header_selector ).html( panel_header );

    paging_holder.init_control_checkbox();
}

PagingHolder.prototype.refresh_list_panel_body = function() {
    var paging_holder = this;

    var panel_body_selector = "#" + paging_holder.panel_body_id;
    var panel_body = paging_holder.create_list_panel_body();
    $( panel_body_selector ).html( panel_body );

}

PagingHolder.prototype.load_data_into_main_body = function() {
    var paging_holder = this;
    var render          = paging_holder.panel_config.render;
    var default_render  = paging_holder.panel_config.default_render;
    var render_to_text  = paging_holder.panel_config.render_to_text;

    var current_page    = paging_holder.current_page;
    var total_page      = paging_holder.total_page;
    var page_size       = paging_holder.page_size;

    var total_num       = paging_holder.total_num;
    var from_num        = paging_holder.from_num;
    var to_num          = paging_holder.to_num;
    var selected_item   = paging_holder.selected_item;

    var display_cols    = paging_holder.get_display_cols();
    var detail_data     = paging_holder.detail_data;

    var listb_tr_selector   = "#" + paging_holder.panel_body_id + " tr";
    var listb_tr            = $( listb_tr_selector );

    var tr_num = 0;
    var div_tmp = $('<div></div>')
    for ( tr_num = 0; tr_num < to_num - from_num; tr_num++ ) {
        var current_line = tr_num + from_num;

        if( !paging_holder.is_load_all_data ) {/*数据是按页加载，detail_data里面只存了一页的数据*/
            current_line = tr_num;
        }
        //PT：这儿可能报bug-- start
        if(!detail_data) 
            return;
        //---end
        var data_item = detail_data[current_line];
        var data_item_id = data_item.id;
        if(data_item_id == selected_item){
            listb_tr.eq(tr_num).addClass( "selected-line" );
        }else{
            listb_tr.eq(tr_num).removeClass( "selected-line" );
            
        }
        for(var j = 0; j < display_cols.length; j++) {
            var variable_name = display_cols[j];
            var rendered_text = data_item[variable_name];
            if (!render_to_text && data_item[variable_name]) {
                rendered_text = div_tmp.text(rendered_text).html()
            }
            /*渲染文本第一步，获取默认渲染值*/
            if ( variable_name in default_render ) {
                rendered_text = paging_holder.render_default( variable_name, data_item,tr_num );
            }

            /*渲染文本第二步，如果定义了渲染对象，并满足一定条件，进行文本渲染*/
            if( render !== undefined && variable_name in render ) {
                if ( render[variable_name].render !== undefined ) {
                    rendered_text = render[variable_name].render( rendered_text, data_item);
                }
            }

            listb_tr.eq(tr_num).find("td").eq( j ).html( rendered_text );
        }
    }

    /*清理掉剩余的数据容器中的数据*/
    if(to_num < from_num + page_size) {
        for (tr_num = to_num - from_num; tr_num < page_size; tr_num++) {
            for(var j = 0; j < display_cols.length; j++) {
                listb_tr.eq(tr_num).find("td").eq( j ).html("&nbsp");
            }
        }
    }
    $("#"+paging_holder.panel_body_id +' tr').each(function() {
        $(this).removeClass('background-checked background-hovered');
    });
}

PagingHolder.prototype.update_paging_tools_info = function(){
    var paging_holder = this;
    var current_page = paging_holder.current_page;
    var total_page = paging_holder.total_page;
    var total_num = paging_holder.total_num;
    var from_num = paging_holder.from_num + 1;/*跟真实数组下标不同*/
    var to_num = paging_holder.to_num;

    /*To handle the situation of no record*/
    if (to_num == 0){
        from_num = 0;
    }
    /*更新翻页数字信息*/
    var current_page_selector = "#" + paging_holder.current_page_id;
    var total_page_selector = "#" + paging_holder.total_page_id;
    var total_num_selector = "#" + paging_holder.total_num_id;
    var from_num_selector = "#" + paging_holder.from_num_id;
    var to_num_selector = "#" + paging_holder.to_num_id;

    $( current_page_selector ).val( current_page );
    $( total_page_selector ).html( total_page );
    $( total_num_selector ).html( total_num );
    $( from_num_selector ).html( from_num );
    $( to_num_selector ).html( to_num );
    /*更新翻页工具按钮状态*/
    if( total_page <= 1 ) {
        /*总共不到一页的数据*/
        paging_holder.disable_first_last_page_op();
        paging_holder.disable_next_end_page_op();
    } else {
        if( current_page == paging_holder.first_page ) {
            paging_holder.disable_first_last_page_op();
            paging_holder.enable_next_end_page_op();
        } else if( current_page == paging_holder.total_page ) {
            paging_holder.enable_first_last_page_op();
            paging_holder.disable_next_end_page_op();
        } else {
            paging_holder.enable_first_last_page_op();
            paging_holder.enable_next_end_page_op();
        }
    }
}

PagingHolder.prototype.render_default = function( type, data_item ,index) {
    var paging_holder = this;

    var rendered_text = "";

    if ( type == "checkbox" ) {
        var checkbox_class = paging_holder.checkbox_class;
        rendered_text += '<input type="checkbox" class="' + checkbox_class + '" index="'+index+'" value="' + data_item.id + '" ';
        if( data_item.checked ) {
            rendered_text += 'checked="checked" ';
        }
        rendered_text += '/>';
    } else if ( type == "radio" ) {
        var radio_name = paging_holder.radio_name;
        rendered_text += '<input type="radio" name="' + radio_name + '" index="'+index+'" value="' + data_item.id + '" ';
        if( data_item.checked ) {
            rendered_text += 'checked="checked" ';
        }
        rendered_text += '/>';
    } else if( type == "action" ) {
        rendered_text += paging_holder.render_default_action( data_item );
    } else if( type == "move" ) {
        rendered_text += paging_holder.render_default_move( data_item );
    }

    return rendered_text;
}

PagingHolder.prototype.render_default_move = function( data_item ) {
    var paging_holder = this;
    var maxid = paging_holder.total_num - 1;
    var rendered_text = "";
    /*设置调整顺序按钮*/
    if(data_item.id != 0){
        var up_class = paging_holder.up_class;
        rendered_text += '<input type="image" class="move-image ' + up_class + '" src="../images/stock_up-16.png" title="上移" alt="Up" value="' + data_item.id + '"/>';
    }else if(data_item.id == 0){
        rendered_text += '<input type="image" class="move-image hover-not-allowed" src="../images/stock_up-16-disabled.png" title="不能再上移了" alt="no-Up" disabled="disabled"/>';        
    }
    if(data_item.id != maxid){
        var down_class = paging_holder.down_class;
        rendered_text += '<input type="image" class="move-image ' + down_class + '" src="../images/stock_down-16.png" title="下移" alt="Down" value="' + data_item.id + '"/>';
    }else if(data_item.id == maxid){
        rendered_text += '<input type="image" class="move-image hover-not-allowed" src="../images/stock_down-16-disabled.png" title="不能再下移了" alt="no-Down" disabled="disabled"/>';        
    }
    /*设置置顶置底按钮*/
    if(data_item.id != 0){
        var top_class = paging_holder.top_class;
        rendered_text += '<input type="image" class="move-image ' + top_class + '" src="../images/to_top.png" title="置顶" alt="Top" value="' + data_item.id + '"/>';
    }else if(data_item.id == 0){
        rendered_text += '<input type="image" class="move-image hover-not-allowed" src="../images/to_top-disabled.png" title="已经在顶部了" alt="no-Top" disabled="disabled"/>';        
    }
    if(data_item.id != maxid){
        var bottom_class = paging_holder.bottom_class;
        rendered_text += '<input type="image" class="move-image ' + bottom_class + '" src="../images/to_bottom.png" title="置底" alt="Bottom" value="' + data_item.id + '"/>';
    }else if(data_item.id == maxid){
        rendered_text += '<input type="image" class="move-image hover-not-allowed" src="../images/to_bottom-disabled.png" title="已经在底部了" alt="no-Bottom" disabled="disabled"/>';        
    }
   
    return rendered_text;
}
PagingHolder.prototype.render_default_action = function( data_item ) {
    var paging_holder = this;
    var maxid = paging_holder.total_num - 1;
    var rendered_text = "";
    
    /*设置启用禁用按钮*/
    if ( data_item.enable !== undefined ) {
        if ( data_item.enable == "on" || data_item.enable == true ){
            var disable_class = paging_holder.disable_class;
            rendered_text += '<input type="image" class="action-image ' + disable_class + '" src="../images/on_blue.png" title="禁用" value="' + data_item.id + '"/>';
        } else {
            var enable_class = paging_holder.enable_class;
            rendered_text += '<input type="image" class="action-image ' + enable_class + '" src="../images/off_blue.png" title="启用" value="' + data_item.id + '"/>';
        }
    }
    /*设置编辑按钮*/
    if( data_item.uneditable === undefined) {
        var edit_class = paging_holder.edit_class;
        rendered_text += '<input type="image" class="action-image ' + edit_class + '" src="../images/edit.png" title="编辑" value="' + data_item.id + '"/>';
    }
    /*设置删除按钮*/
    if( data_item.undeletable === undefined) {
        var delete_class = paging_holder.delete_class;
        rendered_text += '<input type="image" class="action-image ' + delete_class + '" src="../images/delete_blue.png" title="删除" value="' + data_item.id + '"/>';
    }

    return rendered_text;
}

PagingHolder.prototype.toggle_check_current_page = function( element ) {
    var paging_holder = this;
    if (element.checked == true) {
        paging_holder.check_current_page();
    }else{
        paging_holder.uncheck_current_page();
    }
}

PagingHolder.prototype.check_current_page = function() {
    var paging_holder = this;

    paging_holder.set_check_current_page( true );
}

PagingHolder.prototype.uncheck_current_page = function() {
    var paging_holder = this;

    paging_holder.set_check_current_page( false );
}

PagingHolder.prototype.set_check_current_page = function( status ) {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;

    /* 检查外接监听函数 */
    var checkbox_listeners = null;
    if ( panel_config.render !== undefined ) {
        var render = panel_config.render;
        if ( render.checkbox !== undefined ) {
            var checkbox_config = render.checkbox;
            if ( checkbox_config.listeners !== undefined ) {
                checkbox_listeners = checkbox_config.listeners;
            }
        }
    }
    
    var checkbox_class = paging_holder.checkbox_class;
    var checkboxs = document.getElementsByClassName( checkbox_class );
    var from_num = paging_holder.from_num;
    var to_num = paging_holder.to_num;
    //PJ 2016-08-31:add a limit to selectAll checkboxs when the numbers of checkboxs less than detail_data;
    var start_num = paging_holder.to_num - checkboxs.length;
    for (var i = start_num; i < to_num; i++){
        var data_item = paging_holder.detail_data[i];
    //PJ 2016-09-06:modify the index of checkbox
        var checkbox_element = checkboxs[i -start_num];
        checkbox_element.checked = status; /*改变按钮的状态*/
        if (status) {
            $("#"+paging_holder.panel_body_id +' tr').eq(i).addClass('background-checked');
        }else{
            $("#"+paging_holder.panel_body_id +' tr').eq(i).removeClass('background-checked');
        }
        if( paging_holder.is_load_all_data ) {
            data_item.checked = checkbox_element.checked;
        } else {
            data_item = paging_holder.detail_data[i - from_num];
            data_item.checked = checkbox_element.checked;
        }

        if ( checkbox_listeners ) {
            if ( checkbox_listeners.click !== undefined ) {
                checkbox_listeners.click( checkbox_element, data_item, paging_holder );
            }
        }
    }
}

PagingHolder.prototype.reset_control_checkbox = function() {
    var paging_holder = this;

    var control_checkbox_id = paging_holder.control_checkbox_id;
    var control_checkbox_selector = "#" + paging_holder.control_checkbox_id;
    if( $( control_checkbox_selector ).length > 0 ) {
        document.getElementById( control_checkbox_id ).checked =false;
    }
}

PagingHolder.prototype.set_check = function( item_id, checked,index ) {
    var paging_holder = this;

    if (checked) {
        $("#"+paging_holder.panel_body_id +' tr').eq(index).addClass('background-checked');
    }else{
        $("#"+paging_holder.panel_body_id +' tr').eq(index).removeClass('background-checked');
    }
    var detail_data = paging_holder.detail_data;
    for ( var i = 0; i < detail_data.length; i++ ) {
        if( detail_data[i].id == item_id ) {
            paging_holder.detail_data[i].checked = checked;
            break;
        }
    }
}

PagingHolder.prototype.set_check_single = function( item_id, checked ) {
    var paging_holder = this;

    var detail_data = paging_holder.detail_data;
    for ( var i = 0; i < detail_data.length; i++ ) {
        if( detail_data[i].id == item_id ) {
            paging_holder.detail_data[i].checked = checked;
        } else {
            paging_holder.detail_data[i].checked = !checked;
        }
    }
}

PagingHolder.prototype.select_edit_item = function( item_id ) {
    var paging_holder = this;
    
    paging_holder.selected_item = item_id;
    paging_holder.update_info();
}

PagingHolder.prototype.deselect_edit_item = function() {
    var paging_holder = this;
    
    paging_holder.reset_selected_item();
    paging_holder.update_info();
}

PagingHolder.prototype.reset_selected_item = function() {
    var paging_holder = this;
    /*重置选中的行*/
    paging_holder.selected_item = -1;
}

PagingHolder.prototype.is_editing_item = function() {
    var paging_holder = this;

    var result = false;
    if ( paging_holder.selected_item >= 0 ) {
        result = true;
    }

    return result;
}

PagingHolder.prototype.get_checked_items = function() {
    var paging_holder = this;
    var detail_data = paging_holder.detail_data;
    var ret_items = new Array();

    for ( var i = 0; i < detail_data.length; i++ ) {
        var item = detail_data[i];
        if( item.checked ) {
            ret_items.push( item );
        }
    }

    return ret_items;
}

PagingHolder.prototype.get_item = function( item_id ) {
    var paging_holder = this;
    var detail_data = paging_holder.detail_data;
    for ( var i = 0; i < detail_data.length; i++ ) {
        var item = detail_data[i];
        if( item.id == item_id ) {
            return item;
        }
    }
}

PagingHolder.prototype.get_all_items = function() {
    var paging_holder = this;
    var detail_data = paging_holder.detail_data;
    return detail_data;
}

PagingHolder.prototype.init_paging_tools_variable = function() {
    var paging_holder = this;
    var panel_name = paging_holder.panel_name;
    var panel_config = paging_holder.panel_config;

    /*页面搜索相关按钮的ID*/
    paging_holder.search_form_name      = "list_panel_search_form_for_" + panel_name;
    paging_holder.search_key_id         = "search_key_for_" + panel_name;
    paging_holder.search_button_id      = "search_button_for_" + panel_name;
    paging_holder.extend_search_class   = "extend_search_for_" + panel_name;
    /*页面主体部分ID*/
    paging_holder.panel_id          = "list_panel_id_for_" + panel_name;
    paging_holder.panel_detail_id   =  "list_detail_panel_id_for" + panel_name;
    paging_holder.panel_close_id    = "list_panel_close_for_" + panel_name;
    paging_holder.panel_header_id   = "panel_header_id_for_" + panel_name;
    paging_holder.panel_body_id     = "rule_listb_for_" + panel_name;
    /*页面翻页按钮的ID*/
    paging_holder.first_page_icon_id    = "first_page_icon_for_" + panel_name;
    paging_holder.last_page_icon_id     = "last_page_icon_for_" + panel_name;
    paging_holder.next_page_icon_id     = "next_page_icon_for_" + panel_name;
    paging_holder.end_page_icon_id      = "end_page_icon_for_" + panel_name;
    paging_holder.refresh_icon_id       = "refresh_icon_for_" + panel_name;
    /*页面页数及条目信息控件的ID*/
    paging_holder.current_page_id   = "current_page_for_" + panel_name;
    paging_holder.total_page_id     = "total_page_for_" + panel_name;
    paging_holder.from_num_id       = "from_num_for_" + panel_name;
    paging_holder.to_num_id         = "to_num_for_" + panel_name;
    paging_holder.total_num_id      = "total_num_for_" + panel_name;
    /*控制页面选择的名目*/
    paging_holder.control_checkbox_id   = "control_checkbox_for_" + panel_name;
    paging_holder.checkbox_class        = "checkbox_item_for_" + panel_name;
    paging_holder.radio_name            = "radio_item_for_" + panel_name;
    /*控制页面编辑的名目*/
    paging_holder.up_class      = "up_item_for_" + panel_name;
    paging_holder.down_class    = "down_item_for_" + panel_name;
    paging_holder.top_class     = "top_item_for_" + panel_name;
    paging_holder.bottom_class  = "bottom_item_for_" + panel_name;
    paging_holder.enable_class  = "enable_item_for_" + panel_name;
    paging_holder.disable_class = "disable_item_for_" + panel_name;
    paging_holder.edit_class    = "edit_item_for_" + panel_name;
    paging_holder.delete_class  = "delete_item_for_" + panel_name;
    /*页面页数及条目信息*/
    paging_holder.page_size      = panel_config.page_size !== undefined ? panel_config.page_size : 15;/*默认大小*/
    paging_holder.tr_class       = panel_config.tr_class  !== undefined ? panel_config.tr_class : ""; /*默认空对象*/
    paging_holder.first_page     = 1;
    paging_holder.current_page   = 1;
    paging_holder.total_page     = 0;
    paging_holder.from_num       = 0;
    paging_holder.to_num         = 0;
    paging_holder.total_num      = 0;
    paging_holder.detail_data    = [];
    paging_holder.selected_item  = -1; /**记录当前被编辑的行，-1表示没有编辑的行**/
    paging_holder.display_cols   = paging_holder.get_display_cols();
    paging_holder.is_load_all_data  = panel_config.is_load_all_data !== undefined ? panel_config.is_load_all_data : true; /*默认加载所有数据，不分页加载*/

    /*目前没有考虑到的将要传输给服务器的扩展数据*/
    paging_holder.extend_sending_data = {};
}

PagingHolder.prototype.display_list_panel = function() {
    var paging_holder   = this;
    var panel_config = paging_holder.panel_config;
    var colspan_width   = paging_holder.get_list_panel_tools_width();
    var panel_name      = paging_holder.panel_name;

    var panel_body = "";
    panel_body +=   '<div id="' + paging_holder.panel_id + '" class="list">';
    panel_body +=       paging_holder.create_list_panel_title();
    panel_body +=       '<div class="toolbar">';
    panel_body +=           paging_holder.create_top_widgets();
    panel_body +=           paging_holder.create_search_widget();
    panel_body +=           '<div class="clear"></div>' +
                        '</div>';
    var container_class = 'container-main-body';
    if ( panel_config.modal_config !== undefined ) {
            var modal_config = panel_config.modal_config;
            if ( modal_config.modal_box_size !== undefined ) {
                container_class += ' ' + "container-main-body-" + modal_config.modal_box_size;
            }
    }
    panel_body +=       '<div class="' + container_class + '">' +
                            '<table class="rule-list">' +
                                '<thead>';
    panel_body +=                   '<tr id="' + paging_holder.panel_header_id + '" class="rule-listbh">';
    panel_body +=                       paging_holder.create_list_panel_header();
    panel_body +=                   '</tr>';
    panel_body +=               '</thead>' +
                                '<tbody id="' + paging_holder.panel_body_id + '" class="rule-listb">';
    panel_body +=                   paging_holder.create_list_panel_body();
    panel_body +=               '</tbody>' +
                            '</table>' +
                        '</div>';
    panel_body +=       '<div class="toolbar toolbar-paging-tools">';
    panel_body +=           paging_holder.create_bottom_widgets();
    panel_body +=           paging_holder.create_paging_tools();
    panel_body +=           '<div class="clear"></div>' +
                        '</div>';
    panel_body +=       paging_holder.create_bottom_extend_widgets();
                    '</div>';
    panel_body += '<div id="' + paging_holder.panel_detail_id +'" class="pageDetail"></div>';                
    if ( panel_config.is_modal ) {
        panel_body = paging_holder.get_modaled_panel( panel_body );
    }
    var check_in_selector = "#" + panel_config.check_in_id;
    $( check_in_selector ).empty();
    $( check_in_selector ).html( panel_body );

}
// add show_detail_page
PagingHolder.prototype.setDetail =function(config){
    
        var paging_holder = this;
        this.config = config;
            // var panel_body = '<div class="popup-mesg-box-cover" style="z-index: 99; "></div>';
            var panel_body =       '<div class="popup-mesg-box-body mesg-box-s" style="z-index: 100;">';
             panel_body +=          '<table id="showDetail">';
             config = config.config;
                for(var i=0;i<config.length;i++){
                    panel_body +=  '<tr style=""><td >'+config[i].label+':</td><td id="info-'+config[i].text+'"></td></tr>';
                }
             panel_body  +=        '</table></div>';
             paging_holder.panel_body=panel_body;
             this.showDetail();
    
   

}
PagingHolder.prototype.addDetail=function(id){
        var paging_holder = this;
        var obj = paging_holder.get_item(id);
        for(var key in obj){
            $("#info-"+key).text("");
            $("#info-"+key).text(obj[key]);
        }
    }

PagingHolder.prototype.showDetail=function(val){
        var paging_holder = this;
        $(".pageDetail").append(paging_holder.panel_body);
}
   
PagingHolder.prototype.get_modaled_panel = function( panel_body ) {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var panel_name = panel_config.panel_name;

    if( panel_config.is_modal ) {
        if (panel_config.border_transparent) {
            if (panel_config.modal_config !== undefined) {
                var modal_config = panel_config.modal_config;
                var modal_cover = '<div id="popup-mesg-border-box-cover-' + panel_name + '"';
                var modal_body = '<div id="TransparentBorder_' + panel_name + '"class="TransparentBorder-' + modal_config.modal_box_size + '"><div id="modal_border_box_' + panel_name + '"';
                var modal_cover_class = 'popup-mesg-box-cover';
                var modal_body_class = 'popup-mesg-border-box-body';
                var modal_cover_style = '';
                var modal_body_style = '';

                if (modal_config.modal_box_size !== undefined) {
                    modal_body_class += ' ' + "mesg-border-box-" + modal_config.modal_box_size;
                }
                if (modal_config.modal_level !== undefined) {
                    var level = modal_config.modal_level * 10;
                    modal_cover_style = 'z-index: ' + (level - 1) + '; ';
                    modal_body_style = 'z-index: ' + level + '; ';
                }
                if (modal_config.modal_box_position !== undefined) {
                    modal_body_style += 'position: ' + modal_config.modal_box_position + '; ';
                }
            }

            modal_cover += 'class="' + modal_cover_class + '" ';
            modal_cover += 'style="' + modal_cover_style + '" ';
            modal_cover += '></div>';
            modal_body += 'class="' + modal_body_class + '" ';
            modal_body += 'style="' + modal_body_style + '" ';;
            modal_body += '>' + panel_body + '</div></div>';
            panel_body = modal_cover + modal_body;

        }
        else {
            var modal_cover = '<div ';
            var modal_body = '<div ';
            var modal_cover_class = 'popup-mesg-box-cover';
            var modal_body_class = 'popup-mesg-box-body';
            var modal_cover_style = '';
            var modal_body_style = '';

            if ( panel_config.modal_config !== undefined ) {
                var modal_config = panel_config.modal_config;
                if ( modal_config.modal_box_size !== undefined ) {
                    modal_body_class += ' ' + "mesg-box-" + modal_config.modal_box_size;
                }
                if ( modal_config.modal_level !== undefined ) {
                    var level = modal_config.modal_level * 10;
                    modal_cover_style = 'z-index: ' + (level -1) + '; ';
                    modal_body_style = 'z-index: ' + level + '; ';
                }
                if ( modal_config.modal_box_position !== undefined ) {
                    modal_body_style += 'position: ' + modal_config.modal_box_position + '; ';
                }
            }
            modal_cover += 'class="' + modal_cover_class + '" ';
            modal_cover += 'style="' + modal_cover_style + '" ';
            modal_cover += '></div>';
            modal_body += 'class="' + modal_body_class + '" ';
            modal_body += 'style="' + modal_body_style + '" ';;
            modal_body += '>' + panel_body + '</div>';
            panel_body = modal_cover + modal_body;

        }
    }

    return panel_body;
}

PagingHolder.prototype.get_list_panel_tools_width = function() {
    var paging_holder = this;
    var panel_header = paging_holder.panel_config.panel_header;

    var colspan_width = 0;
    for ( var i = 0; i < panel_header.length; i++ ) {
        var item = panel_header[i];
        if( item.enable !== undefined && item.enable ) {
            colspan_width++;
        }
    }
    return colspan_width;
}

PagingHolder.prototype.create_top_widgets = function() {
    var paging_holder = this;
    var top_widgets = paging_holder.panel_config.top_widgets;
    var widgets = "";
    if( top_widgets === undefined ) {
        return widgets;
    }
    widgets += '<span class="opt-tools">';
    widgets += paging_holder.create_widgets( top_widgets );
    widgets += '</span>';
    return widgets;
}

PagingHolder.prototype.create_bottom_widgets = function() {
    var paging_holder = this;
    var bottom_widgets = paging_holder.panel_config.bottom_widgets;
    var widgets = "";
    if( bottom_widgets === undefined ) {
        return widgets;
    }
    widgets += '<span class="opt-tools">';
    widgets += paging_holder.create_widgets( bottom_widgets );
    widgets += '</span>';
    return widgets;
}

PagingHolder.prototype.create_widgets = function( items ) {
    var paging_holder = this;
    var widgets = "";

    if ( items === undefined ) {
        return widgets;
    }
    for ( var i = 0; i < items.length; i++ ) {
        var item = items[i];

        if ( item.enable === undefined || !item.enable ) {
            continue;
        }

        if ( item.type == "image_button" || item.type == "link_button" ) {
            // do nothing
        } else {
            widgets += '<span class="widgets-item">';
        }

        if ( item.type !== undefined && ( item.type == "text" || item.type == "password" || item.type == "button" || item.type == "file" ) ) {
            /* 单行文本输入框 */
            widgets += paging_holder.create_input_widget( item );
        } else if ( item.type !== undefined && item.type == "textarea" ) {
            /* 多行行文本输入框 */
            widgets += paging_holder.create_textarea_widget( item );
        } else if ( item.type !== undefined && item.type == "select" ) {
            /* 单多选select */
            widgets += paging_holder.create_select_widget( item );
        } else if ( item.type !== undefined && ( item.type == "checkbox" || item.type == "radio" ) ) {
            /* 单多选按钮组 */
            widgets += paging_holder.create_choice_widget( item );
        } else if ( item.type !== undefined && item.type == "label" ) {
            /* 只有文字提示 */
            widgets += paging_holder.create_label_widget( item );
        } else if ( item.type !== undefined && item.type == "image_button" ) {
            /* 带图标的按钮 */
            widgets += paging_holder.create_image_button( item );
        } else if ( item.type !== undefined && item.type == "link_button" ) {
            /* 带图标的按钮链接 */
            widgets += paging_holder.create_link_button( item );
        } else {
            item.type = "button";
            widgets += paging_holder.create_input_widget( item );
        }

        if ( item.type == "image_button" || item.type == "link_button" ) {
            // do nothing
        } else {
            widgets += '</span>';
        }

    }
    return widgets;
}

PagingHolder.create_standard_attr = function( item ) {
    var attrs = "";

    if( item.id !== undefined && item.id ) {
        attrs += 'id="' + item.id + '" ';
    }
    if( item.name !== undefined && item.name ) {
        attrs += 'name="' + item.name + '" ';
    }
    if( item['class'] !== undefined && item['class'] ) {
        attrs += 'class="' + item['class'] + '" ';
    }
    if( item.value !== undefined ) {
        attrs += 'value="' + item.value + '" ';
    }
    if( item.href !== undefined ) {
        attrs += 'href="' + item.href + '" ';
    }
    if( item.src !== undefined ) {
        attrs += 'src="' + item.src + '" ';
    }
    if( item.multiple !== undefined && item.multiple ) {
        attrs += 'multiple="multiple" ';
    }
    if( item.disabled !== undefined && item.disabled ) {
        attrs += 'disabled="disabled" ';
    }
    if( item.checked !== undefined && item.checked ) {
        attrs += 'checked="checked" ';
    }
    if( item.selected !== undefined && item.selected ) {
        attrs += 'selected="selected" ';
    }
    if( item.readonly !== undefined && item.readonly ) {
        attrs += 'readonly="readonly" ';
    }
    if( item.style !== undefined && item.style ) {
        attrs += 'style="' + item.style + '" ';
    }
    if( item.functions !== undefined && item.functions ) {
        var functions = item.functions;
        for ( var key in functions ) {
            attrs += key + '="' + functions[key] + '" ';
        }
    }

    return attrs;
}

PagingHolder.prototype.create_widget_prefix_label = function( item ) {
    var paging_holder = this;
    var prefix_label = "";

    if( item.title !== undefined && item.title ) {
        prefix_label += '<label ';
        if( item.id !== undefined && item.id ) {
            prefix_label += 'for="' + item.id + '" ';
        }
        prefix_label += 'class="prefix-label-for-widget" ';
        prefix_label += '>';
        prefix_label += item.title;
        prefix_label += '</label>';
    }

    return prefix_label;
}

PagingHolder.prototype.create_widget_postfix_label = function( item ) {
    var paging_holder = this;
    var widget_label = "";

    if( item.label !== undefined && item.label ) {
        widget_label += '<label ';
        if( item.id !== undefined && item.id ) {
            widget_label += 'for="' + item.id + '" ';
        }
        widget_label += 'class="postfix-label-for-widget" ';
        widget_label += '>';
        widget_label += item.label;
        widget_label += '</label>';
    }

    return widget_label;
}

PagingHolder.prototype.create_widget_prefix_tip = function( item ) {
    var paging_holder = this;
    var prefix_tip = "";

    if( item.title !== undefined && item.title ) {
        prefix_tip += '<span ';
        if( item.id !== undefined && item.id ) {
            prefix_tip += 'for="' + item.id + '" ';
        }
        prefix_tip += 'class="prefix-tip-for-widget" ';
        prefix_tip += '>';
        prefix_tip += item.title;
        prefix_tip += '</span>';
    }

    return prefix_tip;
}

PagingHolder.prototype.create_widget_postfix_tip = function( item ) {
    var paging_holder = this;
    var widget_tip = "";

    if( item.tip !== undefined && item.tip ) {
        widget_tip += '<label ';
        if( item.id !== undefined && item.id ) {
            widget_tip += 'for="' + item.id + '" ';
        }
        widget_tip += 'class="postfix-tip-for-widget" ';
        widget_tip += '>';
        widget_tip += item.tip;
        widget_tip += '</label>';
    }

    return widget_tip;
}

PagingHolder.create_action_buttons = function( action_buttons ) {
    var buttons = "";
    var funArr = new Array();

    if( action_buttons === undefined ) {
        return buttons;/*如果没有定义相应的对象，直接返回*/
    }

    for( var i = 0; i< action_buttons.length; i++ ) {
        var item = action_buttons[i];
        if( item.enable === undefined || !item.enable ){
            continue;
        }
        buttons += '<input type="image" ';
        /* 添加默认样式 */
        if( item.cls !== undefined && item.cls ) {
            item.cls = "action-image " + item.cls;
        } else {
            item.cls = "action-image";
        }
        /* 添加标准属性 */
        buttons += PagingHolder.create_standard_attr( item );
        if( item.button_text !==undefined && item.button_text ) {
            buttons += 'title="' + item.button_text + '" ';
        }
        if( item.button_icon !== undefined && item.button_icon ) {
            buttons += 'src="../images/' + item.button_icon +'" ';
        }
        if( item.onFunc !== undefined && typeof item.onFunc === "function" ) {
            funArr[i] = item.onFunc;
        }
        buttons += '/>';
    }
    if(funArr.length != 0) {
        buttons$ = $(buttons);
        buttons$.each(function (a, b){
            if(funArr[a]) {
                $(b).on("click", funArr[a]);
            }
        });
        return buttons$;
    }
    return buttons;
}

PagingHolder.prototype.create_image_button = function( item ) {
    var paging_holder = this;
    var image_button = "";

    if( item === undefined ) {
        return image_button;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return image_button;
    }
    image_button += '<button ';
    /* 添加默认样式 */
    if( item.class !== undefined && item.class ) {
        item.class = "imaged-button " + item.class;
    } else {
        item.class = "imaged-button";
    }
    /* 添加标准属性 */
    image_button += PagingHolder.create_standard_attr( item );
    image_button += '>';
    if( item.button_icon !== undefined && item.button_icon ) {
        image_button += '<img class="button-image" src="../images/' + item.button_icon +'"/>';
    }
    if( item.button_text === undefined || !item.button_text ) {
        item.button_text = "请设置提示";
    }
    image_button += '<span class="button-text" >' + item.button_text + '</span>';
    image_button += '</button>';

    return image_button;
}

PagingHolder.prototype.create_link_button = function( item ) {
    var paging_holder = this;
    var link_button = "";

    if( item === undefined ) {
        return link_button;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return link_button;
    }
    link_button += '<a ';
    /* 添加标准属性 */
    link_button += PagingHolder.create_standard_attr( item );
    link_button += '>';
    var image_button = {
        enable: true,
        type: "image_button"
    };

    if( item.button_icon !== undefined && item.button_icon ) {
        image_button.button_icon = item.button_icon;
    }
    if( item.button_text === undefined || !item.button_text ) {
        image_button.button_text = "请设置提示";
    } else {
        image_button.button_text = item.button_text;
    }
    /* 添加默认样式 */
    image_button.class = "imaged-button";
    link_button += paging_holder.create_image_button( image_button );
    link_button += '</a>';

    return link_button;
}

PagingHolder.prototype.create_input_widget = function( item ) {
    var paging_holder = this;
    var input_widget = "";

    if( item === undefined ) {
        return input_widget;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return input_widget;
    }
    input_widget += paging_holder.create_widget_prefix_label( item );
    input_widget += '<input ';
    if( item.type !== undefined && item.type ) {
        input_widget += 'type="' + item.type + '" ';
    }
    /* 添加标准属性 */
    input_widget += PagingHolder.create_standard_attr( item );
    input_widget += '/>';
    input_widget += paging_holder.create_widget_postfix_tip( item );

    return input_widget;
}

PagingHolder.prototype.create_textarea_widget = function( item ) {
    var paging_holder = this;
    var textarea_widget = "";

    if( item === undefined ) {
        return textarea_widget;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return textarea_widget;
    }

    /* 添加默认样式类名 */
    
    /* 添加前导label */
    textarea_widget += paging_holder.create_widget_prefix_label( item );
    /* 创建元素-BEGIN */
    textarea_widget += '<textarea ';
    /* 添加标准属性 */
    textarea_widget += PagingHolder.create_standard_attr( item );
    /* 创建元素-END */
    textarea_widget += '>';
    if( item.value !== undefined ) {
        textarea_widget += item.value;
    }
    textarea_widget += '</textarea>';
    /* 添加后缀提示 */
    textarea_widget += paging_holder.create_widget_postfix_tip( item );

    return textarea_widget;
}

PagingHolder.prototype.create_select_widget = function( item ) {
    var paging_holder = this;
    var select_widget = "";

    if( item === undefined ) {
        return select_widget;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return select_widget;
    }
    /* 添加label */
    select_widget += paging_holder.create_widget_prefix_label( item );

    select_widget += '<select ';
    /* 添加标准属性 */
    select_widget += PagingHolder.create_standard_attr( item );
    select_widget += '>';
    if( item.options !== undefined && item.options ) {
        for( var j = 0; j < item.options.length; j++ ) {
            var option = item.options[j];
            select_widget += '<option ';
            /* 添加标准属性 */
            select_widget += PagingHolder.create_standard_attr( option );
            select_widget += '>';
            /* 选项提示 */
            if( option.text !== undefined && option.text ) {
                select_widget += option.text;
            }
            select_widget += '</option>';
        }
    }

    select_widget += '</select>';

    return select_widget;
}

PagingHolder.prototype.create_choice_widget = function ( item ) {
    var paging_holder = this;
    var choice_widget = "";

    if( item === undefined ) {
        return choice_widget; /*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return select_widget;
    }

    /* 添加默认样式类名 */
    // item.class_default_value = panel_control.form_choice_class;
    /* 添加前导提示 */
    choice_widget += paging_holder.create_widget_prefix_tip( item );
    // choice_widget += paging_holder.create_widget_postfix_tip( item );
    /* 创建元素-BEGIN */
    choice_widget += '<input type="' + item.type + '"';
    /* 添加标准属性 */
    choice_widget += PagingHolder.create_standard_attr( item );
    /* 创建元素-END */
    choice_widget += '/>';
    /* 添加后缀label */
    choice_widget += paging_holder.create_widget_postfix_label( item );
    // choice_widget += paging_holder.create_widget_prefix_label( item );

    return choice_widget;
}

PagingHolder.prototype.create_label_widget = function( item ) {
    var paging_holder = this;
    var panel_control = paging_holder.panel_control;
    var label_widget = "";

    if( item === undefined ) {
        return label_widget;/*如果没有定义相应的对象，直接返回*/
    }

    if( item.enable === undefined || !item.enable ){
        return label_widget;
    }

    /* 添加默认样式类名 */
    item.class_default_value = panel_control.form_label_class;
    /* 添加前导label */
    label_widget += paging_holder.create_widget_prefix_label( item );
    /* 创建元素-BEGIN */
    label_widget += '<span ';
    /* 添加标准属性 */
    label_widget += PagingHolder.create_standard_attr( item );
    /* 创建元素-END */
    label_widget += '>';
    if ( item.value !== undefined && item.value ) {
        label_widget += item.value;
    }
    label_widget += '</span>';
    /* 添加后缀提示 */
    label_widget += paging_holder.create_widget_postfix_tip( item );

    return label_widget;
}

PagingHolder.prototype.create_extend_search_widget = function() {
    var paging_holder = this;
    var extend_search = paging_holder.panel_config.extend_search;
    var panel_name = paging_holder.panel_name;

    var widget = "";
    if( extend_search === undefined ) {
        return widget;
    }
    for( var i= 0; i < extend_search.length; i++ ) {
        var item = extend_search[i];
        if(  item.enable === undefined || !item.enable  ) {
            continue;
        }
        widget += '<span class="extend-search-item">';
        var my_widget = new Array();
        if( item.type !== undefined && ( item.type == "text" || item.type == "select" ) ) {
            if( item.class !== undefined && item.class ) {
                item.class = "search-key-input extend-search-input " + paging_holder.extend_search_class + " " + item.class;
            } else {
                item.class = "search-key-input extend-search-input " + paging_holder.extend_search_class;
            }
        } else if ( item.type !== undefined && ( item.type == "button" ||  item.type == "image_button" ) ) {
            if( item.class !== undefined && item.class ) {
                item.class = paging_holder.extend_search_class + " " + item.class;
            } else {
                item.class = paging_holder.extend_search_class;
            }
        } else {
            /* -- 默认是text类型 -- */
            item.type = "text";
        }

        my_widget.push( item );
        widget += paging_holder.create_widgets( my_widget );
        widget += '</span>';
    }

    return widget;
}

PagingHolder.prototype.set_extend_search_item_title_by_id = function( element_id, title ) {
    var paging_holder = this;

    var title_selector = "label[for='" + element_id +"']";
    $( title_selector ).text( title );
}

PagingHolder.prototype.create_default_search_widget = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var default_search = "";
    var attrs = "";
    if( panel_config.is_default_search === true ) {
        default_search +=   '<span class="search-item">';
        var config = undefined;
        if( panel_config.default_search_config !== undefined ) {
            config = panel_config.default_search_config;
        }
        if(config !== undefined && config.title !== undefined ) {
            default_search += paging_holder.create_widget_prefix_label( config );
        }
        // 为搜索框添加标准事件
        if(config !== undefined && config.functions !== undefined ) {
           attrs += PagingHolder.create_standard_attr( config );
        }
        default_search +=       '<input id="' + paging_holder.search_key_id + '" class="search-key-input"' +attrs;

        if( config !== undefined && config.input_tip !== undefined ) {
            default_search +=   'placeholder="' + config.input_tip + '" ';
        } else {
            default_search +=   'placeholder="输入关键字以查询..." ';
        }

        default_search +=       '/>';
        default_search +=       '<button id="' + paging_holder.search_button_id + '" class="imaged-button search-button">' +
                                    '<img class="button-image" src="../images/search16x16.png" />' +
                                    '<span class="button-text">查询</span>' +
                                '</button>' +
                            '</span>';
    }

    return default_search;
}

PagingHolder.prototype.create_search_widget = function() {
    var paging_holder = this;
    var panel_config    = paging_holder.panel_config;

    var search_widget = "";
    var extend_search   = paging_holder.create_extend_search_widget();
    var default_search  = paging_holder.create_default_search_widget();

    if( extend_search == "" && default_search == "" ) {
        return search_widget;
    }

    search_widget = extend_search + default_search;
    search_widget = '<span class="search">' +
                        '<form name="' + paging_holder.search_form_name + '" onsubmit="return false;">' + 
                            search_widget + 
                        '</form>' + 
                    '</span>';

    return search_widget;
}

PagingHolder.prototype.create_paging_tools = function() {
    var paging_holder = this;
    var is_paging_tools = paging_holder.panel_config.is_paging_tools;
    var tools = "";

    if( is_paging_tools === true ) {
        tools +=    '<span class="paging-tools">' +
                        '<img id="' + paging_holder.first_page_icon_id + '" src="../images/first-page.gif" title="第一页" />' +
                        '<img id="' + paging_holder.last_page_icon_id + '" src="../images/last-page.gif" title="上一页" />' +
                        '<span class="paging-text">' +
                            '第<input id="' + paging_holder.current_page_id + '" class="paging-tool-text" type="text"/>页,' +
                            '共<span id="' + paging_holder.total_page_id + '" class="paging-tool-text">0</span>页' +
                        '</span>' +
                        '<img id="' + paging_holder.next_page_icon_id + '" src="../images/next-page.gif" title="下一页" />' +
                        '<img id="' + paging_holder.end_page_icon_id + '" src="../images/end-page.gif" title="最后一页" />' +
                        '<img id="' + paging_holder.refresh_icon_id + '" src="../images/refresh.png" />' +
                        '<span class="paging-text">' +
                            '显示' +
                            '<span id="' + paging_holder.from_num_id + '" class="paging-tool-text">0</span>' +
                            '-' +
                            '<span id="' + paging_holder.to_num_id + '" class="paging-tool-text">0</span>' +
                            '条,共' +
                            '<span id="' + paging_holder.total_num_id + '" class="paging-tool-text">0</span>条' +
                        '</span>' +
                    '</span>';
    }
    return tools;
}

PagingHolder.prototype.create_bottom_extend_widgets = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var widgets = "";

    if ( panel_config.bottom_extend_widgets === undefined ) {
        return widgets;
    }

    var bottom_extend_widgets = panel_config.bottom_extend_widgets;

    widgets += '<div ';

    if ( bottom_extend_widgets.class !== undefined ) {
        bottom_extend_widgets.class = "toolbar " + bottom_extend_widgets.class;
    } else {
        bottom_extend_widgets.class = "toolbar";
    }

    widgets += PagingHolder.create_standard_attr( bottom_extend_widgets );

    widgets += '>';

    widgets += paging_holder.create_widgets( bottom_extend_widgets.sub_items );

    widgets += '</div>';

    return widgets;
}

PagingHolder.prototype.create_list_panel_title = function() {
    var paging_holder = this;
    var panel_title = paging_holder.panel_config.panel_title;
    var title_widget = "";
    var img_path = (paging_holder.title_icon !== "") ? "/images/" + paging_holder.title_icon : "";
    if( panel_title === undefined ) {
        if( paging_holder.panel_config.is_panel_closable ) {
            title_widget += '<div class="list-panel-title">';
            title_widget += '<span id="' + paging_holder.panel_close_id + '" class="close-button"></span>';
            title_widget += '</div>';
        }
        return title_widget;
    }

    title_widget += '<div class="list-panel-title">';
    
   if(img_path){
       title_widget += '<img id="list_panel_icon' + paging_holder.panel_name + '" src='+img_path+'>';
   }
    
    title_widget += '<span class="list-panel-title-text">' + panel_title + '</span>';
    if( paging_holder.panel_config.is_panel_closable ) {
        title_widget += '<button id="' + paging_holder.panel_close_id + '" class="close-button"></button>';
    }
    title_widget += '</div>';

    return title_widget;
}

PagingHolder.prototype.create_list_panel_header = function() {
    var paging_holder = this;
    var panel_header = paging_holder.panel_config.panel_header;
    var panel_name = paging_holder.panel_name;

    var panel_headers = '';
    for( var i = 0; i < panel_header.length; i++ ) {
        var item = panel_header[i];
        if ( item.enable === undefined || !item.enable ) {
            continue;
        }
        //======td开始标签==========//
        panel_headers += '<td ';
        if ( item.td_class !== undefined && item.td_class ) {
            if ( item.type == "checkbox" || item.type == "radio" ) {
                panel_headers += 'class="rule-listbc ' + item.td_class + '" ';
            } else {
                panel_headers += 'class="' + item.td_class + '" ';
            }
        }

        if ( item.width !== undefined && item.width ) {
            panel_headers += 'width="' + item.width + '" ';
        }
        panel_headers += '>';

        //======根据不同类型，展示不同内容=====================//
        if ( item.type == 'checkbox' ) {
            //===如果是checkbox=====//
            panel_headers += '<input type="checkbox" ';
            panel_headers += 'id="' + paging_holder.control_checkbox_id + '" ';
            if( item.name !== undefined && item.name ) {
                panel_headers += 'name="' + item.name + '" ';
            }
            if ( item.class !== undefined && item.class ) {
                panel_headers += 'class="' + item.class + '" ';
            }
            if ( item.functions ) {
                var functions = item.functions;
                for ( var key in functions ) {
                    panel_headers += key + '="' + functions[key] + '" ';
                }
            }
            panel_headers += '/>';
        } else if ( item.type == 'radio' ) {
            //===如果是单选按钮===//
            panel_headers += '请选择';
        } else {
            //===默认是普通表头=====//
            panel_headers += '<span ';
            if ( item.id !== undefined && item.id ) {
                panel_headers += 'id="' + item.id + '" ';
            }

            if ( item.name !== undefined && item.name ) {
                panel_headers += 'name="' + item.name + '" ';
            }

            if ( item.class !== undefined && item.class ) {
                panel_headers += 'class="' + item.class + '" ';
            }
            panel_headers += '>';
            if( item.title !== undefined && item.title ) {
                panel_headers += item.title;
            } else if ( item.type == "action" ) {
                panel_headers += "活动/动作";
            } else if ( item.type == "move" ) {
                panel_headers += "移动";
            }
            panel_headers += '</span>';
        }

        panel_headers += '</td>';
    }

    return panel_headers;
}

PagingHolder.prototype.create_list_panel_body = function() {
    var paging_holder = this;
    var panel_header = paging_holder.panel_config.panel_header

    var page_size = paging_holder.page_size;
    var panel_body = "";
    /*扩展tr_class,对每行的样式进行设置自定义的*/
    var tr_class = (paging_holder.tr_class === "" )? {}: paging_holder.tr_class;
    for( var i = 0; i < page_size; i++ ) {
        panel_body += '<tr class="';
        if( i % 2 == 0 ) {
            panel_body += (tr_class.even_class === undefined) ? 'even-num-line' :  tr_class.even_class ;
        } else {
            panel_body += (tr_class.odd_class === undefined) ?  'odd-num-line' : tr_class.odd_class;
        }
        panel_body += '">';
        for( var j = 0; j < panel_header.length; j++ ) {
            var item = panel_header[j];
            if( item.enable === undefined || !item.enable ) {
                continue;
            }
            panel_body += '<td ';
            if( item.td_class !== undefined && item.td_class ) {
                if( item.type == "checkbox" || item.type == "radio" ) {
                    panel_body += 'class="rule-listbc ' + item.td_class + '" ';
                } else {
                    panel_body += 'class="text-hidden ' + item.td_class + '" ';
                }
            } else {
                if( item.type == "checkbox" || item.type == "radio" ) {
                    panel_body += 'class="rule-listbc" ';
                }
                else {
                    panel_body += 'class="text-hidden" ';
                }
            }
            panel_body += '>';
            panel_body += "&nbsp;";
            panel_body += '</td>';
        }
        panel_body += '</tr>';
    }
    return panel_body;
}

PagingHolder.prototype.get_display_cols = function() {
    var paging_holder = this;
    var panel_header = paging_holder.panel_config.panel_header;
    var display_cols = new Array();


    for ( var i = 0; i < panel_header.length; i++ ) {
        var item = panel_header[i];
        if( item.enable !== undefined && item.enable ) {
            display_cols.push( item.name );
        }
    }

    return display_cols;
}

PagingHolder.prototype.is_operation_succeed = function( data ) {
    if( data.status == 0 ) {
        return true;
    } else {
        return false
    }
}

PagingHolder.prototype.is_need_reload = function( data ) {
    if( data.reload == 1 ) {
        return true;
    } else {
        return false;
    }
}

PagingHolder.prototype.apply_data = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var panel_name = paging_holder.panel_name;

    var sending_data = {
        ACTION: 'apply_data',
        panel_name: panel_name
    }

    function ondatareceived( data ) {
        if( paging_holder.is_operation_succeed( data ) ) {
            if ( data.mesg !== undefined && data.mesg != "" ) {
                paging_holder.show_note_mesg( data.mesg );
            }
            paging_holder.hide_apply_mesg();
        } else {
            if ( data.mesg !== undefined && data.mesg != "" ) {
                paging_holder.show_error_mesg( data.mesg );
            }
        }
    }

    paging_holder.request_for_json( sending_data, ondatareceived );
}

PagingHolder.prototype.show_apply_mesg = function( mesg ) {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var message_manager = panel_config.ass_message_manager;
    var panel_name = paging_holder.panel_name;

    if ( mesg === undefined ) {
        mesg = "规则已改变，需要重新应用以使规则生效";
    }

    if ( message_manager !== undefined && message_manager !== null ) {
        message_manager.show_apply_mesg( mesg );
    } else {
        mesg += ",现在应用?";
        if ( confirm( mesg ) ) {
            paging_holder.apply_data();
        }
    }
}

PagingHolder.prototype.show_note_mesg = function( mesg ) {
    var paging_holder = this;
    var message_manager = paging_holder.panel_config.ass_message_manager;
    if( message_manager !== undefined && message_manager !== null ) {
        message_manager.show_popup_note_mesg( mesg );
    } else {
        alert( mesg );
    }
}

PagingHolder.prototype.show_warn_mesg = function( mesg ) {
    var paging_holder = this;
    var message_manager = paging_holder.panel_config.ass_message_manager;
    if( message_manager !== undefined && message_manager !== null ) {
        message_manager.show_popup_error_mesg( mesg );
    } else {
        alert( mesg );
    }
}

PagingHolder.prototype.show_error_mesg = function( mesg ) {
    var paging_holder = this;
    var message_manager = paging_holder.panel_config.ass_message_manager;
    if( message_manager !== undefined && message_manager !== null ) {
        message_manager.show_popup_error_mesg( mesg );
    } else {
        alert( mesg );
    }
}

PagingHolder.prototype.show = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var panel_name = panel_config.panel_name;
    var TB_id = 'TransparentBorder_' + panel_name;
    var panel_id = paging_holder.panel_id;
    
    var box_cover_id = 'popup-mesg-border-box-cover-' + panel_name;
    var box_cover_id_for_jquery = '#' + box_cover_id;
    var check_in_selector = "#" + panel_config.check_in_id;

    $(check_in_selector).show().children('.popup-mesg-box-body').css({
        'margin-left': - ($(check_in_selector).children('.popup-mesg-box-body').width()/2)+'px',
        'margin-top': - ($(check_in_selector).children('.popup-mesg-box-body').height()/2)+'px'
    });;
	if(panel_config.is_modal){
		// setTimeout(function() {
		// 	document.getElementById(box_cover_id).setAttribute('class','open-dialog__overlay');
		// },0);
	
	
    
		if (panel_config.border_transparent) {

			if(panel_config.modal_config !== undefined) {
					var modal_config = panel_config.modal_config;
					var close_class_name = 'close_TransparentBorder_' + modal_config.modal_box_size;
					var open_class_name = 'open_TransparentBorder_' + modal_config.modal_box_size;
					document.getElementById(TB_id).setAttribute('class',open_class_name);
					document.getElementById(TB_id).style.zIndex = 1000;
			}
			var boder_height = document.getElementById(panel_id).offsetHeight;
			// var boder_width = document.getElementById(panel_id).offsetWidth;
			document.getElementById(TB_id).style.height = boder_height + 'px';
			// document.getElementById('TransparentBorder').style.width = boder_width + 'px';

			var cover_height = parseInt(document.getElementById(box_cover_id).offsetHeight);
			var cover_width = parseInt(document.getElementById(box_cover_id).offsetWidth);

			var border_height = parseInt(document.getElementById(TB_id).offsetHeight);
			var border_width = parseInt(document.getElementById(TB_id).offsetWidth);

			var temp_top = (cover_height - border_height) / 2 - 78;
			var temp_left = (cover_width - border_width) / 2;

			document.getElementById(TB_id).style.top = temp_top + 'px';
			document.getElementById(TB_id).style.left = temp_left + 'px';


			$(box_cover_id_for_jquery).on('click', function() {
				document.getElementById(box_cover_id).setAttribute('class','dialog__overlay');
				document.getElementById(TB_id).setAttribute('class',close_class_name);
				setTimeout(function(){
					$(check_in_selector).hide();
				},300);
			})

			$(window).resize(function() {
				if ($(check_in_selector).css("display") == 'block') {
					var cover_height = parseInt(document.getElementById(box_cover_id).offsetHeight);
					var cover_width = parseInt(document.getElementById(box_cover_id).offsetWidth);

					var border_height = parseInt(document.getElementById(TB_id).offsetHeight);
					var border_width = parseInt(document.getElementById(TB_id).offsetWidth);

					var temp_top = (cover_height - border_height) / 2 - 78;
					var temp_left = (cover_width - border_width) / 2;

					document.getElementById(TB_id).style.top = temp_top + 'px';
					document.getElementById(TB_id).style.marginTop = 0 + 'px';
					document.getElementById(TB_id).style.left = temp_left + 'px';
					document.getElementById(TB_id).style.marginLeft = 0 + 'px';

                    var boder_height = document.getElementById(panel_id).offsetHeight;
                    var boder_width = document.getElementById(panel_id).offsetWidth;
                    document.getElementById(TB_id).style.height = boder_height + 'px';
                    document.getElementById(TB_id).style.width = boder_width + 'px';
				}

			})
		}else{
            $('#'+panel_config.check_in_id+' .popup-mesg-box-cover').on('click',function(){
                $( check_in_selector ).hide()
            })
        }
	}
    paging_holder.text_hidden();
}

PagingHolder.prototype.hide = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    
    var check_in_selector = "#" + panel_config.check_in_id;
    $( check_in_selector ).hide();
}

PagingHolder.prototype.HideForBorder = function() {
    var paging_holder = this;
    var panel_config = paging_holder.panel_config;
    var panel_name = panel_config.panel_name;
    var TB_id = 'TransparentBorder_' + panel_name;
    var panel_id = paging_holder.panel_id;
    
    var box_cover_id = 'popup-mesg-border-box-cover-' + panel_name;
    var box_cover_id_for_jquery = '#' + box_cover_id;
    var check_in_selector = "#" + panel_config.check_in_id;

    if(panel_config.modal_config !== undefined){
        var modal_config = panel_config.modal_config;
        var close_class_name = 'close_TransparentBorder_' + modal_config.modal_box_size;
        var open_class_name = 'open_TransparentBorder_' + modal_config.modal_box_size;
        if (panel_config.border_transparent) {
            document.getElementById(TB_id).setAttribute('class',close_class_name);
            document.getElementById(box_cover_id).setAttribute('class','dialog__overlay');
            setTimeout(function(){
                $(check_in_selector).hide();
            },300);
        }
        else {
            $(check_in_selector).hide();
        }
    }
    else {
        $(check_in_selector).hide();
    }
}

/* *****************字符串处理函数*************************** */

/*
 * 功能： 返回字符串的真实长度
 * 参数： 要测试真实长度的字符串
 */
PagingHolder.get_string_length = function( str ) {
    var real_length = 0,
        str_len = str.length,
        char_code = -1;
    for (var i = 0; i < str_len; i++) {
        char_code = str.charCodeAt(i);
        if (char_code >= 0 && char_code <= 128) {
            real_length += 1;
        } else {
            real_length += 2;
        }
    }
    return real_length;
}

/*
 * 功能： 返回字符串的子串
 * 参数
 *      str -- 要操作的字符串
 *      start -- 开始的位置
 *      num -- 要截取的长度
 */
PagingHolder.get_sub_str = function( str, start, num ) {

}

//为隐藏的字段添加标题
PagingHolder.prototype.text_hidden = function() {
    $("td.text-hidden").map(function() {
        if (this.offsetWidth < this.scrollWidth) {
            $(this).prop("title", $(this).text());
        }else{
            $(this).removeAttr('title');
        }
    });
}
