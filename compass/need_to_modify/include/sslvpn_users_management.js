Ext.require([
    'Ext.grid.*',
    'Ext.data.*',
    'Ext.util.*',
    'Ext.state.*',
    'Ext.window.*'
]);
Ext.define('Openvpnuser', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'username'},
       {name: 'user_enabled'},
       {name: 'setred'},
       {name: 'remotenets'},
       {name: 'dontpushroutes'},
       {name: 'explicitroutes'},
       {name: 'static_ip'},
       {name: 'push_custom_dns'},
       {name: 'firstdns'},
       {name: 'seconddns'},
       {name: 'push_custom_domain'},
       {name: 'custom_domain'},
       {name: 'user_cert'},
       {name: 'user_cert_value'},
       {name: 'whitelist'},
       {name: 'comments'},
       {name: 'group_info'}

    ],
    idProperty: 'openvpnuser'
});
Ext.define('OpenvpnuserGroup', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'text'},
       {name: 'leaf'},
       {name: 'type'},
       {name: 'desc'},
       {name: 'state'},
       {name: 'expanded'},
       {name: 'full_name'},
       {name: 'children'},
       {name: 'res'},
       {name: 'users'}
    ],
    idProperty: 'openvpnusergroup'
});

Ext.define('OpenvpnResGroup', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'text'},
       {name: 'leaf'},
       {name: 'type'},
       {name: 'desc'},
       {name: 'state'},
       {name: 'expanded'},
       {name: 'children'},
       {name: 'resources'}
    ],
    idProperty: 'openvpnresgroup'
});

var mesgBoxWidth = 300;
/*各种url*/
var handlerurl = '/cgi-bin/sslvpn_users_handler.cgi';
var aedurl = '/cgi-bin/sslvpn_users_aed.cgi';
/*默认的用户组*/
var root_group = "所有用户";
var default_group = "默认用户组";
var enable_color = "#11C822";
var disable_color = "red";

