function page_turn() {
    var next_page;

    $("#current_page_for_list_panel").unbind().keydown(function( event){
        var temp_for_current_page = event || window.event;
        var cod = temp_for_current_page.charCode||temp_for_current_page.keyCode;
        if (cod == 13) {
            next_page = Number($("#current_page_for_list_panel").val());
            var total_page = Number($("#total_page_for_list_panel").html());
            if (next_page > total_page) {
                alert("您输入的页码无效！");
                return;
            }

            update_log_data(next_page);
        }
    });

    $("#refresh_icon_for_list_panel").unbind().on('click', function() {
        var current_page = $("#current_page_for_list_panel").val();
        update_log_data(current_page);
    }).siblings("img").each(function(){
        $(this).unbind().on("click",function(){
            var end_page = $("#total_page_for_list_panel").text();

            var current_page = $("#current_page_for_list_panel").val();
            var icon_name = "_page_icon_for_list_panel";
            if($(this).attr('id')==$("#first"+icon_name).attr('id')){
                (current_page == "1") ? next_page = false : next_page = 1;
            }
            else if($(this).attr('id')==$("#end"+icon_name).attr('id')){
                (current_page == end_page) ? next_page = false : next_page = end_page;
            }
            else if($(this).attr('id')==$("#last"+icon_name).attr('id')){
                (current_page == "1") ? next_page = false : next_page = parseInt(current_page)-1;
            }
            else if($(this).attr('id')==$("#next"+icon_name).attr('id')){
                (current_page == end_page) ? next_page = false : next_page = parseInt(current_page) + 1;
            }
            if (next_page) {
                update_log_data(next_page);
            }  
        })
    })

}

function update_log_data(turn_page,update_button,e){
    var error_imgs = $(e).parents('form').find('img[src="../images/error_note.png"]')
    if (error_imgs.length) {
        message_manager.show_popup_error_mesg('表格输入有误')
        return
    };
    if ($('#export_log')) {
        $("#export_log").attr('value',$('#searchTime').val());
        
    };
    var sending_data = {
        current_page: turn_page,
        page_size: list_panel_config.page_size
    };

    var add_panel_form_arr = $('#add_panel_body_form_id_for_add_panel').serializeArray();
    for (var i = 0; i < add_panel_form_arr.length; i++) {
            sending_data[add_panel_form_arr[i].name] = add_panel_form_arr[i].value ;
    }

    function ondatareceived(data) {

        console.log(data);
        list_panel.detail_data = data.detail_data;
        list_panel.total_num = data.total_num;
        list_panel.current_page = turn_page;
        list_panel.is_load_all_data = false;
        list_panel.is_log_search = true;
        list_panel.update_info();
        if ( update_button == 'false' ) {
            add_panel.hide();
        }else{
            var last_image_on = '/images/last-page.gif';
            var first_image_on = '/images/first-page.gif';
            var next_image_off = '/images/next-page-off.png';
            var end_image_off = '/images/end-page-off.png';
            
            $("#current_page_for_list_panel").val(turn_page);
            if($("#current_page_for_list_panel").val()!=1) {
                $("#last_page_icon_for_list_panel").attr("src",last_image_on);
                $("#first_page_icon_for_list_panel").attr("src",first_image_on);
            }

            var end_page = $("#total_page_for_list_panel").text();
            if($("#current_page_for_list_panel").val() == end_page ){
                $("#next_page_icon_for_list_panel").attr("src",next_image_off);
                $("#end_page_icon_for_list_panel").attr("src",end_image_off);
            }
        }
    }
    do_request(sending_data, ondatareceived, function(){
        message_manager.show_popup_error_mesg("数据错误！");
    });
}