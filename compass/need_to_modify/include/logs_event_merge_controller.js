/**author:刘炬隆（liujulong）
date:2014/04/17
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'EVENT_MERGE_FORM',
   'option':{
        'mergecyle':{
            'type':'text',
            'required':'1',
            'check':'int|',
            'ass_check':function(eve){
                                        var msg="";
                                        var viewsize = eve._getCURElementsByName("mergecyle","input","EVENT_MERGE_FORM")[0].value;
                                        if (viewsize > 120) {
                                        msg = "请输入0-120的整数";
                                        }
                                        return msg;
                                     }
        },
        
    }
}


$(document).ready(function(){
    check._main(object);
});