Ext.onReady(function() {
    Ext.QuickTips.init();
    
    var users_toolbar = Ext.create('Ext.toolbar.Toolbar',{
        width: document.body.clientWidth*0.948,
        height: 32,
        viewConfig: {
            forceFit:true
        },
        items: [
            {
                text:'显示全部',
                handler: function(me){
                    var grid = me.up('container[name=openvpn_user_top_container]').down('grid');
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
                emptyText: '输入用户名或者备注以查询...',
                listeners: {
                    change:function(me,  e, eOpts ){
                        var text = Ext.String.trim(me.getValue());
                        /*显示一页搜索到的数据*/
                        var grid = me.up('container[name=openvpn_user_top_container]').down('grid');
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
                    var text = Ext.String.trim(me.up('container[name=openvpn_user_top_container]').down('toolbar').down('textfield').getValue());
                    /*显示一页搜索到的数据*/
                    var grid = me.up('container[name=openvpn_user_top_container]').down('grid');
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
    
    var groups_store = Ext.create('Ext.data.TreeStore', {
        model: 'OpenvpnuserGroup',
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/sslvpn_users_tree.cgi',
            actionMethods:{
                read: 'POST'
            }
        },
        autoLoad: false,
        sorters: [{
            property: 'leaf',
            direction: 'ASC'
        }, {
            property: 'text',
            direction: 'ASC'
        }]
    });

    var groups_tree = Ext.create('Ext.tree.Panel', {
        width: document.body.clientWidth*0.2,
        height: 480,
        id: 'openvpn_users_tree',
        rootVisible: true,
        root: {
            text: '所有用户',
            id: '所有用户',
            full_name: '所有用户',
            type: 'org',
            desc: '该组织结构不能进行编辑、删除操作',
            expanded: true,
            state:'on'
        },
        store: groups_store,
        listeners: {
            afterrender: function(me){
                //me.getStore().load();
                var panel = me.up('container[name=openvpn_user_top_container]').down('panel[name=group_descri_panel]');
                panel.org_info = me.getRootNode( );
            },
            itemclick: function(view, record, item, index, e, eOpts){
                /*显示组信息*/
                var panel = view.up('container[name=openvpn_user_top_container]').down('panel[name=group_descri_panel]');
                var group_descri_label = panel.down('displayfield[name=group_descri_label]');
                //var group_info_label = panel.down('displayfield[name=group_info_label]');
                group_descri_label.setValue(record.data.desc);
                /*显示组启用禁用状态*/
                /*var group_info = "";
                if(record.data.state == "on"){
                    group_info = '<font color = "' + enable_color + '">启用状态</font>';
                }else{
                    group_info = '<font color="' + disable_color+ '">禁用状态</font>';
                }
                group_info_label.setValue(group_info);*/
                
                /*分页显示*/
                var grid = view.up('container[name=openvpn_user_top_container]').down('grid');
                var store = grid.getStore();
                var text = view.up('container[name=openvpn_user_top_container]').down('toolbar').down('textfield').getValue();
                var params ={
                    start:0,
                    limit: 15,
                    search: text,
                    full_name: record.data.full_name,
                    type:record.data.type
                };
                Ext.apply(store.proxy.extraParams, params);
                store.loadPage(1);
                
                /*储存必要信息，用以禁用组，编辑组，删除组之用*/
                panel.current_data = record.data;
            }
        }
    });
    
    var group_info_panel = Ext.create('Ext.panel.Panel',{
        width: document.body.clientWidth*0.748,
        height: 100,
        name: 'group_descri_panel',
        id: 'group_descri_panel',
        current_data: '',
        org_info: '',
        res_data: '',
        listeners: {
            afterrender: function(me){
                Ext.Ajax.request({
                    url: '/cgi-bin/resourceset_data.cgi',
                    method: 'POST',
                    params: {
                        limit: 'nolimit'
                    },
                    callback: function(opt, success, response) {
                        me.res_data = Ext.JSON.decode(response.responseText);
                    }
                });
            }
        },
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
                },{
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
                },{
                    xtype: 'button',
                    icon: '/images/search16x16.png',
                    tooltip: '查看用户组详情',
                    text: '详情',
                    margin: '5',
                    handler: function(me){
                        var panel = me.up('panel[name=group_descri_panel]');
                        var data = panel.current_data;
                        var res_data = panel.res_data;
                        if(data.type == 'ug'){
                            ViewUgDetail(data,res_data);
                        }else{
                            showWarningMsg("请选择用户组~");
                        }
                    }
                },
                /*{
                    xtype: 'button',
                    icon: '/images/on.png',
                    tooltip: '启用组',
                    text: '启用组',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=group_descri_panel]').current_data;
                        if(data.type == 'org'){
                            if(data.text == root_group){
                                showWarningMsg("该组织结构不能进行启用、禁用、编辑、删除操作，请重新选择~");
                                return;
                            }
                            if(data.state == 'on'){
                                showWarningMsg("该组织结构已是启用状态");
                                return;
                            }
                            EidtOrgzOrUgrp(data, "orgz", "enable", "启用组织结构");
                        }else if(data.type == 'ug'){
                            if(data.state == 'on'){
                                showWarningMsg("该用户组已是启用状态");
                                return;
                            }
                            EidtOrgzOrUgrp(data, "ugrp", "enable", "启用用户组");
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要启用的节点~");
                        }
                    }
                },
                {
                    xtype: 'button',
                    icon: '/images/off.png',
                    tooltip: '禁用组',
                    text: '禁用组',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=group_descri_panel]').current_data;
                        if(data.type == 'org'){
                            if(data.text == root_group){
                                showWarningMsg("该组织结构不能进行启用、禁用、编辑、删除操作，请重新选择~");
                                return;
                            }
                            if(data.state == 'off'){
                                showWarningMsg("该组织结构已被禁用");
                                return;
                            }
                            var action = confirm("确定要禁用该组织结构？");
                            if(action == true){
                                EidtOrgzOrUgrp(data, "orgz", "disable", "禁用组织结构");
                            }
                        }else if(data.type == 'ug'){
                            if(data.state == 'off'){
                                showWarningMsg("该用户组已被禁用");
                                return;
                            }
                            var action = confirm("确定要禁用该用户组？");
                            if(action == true){
                                EidtOrgzOrUgrp(data, "ugrp", "disable", "禁用用户组");
                            }
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要禁用的节点~");
                        }
                    }
                },*/
                {
                    xtype: 'button',
                    icon: '/images/edit.png',
                    tooltip: '编辑',
                    text: '编辑',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=group_descri_panel]').current_data;
                        if(data.type == 'org'){
                            if(data.text == root_group){
                                showWarningMsg("该组织结构不能进行编辑、删除操作");
                                return;
                            }
                            addContentOrgz(data);
                            slideEditOrgz();
                            check._submit_check(object_orgz,check);
                        }else if(data.type == 'ug'){
                            addContentUgrp(data);
                            slideEditUgrp();
                            check._submit_check(object_ugrp,check);
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要编辑的节点~");
                        }
                    }
                },{
                    xtype: 'button',
                    icon: '/images/delete.png',
                    tooltip: '删除组织结构或者用户组',
                    text: '删除',
                    margin: '5',
                    handler: function(me){
                        var data = me.up('panel[name=group_descri_panel]').current_data;
                        if(data.type == 'org'){
                            if(data.text == root_group){
                                showWarningMsg("该组织结构不能进行编辑、删除操作");
                                return;
                            }
                            var action = confirm("确定要删除该组织结构？");
                            if(action == true){
                                EidtOrgzOrUgrp(data, "orgz", "del", "删除组织结构");
                            }
                        }else if(data.type == 'ug'){
                            if(data.text == default_group){
                                showWarningMsg("默认用户组不能进行删除操作");
                                return;
                            }
                            var action = confirm("确定要删除该用户组？");
                            if(action == true){
                                EidtOrgzOrUgrp(data, "ugrp", "del", "删除用户组");
                            }
                        }else{
                            showWarningMsg("请在左侧面板中选择你需要删除的节点~");
                        }
                        
                    }
                }]
            }]
        }]
    });
    
    var users_store = Ext.create('Ext.data.ArrayStore', {
        model: 'Openvpnuser',
        autoLoad: true,
        pageSize: 15,
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/sslvpn_users_data.cgi',
            actionMethods:{
                read: 'POST'
            },
            reader: {
                type: 'json',
                root: 'users'
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
    
    /*用户列表*/
    var users_grid = Ext.create('Ext.grid.Panel', {
        store: users_store,
        id: 'openvpn_users_grid',
        stateful: true,
        multiSelect: true,
        stateId: 'stateGrid',
        height: 380,
        width: document.body.clientWidth*0.748,
        /*viewConfig: {
            stripeRows: true,
            enableTextSelection: true
        },*/
        columns: [{
            text     : '用户名',
            width    : 100,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'username'
        },{
            text     : '本地子网',
            width    : 120,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'explicitroutes',
            renderer: function(val){
                var explicitroutes = val.split(",");
                return explicitroutes.join('<br/>');
            }
        },{
            text     : '地址分配',
            width    : 120,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'static_ip',
            renderer: function(val){
                if(val == ''){
                    return '动态分配';
                }else{
                    return val;
                }
            }
        },{
            text     : '证书序列号',
            width    : 100,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'user_cert_value'
        },{
            text     : '备注',
            flex     : 1,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'comments'
        },{
            text     : '启用状态',
            width    : 80,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'user_enabled',
            renderer: function(val){
                if(val == 'true'){
                    return '<font color = "' + enable_color + '">启用状态</font>';
                }else{
                    return '<font color = "' + disable_color+ '">禁用状态</font>';
                }
            }
        },{
            text     : '白名单状态',
            width    : 80,
            align: 'center',
            //sortable : false,
            //hideable : false,
            dataIndex: 'whitelist',
            renderer: function(val){
                if(val == 'true'){
                    return '<font color = "' + enable_color + '">已移入</font>';
                }else{
                    return '<font color = "' + disable_color+ '">已移出</font>';
                }
            }
        },{
            xtype: 'actioncolumn',
            header: '操作',
            width: 150,
            align: 'center',
           // sortable : false,
           // hideable : false,
            iconCls: 'imagecursor',
            items: [{
                icon: '/images/search16x16.png',
                tooltip: '查看详情',
                margin: '5 5 5 5',
                handler: function(grid, rowIndex, colIndex){
                    var userData = grid.getStore().getAt(rowIndex).data;
                    var userGroupInfo = userData.group_info.split(":");//保存分组信息的数组
                    var panel = grid.up('container[name=openvpn_user_top_container]').down('panel[name=group_descri_panel]');
                    var org_info = panel.org_info;
                    var res_data = panel.res_data;
                    var details = getUserResourceDetails(userGroupInfo, org_info, res_data);//得到的是个二维数组
                    ViewUserDetail(userData,details);
                }
            },{
                icon: '/images/on.png',
                tooltip: '启用账号',
                margin: '5 5 5 5',
                handler: function(grid, rowIndex, colIndex){
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.data.user_enabled == 'true'){
                        showWarningMsg("该账号已是启用状态");
                        return;
                    }
                    var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
                    Ext.Ajax.request({
                        method: 'POST',
                        url: handlerurl,
                        params: {
                            action: 'enable',
                            username: record.data.username
                        },
                        callback: function(opt, success, response) {
                            wait.close();
                            var text = Ext.String.trim(response.responseText);
                            if(text == '1'){
                                showInfoMsg("启用成功！");
                                var store = grid.getStore();
                                store.removeAll();
                                store.loadPage(1);
                            }else if(text == '-1'){
                                showWarningMsg("启用失败，请重试~");
                            }else{
                                showWarningMsg(text);
                            }
                        }
                    });
                }
            },{
                icon: '/images/off.png',
                tooltip: '禁用账号',
                margin: '5 5 5 5',
                handler: function(grid, rowIndex, colIndex){
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.data.user_enabled == 'false'){
                        showWarningMsg("该账号已被禁用");
                        return;
                    }
                    var action = confirm("确定要禁用用户？");
                    if(action == true){
                        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
                        Ext.Ajax.request({
                            method: 'POST',
                            url: handlerurl,
                            params: {
                                action: 'disable',
                                username: record.data.username
                            },
                            callback: function(opt, success, response) {
                                wait.close();
                                var text = Ext.String.trim(response.responseText);
                                if(text == '1'){
                                    showInfoMsg("禁用成功！");
                                    var store = grid.getStore();
                                    store.removeAll();
                                    store.loadPage(1);
                                }else if(text == '-1'){
                                    showWarningMsg("禁用失败，请重试~");
                                }else{
                                    showWarningMsg(text);
                                }
                            }
                        });
                    }
                }
            },{
                icon: '/images/edit.png',
                tooltip: '编辑',
                handler: function(grid, rowIndex, colIndex){
                    addContent(grid.getStore().getAt(rowIndex).data);
                    slideEdit();
                    check._submit_check(object,check);
                }
            },{
                icon: '/images/white_list.png',
                tooltip: '移入白名单',
                handler: function(grid, rowIndex, colIndex){
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.data.whitelist == 'true'){
                        showWarningMsg("该账号已移入白名单");
                        return;
                    }
                    var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
                    Ext.Ajax.request({
                        method: 'POST',
                        url: handlerurl,
                        params: {
                            action: 'shiftin',
                            username: record.data.username
                        },
                        callback: function(opt, success, response) {
                            wait.close();
                            var text = Ext.String.trim(response.responseText);
                            if(text == '1'){
                                showInfoMsg("移入成功！");
                                var store = grid.getStore();
                                store.removeAll();
                                store.loadPage(1);
                            }else if(text == '-1'){
                                showWarningMsg("移入失败，请重试~");
                            }else{
                                showWarningMsg(text);
                            }
                        }
                    });
                }
            },{
                icon: '/images/black_list.png',
                tooltip: '移出白名单',
                handler: function(grid, rowIndex, colIndex){
                    var record = grid.getStore().getAt(rowIndex);
                    if(record.data.whitelist == 'false'){
                        showWarningMsg("该账号已移出白名单");
                        return;
                    }
                    var action = confirm("确定要将用户移出白名单？");
                    if(action == true){
                        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
                        Ext.Ajax.request({
                            method: 'POST',
                            url: handlerurl,
                            params: {
                                action: 'remove',
                                username: record.data.username
                            },
                            callback: function(opt, success, response) {
                                wait.close();
                                var text = Ext.String.trim(response.responseText);
                                if(text == '1'){
                                    showInfoMsg("移出成功！");
                                    var store = grid.getStore();
                                    store.removeAll();
                                    store.loadPage(1);
                                }else if(text == '-1'){
                                    showWarningMsg("移出失败，请重试~");
                                }else{
                                    showWarningMsg(text);
                                }
                            }
                        });
                    }
                }
            },{
                icon: '/images/delete.png',
                tooltip: '删除',
                handler: function(grid, rowIndex, colIndex){
                    var record = grid.getStore().getAt(rowIndex);
                    var action = confirm("确定要删除用户？");
                    if(action == true){
                        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
                        Ext.Ajax.request({
                            method: 'POST',
                            url: handlerurl,
                            params: {
                                action: 'del',
                                username: record.data.username
                            },
                            callback: function(opt, success, response) {
                                wait.close();
                                var text = Ext.String.trim(response.responseText);
                                if(text == '1'){
                                    showInfoMsg("删除成功！");
                                    grid.getStore().loadPage(1);
                                }else if(text == '-1'){
                                    showWarningMsg("删除失败，请重试~");
                                }else{
                                    showWarningMsg(text);
                                }
                            }
                        });
                    }
                    
                }
            }]
        }],
        dockedItems: [{
            xtype: 'container',
            dock: 'bottom',
            layout: 'hbox',
            items: [{
                xtype: 'pagingtoolbar',
                store: users_store,
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
                //width: document.body.clientWidth*0.67 + document.body.clientWidth*0.078,//如果要打开下载全部用户，则减去后面一部分宽度
                width: document.body.clientWidth*0.67,//如果要打开下载全部用户，则减去后面一部分宽度
                height: 32
            },{
                xtype: 'panel',
                width: document.body.clientWidth*0.078,
                height: 32,
                html:    '<form enctype="multipart/form-data" method="post" action="/cgi-bin/sslvpn_users_management.cgi">'+
                        '<input class="submitbutton" type="submit" name="ACTION" value="下载全部用户" style="height:32px;width:100%;">'+
                        '</form>'
            }]
        }]
    });
    /*用户列表模块*/
    var users_container = Ext.create('Ext.container.Container',{
        height: 532,
        width: document.body.clientWidth*0.948,
        name: 'openvpn_user_top_container',    
        margin: '5 20 20 25',
        renderTo: 'openvpn_users_list',
        layout: 'vbox',
        viewConfig: {
            forceFit:true
        },
        
        items:[{
            xtype: users_toolbar
        },{
            xtype: 'container',
            layout: 'hbox',
        items:[{
                xtype: groups_tree
            },{
                xtype: 'container',
                name: 'openvpn_user_main_container',
                layout: 'vbox',
                items: [{
                        xtype: group_info_panel
                    },{
                        xtype: users_grid
                    }]
            }]
        }]
    });
});
var showWarningMsg =function(msg){
    /*Ext.Msg.show({
        title:'提示',
        msg: msg,
        buttons: Ext.Msg.OK,
        icon: Ext.Msg.WARNING,
        width:mesgBoxWidth
    });*/
    alert(msg);
}
var showInfoMsg =function(msg){
    /*Ext.Msg.show({
        title:'提示',
        msg: msg,
        buttons: Ext.Msg.OK,
        icon: Ext.Msg.INFO,
        width:mesgBoxWidth
    });*/
    alert(msg);
}
var slideEdit = function(){
    //修改显示样式
    $('#add-div-header span span').html("编辑用户");
    $('#username').attr('readonly','readonly');
    $('#openvpn_users_submit').attr("value","编辑");
    
    //下拉
    $('#add-div-content').slideDown('1000');
    $('#add-div-header img').attr("src","/images/del.png");
}

