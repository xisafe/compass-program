/**author:刘炬隆（liujulong）
date:2014/04/17
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'SOC_LINKAGE_FORM',
   'option':{
        'ip_addr_soc':{
            'type':'text',
            'required':'1',
            'check':'ip|',
        },
        'port_soc':{
            'type':'text',
            'required':'1',
            'check':'port|',
        },
    }
}
var paging_holder = {
    url: "/cgi-bin/idps_soc_linkage.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
    //$(".containter-div").css({"width":"47%","margin-left":"20px","float":"left"});
    load_type();
    load_data();
    //init_data();
});

function load_type(){
    var sending_data = {
        ACTION: "load_type",
    };

    function ondatareceived(data) {
        var data_content = eval("("+data+")");
        document.getElementById("soc_type").options.add(new Option(data_content.soc_name_cn,data_content.soc_name_en));
        for(var i=0;i<data_content.linkage_mode.length;i++){
            document.getElementById("linkage_way_soc").options.add(new Option(data_content.linkage_mode[i].mode_name_cn,data_content.linkage_mode[i].mode_name_en));
        }
       
    }

    do_request(sending_data, ondatareceived);
}

function load_data(){
    var sending_data = {
        ACTION: "load_data",
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        paging_holder.detail_data = data_content.detail_data;
        document.getElementById("ip_addr_soc").value = paging_holder.detail_data[2].IPADDR;
        document.getElementById("port_soc").value = paging_holder.detail_data[3].PORT;
        document.getElementById("protocol").value = paging_holder.detail_data[4].PROTOCOL;
    }

    do_request(sending_data, ondatareceived);
}

function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: paging_holder.url,
        data: sending_data,
        async: false,
        error: function(request){
            show_error_mesg("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}

function load_detail_data(e){
    var policy_name = e.value;
    var whole_data = paging_holder.detail_data;
    var detail_data = [];

    var table = document.getElementById('table_type_list');
    var trs = table.getElementsByTagName('tr');
    for(var i=trs.length-1;i>1;i--){
        table.deleteRow(i);
    }

    var ele = document.getElementById("TEMPLATE_FORM");
    var inputs=document.getElementsByName("added_header_types");
    while(inputs.length>0){
        ele.removeChild(inputs[0]);
    }
    
    for (var i=0;i<whole_data.length;i++){
        if(policy_name == whole_data[i].policy_name){
            detail_data = whole_data[i].detail_data;
        }
    }
    for(var j=0;j<detail_data.length;j++){
        var table = document.getElementById('table_type_list');
        var newRow = table.insertRow(table.rows.length);
        var td1 = newRow.insertCell(-1);
        var td2 = newRow.insertCell(-1);
        var newType = {value:detail_data[j]};
        td2.style.padding="5px";
        td1.innerHTML = '<p name="headers">'+newType.value+'</p>';
        td1.setAttribute('align','center');
        td2.innerHTML = '<input style="padding-left:15px" type="image" class="action-image" src="../images/delete.png" title="删除" value='+newType.value+' onclick="delete_one_row(this);"/>';
        add_input(newType);
    }

}

function init_state(e){
    //debugger;
    var policy_name = e.value;
    var whole_data = paging_holder.detail_data;
    var states = paging_holder.states_all;
    var state_for_checked;
    for (var i=0;i<whole_data.length;i++){
        if(policy_name == whole_data[i].policy_name){
            state_for_checked = states[i];
        }
    }
    if(state_for_checked == "on"){
        document.getElementById("on").checked = true;
    }else{
        document.getElementById("off").checked = true;
    }
}

function init_data(){
    var data = paging_holder.detail_data;
    var temp = {value:data[0].policy_name};
    load_detail_data(temp);
	var policy_name = "P_default";
    var whole_data = paging_holder.detail_data;
    var states = paging_holder.states_all;
    var state_for_checked;
    for (var i=0;i<whole_data.length;i++){
        if(policy_name == whole_data[i].policy_name){
            state_for_checked = states[i];
        }
    }
    if(state_for_checked == "on"){
        document.getElementById("on").checked = true;
    }else{
        document.getElementById("off").checked = true;
    }
}
