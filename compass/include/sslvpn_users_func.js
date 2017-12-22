function user_certificate(){
   var obj1 = document.getElementById("up_file");
   var obj2 = document.getElementById("serial_num");
   var elems = document.getElementsByName("certificate");
   var value;
   for(var i=0;i<elems.length;i++)
   {
       if(elems.item(i).checked)
       {
          value = elems.item(i).getAttribute("value");
       }
   }
   if(value=="upload")
   {
      obj1.style.display = "block";
      obj2.style.display = "none";
   }
   if(value=="enter")
   {
      obj1.style.display = "none";
      obj2.style.display = "block";
   }
   if(value=="not")
   {
      obj1.style.display = "none";
      obj2.style.display = "none";
   }
}

function createInputWithValue(parentID,inputTextID,inputValue){  
    var parent=document.getElementById(parentID);//获取父元素
     
    var div=document.createElement("div");//创建一个div容器用于包含input
    var x=parseInt(Math.random()*(1000-1))+1;
    var y=parseInt(Math.random()*(1000-1))+1;
    var divName=inputTextID+x.toString();//随机div容器的名称
    div.id=divName;
    div.className="multi_line";
     
    var  aElement=document.createElement("input"); //创建input
    aElement.name=inputTextID;
    aElement.id=inputTextID+y.toString();
    aElement.type="text";//设置类型为text
    aElement.style.width ="400px";
    aElement.value =inputValue;
    aElement.readOnly="true";
    aElement.onclick=function(){createTreeWindow(inputTextID+y.toString());};//为input设置onclick方法
     
    var delBtn=document.createElement("img");//再创建一个用于删除input file的Button
    delBtn.className="appendimage";
    delBtn.src="/images/del16x16.png";
    delBtn.onclick=function(){ removeInput(parentID,divName)};//为image设置onclick方法
     
    div.appendChild(aElement);//将input text加入div容器
    div.appendChild(delBtn);//将删除按钮加入div容器
    parent.appendChild(div);//将div容器加入父元素
}

function createInput(parentID,inputTextID){  
    var parent=document.getElementById(parentID);//获取父元素
     
    var div=document.createElement("div");//创建一个div容器用于包含input
    var x=parseInt(Math.random()*(1000-1))+1;
    var y=parseInt(Math.random()*(1000-1))+1;
    var divName=inputTextID+x.toString();//随机div容器的名称
    div.id=divName;
    div.className="multi_line";
     
    var  aElement=document.createElement("input"); //创建input
    aElement.name=inputTextID;
    aElement.id=inputTextID+y.toString();
    aElement.type="text";//设置类型为text
    aElement.style.width ="400px";
    aElement.readOnly="true";
    aElement.onclick=function(){createTreeWindow(inputTextID+y.toString());};//为input设置onclick方法
     
    var delBtn=document.createElement("img");//再创建一个用于删除input file的Button
    delBtn.className="appendimage";
    delBtn.src="/images/del16x16.png";
    delBtn.onclick=function(){ removeInput(parentID,divName)};//为image设置onclick方法
     
    div.appendChild(aElement);//将input text加入div容器
    div.appendChild(delBtn);//将删除按钮加入div容器
    parent.appendChild(div);//将div容器加入父元素
}
//==============================================+
//功能:删除一个包含input text的div 容器            |
//参数:parentID---input text控件的父元素ID        |
//     DelDivID---包含input text的div 容器ID    |
//==============================================+
function removeInput(parentID,DelDivID){
    var parent=document.getElementById(parentID);
    parent.removeChild(document.getElementById(DelDivID));
}
//==============================================+
//功能:向一个intput text的value填值                |
//参数:elementID---该input元素ID                |
//==============================================+
function addValueTo(elementID){
    var inputElement = document.getElementById(elementID);
    inputElement.value = "所有用户";
}

