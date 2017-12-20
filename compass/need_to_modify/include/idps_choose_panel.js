/*
 * 参数: 传入整个控件要提交值的name
 * 功能：当点击>>方向键时，将用户在左边栏选择的值放到右边栏
 */
function add_choosed_items( commit_name ) {
    var left_select     = "#left_select_for_" + commit_name;
    var right_select    = "#right_select_for_" + commit_name;

    var selected_selector   = left_select + " option:selected";
    var selected_items       = $( selected_selector );

    if( selected_items.length ) {
        selected_items.attr("selected", false).appendTo( $( right_select ) );
        refresh_commit_value( commit_name );
    }
}

/*
 * 参数: 传入整个控件要提交值的name
 * 功能：当点击<<方向键时，将用户在右边栏选择的值放到左边栏
 */
function del_choosed_items( commit_name ) {
    var left_select     = "#left_select_for_" + commit_name;
    var right_select    = "#right_select_for_" + commit_name;

    var selected_selector   = right_select + " option:selected";
    var selected_items       = $( selected_selector );

    if( selected_items.length ) {
        selected_items.attr("selected", false).appendTo( $( left_select ) );
        refresh_commit_value( commit_name );
    }
}

/*
 * 参数: 传入整个控件要提交值的name
 * 功能：更新整个控件要提交的值，凡是放在右边栏里的项目都属于将要提交的值，多个值以‘|’隔开
 */
function refresh_commit_value( commit_name ) {
    var option_selector        = "select#right_select_for_" + commit_name + " option";
    var commit_value_selector  = "input[name='" + commit_name + "']";

    var values = Array();
    var options = $( option_selector );
    options.each( function() {
        values.push( $(this).text() );
    });
    var value = values.join( "|" );
    $(commit_value_selector).val(value);
}

/*
 * 参数: 传入整个控件要提交值的name
 * 功能：将左边两栏选择的一对值放到右边栏
 */
function add_choosed_pair( commit_name ) {
    var left_left_select     = "#left_left_select_for_" + commit_name;
    var letf_right_select    = "#left_right_select_for_" + commit_name;
    var pair_right_select    = "#pair_right_select_for_" + commit_name;

    var left_left_selected_selector     = left_left_select + " option:selected";
    var letf_right_selected_selector    = letf_right_select + " option:selected";

    var left_left_selected_item     = $( left_left_selected_selector );
    var left_right_selected_item    = $( letf_right_selected_selector );

    if( left_left_selected_item.length && left_right_selected_item.length && 
        ( left_left_selected_item.text() != left_right_selected_item.text() ) ) {
        var pair = '<option>' + left_left_selected_item.text() + "<=>" + left_right_selected_item.text() + '</option>';
        $( pair_right_select ).append( pair );
        reomve_pair_from_left( commit_name, left_left_selected_item.text(), left_right_selected_item.text() );
        refresh_pair_commit_value ( commit_name );
    }
}

/*
 * 参数: 传入整个控件要提交值的name
 * 功能：将右边选择的一对值放回左边两栏
 */
function del_choosed_pairs( commit_name ) {
    var pair_right_select    = "#pair_right_select_for_" + commit_name;
    var pair_right_selected_selector    = pair_right_select + " option:selected";

    var options = $( pair_right_selected_selector );
    options.each( function() {
        var pair_text = $(this).text();
        var pair = pair_text.split( "<=>" );
        add_pair_to_left( commit_name, pair[0], pair[1] );
        $(this).remove();
    });
    refresh_pair_commit_value ( commit_name );
}

/*
 * 参数: 传入整个控件要提交值的name,和要移除的一对值
 * 功能：将左边的两栏中符合传入的一对值的项目都移除
 */
function reomve_pair_from_left( commit_name, left_item, right_item ) {
    var left_left_select     = "#left_left_select_for_" + commit_name;
    var letf_right_select    = "#left_right_select_for_" + commit_name;
    var left_left_selector     = left_left_select + " option";
    var letf_right_selector    = letf_right_select + " option";

    var left_left_items     = $( left_left_selector );
    var left_right_items    = $( letf_right_selector );

    left_left_items.each( function() {
        if( $(this).text() == left_item || $(this).text() == right_item ) {
            $(this).remove();
        } 
    });
    left_right_items.each( function() {
        if( $(this).text() == left_item || $(this).text() == right_item ) {
            $(this).remove();
        } 
    });
}


/*
 * 参数: 传入整个控件要提交值的name,和要添加的一对值
 * 功能：将左边的两栏中符合传入的一对值的项目都添加上
 */
function add_pair_to_left( commit_name, left_item, right_item ) {
    var left_left_select     = "#left_left_select_for_" + commit_name;
    var letf_right_select    = "#left_right_select_for_" + commit_name;

    var to_append_value = '<option>' + left_item + '</option><option>' + right_item + '</option>';
    $( left_left_select ).append( to_append_value );
    $( letf_right_select ).append( to_append_value );
}

/*
 * 参数: 传入整个控件要提交值的name
 * 功能：更新整个控件要提交的值，凡是放在右边栏里的项目都属于将要提交的值，多个值以‘|’隔开，一对值以‘:’隔开
 */
function refresh_pair_commit_value ( commit_name ) {
    var option_selector        = "select#pair_right_select_for_" + commit_name + " option";
    var commit_value_selector  = "input[name='" + commit_name + "']";

    var values = Array();
    var options = $( option_selector );
    options.each( function() {
        values.push( $(this).text().replace( "<=>", ":" ) );
    });
    var value = values.join( "|" );
    $(commit_value_selector).val(value);
}