/**author:刘炬隆（liujulong）
date:2015/04/07
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'BWLIST_FORM',
   'option':{
        'sender_whitelist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#sender_whitelist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "白名单元素重复";
                }
                return mesg;
            }
        },
        'sender_blacklist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#sender_blacklist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "黑名单元素重复";
                }
                return mesg;
            }
        },
        'recipient_whitelist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#recipient_whitelist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "白名单元素重复";
                }
                return mesg;
            }
        },
        'recipient_blacklist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#recipient_blacklist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "黑名单元素重复";
                }
                return mesg;
            }
        },
        'client_whitelist':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#client_whitelist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "白名单元素重复";
                }
                return mesg;
            }
        },
        'client_blacklist':{
            'type':'textarea',
            'required':'0',
            'check':'ip|',
            'ass_check':function(eve){
                var mesg = "";
                var arr_temp = $("#client_blacklist").val().split("\n");
                if(isRepeat(arr_temp)){
                    mesg = "黑名单元素重复";
                }
                return mesg;
            }
        }
    }
}
var paging_holder = {
    url: "/cgi-bin/sender_black_white_list.cgi"
};

$(document).ready(function(){
    check._main(object);
});
//数组查重方法
function isRepeat(arr){
    var hash = {};
    for(var i in arr) {
        if(hash[arr[i]])
            return true;
        hash[arr[i]] = true;
    }
    return false;
}