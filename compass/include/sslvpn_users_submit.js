Ext.onReady(function() {

    check._main(object);
    check._main(object_orgz);
    check._main(object_ugrp);
    check._main(object_upload);
    //check._get_form_obj_table("USER_FORM_NEW");
    
    $('#add-div-header-orgz').click(function(){
        if($('#add-div-content-orgz').css('display')=='none')
        {
            $('#add-div-content-orgz').slideDown('1000');
            $('#add-div-header-orgz img').attr('src','/images/del.png');
        }else{
            $('#add-div-content-orgz').slideUp('1000');
            $('#add-div-header-orgz img').attr('src','/images/add.png');
        }
    });
    
    $('#add-div-header-ugrp').click(function(){
        if($('#add-div-content-ugrp').css('display')=='none')
        {
            $('#add-div-content-ugrp').slideDown('1000');
            $('#add-div-header-ugrp img').attr('src','/images/del.png');
        }else{
            $('#add-div-content-ugrp').slideUp('1000');
            $('#add-div-header-ugrp img').attr('src','/images/add.png');
        }
    });
    
    $('#add-div-header-upload').click(function(){
        if($('#add-div-content-upload').css('display')=='none')
        {
            $('#add-div-content-upload').slideDown('1000');
            $('#add-div-header-leftspan-upload img').attr('src','/images/del.png');
        }else{
            $('#add-div-content-upload').slideUp('1000');
            $('#add-div-header-leftspan-upload img').attr('src','/images/add.png');
        }
    });
    
    $('#openvpn_users_submit_orgz').click(function(){
        var action = document.getElementById("openvpn_users_submit_orgz").value;
        if(action == "添加"){
            addEidtOrgzOrUgrp("orgz", "add", "添加");
        }else if(action == "编辑"){
            addEidtOrgzOrUgrp("orgz", "edit", "编辑");
        }
    });

    $('#openvpn_users_submit_ugrp').click(function(){
        var action = document.getElementById("openvpn_users_submit_ugrp").value;
        if(action == "添加"){
            addEidtOrgzOrUgrp("ugrp", "add","添加");
        }else if(action == "编辑"){
            addEidtOrgzOrUgrp("ugrp", "edit","编辑");
        }
    });
    
    $('#openvpn_users_submit').click(function(){
        var action = document.getElementById("openvpn_users_submit").value;
        if(action == "添加"){
            addEidt("add","添加");
        }else if(action == "编辑"){
            addEidt("edit","编辑");
        }
    });
    
    
});

var addEidtOrgzOrUgrp = function( type, operation, msg ){

    var full_name;
    var related_resource;
    var description;
    var state;
    var bechecked;
    if(type == 'orgz'){
        var orgz_name = Ext.String.trim(document.getElementById("orgz_name").value);
        var orgz_belong_to = Ext.String.trim(document.getElementById("orgz_belong_to").value);
        full_name = orgz_belong_to + "/" + orgz_name;
        related_resource = "";
        description = Ext.String.trim(document.getElementById("orgz_description").value);
        state = "off";
        if(document.getElementById("orgz_enable").checked){
            state = "on";
        }
        bechecked = object_orgz;
    }else if(type == 'ugrp'){
        var ugrp_name = Ext.String.trim(document.getElementById("ugrp_name").value);
        var ugrp_belong_to = Ext.String.trim(document.getElementById("ugrp_belong_to").value);
        full_name = ugrp_belong_to + "/" + ugrp_name;
        related_resource = Ext.String.trim(document.getElementById("related_resource").value);
        description = Ext.String.trim(document.getElementById("ugrp_description").value);
        state = "off";
        if(document.getElementById("ugrp_enable").checked){
            state = "on";
        }
        bechecked = object_ugrp;
    }

    if(check._submit_check(bechecked,check)){
        showWarningMsg("请填写正确的表单后再提交~");
    }else{
        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
        Ext.Ajax.request({
            method: 'POST',
            url: '/cgi-bin/sslvpn_users_aed.cgi',
            params: {
                action: operation,
                type: type,
                full_name: full_name,
                related_resource: related_resource,
                description: description,
                state: state
            },
            callback: function(opt, success, response) {
                wait.close();
                var text = Ext.String.trim(response.responseText);
                if(text == '1'){
                    showInfoMsg(msg+'成功！');
                    //根据类型不同，清空不同的内容
                    if(type == 'orgz'){
                        //清空表单内容
                        //emptyContentOrgz();
                        //上拉添加菜单菜单
                        cancelAddOrEditOrgz();
                    }else if(type == 'ugrp'){
                        //清空表单内容
                        //emptyContentUgrp();
                        //上拉添加菜单菜单
                        cancelAddOrEditUgrp();

                    }
                    //销毁资源选择窗口,以利于下次选择时重置选择
                    if(Ext.getCmp('openvpnresgroupwindow')){
                        Ext.getCmp('openvpnresgroupwindow').destroy();
                    }
                    //刷新组织结构面板
                    Ext.getCmp('openvpn_users_tree').getStore().load();
                }else if(text == '-1'){
                    showWarningMsg(msg+"失败，请重试~");
                }else{
                    showWarningMsg(text);
                }
            }
        });
    }
}

