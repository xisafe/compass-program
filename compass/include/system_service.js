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


    list_panel.render();

    /* 设置面板关联 */





    list_panel.update_info( true );

});

/*
 * 第一步，定义全局变量
 */

var ass_url = "/cgi-bin/system_service.cgi";




var list_panel_config = {
    url: ass_url,                   /* ***必填***，控制数据在哪里加载数据 */
    check_in_id: "list_panel",      /* ***必填***，确定面板挂载在哪里 */
    panel_name: "list_panel",       /* ==*可选*==，默认名字my_list_panel，当一个页面存在多个列表面板，此字段必填，
                                                   以区别不同面板 */
    page_size: 20,
    panel_title: "预定义服务",		/* ===可选===，默认是true，控制搜索框是否展示，*/
	is_default_search: false, 
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
        },
    },
    panel_header: [                 /* ***必填***，控制数据的加载以及表头显示 */
        {
            enable: true,
            type: "text",
            title: "序号",
            name: "idView",
            "td_class":"align-center",
            width: "5%"
        }, {
            enable: true,
            type: "text",
            title: "名称",
            name: "name",
            width: "25%"
        }, {
            enable: true,
            type: "text",
            title: "协议",
            name: "agreement",
            width: "70%"
        }, {
             enable: false,
             type: "text",
             title: "描述",
             name: "description",
             width: "30%"
         }
    ]
};


var list_panel = new PagingHolder( list_panel_config );