var slideEditOrgz = function(){
    //修改显示样式
    $('#add-div-header-orgz span span').html("编辑组织结构");
    $('#orgz_name').attr('readonly','readonly');
    $('#openvpn_users_submit_orgz').attr("value","编辑");
    
    //下拉
    $('#add-div-content-orgz').slideDown('1000');
    $('#add-div-header-orgz img').attr("src","/images/del.png");
}
var slideEditUgrp = function(){
    //修改显示样式
    $('#add-div-header-ugrp span span').html("编辑用户组");
    $('#ugrp_name').attr('readonly','readonly');
    $('#openvpn_users_submit_ugrp').attr("value","编辑");
    
    //下拉
    $('#add-div-content-ugrp').slideDown('1000');
    $('#add-div-header-ugrp img').attr("src","/images/del.png");
}

var addContentOrgz = function(data){
    document.getElementById("orgz_name").value = data.text;
    document.getElementById("orgz_description").value = data.desc;
    var name = data.full_name.split("/");
    var names = new Array();
    var i = 0;
    for(i = 0; i < name.length - 1; i++){
        names.push(name[i]);
    }
    var belong_to = names.join("/");
    document.getElementById("orgz_belong_to").value = belong_to;
    var enable = true;
    if(data.state == "off"){
        enable = false;
    }
    document.getElementById("orgz_enable").checked = enable;
}
var addContentUgrp = function(data){
    document.getElementById("ugrp_name").value = data.text;
    document.getElementById("ugrp_description").value = data.desc;
    document.getElementById("related_resource").value = data.res;
    var name = data.full_name.split("/");
    var names = new Array();
    var i = 0;
    for(i = 0; i < name.length - 1; i++){
        names.push(name[i]);
    }
    var belong_to = names.join("/");
    document.getElementById("ugrp_belong_to").value = belong_to;
    var enable = true;
    if(data.state == "off"){
        enable = false;
    }
    document.getElementById("ugrp_enable").checked = enable;
}