var addEidt = function(operation, msg){

    var username = Ext.String.trim(document.getElementById("username").value);
    var password = Ext.String.trim(document.getElementById("password").value);
    var password2 = Ext.String.trim(document.getElementById("password2").value);
    
    var user_cert = Ext.String.trim(document.getElementById("user_cert").value);
    var user_cert_value = "";
    if(user_cert == "upload"){
        user_cert_value = Ext.String.trim(document.getElementById("cert_file_value").value);
    }else if(user_cert == "input"){
        user_cert_value = Ext.String.trim(document.getElementById("cert_sn").value);
    }
    
    var comments = Ext.String.trim(document.getElementById("comments").value);
    
    //针对取得的数组，可能没有项目，也可能存在有空项目，也可能有重复项目，要进行处理
    var group_info_inputs = document.getElementsByName("group_info");
    var group_info_array = RmDuplicate(group_info_inputs);
    var group_info = group_info_array.join(":");
    
    var whitelist = document.getElementById("whitelist").checked;
    
    var addresschoose_autoset = document.getElementsByName("addresschoose")[0].checked;
    var static_ip = "";
    if(!addresschoose_autoset){
        static_ip = Ext.String.trim(document.getElementById("ipaddress").value);
    }
    
    var explicitroutes = Ext.String.trim(document.getElementById("explicitroutes").value);
    
    
    var push_custom_dns = document.getElementById("push_custom_dns").checked;
    var firstdns = "";
    var seconddns = "";
    if(push_custom_dns){
        firstdns = Ext.String.trim(document.getElementById("firstdns").value);
        seconddns = Ext.String.trim(document.getElementById("seconddns").value);
    }
    
    var push_custom_domain = document.getElementById("push_custom_domain").checked;
    var custom_domain = "";
    if(push_custom_domain){
        custom_domain = Ext.String.trim(document.getElementById("custom_domain").value);
    }
    
    var setred = document.getElementById("setred").checked;
    var remotenets = Ext.String.trim(document.getElementById("remotenets").value);
    var user_enabled = document.getElementById("user_enabled").checked;
    
    
    if(check._submit_check(object,check)){
        showWarningMsg("请填写正确的表单后再提交~");
    }else{
        var wait = Ext.MessageBox.wait("操作正在执行，请稍后...");
        Ext.Ajax.request({
            method: 'POST',
            url: '/cgi-bin/sslvpn_users_handler.cgi',
            params: {
                action: operation,
                username: username,
                password: password,
                password2: password2,
                user_cert: user_cert,
                user_cert_value: user_cert_value,
                comments: comments,
                group_info: group_info,
                whitelist: whitelist,
                static_ip: static_ip,
                explicitroutes: explicitroutes,
                push_custom_dns: push_custom_dns,
                firstdns: firstdns,
                seconddns: seconddns,
                push_custom_domain: push_custom_domain,
                custom_domain: custom_domain,
                setred: setred,
                remotenets: remotenets,
                user_enabled: user_enabled
            },
            callback: function(opt, success, response) {
                wait.close();
                var text = Ext.String.trim(response.responseText);
                if(text == '1'){
                    /*Ext.Msg.show({
                        title:'提示',
                        msg: msg+'用户成功！',
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.INFO,
                        width:200,
                        fn: function(){
                            //清空表单内容
                            emptyContent();
                            //上拉添加菜单菜单
                            cancelAddOrEdit();
                        }
                    });*/
                    showInfoMsg(msg+'用户成功！');
                    //清空表单内容
                    emptyContent();
                    //上拉添加菜单菜单
                    cancelAddOrEdit();
                    
                    //添加用户成功后，清空请求来的数据，以便于用户名重名检测
                    check.users = '';
                    
                    //刷新用户数据
                    var grid = Ext.getCmp('openvpn_users_grid');
                    var store = grid.getStore();
                    store.removeAll();
                    store.loadPage(1);
                }else if(text == '-1'){
                    showWarningMsg(msg+"用户失败，请重试~");
                }else{
                    showWarningMsg(text);
                }
            }
        });
    }

}

