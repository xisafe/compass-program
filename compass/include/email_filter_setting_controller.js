/**author:����¡��liujulong��
date:2015/04/07
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'BASIC_WEBFILTER_FORM',
   'option':{
        'BYPASS_SOURCE':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|mac',
            'ass_check':function(eve){
                
            }
        },
        'BYPASS_DESTINATION':{
            'type':'textarea',
            'required':'0',
            'check':'ip|ip_mask|mac',
            'ass_check':function(eve){
                
            }
        }
    }
}
var paging_holder = {
    url: "/cgi-bin/email_filter_setting.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    //check._main(object);
    change_show_bomb();
    change_show_ext();
    check_havp();
});
//�������һ����ʾ���
function change_show_bomb(){
    if($("#GARBAGE_BOMB").attr("checked")){
        $(".ctr_bomb").show();
    }else{
        $(".ctr_bomb").hide();
    }
}
function change_show_ext(){
    if($("#EXT_ENABLED").attr("checked")){
        $(".ctr_ext").show();
    }else{
        $(".ctr_ext").hide();
    }
}
function do_request(sending_data, ondatareceived) {
    $.ajax({
        type: 'POST',
        url: paging_holder.url,
        dataType: "json",
        data: sending_data,
        async: false,
        error: function(request){
            alert("�������,���ֹ��ܿ��ܳ����쳣");
        },
        success: ondatareceived
    });
}
function enable_smtpscan(){
    var sending_data = {
        ACTION: 'enable_smtpscan'
    };
    function ondatareceived(data) {
        
    }
    do_request(sending_data, ondatareceived);
}
//������ò����Ƿ����
function check_havp(){
    var sending_data = {
        ACTION: 'judge_havp'
    };
    function ondatareceived(data) {
        if(data.status == "1"){
            $("#AV_ENABLED").attr("disabled",true);
            $("#AV_ENABLED").attr("checked",false);
            $("#label_tip").html("��������δ����ù����޷�ʹ�á����ȼ����");
        }else if(data.status == "2"){
            $("#AV_ENABLED").attr("disabled",true);
            $("#AV_ENABLED").attr("checked",false);
            $("#label_tip").html("��������δ����ù����޷�ʹ�á����ȼ����");
        }
    }
    do_request( sending_data, ondatareceived );
}