var addContent = function(data){
    document.getElementById("username").value = data.username;
    document.getElementById("password").value = "_NOTCHANGED_";
    document.getElementById("password2").value = "_NOTCHANGED_";
    
    document.getElementById("user_cert").value = data.user_cert;
    change_cert_type();
    if(data.user_cert == 'input'){
        document.getElementById("cert_sn").value = data.user_cert_value;
    }
    
    document.getElementById("comments").value = data.comments;
    document.getElementById("group_infos").innerHTML = "";
    var group_infos = new Array(); 
    group_infos = data.group_info.split(":");
    var i = 0;
    for(i=0;i<group_infos.length;i++ ){
        createInputWithValue('group_infos','group_info',group_infos[i]);
    }
    if(data.whitelist == 'true'){
        document.getElementById("whitelist").checked = true;
    }else{
        document.getElementById("whitelist").checked = false;
    }
    
    if(data.static_ip == ''){
        document.getElementsByName("addresschoose").item(0).checked = true;
        address_choose();
    }else{    
        document.getElementsByName("addresschoose").item(1).checked = true;
        address_choose();
        document.getElementById("ipaddress").value = data.static_ip;
    }
    
    var explicitroutes = data.explicitroutes.split(",");
    var myexplicitroutes = explicitroutes.join('\n');
    document.getElementById("explicitroutes").value = myexplicitroutes;
    
    if(data.push_custom_dns == 'true'){
        document.getElementById("push_custom_dns").checked = true;
    }else{
        document.getElementById("push_custom_dns").checked = false;
    }
    start_dns();
    document.getElementById("firstdns").value = data.firstdns;
    document.getElementById("seconddns").value = data.seconddns;
    
    if(data.push_custom_domain == 'true'){
        document.getElementById("push_custom_domain").checked = true;
    }else{
        document.getElementById("push_custom_domain").checked = false;
    }
    
    document.getElementById("custom_domain").value = data.custom_domain;
    
    if(data.setred == 'true'){
        document.getElementById("setred").checked = true;
    }else{
        document.getElementById("setred").checked = false;
    }
    
    var remotenets = data.remotenets.split(",");
    var myremotenets = remotenets.join('\n');
    document.getElementById("remotenets").value = myremotenets;
    
    if(data.user_enabled == 'true'){
        document.getElementById("user_enabled").checked = true;
    }else{
        document.getElementById("user_enabled").checked = false;
    }
}



