var paging_holder = {
    url: "/cgi-bin/top.cgi"
};
//表示预警文件存在与否的标志
var flag_warn = "unexercise";
$(document).ready(function(){
    is_exercise_warnfile();
    //lock_check();
    // init_click();
});



function closedetail(){
    document.getElementById("bgDiv").style.display = "none";
    document.getElementById("bgDiv2").style.display = "none";
}

function doaction_ok(){
    var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
    topframe.document.swf.Play();
}

//显示详细信息的请求函数
function load_data_detail(){
    var sending_data = {
        ACTION: "load_data_detail"
    };

    function ondatareceived(data) {
        var data_content = JSON.parse(data);
        var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
        mainframe.document.getElementById("bgDiv").style.display = "";
        mainframe.document.getElementById("bgDiv2").style.display = "";
        mainframe.document.getElementById("detail_indo").innerHTML = data_content.detail_info;        
        
     
    }
    if(flag_warn == "exercise"){
        do_request(sending_data, ondatareceived);
    }
}

//点击确定按钮事件
function doaction_confirm(){
    // var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
    document.querySelector('#alarm_controller img').src='/images/alarm.png';
    document.querySelector('#alarm_controller audio').src='#';
    var sending_data = {
        ACTION: "confirm"
    };

    function ondatareceived(data) {
        flag_warn = "unexercise";
        is_exercise_warnfile_bak();
    }

    do_request(sending_data, ondatareceived);
    flag_warn = "unexercise";
}

//检查预警文件存在与否的函数
function is_exercise_warnfile(){
    var sending_data = {
        ACTION: "check_warnfile"
    };

    function ondatareceived(data) {
        var state = data;
        if (state == "exercise"){
             // var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
            // topframe.document.swf.Play();
            document.querySelector('#alarm_controller img').src='/images/alarm.gif';
            document.querySelector('#alarm_controller audio').src='/images/alarm.mp3';
             // var temp = document.swf;
             // console.log(temp);
             //    temp.Play();
           
            flag_warn = "exercise";
        }else{
            flag_warn = "unexercise";
            window.setTimeout("is_exercise_warnfile()",1000);
        }
     
    }

    do_request(sending_data, ondatareceived);
}

//检查预警文件存在与否的函数
function is_exercise_warnfile_bak(){
    var sending_data = {
        ACTION: "check_warnfile"
    };

    function ondatareceived(data) {
        var state = data;
        if (state == "exercise"){
            var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
            // topframe.document.swf.Play();
            topframe.querySelector('#alarm_controller img').src='/images/alarm.gif';
            topframe.querySelector('#alarm_controller audio').src='/images/alarm.mp3';
            flag_warn = "exercise";
        }else{
            flag_warn = "unexercise";
            window.setTimeout("is_exercise_warnfile()",1000);
        }
     
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
            //alert("网络错误,部分功能可能出现异常");
        },
        success: ondatareceived
    });
}
//展示预警列表
function show_alarm_panel(){
    document.querySelector('#alarm_controller img').src='/images/alarm.png';
    document.querySelector('#alarm_controller audio').src='#';
    var mainframe = window.parent.parent.document.getElementById("mainFrame").contentWindow;
    mainframe.document.getElementById("panel_list").style.display = "block";
    mainframe.document.getElementById("TransparentBorder_list_panel").style.display = "block";
    mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").style.display = "block";

    var boder_height = mainframe.document.getElementById("list_panel_id_for_list_panel").offsetHeight;
    // var boder_width = document.getElementById(panel_id).offsetWidth;
    mainframe.document.getElementById("TransparentBorder_list_panel").style.height = boder_height + 'px';
    // document.getElementById('TransparentBorder').style.width = boder_width + 'px';

    var cover_height = parseInt(mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").offsetHeight);
    var cover_width = parseInt(mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").offsetWidth);

    var border_height = parseInt(mainframe.document.getElementById("TransparentBorder_list_panel").offsetHeight);
    var border_width = parseInt(mainframe.document.getElementById("TransparentBorder_list_panel").offsetWidth);
    mainframe.list_panel.update_info(true);
    
    var close_button = mainframe.document.querySelector('#list_panel_close_for_list_panel');
    close_button.style.display = 'none' ; 

    var temp_top = (cover_height - border_height) / 2;
    var temp_left = (cover_width - border_width) / 2;

    mainframe.document.getElementById("TransparentBorder_list_panel").style.top = temp_top + 'px';
    mainframe.document.getElementById("TransparentBorder_list_panel").style.left = temp_left + 'px';

    mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").onclick = hide_alarm_panel;
    function hide_alarm_panel() {
        mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").style.display = 'none';
        mainframe.document.getElementById("TransparentBorder_list_panel").style.display = 'none';
    }

    $(window).resize(function() {
        if (mainframe.document.getElementById("TransparentBorder_list_panel").style.display == 'block') {
            var cover_height = parseInt(mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").offsetHeight);
            var cover_width = parseInt(mainframe.document.getElementById("popup-mesg-border-box-cover-list_panel").offsetWidth);

            var border_height = parseInt(mainframe.document.getElementById("TransparentBorder_list_panel").offsetHeight);
            var border_width = parseInt(mainframe.document.getElementById("TransparentBorder_list_panel").offsetWidth);

            var temp_top = (cover_height - border_height) / 2 - 78;
            var temp_left = (cover_width - border_width) / 2;

            mainframe.document.getElementById("TransparentBorder_list_panel").style.top = temp_top + 'px';
            mainframe.document.getElementById("TransparentBorder_list_panel").style.marginTop = 0 + 'px';
            mainframe.document.getElementById("TransparentBorder_list_panel").style.left = temp_left + 'px';
            mainframe.document.getElementById("TransparentBorder_list_panel").style.marginLeft = 0 + 'px';
        }

    })
    doaction_confirm();
}
//解决谷歌浏览器不支持onclick事件


// function init_click(){
//     var timeoutID,
//         c = 0,
//         flashObj = document.getElementById('swf'),
//         flashEmbed = document.getElementById('flash_embed');
//     function over(){
//       c |= 1;
//     }
//     function out(){
//       c = 0;
//     }
//     function down(){
//       c |= 2;
//     }
//     function up(){
//       c |= 4;
//         click();
//         c |= 8;
//         if(! timeoutID){
//           timeoutID = setTimeout(function(){
//             c ^= 8; //异或，a ^ b， ab不同则返回1
//             timeoutID = undefined;
//           },100);
//         }
//     }
//     function click(){
//       show_alarm_panel();
//     }
//     if(flashObj){
//       flashObj.onmouseover = over;
//       flashObj.onmouseout = out;
//       flashObj.onmousedown = down;
//       flashObj.onmouseup = up;
//     }
//     if(flashEmbed){
//       flashEmbed.onmouseover = over;
//       flashEmbed.onmouseout = out;
//       flashEmbed.onmousedown = down;
//       flashEmbed.onmouseup = up;
//     }
// }
function refresh_page(){
    window.parent.location.reload()
}