/**author:����¡��liujulong��
date:2015/04/07
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'FTP_FILTER_FORM',
   'option':{
        'white_list':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        },
        'black_list':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                
            }
        }
    }
}
var paging_holder = {
    url: "/cgi-bin/filter_ftp.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
    change_show_ftp();
    check_havp();
});
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
//�������һ����ʾ���
function change_show_ftp(){
    if($("#FTP_LIST").attr("checked")){
        $(".ctr_ftp").show();
    }else{
        $(".ctr_ftp").hide();
    }
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