Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.util.*',
    'Ext.state.*',
    'Ext.window.*'
]);
Ext.define('Resource', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'name'},
       {name: 'desc'},
       {name: 'am'},
       {name: 'ip'},
       {name: 'protocol'},
       {name: 'port'},
       {name: 'url'},
       {name: 'state'},
       {name: 'res_group'},
       {name: 'user_groups'}

    ],
    idProperty: 'resource'
});
Ext.define('ResourceGrep', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'text'},
       {name: 'leaf'},
       {name: 'type'},
       {name: 'desc'},
       {name: 'state'},
       {name: 'expanded'},
       {name: 'children'}
    ],
    idProperty: 'resourcegrep'
});

var mesgBoxWidth = 300;
//各种url
var handlerurl = '/cgi-bin/resourceset_handler.cgi';

var root_res_group = "所有资源";
var default_res_group = "默认资源组";

//启用禁用颜色
var enable_color = "#11C822";
var disable_color = "red";

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    var res_toolbar = Ext.create('Ext.toolbar.Toolbar',{
        width: document.body.clientWidth*0.948,
        viewConfig: {
            forceFit:true
        },
        items: [
            {
                text:'显示全部',
                handler: function(me){
                    var grid = me.up('container[name=resource_top_container]').down('grid');
                    var store = grid.getStore();
                    var params ={
                        start:0,
                        limit: 15,
                        search: '',
                        full_name: '',
                        type:''
                    };
                    Ext.apply(store.proxy.extraParams, params);
                    store.removeAll();
                    store.loadPage(1);
                }
            },
            '->',
            {
                xtype: 'textfield',
                width: 250,
                emptyText: '输入资源名或者描述以查询...',
                listeners: {
                    change:function(me,  e, eOpts ){
                        var text = Ext.String.trim(me.getValue());
                        /*显示一页搜索到的数据*/
                        var grid = me.up('container[name=resource_top_container]').down('grid');
                        var store = grid.getStore();
                        var params ={
                            start:0,
                            limit: 15,
                            search: text
                        };
                        Ext.apply(store.proxy.extraParams, params);
                        store.removeAll();
                        store.loadPage(1);
                    }
                }
                
            },
            '-',
            {
                icon: '/images/search16x16.png',
                handler: function(me){
                    var text = Ext.String.trim(me.up('container[name=resource_top_container]').down('toolbar').down('textfield').getValue());
                    /*显示一页搜索到的数据*/
                    var grid = me.up('container[name=resource_top_container]').down('grid');
                    var store = grid.getStore();
                    var params ={
                        start:0,
                        limit: 15,
                        search: text
                    };
                    Ext.apply(store.proxy.extraParams, params);
                    store.removeAll();
                    store.loadPage(1);
                }
            }
        ]
    });
    
    var resgroup_store = Ext.create('Ext.data.TreeStore', {
        model: 'ResourceGrep',
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/resourceset_group_tree.cgi',
            actionMethods:{
                read: 'POST'
            }
        },
        autoLoad: true,
        sorters: [{
            property: 'leaf',
            direction: 'ASC'
        }, {
            property: 'text',
            direction: 'ASC'
        }]
    });

    var resgroup_tree = Ext.create('Ext.tree.Panel', {
        width: document.body.clientWidth*0.2,
        height: 480,
        id: 'resgroup_tree',
        rootVisible: true,
        root: {
            text: root_res_group,
            desc: '该资源组不能进行编辑、删除操作。',
            type: 'resg',
            expanded: true,
            state:'on'
        },
        store: resgroup_store,
        listeners: {
            itemclick: function(view, record, item, index, e, eOpts){
                /*显示组信息*/
                var panel = view.up('container[name=resource_top_container]').down('panel[name=resgroup_info_panel]');
                var group_descri_label = panel.down('displayfield[name=group_descri_label]');
                //var group_info_label = panel.down('displayfield[name=group_info_label]');
                group_descri_label.setValue(record.data.desc);
                /*显示组启用禁用状态*/
                /*var group_info = "";
                if(record.data.state == "on"){
                    group_info = '<font color = "' + enable_color + '">启用状态</font>';
                }else{
                    group_info = '<font color="' + disable_color + '">禁用状态</font>';
                }
                group_info_label.setValue(group_info);*/
                
                /*分页显示*/
                var grid = view.up('container[name=resource_top_container]').down('grid');
                var store = grid.getStore();
                var text = view.up('container[name=resource_top_container]').down('toolbar').down('textfield').getValue();
                var full_name = record.data.text;
                var params ={
                    start:0,
                    limit: 15,
                    search: text,
                    full_name: full_name
                };
                Ext.apply(store.proxy.extraParams, params);
                store.loadPage(1);
                
                /*储存必要信息，用以禁用组，编辑组，删除组之用*/
                panel.current_data = record.data;
            }
        }
    });
    
    var resgroup_info_panel = Ext.create('Ext.panel.Panel',{
        width: document.body.clientWidth*0.748,
        height: 100,
        name: 'resgroup_info_panel',
        current_data: '',
        items: [{
            xtype: 'container',
            layout: 'vbox',
            items: [{
                xtype: 'container',
                layout: 'hbox',
                margin: '15 5 5 20',
                items: [{
                    xtype: 'label',
                    text: '组描述：',
                    height: 20,
                    padding: '6 0 0 0'
                },
                {
                    xtype: 'displayfield',
                    name: 'group_descri_label',
                    readOnly: true,
                    padding: '3 0 0 0',
                    value: '未选择组...',
                    renderer: function(val){
                        if(val.length > 50){
                            var ret = val.substr(0, 50) + "...";
                            return ret;
                        }else{
                            return val;
                        }
                    }
                }]
            },
            /*{
                xtype: 'container',
                layout: 'hbox',
                margin: '5 5 5 20',
                items: [
                    {
                        xtype: 'label',
                        text: '组信息：',
                        height: 20,
                        padding: '6 0 0 0'
                    },
                    {
                        xtype: 'displayfield',
                        name: 'group_info_label',
                        readOnly: true,
                        width: 500,
                        height: 20,
                        value: '未选择组...'
                    }
                ]
            },*/
            {
                xtype: 'container',
                layout: 'hbox',
                margin: '15 5 5 20',
                items: [{
                    xtype: 'label',
                    text: '组操作：',
                    height: 20,
                    padding: '6 0 0 0'
                },
                {
                    xtype: 'button',
                    icon: '/images/search16x16.png',
                    tooltip: '查看资源组详情',
                    text: '详情',
                    margin: '5',
                    handler: function(me){
                        var panel = me.up('panel[name=resgroup_info_panel]');
                        var data = panel.current_data;
                        if(data.type == 'resg'){
                            ViewResgDetail(data);
                        }else{
                            showWarningMsg("请选择资源组~");
                        }
                    }
                },
                /*{
                    xtype: 'button',
                    name: 'enable',
                    icon: '/images/on.png',
                    tooltip: '启用组',
                    text: '启用组',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=resgroup_info_panel]').current_data;
                        if(data != ''){
                            if(data.text == root_res_group){
                                showWarningMsg("该资源组不能进行禁用、编辑、删除操作，请重新选择资源组~");
                                return;
                            }
                            if(data.state == 'on'){
                                showWarningMsg("该资源组已是启用状态状态");
                                return;
                            }
                            EidtResg(data, "enable", "启用资源组");
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要操作的资源组~");
                        }
                    }
                },
                {
                    xtype: 'button',
                    name: 'disable',
                    icon: '/images/off.png',
                    tooltip: '禁用组',
                    text: '禁用组',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=resgroup_info_panel]').current_data;
                        if(data != ''){
                            if(data.text == root_res_group){
                                showWarningMsg("该资源组不能进行禁用、编辑、删除操作，请重新选择资源组~");
                                return;
                            }
                            if(data.state == 'off'){
                                showWarningMsg("该资源组已是禁用状态状态");
                                return;
                            }
                            var action = confirm("确定要禁用该资源组？");
                            if(action == true){
                                EidtResg(data, "disable", "禁用资源组");
                            }
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要操作的资源组~");
                        }
                    }
                },*/
                {
                    xtype: 'button',
                    name: 'edit',
                    icon: '/images/edit.png',
                    tooltip: '编辑',
                    text: '编辑',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=resgroup_info_panel]').current_data;
                        if(data != ''){
                            if(data.text == root_res_group){
                                showWarningMsg("该资源组不能进行编辑、删除操作，请重新选择资源组~");
                                return;
                            }
                            addContentResg(data);
                            slideEditResg();
                            check._submit_check(object_resg,check);
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要编辑的资源组~");
                        }
                    }
                },
                {
                    xtype: 'button',
                    name: 'del',
                    icon: '/images/delete.png',
                    tooltip: '删除',
                    text: '删除',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=resgroup_info_panel]').current_data;
                        if(data != ''){
                            if(data.text == root_res_group){
                                showWarningMsg("该资源组不能进行编辑、删除操作，请重新选择资源组~");
                                return;
                            }
                            if(data.text == default_res_group){
                                showWarningMsg("默认资源组不能进行删除操作，请重新选择资源组~");
                                return;
                            }
                            var action = confirm("确定要删除该资源组？");
                            if(action == true){
                                EidtResg(data, "del", "删除资源组");
                            }
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要删除的资源组~");
                        }
                        
                    }
                }]
            }]
        }]
    });
    
    var resources_store = Ext.create('Ext.data.ArrayStore', {
        model: 'Resource',
        autoLoad: true,
        pageSize: 15,
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/resourceset_data.cgi',
            actionMethods:{
                read: 'POST'
            },
            reader: {
                type: 'json',
                root: 'resources'
            }
        },
        listeners: {
            beforeload: function(store, operation, eOpts){
                var new_params = {
                    limit: 15
                };
                Ext.apply(store.proxy.extraParams, new_params);
            }
        }
    });
    
    /*资源列表*/
    var resources_grid = Ext.create('Ext.grid.Panel', {
        id: 'resources_grid',
        height: 380,
        width: document.body.clientWidth*0.748,
        store: resources_store,
        viewConfig: {
            stripeRows: true,
            enableTextSelection: true
        },
        columns: [
            {
                text     : '资源名称',
                width    : 100,
                align: 'center',
                //sortable : false,
                //hideable : false,
                dataIndex: 'name'
            },
            {
                text     : '访问方式',
                width    : 120,
                align: 'center',
                //sortable : false,
                //hideable : false,
                dataIndex: 'am',
                renderer: function(val){
                    if(val == "web"){
                        return "WEB访问";
                    }else{
                        return "其他访问";
                    }
                }
            },
            {
                text     : '描述',
                flex     : 1,
                align: 'center',
                //sortable : false,
                //hideable : false,
                dataIndex: 'desc'
            },
            {
                text     : '启用状态',
                width    : 120,
                align: 'center',
                //sortable : false,
                //hideable : false,
                dataIndex: 'state',
                renderer: function(val){
                    if(val == 'on'){
                        return '<font color = "' + enable_color + '">启用状态</font>';
                    }else{
                        return '<font color = "' + disable_color + '">禁用状态</font>';
                    }
                }
            },
            {
                xtype: 'actioncolumn',
                header: '操作',
                width: 200,
                align: 'center',
                //sortable : false,
                //hideable : false,
                iconCls: 'imagecursor',
                items: [{
                    icon: '/images/search16x16.png',
                    tooltip: '查看详情',
                    margin: '5 5 5 5',
                    handler: function(grid, rowIndex, colIndex){
                        var resData = grid.getStore().getAt(rowIndex).data;
                        var userGroups = resData.user_groups;
                        var ugDetails = getUserGroupDetails(userGroups);
                        ViewResDetail(resData,ugDetails);
                    }
                },　{
                    icon: '/images/on.png',
                    tooltip: '启用资源',
                    padding: '5 5 5 5',
                    handler: function(grid, rowIndex, colIndex){
                        var record = grid.getStore().getAt(rowIndex);
                        if(record.data.state == 'on'){
                            showWarningMsg("该资源已是启用状态");
                            return;
                        }
                        EidtResource(record.data, "enable", "启用资源");
                    }
                },　{
                    icon: '/images/off.png',
                    tooltip: '禁用资源',
                    margin: '5 5 5 5',
                    handler: function(grid, rowIndex, colIndex){
                        var record = grid.getStore().getAt(rowIndex);
                        if(record.data.state == 'off'){
                            showWarningMsg("该资源已是禁用状态");
                            return;
                        }
                        var action = confirm("确定要禁用该资源？");
                        if(action == true){
                            EidtResource(record.data, "disable", "禁用资源");
                        }
                    }
                },　{
                    icon: '/images/edit.png',
                    tooltip: '编辑',
                    handler: function(grid, rowIndex, colIndex){
                        addContentResource(grid.getStore().getAt(rowIndex).data);
                        slideEditResource();
                        check._submit_check(object_resource,check);
                    }
                },　{
                    icon: '/images/delete.png',
                    tooltip: '删除',
                    handler: function(grid, rowIndex, colIndex){
                        var record = grid.getStore().getAt(rowIndex);
                        var action = confirm("确定要删除该资源？");
                        if(action == true){
                            EidtResource(record.data, "del", "删除资源");
                        }
                        
                    }
                }]
            }
        ],
        dockedItems: [{
            xtype: 'pagingtoolbar',
            store: resources_store,
            dock: 'bottom',
            displayInfo:true,
            firstText: '第一页',
            prevText :'上一页',
            lastText: '最后一页',
            nextText: '下一页',
            refreshText:'刷新',
            beforePageText:'第',
            afterPageText:'页, 共{0}页',
            displayMsg: '显示第 {0}~{1} 条，共有{2} 条',
            emptyMsg: "没有可显示的页面",
            width: document.body.clientWidth*0.67,
            height: 32
        }]
    });
    var resources_container = Ext.create('Ext.container.Container',{
        height: 532,
        width: document.body.clientWidth*0.948,
        name: 'resource_top_container',    
        margin: '5 20 20 25',
        renderTo: 'resource_list',
        layout: 'vbox',
        viewConfig: {
            forceFit:true
        },
        
        items:[{
            xtype: res_toolbar
        },　{
            xtype: 'container',
            layout: 'hbox',
            items:[
                {
                    xtype: resgroup_tree
                },　{
                    xtype: 'container',
                    name: 'resource_main_container',
                    layout: 'vbox',
                    items: [{
                        xtype: resgroup_info_panel
                    },　{
                        xtype: resources_grid
                    }]
                }
            ]
        }]
    });
});
var showWarningMsg =function(msg){
    alert(msg);
}