function createResTreeWindow(inputID){
    var orgz_store = Ext.create('Ext.data.TreeStore', {
        model: 'OpenvpnResGroup',
        id: 'openvpnresgrouptreestore',
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/sslvpn_users_restree.cgi',
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
        }],
        listeners: {
            beforeload: function(store){
                var related_resource = document.getElementById('related_resource').value;
                var params ={
                    related_resource: related_resource
                };
                Ext.apply(store.proxy.extraParams, params);
            }
        }
    });
    
    var orgz_tree = Ext.getCmp('openvpnresgrouptreepanel');
    if(!orgz_tree){
        orgz_tree = Ext.create('Ext.tree.Panel', {
            //width: 200,
            id: 'openvpnresgrouptreepanel',
            closeAction: 'hide',
            width: document.body.clientWidth*0.37,
            height: 480,
            rootVisible: true,
            root: {
                text: '所有资源',
                id: 'res_all',
                desc: '',
                expanded: true,
                checked:false
            },
            store: orgz_store,
            listeners: {
                checkchange:function(node,checked){
                    if(checked){
                        node.eachChild(function (child) { 
                            chd(child,true);
                        });
                    }else{
                        node.eachChild(function (child) {
                            chd(child,false);
                        });
                    }
                    //进行父级选中操作
                    parentnode(node); 
                },
                afterrender:function(me){
                    
                }
            }
        });
    }
    
    var orgz_tree_window = Ext.getCmp('openvpnresgroupwindow');
    if(!orgz_tree_window){
        orgz_tree_window = Ext.create('Ext.window.Window', {
            title: '选择资源',
            id: 'openvpnresgroupwindow',
            closeAction: 'hide',
            height: 500,
            modal: true,
            width: document.body.clientWidth*0.37,
            layout: 'fit',
            data: '',
            items: { 
                xtype: orgz_tree
            },
            buttons:[
                {
                    text: '确定',
                    handler: function(me){
                        var nodes = me.up('window').down('treepanel').getChecked();
                        var str = "";
                        var i = 0;
                        var array = new Array();
                        for( i = 0; i < nodes.length; i++ ){
                            if(nodes[i].data.type == "res"){
                                array.push(nodes[i].data.text);
                            }
                        }
                        str = array.join(',');
                        var element = document.getElementById(inputID);
                        element.value = str;
                        me.up('window').close();
                    }
                },{
                    text: '取消',
                    handler: function(me){
                        me.up('window').close();
                    }
                }
            ]
        })
    }
    orgz_tree_window.show();
    
}

