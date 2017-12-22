

var object = {
      'form_name':'L2TP_FORM',//这里填写表单的名字
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

                  var vals    = ip_start.split(/\./);
                  var valus   = ip_end.split(/\./);

                  if(ip_start !== "" && ip_end !== ""){   //此处必须先检测是否有一个为空,不然有bug
                    for(i=0; i<3 ; i++) {   //  只检测前三个字段是否均相等，故 i 从0至2 
                           if(vals[i] !== valus[i]){
                                msg = "起始地址与结束地址的前三个字段必须相同,请重新输入";
                                // $("#remote_ip_1").val("");
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
                          data : 'path=/var/efw/xl2tpd/config',
                          success : function(data){ 
                            eve.gres = data;
                          }
                      });
                  }
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
                    if( ip_start != "" && ip_end != "" &&(ip >= begin_ip)&&(ip <= end_ip) ) {  //如果大于大的，小于小的，那么就不在范围以内了。
                          msg = "本地隧道IP地址不能在起始地址和结束地址之间";
                          // $("#local_ip_0").val("");   //要清空以便用户重新输入
                          $("#local_ip_0").focus();   //使光标焦点定位到这个输入框内
                          return msg;
                       /*   $( "form[name=L2TP_FORM]" ).submit(function(){    //把表单禁止提交放在check_local_tunnel_ip()函数里不好使。
                          return false;    //禁止表单提交
                      });  */
                     }
                    if(!eve.gres) {
                         $.ajax({
                            type : "get",
                            url : '/cgi-bin/chinark_back_get.cgi',
                            async : false,
                            data : 'path=/var/efw/xl2tpd/config',
                            success : function(data){ 
                              eve.gres = data;
                            }
                         });
                      }
                   }
            }
      }
}

var check = new ChinArk_forms();


$( document ).ready(function(){
    check._main(object);
    var v = $(":selected").val();
    if(v == "NOIPSEC") {
      $( "#pre_shared_tr" ).hide();
    }
    //$( "select option:eq(1)" ).select( function(){ } );   //select事件根本不起作用，弃用，改成change就好使了
    $( "select option:eq(1)" ).click( function(){
        $("#pre_shared_tr").css("display","none");   //测试成功
     } );

    $( "#encryp" ).change(function(){    //jquery里的事件名称前面是没有on的，onselect必须改成select，切记啊
      var value = $( "#encryp" ).val();
      if ( value == "NOIPSEC" ) {
        $( "#pre_shared_tr" ).hide();
      } else {
        $( "#pre_shared_tr" ).show();
      }
    });

});