var EidtOrgzOrUgrp = function(data, type, operation, msg){
    full_name = data.full_name;
    description = data.desc;
    related_resource = data.res;
    state = data.state;
    
    var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
    Ext.Ajax.request({
        method: 'POST',
        url: aedurl,
        params: {
            action: operation,
            type: type,
            full_name: full_name,
            description: description,
            related_resource:related_resource,
            state: state
        },
        callback: function(opt, success, response) {
            wait.close();
            var text = Ext.String.trim(response.responseText);
            if(text == '1'){
                showInfoMsg(msg+'成功！');
                //清空表单内容
                emptyContentOrgz();
                //上拉添加菜单菜单
                cancelAddOrEditOrgz();
                //刷新组织结构面板
                Ext.getCmp('openvpn_users_tree').getStore().load();
                //将面板信息置空
                var panel = Ext.getCmp('group_descri_panel')
                var group_descri_label = panel.down('displayfield[name=group_descri_label]');
                //var group_info_label = panel.down('displayfield[name=group_info_label]');
                group_descri_label.setValue("未选择组...");
                //group_info_label.setValue("未选择组...");
            }else if(text == '-1'){
                showWarningMsg(msg+"失败，请重试~");
            }else{
                showWarningMsg(text);
            }
        }
    });
}



