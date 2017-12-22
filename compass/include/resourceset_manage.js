Ext.onReady(function() {

    check._main(object_resg);
    check._main(object_resource);
    //check._get_form_obj_table("USER_FORM_RESG");
    
    $('#add-div-header-resg').click(function(){
        slideAddOrEditResg();
    });
    
    $('#resg_submit').click(function(){
        var action = document.getElementById("resg_submit").value;
        if(action == "添加"){
            addEidtResg( "add", "添加");
        }else if(action == "编辑"){
            addEidtResg("edit", "编辑");
        }
    });

    $('#resource_submit').click(function(){
        var action = document.getElementById("resource_submit").value;
        if(action == "添加"){
            addEidtResource("add","添加");
        }else if(action == "编辑"){
            addEidtResource("edit","编辑");
        }
    });
});

var addEidtResg = function(operation, msg ){

    var resg_name = Ext.String.trim(document.getElementById("resg_name").value);
    var resg_description = Ext.String.trim(document.getElementById("resg_description").value);
    var state = "off";
    if(document.getElementById("resg_enable").checked){
        state = "on";
    }

    if(check._submit_check(object_resg,check)){
        showWarningMsg("请填写正确的表单后再提交~");
    }else{
        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
        Ext.Ajax.request({
            method: 'POST',
            url: '/cgi-bin/resourceset_handler.cgi',
            params: {
                action: operation,
                type: 'resg',
                resg_name: resg_name,
                resg_description: resg_description,
                state: state
            },
            callback: function(opt, success, response) {
                wait.close();
                var text = Ext.String.trim(response.responseText);
                if(text == '1'){
                    showInfoMsg(msg+'资源组成功！');
                    //上拉添加菜单
                    cancelAddOrEditResg();
                    //刷新组织结构面板
                    Ext.getCmp('resgroup_tree').getStore().load();
                }else if(text == '-1'){
                    showWarningMsg(msg+"资源组失败，请重试~");
                }else{
                    showWarningMsg(text);
                }
            }
        });
    }
}

var addEidtResource = function(operation, msg){

    var resource_name = Ext.String.trim(document.getElementById("resource_name").value);
    var resource_description = Ext.String.trim(document.getElementById("resource_description").value);
    var access_method = document.getElementById("access_method").value;
    var ip_addr = Ext.String.trim(document.getElementById("ip_addr").value);
    var protocol = document.getElementById("protocol").value;
    var port = Ext.String.trim(document.getElementById("port").value);
    var url_addr = Ext.String.trim(document.getElementById("url_addr").value);
    if(access_method == 'other'){
        url_addr = '';
    }
    var resource_grep = Ext.String.trim(document.getElementById("resource_grep").value);
    var resource_enable = document.getElementById("resource_enable").checked;
    var state = "off";
    if(resource_enable){
        state = "on";
    }
    
    
    if(check._submit_check(object_resource,check)){
        showWarningMsg("请填写正确的表单后再提交~");
    }else{
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
                    showInfoMsg(msg+'资源成功！');
                    //上拉添加菜单菜单
                    cancelAddOrEditResource();
                    
                    //添加成功后，清空请求来的数据，以便于重名检测
                    check.users = '';
                    
                    //刷新数据
                    Ext.getCmp('resources_grid').getStore().load();
                }else if(text == '-1'){
                    showWarningMsg(msg+"资源失败，请重试~");
                }else{
                    showWarningMsg(text);
                }
            }
        });
    }

}

var check = new ChinArk_forms();

var emptyContentResg = function(){
    document.getElementById("resg_name").value = "";
    document.getElementById("resg_description").value = "";
    document.getElementById("resg_enable").checked = true;
}

var emptyContentResource = function(){
    document.getElementById("resource_name").value = "";
    document.getElementById("resource_description").value = "";
    document.getElementById("access_method").value = "web";
    change();
    document.getElementById("ip_addr").value = "";
    document.getElementById("protocol").value = "tcp";
    document.getElementById("port").value = "";
    document.getElementById("url_addr").value = "";    
    document.getElementById("resource_grep").value = "";
    document.getElementById("resource_enable").checked = true;
}

var slideAddOrEditResg = function(){
    if($('#add-div-content-resg').css('display')=='none')
    {
        $('#add-div-content-resg').slideDown('1000');
        $('#add-div-header-resg img').attr("src","/images/del.png");
    }else{
        $('#add-div-content-resg').slideUp('1000');
        $('#add-div-header-resg img').attr("src","/images/add.png")
    }
}

var cancelAddOrEditResg = function(){
    //上拉
    $('#add-div-content-resg').slideUp('1000');
    $('#add-div-header-resg img').attr("src","/images/add.png");
    //清空数据
    emptyContentResg();
    //修改显示
    $('#add-div-header-resg span span').html("添加资源组");
    $('#resg_name').attr('readonly',false);
    $('#resg_submit').attr("value","添加");
}

var cancelAddOrEditResource = function(){
    //上拉
    $('#add-div-content').slideUp('1000');
    $('#add-div-header img').attr("src","/images/add.png");
    //清空数据
    emptyContentResource();
    //修改显示
    $('#add-div-header span span').html("添加资源");
    $('#resource_name').attr('readonly',false);
    $('#resource_submit').attr("value","添加");
}

function change(){
    var obj = document.getElementById("access_method");
    var obj2 = document.getElementById("hreftr");
    if(obj.value=="web")
    {
        obj2.style.display = "table-row";
    }else{
        obj2.style.display = "none";
    }
}

var object_resg = {
    'form_name':'USER_FORM_RESG',
    'option'   :{
        'resg_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(){
                //此处添加自己的代码
            }
        },
        'resg_description':{
            'type':'textarea',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        }
    }
}

var object_resource = {
    'form_name':'USER_FORM_RESOURCE',
    'option'   :{
        'resource_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(){
                //此处添加你自己的代码吧
            }
        },
        'ip_addr':{
            'type':'text',
            'required':'1',
            'check':'ip|'
        },
        'port':{
            'type':'text',
            'required':'1',
            'check':'port|'
        },
        'url_addr':{
            'type':'text',
            'required':'1',
            'check':'url|'
        },
        'resource_grep':{
            'type':'text',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        },
        'resource_description':{
            'type':'textarea',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        }
    }
}

function createTreeWindow(inputID){
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
        rootVisible: false,
        root: {
            text: root_res_group,
            desc: '这是根组织结构',
            expanded: true
        },
        store: resgroup_store,
        listeners: {
            itemclick: function(view, record, item, index, e, eOpts){
                var window = view.up('window');
                window.full_name = record.data.text;
            }
        }
    });
    
    Ext.create('Ext.window.Window', {
        title: '选择资源组',
        height: 500,
        modal: true,
        width: document.body.clientWidth*0.37,
        layout: 'fit',
        full_name: '',
        items: { 
            xtype: resgroup_tree
        },
        buttons:[{
            text: '确定',
            handler: function(me){
                var group_full_name = me.up('window').full_name;
                var element = document.getElementById(inputID);
                element.value = group_full_name;
                me.up('window').close();
                
            }
        },{
            text: '取消',
            handler: function(me){
                me.up('window').close();
            }
        }]
    }).show();
}