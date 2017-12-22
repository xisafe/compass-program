/**author:Áõ¾æÂ¡£¨liujulong£©
date:2015/04/23
**/

var check = new ChinArk_forms();
var object = {
   'form_name':'JUNK_FORM',
   'option':{
        'spam_blacklist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                
            }
        },
        'spam_whitelist':{
            'type':'textarea',
            'required':'0',
            'check':'domain|mail|',
            'ass_check':function(eve){
                
            }
        }
    }
}

$(document).ready(function(){
    check._main(object);
});