var RmDuplicate = function(initialArray){
    //针对取得的数组，可能没有项目，也可能存在有空项目，也可能有重复项目，要进行处理
    var ret = []
    var hash = {}
    var length = initialArray.length;    
    if(length == 0){
        return ret;
    }
    for (var i = 0; i < length; i++) {
        var item = initialArray.item(i).value;
        var key = typeof(item) + item;
        if (hash[key] !== 1) {
            if(item != ""){
                ret.push(item);
            }
            hash[key] = 1;
        }
    }

    return ret
}

var check = new ChinArk_forms();

var emptyContentOrgz = function(){
    document.getElementById("orgz_name").value = "";
    document.getElementById("orgz_description").value = "";
    document.getElementById("orgz_belong_to").value = "";
    document.getElementById("orgz_enable").checked = true;
}

var emptyContentUgrp = function(){
    document.getElementById("ugrp_name").value = "";
    document.getElementById("ugrp_description").value = "";
    document.getElementById("related_resource").value = "";    
    document.getElementById("ugrp_belong_to").value = "";
    document.getElementById("ugrp_enable").checked = true;
    //销毁资源选择窗口,以利于下次选择时重置选择
    if(Ext.getCmp('openvpnresgroupwindow')){
        Ext.getCmp('openvpnresgroupwindow').destroy();
    }
}

var emptyContent = function(){
    document.getElementById("username").value = "";
    document.getElementById("password").value = "";
    document.getElementById("password2").value = "";
    
    document.getElementById("user_cert").value = "none";
    document.getElementById("cert_file").value = "";
    document.getElementById("cert_sn").value = "";
    change_cert_type();
    
    document.getElementById("comments").value = "";
    document.getElementById("group_infos").innerHTML = "";
    document.getElementById("whitelist").checked = true;
    
    document.getElementsByName("addresschoose").item(0).checked = true;
    address_choose();
    
    document.getElementById("explicitroutes").value = "";
    document.getElementById("push_custom_dns").checked = false;
    start_dns();
    
    document.getElementById("push_custom_domain").checked = false;
    document.getElementById("custom_domain").value = "";
    document.getElementById("setred").checked = true;
    document.getElementById("remotenets").value = "";
    document.getElementById("user_enabled").checked = true;
    //check._main(object);
}

var emptyContentUpload = function(){
    document.getElementById("upload_name").value = "";
    document.getElementById("upload_group_info").value = "";
    document.getElementsByName("conflict_policy")[0].checked = true;;
}

var slideAddOrEdit = function(){
    if($('#add-div-content').css('display')=='none')
    {
        $('#add-div-content').slideDown('1000');
        $('#add-div-header img').attr("src","/images/del.png");
    }else{
        $('#add-div-content').slideUp('1000');
        $('#add-div-header img').attr("src","/images/add.png")
    }
}

var slideAddOrEditOrgz = function(){
    if($('#add-div-content-orgz').css('display')=='none')
    {
        $('#add-div-content-orgz').slideDown('1000');
        $('#add-div-header-orgz img').attr("src","/images/del.png");
    }else{
        $('#add-div-content-orgz').slideUp('1000');
        $('#add-div-header-orgz img').attr("src","/images/add.png")
    }
}
var slideAddOrEditUgrp = function(){
    if($('#add-div-content-ugrp').css('display')=='none')
    {
        $('#add-div-content-ugrp').slideDown('1000');
        $('#add-div-header-ugrp img').attr("src","/images/del.png");
    }else{
        $('#add-div-content-ugrp').slideUp('1000');
        $('#add-div-header-ugrp img').attr("src","/images/add.png")
    }
}

