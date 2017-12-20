/**author:刘炬隆（liujulong）
date:2014/05/30
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'BASIC_SESSION_SETTING_FORM',
   'option':{
        'SYN_SENT':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var SYN_SENT = eve._getCURElementsByName("SYN_SENT","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (SYN_SENT < 10 || SYN_SENT > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'SYN_RCV':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var SYN_RCV = eve._getCURElementsByName("SYN_RCV","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (SYN_RCV < 10 || SYN_RCV > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'FIN_WAIT':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var FIN_WAIT = eve._getCURElementsByName("FIN_WAIT","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (FIN_WAIT < 10 || FIN_WAIT > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'TIME_WAIT':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var TIME_WAIT = eve._getCURElementsByName("TIME_WAIT","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (TIME_WAIT < 10 || TIME_WAIT > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'ESTABLISHED':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var ESTABLISHED = eve._getCURElementsByName("ESTABLISHED","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (ESTABLISHED < 10 || ESTABLISHED > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'UDP_CONNECT':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var UDP_CONNECT = eve._getCURElementsByName("UDP_CONNECT","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (UDP_CONNECT < 10 || UDP_CONNECT > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'UDP_CLOSE':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var UDP_CLOSE = eve._getCURElementsByName("UDP_CLOSE","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (UDP_CLOSE < 10 || UDP_CLOSE > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        },
        'ICMP_CLOSE':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                var msg="";
                var ICMP_CLOSE = eve._getCURElementsByName("ICMP_CLOSE","input","BASIC_SESSION_SETTING_FORM")[0].value;
                if (ICMP_CLOSE < 10 || ICMP_CLOSE > 86400 ){
                    msg = "请填写10-86400的整数";
                }
                return msg;
            }
        }
    }
};

var paging_holder = {
    url: "/cgi-bin/basic_session_setting.cgi",
    detail_data:[],
    states_all:[]
};

$(document).ready(function(){
    check._main(object);
});

//恢复默认值
function recovery_data(){
    $(".ctr_tcp").val("60");
    $("#ESTABLISHED").val("3600");
    $("#UDP_CONNECT").val("180");
    $("#UDP_CLOSE").val("30");
    $("#ICMP_CLOSE").val("30");
}