var showInfoMsg =function(msg){
    alert(msg);
}

var slideEditResg = function(){
    //修改显示样式
    $('#add-div-header-resg span span').html("编辑资源组");
    $('#resg_name').attr('readonly','readonly');
    $('#resg_submit').attr("value","编辑");
    
    //下拉
    $('#add-div-content-resg').slideDown('1000');
    $('#add-div-header-resg img').attr("src","/images/del.png");
}

var slideEditResource = function(){
    //修改显示样式
    $('#add-div-header span span').html("编辑资源");
    $('#resource_name').attr('readonly','readonly');
    $('#resource_submit').attr("value","编辑");
    
    //下拉
    $('#add-div-content').slideDown('1000');
    $('#add-div-header img').attr("src","/images/del.png");
}

var addContentResg = function(data){
    document.getElementById("resg_name").value = data.text;
    document.getElementById("resg_description").value = data.desc;
    var enable = true;
    if(data.state == "off"){
        enable = false;
    }
    document.getElementById("resg_enable").checked = enable;
}

var addContentResource = function(data){
    document.getElementById("resource_name").value = data.name;    
    document.getElementById("resource_description").value = data.desc;    
    document.getElementById("access_method").value = data.am;
    change();
    document.getElementById("ip_addr").value = data.ip;
    document.getElementById("protocol").value = data.protocol;    
    document.getElementById("port").value = data.port;    
    document.getElementById("url_addr").value = data.url;
    document.getElementById("resource_grep").value = data.res_group;
    document.getElementById("resource_enable").checked = true;
    if(data.state == 'off'){
        document.getElementById("resource_enable").checked = false;
    }
    if(data.am == 'other'){
        document.getElementById("hreftr").style.display = "none";
    }
}



