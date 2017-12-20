/**author:刘炬隆（liujulong）
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
            alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//控制最后一列显示与否
function change_show_ftp(){
    if($("#FTP_LIST").attr("checked")){
        $(".ctr_ftp").show();
    }else{
        $(".ctr_ftp").hide();
    }
}
//检查启用病毒是否可用
function check_havp(){
    var sending_data = {
        ACTION: 'judge_havp'
    };
    function ondatareceived(data) {
        if(data.status == "1"){
            $("#AV_ENABLED").attr("disabled",true);
            $("#AV_ENABLED").attr("checked",false);
            $("#label_tip").html("（病毒库未激活，该功能无法使用。请先激活！）");
        }else if(data.status == "2"){
            $("#AV_ENABLED").attr("disabled",true);
            $("#AV_ENABLED").attr("checked",false);
            $("#label_tip").html("（病毒库未激活，该功能无法使用。请先激活！）");
        }
    }
    do_request( sending_data, ondatareceived );
}