var cancelAddOrEditOrgz = function(){
    //上拉
    $('#add-div-content-orgz').slideUp('1000');
    $('#add-div-header-orgz img').attr("src","/images/add.png");
    //清空数据
    emptyContentOrgz();
    //修改显示
    $('#add-div-header-orgz span span').html("添加组织结构");
    $('#orgz_name').attr('readonly',false);
    $('#openvpn_users_submit_orgz').attr("value","添加");
}

var cancelAddOrEditUgrp = function(){
    //上拉
    $('#add-div-content-ugrp').slideUp('1000');
    $('#add-div-header-ugrp img').attr("src","/images/add.png");
    //清空数据
    emptyContentUgrp();
    //修改显示
    $('#add-div-header-ugrp span span').html("添加用户组");
    $('#ugrp_name').attr('readonly',false);
    $('#openvpn_users_submit_ugrp').attr("value","添加");
}

var cancelAddOrEdit = function(){
    //上拉
    $('#add-div-content').slideUp('1000');
    $('#add-div-header img').attr("src","/images/add.png");
    //清空数据
    emptyContent();
    //修改显示
    $('#add-div-header span span').html("添加用户");
    $('#username').attr('readonly',false);
    $('#openvpn_users_submit').attr("value","添加");
}

var cancelAddOrEditUpload = function(){
    //上拉
    $('#add-div-content-upload').slideUp('1000');
    $('#add-div-header-leftspan-upload img').attr("src","/images/add.png");
    //清空数据
    emptyContentUpload();
}

var object_orgz = {
   'form_name':'USER_FORM_ORGZ',
   'option'   :{
        'orgz_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(){
                                           //此处添加你自己的代码吧
            }
        },
        'orgz_belong_to':{
            'type':'text',
            'required':'1',
            'check':'other|',
            'other_reg':'/\.\*/'
        },
        'orgz_description':{
            'type':'textarea',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        }
    }
}

var object_ugrp = {
   'form_name':'USER_FORM_UGRP',
   'option'   :{
        'ugrp_name':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(){
                                           //此处添加你自己的代码吧
            }
        },
        'related_resource':{
            'type':'text',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        },
        'ugrp_belong_to':{
            'type':'text',
            'required':'1',
            'check':'other|',
            'other_reg':'/\.\*/'
        },
        'ugrp_description':{
            'type':'textarea',
            'required':'0',
            'check':'other|',
            'other_reg':'/\.\*/'
        }
    }
}