var EidtResg = function(data, operation, msg){
    var resg_name = data.text;
    var description = data.desc;
    var state = data.state;
    
    var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
    Ext.Ajax.request({
        method: 'POST',
        url: handlerurl,
        params: {
            action: operation,
            type: 'resg',
            resg_name: resg_name,
            description: description,
            state: state
        },
        callback: function(opt, success, response) {
            wait.close();
            var text = Ext.String.trim(response.responseText);
            if(text == '1'){
                showInfoMsg(msg+'成功！');
                //清空表单内容
                //emptyContentResg();
                //上拉添加菜单
                //cancelAddOrEditResg();
                //刷新资源组面板
                Ext.getCmp('resgroup_tree').getStore().load();
            }else if(text == '-1'){
                showWarningMsg(msg+"失败，请重试~");
            }else{
                showWarningMsg(text);
            }
        }
    });
}
var EidtResource = function(data, operation, msg){
    var resource_name = data.name;
    var resource_description = data.desc;
    var access_method = data.am;
    var ip_addr = data.ip;
    var protocol = data.protocol;
    var port = data.port;
    var url_addr = data.url;
    var resource_grep = data.res_group;
    var state = data.state;
    
    var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
    Ext.Ajax.request({
        method: 'POST',
        url: handlerurl,
        params: {
            action: operation,
            type: 'res',
            resource_name: resource_name,
            resource_description: resource_description,
            access_method: access_method,
            ip_addr: ip_addr,
            protocol: protocol,
            port: port,
            url_addr: url_addr,
            resource_grep: resource_grep,
            state: state
        },
        callback: function(opt, success, response) {
            wait.close();
            var text = Ext.String.trim(response.responseText);
            if(text == '1'){
                showInfoMsg(msg+'成功！');
                //清空表单内容
                //emptyContentResource();
                //上拉添加菜单
                //cancelAddOrEditResource();
                //刷新资源列表面板
                Ext.getCmp('resources_grid').getStore().load();
            }else if(text == '-1'){
                showWarningMsg(msg+"失败，请重试~");
            }else{
                showWarningMsg(text);
            }
        }
    });
}