function createTreeWindow(inputID){
    //如果是用户组或者组织结构的编辑状态，则直接返回
    if(inputID == "orgz_belong_to"){
        if(document.getElementById("openvpn_users_submit_orgz").value == "编辑"){
            return;
        }
    }
    if(inputID == "ugrp_belong_to"){
        if(document.getElementById("openvpn_users_submit_ugrp").value == "编辑"){
            return;
        }
    }
    var groups_store = Ext.create('Ext.data.TreeStore', {
        model: 'OpenvpnuserGroup',
        proxy: {
            type: 'ajax',
            url: '/cgi-bin/sslvpn_users_tree.cgi',
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

    var groups_tree = Ext.create('Ext.tree.Panel', {
        //width: 200,
        width: document.body.clientWidth*0.37,
        height: 480,
        rootVisible: true,
        root: {
            text: '所有用户',
            id: '所有用户',
            full_name: '所有用户',
            type: 'org',
            desc: '这是根组织结构',
            expanded: true
        },
        store: groups_store,
        listeners: {
            itemclick: function(view, record, item, index, e, eOpts){
                var window = view.up('window');
                window.full_name = record.data.full_name;
                window.group_type = record.data.type;
            }
        }
    });
    
    Ext.create('Ext.window.Window', {
        title: '选择用户组',
        height: 500,
        modal: true,
        width: document.body.clientWidth*0.37,
        layout: 'fit',
        full_name: '',
        group_type: '',
        items: { 
            xtype: groups_tree
        },
        buttons:[{
            text: '确定',
            handler: function(me){
                var group_full_name = me.up('window').full_name;
                var group_type = me.up('window').group_type;
                var reg = /group_info/;
                var orgz_reg = /orgz_belong_to/;
                var ugrp_reg = /ugrp_belong_to/;
                var upload_reg = /upload_group_info/;
                if(reg.test(inputID) || upload_reg.test(inputID)){
                    if(group_full_name == ''){
                        showWarningMsg("请选择用户组");
                    }else{
                        if(group_type != 'ug'){
                            showWarningMsg("用户只能添加在用户组下，不能添加在组织结构下，请重新选择~");
                        }else{
                            var element = document.getElementById(inputID);
                            element.value = group_full_name;
                            me.up('window').close();
                        }
                    }
                }else if(orgz_reg.test(inputID)){
                    if(group_full_name == ''){
                        showWarningMsg("请选择组织结构");
                    }else{
                        if(group_type != 'org'){
                            showWarningMsg("组织结构只能添加在组织结构下，不能添加在用户组下，请重新选择~");
                        }else{
                            var element = document.getElementById(inputID);
                            element.value = group_full_name;
                            me.up('window').close();
                        }
                    }
                }else if(ugrp_reg.test(inputID)){
                    if(group_full_name == ''){
                        showWarningMsg("请选择组织结构");
                    }else{
                        if(group_type != 'org'){
                            showWarningMsg("用户组只能添加在组织结构下，不能添加在用户组下，请重新选择~");
                        }else{
                            var element = document.getElementById(inputID);
                            element.value = group_full_name;
                            me.up('window').close();
                        }
                    }
                }
                
            }
        },{
            text: '取消',
            handler: function(me){
                me.up('window').close();
            }
        }]
    }).show();
}

function address_choose(){
    var obj = document.getElementById("ipaddress_text");
    var elems = document.getElementsByName("addresschoose");
    var ipaddress_label = document.getElementById("ipaddress_label");
    var replaceHTML = '<input type="text" name="static_ip" id="ipaddress" value="" style="float:left;vertical-align:middle;width:100px;display:block;"/>';  
    var value;
    for(var i=0;i<elems.length;i++)
    {
        if(elems.item(i).checked)
        {
            value = elems.item(i).getAttribute("value");
        }
    }
   if(value=="autoset")
   {
        ipaddress_label.innerHTML = "";
        obj.style.display="none";
   } else if(value=="byhand"){
        ipaddress_label.innerHTML = replaceHTML;
        obj.style.display="block";
        /*移除移入html元素后，表单检测会失效，要重新加载一次检测*/
        check._main(object);
   }
}
function start_dns() {
   var obj = document.getElementById("push_custom_dns");
   var obj1 = document.getElementById("first_dns_display");
   var obj2 = document.getElementById("second_dns_display");
   if(obj.checked)
   {
     obj1.style.display="block";  
     obj2.style.display="block";  
   } else {
     obj1.style.display="none";
     obj2.style.display="none";
   }
}
function add_domain(){
   var obj = document.getElementById("adddomain");
   var obj1 = document.getElementById("adddomain_add");
   if(obj.checked)
   {
     obj1.style.display="block";  
   } else {
     obj1.style.display="none";
   }
}

function change_cert_type() {
    var cert_type = document.getElementById("user_cert");
    var user_cert_file = document.getElementById("user_cert_file");
    var cert_file_value = document.getElementById("cert_file_value");
    var user_cert_input = document.getElementById("user_cert_input");
    var user_cert_hidden = document.getElementById("user_cert_hidden");
    
    if (cert_type.value == "upload") {
        user_cert_file.style.display = "inline";
        user_cert_input.style.display = "none";
        user_cert_hidden.style.display = "none";
    }
    else if(cert_type.value == "input"){
        user_cert_file.style.display = "none";
        user_cert_input.style.display = "inline";
        user_cert_hidden.style.display = "none";
    }else{
        user_cert_file.style.display = "none";
        user_cert_input.style.display = "none";
        user_cert_hidden.style.display = "inline";
    }
}

function reset_upload() {
    var cert_file = document.getElementById("cert_file");
    var cert_file_value = document.getElementById("cert_file_value");
    var cert_file_reset = document.getElementById("cert_file_reset");
    cert_file.style.display = "inline";
    cert_file_value.style.display = "none";
    cert_file_value.value = "";
    cert_file_reset.style.display = "none";
}

function cert_upload(){
    $.ajaxFileUpload
    (
        {
            url:'/cgi-bin/sslvpn_users_certupload.cgi',
            secureuri:false,
            fileElementId:'cert_file',
            dataType: 'json',
            success: function (data)
            {
                status = data.status;
                sn = data.sn;
                if(status != "1"){
                    check._main(object);
                    alert(status);
                }else{
                    var cert_file = document.getElementById('cert_file');
                    var cert_file_value = document.getElementById('cert_file_value');
                    var cert_file_reset = document.getElementById('cert_file_reset');
                    cert_file.style.display = "none"
                    cert_file_value.value = sn;
                    cert_file_value.style.display = "inline";
                    cert_file_reset.style.display = "inline";
                }
            }, 
            error: function (data)//服务器响应失败处理函数
            {
                alert("error");
            }
        }
    );
}

function error_read(){
    $('#add-div-header-rightspan-upload img').attr('src','/images/read_note.png');
}