function ViewUgDetail(data, res_data){
    var marginSize = '5 15 0 0';
    Ext.create('Ext.window.Window',{
        title: data.text+'的详情',
        height: 450,
        modal: true,
        width: document.body.clientWidth*0.6,
        padding: 5,
        layout: 'fit',
        data: '',
        items: { 
            xtype: 'form',
            defaultType: 'displayfield',
            bodyPadding: 15,
            autoScroll: true,
            items:[{
                fieldLabel: '用户组名称',
                margin: marginSize,
                value: data.text
            },{
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
            },*/
            {
                fieldLabel: '关联资源',
                margin: marginSize,
                value: data.res,
                renderer: function(res){
                    var choosedRes = res.split(",");
                    var display = "<table class='ruleslist' width='96%'>";
                    display = display + '<tr><td class="boldbase" width="15%">名称</td><td class="boldbase" width="50%">描述</td><td class="boldbase" width="12%">访问方式</td><td class="boldbase"  width="23%">IP地址</td></tr>';
                    var hasContentFlag = 0;
                    for(var i = 0; i < choosedRes.length; i++){
                        for(var j = 0; j < res_data.total; j++){
                            var item = res_data.resources[j];
                            if(choosedRes[i] == res_data.resources[j].name){
                                display = display + "<tr>";
                                display = display + "<td>" + item.name + "</td>";
                                display = display + "<td>" + item.desc + "</td>";
                                var amethod = "WEB访问";
                                if(item.am != 'web'){
                                    amethod = "其他访问";
                                }
                                display = display + "<td>" + amethod + "</td>";
                                display = display + "<td>" + item.ip + "</td>";
                                display = display + "</tr>";
                                hasContentFlag++;
                            }
                        }
                    }
                    if(hasContentFlag == 0){
                        display = display + '<tr class="env table_note fordel"><td colspan="4"><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
                    }
                    display = display + "</table>";
                    return display;
                }
            }]
        },
        buttons: [{
            text:"确定",
            handler: function(me){
                me.up('window').close();
            }
        }]
    }).show();
}