function ViewResgDetail(data){
    var marginSize = '5 15 0 0';
    Ext.create('Ext.window.Window',{
        title: data.text+'的详情',
        height: 300,
        modal: true,
        width: document.body.clientWidth*0.5,
        padding: 5,
        layout: 'fit',
        data: '',
        items: { 
            xtype: 'form',
            defaultType: 'displayfield',
            bodyPadding: 15,
            autoScroll: true,
            items:[
                {
                    fieldLabel:'资源组名称',
                    margin: marginSize,
                    value: data.text
                },
                {
                    fieldLabel: '描述',
                    margin: marginSize,
                    value: data.desc
                },
                /*{
                    fieldLabel: '是否启用',
                    margin: marginSize,
                    value: data.state,
                    renderer: function(val){
                        if( val == 'on'){
                            return '<font color = "' + enable_color + '">启用状态</font>';
                        }else{
                            return '<font color = "' + disable_color+ '">禁用状态</font>';
                        }
                    }
                }*/
            ]
        },
        buttons: [
            {
                text:"确定",
                handler: function(me){
                    me.up('window').close();
                }
            }
        ]
    }).show();
}

function getUserGroupDetails(userGroups){
    var ret = '';
    /*Ext.Ajax.request({
        url: '/cgi-bin/resourceset_ug_data.cgi',
        method: 'POST',
        params: {
            userGroups: userGroups
        },
        success: function(response, opts) {
            var mydata = response.responseText;
            ret = Ext.JSON.decode(response.responseText);
        },
        failure: function(response, opts) {
            alert("用户组信息请求失败，请重试");
        }
    });*/
    //这里需要用同步请求方式
    $.ajax({
        type: 'POST',
        url: '/cgi-bin/resourceset_ug_data.cgi',
        async : false,
        data : 'userGroups='+userGroups,
        success : function(data){ 
            ret = data;                                                                     
        }
    });
    return ret;
}

