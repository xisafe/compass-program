var paging_holder = {
    url: "/cgi-bin/top.cgi"
};
//表示预警文件存在与否的标志
var flag_warn = "unexercise";


function closedetail(){
    document.getElementById("bgDiv").style.display = "none";
    document.getElementById("bgDiv2").style.display = "none";
}





//点击确定按钮事件
function doaction_confirm(){
    var topframe = window.parent.parent.document.getElementById("topFrame").contentWindow;
    topframe.document.swf.StopPlay();
    document.getElementById("bgDiv2").style.display = "none";
    document.getElementById("bgDiv").style.display = "none";
    var sending_data = {
        ACTION: "confirm"
    };

    function ondatareceived(data) {
        flag_warn = "unexercise";
        is_exercise_warnfile_bak();
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
            topframe.document.swf.Play();
            flag_warn = "exercise";
        }else{
            window.setTimeout("is_exercise_warnfile_bak()",1000);
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