var object = {
    'form_name':'USER_FORM_NEW',
    'option'   :{
        'username':{
            'type':'text',
            'required':'1',
            'check':'name|',
            'ass_check':function(eve){
                var action = document.getElementById("openvpn_users_submit").value;
                if(action == "编辑"){
                    return;
                }
                var msg="";
                var key = 0;
                var username = eve._getCURElementsByName("username","input","USER_FORM_NEW")[0].value;
                //先检测输入是否合法
                var pattern = /^[a-zA-Z][_a-zA-Z0-9]{3,20}$/;
                if(! pattern.test(username)){
                    msg = "用户名含有非法字符，请输入只包含字母、数字、下划线并以字母开头的用户名";
                    return msg;
                }
                if(!eve.users){
                    $.ajax({
                          type : "get",
                          url : '/cgi-bin/chinark_back_get.cgi',
                          async : false,
                          data : 'path=/var/efw/openvpn/passwd',
                          success : function(data){ 
                            eve.users = data;                                                                     
                          }
                    });
                }
                var exist = eve.users.split('\n');
                for (var i = 0; i < exist.length; i++) {
                    var tmp = exist[i].split(':');
                    if(username == tmp[0]){
                        msg = '用户名'+username+'已存在';
                        break;
                    }
                }
                return msg;
            }
        },
        'password':{
            'type':'password',
            'required':'1',
            'ass_check':function(eve){
                var msg ='';
                var pass1 = eve._getCURElementsByName("password","input","USER_FORM_NEW")[0].value;
                var pattern = /^[a-zA-Z0-9_]{6,16}$/;
                if(!pattern.test(pass1)){
                    msg = "密码只能输入字母数字和下划线";
                }
                return msg;
            }
        },
        'password2':{
            'type':'password',
            'required':'1',
            'ass_check':function(eve){
                var msg ='';
                var pass1 = eve._getCURElementsByName("password","input","USER_FORM_NEW")[0].value;
                var pass2 = eve._getCURElementsByName("password2","input","USER_FORM_NEW")[0].value;
                if (pass1 != pass2){
                    msg = "密码不一致";
                }
                return msg;
            }
        },
        'custom_domain':{
            'type':'text',
            'required':'0',
            'check':'domain_suffix|'
        },
        'main_dns':{
            'type':'text',
            'required':'1',
            'check':'ip|'
        },
        'second_dns':{
            'type':'text',
            'required':'1',
            'check':'ip|'
        },
        'comments':{
            'type':'text',
            'required':'0',
            'check':'other|',
            'other_reg':'!/^$/',
            'ass_check':function(eve){
                var msg = "";
                var str = eve._getCURElementsByName("comments","input","USER_FORM_NEW")[0].value;
                var reg = /[@#\$\%^&*~`]/;
                if(str.length<=20){
                    if(reg.test(str)){msg=str+"含有非法字符！";}
                } else{
                    msg="注释长度应小于等于20个字符！";
                }
              return msg;
            }
        },
        'remotenets':{
            'type':'textarea',
            'required':'0',
            'check':'ip_mask|'
         },
        'explicitroutes':{
            'type':'textarea',
            'required':'0',
            'check':'other|',
            'other_reg':'!/^$/',
            'ass_check':function(eve){
                var msg = ""; 
                var ips = eve._getCURElementsByName("explicitroutes","textarea","USER_FORM_NEW")[0].value;
                var ip = ips.split("\n");
                if(ips.length==1&&ip[0]=='')
                {
                    return msg;
                }
                
                for(var i=0;i<ip.length;i++)
                {
                    msg = '';
                    if(ip[i]!='')
                    {
                        var one_split = ip[i].split("/");
                        var one_ip = one_split[0];
                        var mask = one_split[1];
                        var zero = /^0+/;
                      
                        if (mask < 1 || mask >32 || one_split.length != 2 || zero.test(mask)){
                            msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                            return msg;
                        }
                      
                        var ip_reg = /^([1-9]|[1-9]\d|1\d{2}|2[0-1]\d|22[0-3])(\.(\d|[1-9]\d|1\d{2}|2[0-4]\d|25[0-5])){3}$/;
                        if(!ip_reg.test(one_ip))
                        {
                            msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                            return msg;
                        }
                        var total_str = "";
                        var temp = new Array(); 
                        temp = one_ip.split(".");
                        for (var j = 0;j < 4;j ++){
                            temp[j] = parseInt(temp[j]);
                            temp[j] = eve.formatIP(temp[j]);
                            total_str += temp[j];
                        }
                        var segment = total_str.substring(mask);
                        var all_zero = /^0+$/;
                        if(mask==32||all_zero.test(segment))
                        {
                        } else {
                            msg=ip[i]+" 输入不合法,应是IP/掩码类型！";
                            return msg;
                        }
                    } else {
                        msg = '不能出现空行！';
                        return msg;
                    }
                }
                return msg;
                                 }
        }, 
        'cert_file':{
            'type':'file',
            'required':'1',
            'ass_check':function(eve){
            
            }
        },
        'cert_file_value':{
            'type':'text',
            'required':'1',
            'check':'other|',
            'other_reg':'!/^$/',
            'ass_check':function(eve){
                var msg = ""; 
                var cert_file_value = eve._getCURElementsByName("cert_file_value","input","USER_FORM_NEW")[0].value;
                var sn = cert_file_value.split(":");
                var reg = /^([\dA-Fa-f]{2})$/;
                for (var i = 0; i < sn.length; i++) {
                    if(!reg.test(sn[i])){
                        msg = "证书序列号格式有误";
                        break;
                    }
                }
                return msg;
            }
        },
        'cert_sn':{
            'type':'text',
            'required':'1',
            'check':'other|',
            'other_reg':'!/^$/',
            'ass_check':function(eve){
                var msg = ""; 
                var cert_sn = eve._getCURElementsByName("cert_sn","input","USER_FORM_NEW")[0].value;
                var cert_sn1 = eve._getCURElementsByName("cert_sn","input","USER_FORM_NEW")[0].value;
                var cert_sn2 = eve._getCURElementsByName("cert_sn","input","USER_FORM_NEW")[0].value;
                var right = 0;
                
                var sn = cert_sn.split(":");
                var reg = /^([\dA-Fa-f]{2})$/;
                var i = 0;
                for (var i = 0; i < sn.length; i++) {
                    if(!reg.test(sn[i])){
                        break;
                    }
                }
                if (i == sn.length) 
                    right = 1;
                
                var sn1 = cert_sn1.split(" ");
                var reg1 = /^([\dA-Fa-f]{2})$/;
                var j = 0;
                for (var j = 0; j < sn1.length; j++) {
                    if(!reg1.test(sn1[j])){
                        break;
                    }
                }
                if (j == sn1.length) 
                    right = 1;
                
                var reg2 = /^([\dA-Fa-f]+)$/;
                if (reg2.test(cert_sn2) && cert_sn2.length % 2 == 0)
                    right = 1;
                    
                if (right == 0)
                    msg = "证书序列号格式有误";
                    
                return msg;
            }
        },
        'static_ip':{
            'type':'text',
            'required':'1',
            'check':'ip|',
            'ass_check':function(eve){
                var msg="";
                var ip = eve._getCURElementsByName("static_ip","input","USER_FORM_NEW")[0].value;
                /*if(!eve.subnet){
                    $.ajax({
                        type : "get",
                        url : '/cgi-bin/sslvpn_getnet.cgi',
                        async : false,
                        data : 'path=/var/efw/openvpn/settings"',
                        success : function(data){ 
                            eve.subnet = data; 
                        }
                    });
                }
                
                var subnet = eve.subnet.split("/");
                var net_number = subnet[1];
                var nets = new Array();
                nets = subnet[0].split(".");
                var total_str = "";
                for (i = 0;i < 4;i ++){
                    nets[i] = parseInt(nets[i]);
                    nets[i] = eve.formatIP(nets[i]);
                    total_str += nets[i];
                }
                var netnum = total_str.substr(0,subnet[1]);
             
                nets = new Array();
                nets = ip.split(".");
                total_str = "";
                for (i = 0;i < 4;i ++){
                    nets[i] = parseInt(nets[i]);
                    nets[i] = eve.formatIP(nets[i]);
                    total_str += nets[i];
                }
                var newnet = total_str.substr(0,net_number);
                if(newnet!=netnum)
                {
                    return "IP地址不在已设定的虚拟网段"+eve.subnet+"中！";
                }*/
                
                if(!eve.users){
                    $.ajax({
                          type : "get",
                          url : '/cgi-bin/chinark_back_get.cgi',
                          async : false,
                          data : 'path=/var/efw/openvpn/passwd',
                          success : function(data){ 
                            eve.users = data;                                                                     
                          }
                    });
                }
                var exist = eve.users.split('\n');
                var username = eve._getCURElementsByName("username","input","USER_FORM_NEW")[0].value;
                for (var i = 0; i < exist.length; i++) {
                    var tmp = exist[i].split(':');
                    if(ip == tmp[8]){
                        if(username == tmp[0]){
                            //如果username与之前存的用户名相同，说明是编辑状态，则不检查占用
                        }else{
                            return 'IP地址'+ip+'已被占用';
                        }
                    }
                }
            }
        },
        'custom_dns':{
            'type':'textarea',
            'required':'0',
            'check':'ip|'
        }
    }
}

var object_upload = {
       'form_name':'USER_FORM_UPLOAD',
       'option'   :{
            'upload_name':{
                'type':'file',
                'required':'1'
            },
            'upload_group_info':{
                'type':'text',
                'required':'0',
                'check':'note|'
            }
        }
    }