function ViewResDetail(resData,ugDetails){
    var innerWidth = document.body.clientWidth*0.6;
    var outerWidth = document.body.clientWidth*0.61;
    var windowHeight = 500;
    var resDataHeight = 150;
    var ugDataHeight = 283;
    var resDataForm = Ext.create('Ext.form.Panel', {
        height: resDataHeight,
        autoScroll : true,
        width: innerWidth,
        bodyPadding: '5 15',
        layout: {
            type: 'table',
            columns: 2
            //columns: 1
        },
        defaultType: 'displayfield',
        items: [{
            fieldLabel: '资源名称',
            value: resData.name
        },　{
            fieldLabel: '访问方式',
            value: resData.am,
            renderer: function(val){
                if(val == 'web'){
                    return "WEB访问";
                }else{
                    return "其他访问";
                }
            }
        },　{
            fieldLabel: 'IP地址',
            value: resData.ip
        },　{
            fieldLabel: '协议',
            value: resData.protocol
        },　{
            fieldLabel: '端口',
            value: resData.port
        },　{
            fieldLabel: 'URL地址',
            value: resData.url
        },　{
            fieldLabel: '所属资源组',
            value: resData.res_group
        },　{
            fieldLabel: '是否启用',
            value: resData.state,
            renderer: function(val){
                if(val == 'on'){
                    return '<font color="' + enable_color + '">启用状态</font>';
                }else{
                    return '<font color="' + disable_color + '">禁用状态</font>';;
                }
            }
        },　{
            fieldLabel: '描述',
            colspan: 2,
            value: resData.desc
        }]
    });
    var ugInfoForm = Ext.create('Ext.form.Panel', {
        height: ugDataHeight,
        width: innerWidth,
        autoScroll : true,
        defaultType: 'displayfield',
        bodyPadding: '5 15',
        layout: 'anchor',
        items: [
            {
                fieldLabel: '关联用户组',
                value: '',
                renderer: function(val){
                    var display = '';
                    var ugDetailObj = JSON.parse(ugDetails).data;
                    var length = ugDetailObj.length;
                    //开始渲染table
                    display = "<table class='ruleslist'>";
                    display = display + '<tr><td class="boldbase">关联用户组</td><td class="boldbase">描述</td></tr>';
                    for(var i = 0; i < length; i++){
                        var item = ugDetailObj[i];
                        display = display +"<tr><td class='add-div-type'>" + item.full_name + "</td>";
                        display = display +"<td>" + item.desc + "</td></tr>";
                    }
                    if(length < 1){
                        display = display + '<tr class="env table_note fordel"><td colspan="2"><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
                    }
                    return display;
                }
            }
        ]
    });
    Ext.create('Ext.window.Window',{
        title: resData.name+'的详情',
        height: windowHeight,
        modal: true,
        width: outerWidth,
        autoScroll: false,
        layout: 'anchor',
        items:[{
            xtype: resDataForm
            
        },{
            xtype: ugInfoForm
            
        }],
        buttons: [{
            text:"确定",
            padding: 5,
            handler: function(me){
                me.up('window').close();
            }
        }]
    }).show();
}