function ViewUserDetail(data, userResourceDetails){
    var innerWidth = document.body.clientWidth*0.6;
    var outerWidth = document.body.clientWidth*0.61;
    var windowHeight = 500;
    var userDataHeight = 150;
    var resourceDataHeight = 283;
    var userDataForm = Ext.create('Ext.form.Panel', {
        height: userDataHeight,
        width: innerWidth,
        bodyPadding: '5 15',
        layout: {
            type: 'table',
            columns: 2
        },
        defaultType: 'displayfield',
        items: [{
            fieldLabel: '用户名',
            value: data.username
        },{
            fieldLabel: '备注',
            value: data.comments
        },{
            fieldLabel: '用户证书',
            value: data.user_cert_value
        },{
            fieldLabel: '地址分配',
            value: data.static_ip
        },{
            fieldLabel: '本地子网',
            value: data.explicitroutes
        },{
            fieldLabel: '首选DNS',
            value: data.firstdns
        },{
            fieldLabel: '备选DNS',
            value: data.seconddns
        },
        {
            fieldLabel: '加入域',
            value: data.custom_domain
        },{
            fieldLabel: '默认网关',
            value: data.setred,
            renderer: function(val){
                if(val == 'true'){
                    return "开启";
                }else{
                    return "未设置";
                }
            }
        },{
            fieldLabel: '是否启用',
            value: data.user_enabled,
            renderer: function(val){
                if(val == 'true'){
                    return '<font color = "' + enable_color + '">启用状态</font>'
                }else{
                    return '<font color = "' + disable_color+ '">禁用状态</font>';
                }
            }
        },{
            fieldLabel: '白名单状态',
            value: data.whitelist,
            renderer: function(val){
                if(val == 'true'){
                    return '<font color = "' + enable_color + '">已移入</font>'
                }else{
                    return '<font color = "' + disable_color+ '">已移出</font>';
                }
            }
        }]
    });
    var resourceInfoForm = Ext.create('Ext.form.Panel', {
        height: resourceDataHeight,
        width: innerWidth,
        autoScroll : true,
        defaultType: 'displayfield',
        bodyPadding: '5 15',
        layout: 'anchor',
        items: [{
            fieldLabel: '关联资源',
            value: '',
            renderer: function(val){
                return renderResourceTable(userResourceDetails);
            }
        }]
    });
    Ext.create('Ext.window.Window',{
        title: data.username+'的详情',
        height: windowHeight,
        modal: true,
        width: outerWidth,
        autoScroll: false,
        layout: 'anchor',
        items:[{
            xtype: userDataForm
            
        },{
            xtype: resourceInfoForm
            
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

function renderResourceTable(userResourceDetails){
    var display = "<table class='ruleslist'>";
    display = display + '<tr><td class="boldbase">所属用户组</td><td class="boldbase" width="25%">资源名称</td><td class="boldbase" width="13%">访问方式</td><td class="boldbase" width="21%">IP地址</td><td class="boldbase" width="13%">启用状态</td></tr>';
    var hasContentFlag = 0;
    for(var i = 0; i < userResourceDetails.length; i++){
        var ugFullName = userResourceDetails[i][0];
        var reourseInfo = userResourceDetails[i][1][0];
        var rowspan = userResourceDetails[i][1].length;
        if(rowspan > 0){
            //当资源有的时候显示资源
            display = display + "<tr>";
            display = display + "<td class='add-div-type' rowspan='" + rowspan + "'>" + ugFullName + "</td>";
            display = display + "<td>" + reourseInfo.name + "</td>";
            //display = display + "<td>" + reourseInfo.desc + "</td>";
            var acessMethod = "WEB访问";
            if(reourseInfo.am != 'web'){
                acessMethod = "其他访问";
            }
            display = display + "<td>" + acessMethod + "</td>";
            display = display + "<td>" + reourseInfo.ip + "</td>";
            var state = '<font color="' + enable_color + '">启用状态</font>';
            if(reourseInfo.state != 'on'){
                state = '<font color="' + disable_color + '">禁用状态</font>';
            }
            display = display + "<td>" + state + "</td>";
            display = display + "</tr>";
            hasContentFlag++;
            for(var j = 1; j < rowspan; j++){
                reourseInfo = userResourceDetails[i][1][j];
                display = display + "<tr >";
                display = display + "<td>" + reourseInfo.name + "</td>";
                //display = display + "<td>" + reourseInfo.desc + "</td>";
                acessMethod = "WEB访问";
                if(reourseInfo.am != 'web'){
                    acessMethod = "其他访问";
                }
                display = display + "<td>" + acessMethod + "</td>";
                display = display + "<td>" + reourseInfo.ip + "</td>";
                state = '<font color="' + enable_color + '">启用状态</font>';
                if(reourseInfo.state != 'on'){
                    state = '<font color="' + disable_color + '">禁用状态</font>';
                }
                display = display + "<td>" + state + "</td>";
                display = display + "</tr>";
                hasContentFlag++;
            }
        }else{
            //否则创建一个空行以显示用户组
            display = display + "<tr>";
            display = display + "<td class='add-div-type'>" + ugFullName + "</td>";
            display = display + "<td colspan='4' style='text-align:center;color:#CBC6C6;'>-  -  -  -  -  无内容  -  -  -  -  -</td>";
            display = display + "</tr>";
        }
    }
    /*if(hasContentFlag == 0){
        display = display + '<tr class="env table_note fordel"><td colspan="4"><div><img src="/images/pop_warn_min.png">无内容</div></td></tr>';
    }*/
    display = display + "</table>";
    return display;
}

/*根据用户组名字，用户组json数据和资源json数据，返回资源数组*/
function getUserResourceDetails(userGroupInfo, org_info, res_data){
    var userResourceDetails = new Array();//一个二维数组
    for(var i = 0; i < userGroupInfo.length; i++){
        userResourceDetails[i] = new Array();
        var userGroup = userGroupInfo[i];
        var choosedRes = getResourceNames(userGroup, org_info);//返回的是所包含资源的数组
        var resourceDetails = getResourceDetails(choosedRes, res_data);
        userResourceDetails[i].push(userGroup);
        userResourceDetails[i].push(resourceDetails);
    }
    return userResourceDetails;
}

/*根据用户组全路径名称，返回用户组所包含的资源的名称集合(数组)*/
function getResourceNames(userGroup, org_info){    
    var ret = "";
    for(var i = 0; i < org_info.childNodes.length; i++){
        var data = org_info.childNodes[i].data
        if(data.type == "ug"){  
            if(data.full_name == userGroup){
                ret = data.res;
                break;
            }     
        }else if(data.type == "org"){
            ret = getResourceNames(userGroup, org_info.childNodes[i]);
            if(ret != ""){
                break;
            }
        }
    }
    return ret;
}

/*根据资源的名称集合(数组),返回资源详细信息集合(数组)*/
function getResourceDetails(choosedRes, res_data){
    var resourceDetails = new Array();
    for(var i = 0; i < choosedRes.length; i++){
        for(var j = 0; j < res_data.total; j++){
            var item = res_data.resources[j];
            if(choosedRes[i] == item.name){
                resourceDetails.push(item);
            }
        }
    }
    return resourceDetails;
}
