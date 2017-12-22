

var object = {
            'form_name':'PPTP_FORM',//这里填写表单的名字
            'option':{
                'remote_ip_start':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|',
                    'ass_check':function(eve){ }
                    },
                 'remote_ip_end':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|',
                    'ass_check':function(eve){
                        var msg = "";
                        var ip_start = $("#remote_ip_0").val();
                        var ip_end   = $("#remote_ip_1").val();

                        var vals    = ip_start.split(/\./);   //千万注意分割后的vals是字符串类型变量而非整型变量
                        var valus   = ip_end.split(/\./);
                        if(ip_start !== "" && ip_end !== ""){   //此处必须先检测是否有一个为空,不然有bug
                            for(i=0; i<3 ; i++) {   //  只检测前三个字段是否均相等，故 i 从0至2 
                                if(vals[i] !== valus[i]) {
                                    msg = "起始地址与结束地址的前三个字段必须相同,请重新输入";
                                    // $("#remote_ip_1").val("");   //直接把人家输的内容迅速清空体验很不好，要删掉
                                    return msg;
                                }
                            }
                            if( parseInt( vals[3] ) > parseInt( valus[3] ) ) {
                                msg = "起始地址不能大于结束地址";
                                // $("#remote_ip_1").val("");
                                return msg;
                            }
                          }
                         if(!eve.gres) {
                         $.ajax({
                                  type : "get",
                                  url : '/cgi-bin/chinark_back_get.cgi',
                                  async : false,
                                  data : 'path=/var/efw/pptpd/config',
                                  success : function(data){ 
                                    eve.gres = data;
                                  }
                            });    }
                               return msg;
                        }
                    },
                'local_ip_addr':{
                    'type':'text',
                    'required':'1',
                    'check':'ip|',
                    'ass_check':function(eve){ 
                    //原来检测本地隧道IP地址不能在起始地址和结束地址之间都在这里，现在都放到了函数check_local_tunnel_ip里
                    var msg = "";
                    var ip_start = $("#remote_ip_0").val();
                    var ip_end   = $("#remote_ip_1").val();
                    var ip_addr  = $("#local_ip_0").val();

                    var vals_0 = ip_start.split(/\./);
                    var vals_1 = ip_end.split(/\./);
                    var vals_2   = ip_addr.split(/\./);
                    var begin_ip = vals_0[0] << 24 | vals_0[1] << 16 | vals_0[2] << 8 | vals_0[3];
                    var end_ip   = vals_1[0] << 24 | vals_1[1] << 16 | vals_1[2] << 8 | vals_1[3];
                    var ip       = vals_2[0] << 24 | vals_2[1] << 16 | vals_2[2] << 8 | vals_2[3];
                    if( (ip >= begin_ip)&&(ip <= end_ip) ){  //如果大于大的，小于小的，那么就不在范围以内了。
                        msg = "本地隧道IP地址不能在起始地址和结束地址之间";
                        // $("#local_ip_0").val("");   //要清空以便用户重新输入
                        // $("#local_ip_0").focus();   //使光标焦点定位到这个输入框内
                        return msg;
                    }
                    if(!eve.gres) {
                        $.ajax({
                              type : "get",
                              url : '/cgi-bin/chinark_back_get.cgi',
                              async : false,
                              data : 'path=/var/efw/pptpd/config',
                              success : function(data){
                                eve.gres = data;
                              }
                        });
                    }
                         return msg;
                       }
                    }
                 }
}

var check = new ChinArk_forms();

$( document ).ready(function(){
    check._main(object);
});