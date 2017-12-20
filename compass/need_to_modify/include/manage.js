/*
 * 描述: 管理性质的js 包括页面跳转函数
 *
 * 作者: WangLin，245105947@qq.com
 * 历史：
 *       2014.12.26 WangLin创建
 */

/*
 * 功能：站内页面跳转
 *
 */
function jump_to_page( url ) {
    var menu_list_dt = $( parent.window.document ).find( "#leftFrame" ).contents().find( "#menu-content dl dt" );
    var menu_list_dd = $( parent.window.document ).find( "#leftFrame" ).contents().find( "#menu-content dl dd" );

    var first_level_menu = 0, sec_level_memu = 0, found = false;
    if( url =="/cgi-bin/main_star.cgi" ) {
        // do nothing
    } else {
        /* 开始遍历dd 需找href属性与url相等的链接 */
        for ( var i = 0; i < menu_list_dd.length; i++ ) {
            var links = $( menu_list_dd ).eq( i ).find( "ul li" );
            sec_level_memu = 0;
            for ( var j = 0; j < links.length; j++ ) {
                var third_level_links = $( links ).eq( j ).find( "div span" );
                for( var k = 0; k < third_level_links.length; k++ ) {
                    var exit_url = $( third_level_links ).eq( k ).text();
                    if ( exit_url == url ) {
                       found = true;
                       break;
                    }
                }
                 if ( found ) {
                    break;
                } else {
                    sec_level_memu++;
                }
            }
            if ( found ) {
                break;
            } else {
                first_level_menu++;
            }
        }
    }

    if ( found ) {
        var first_level_menu_link = $( menu_list_dt ).eq( first_level_menu ).find( "a" );
        var sec_level_memu_el = $( menu_list_dd ).eq( first_level_menu ).find( "ul li" );
        if ( $( first_level_menu_link ).parent().next().css("display") == "block" ) {
            // do nothing
        } else {
            $( first_level_menu ).trigger( "click" );
        }
        $( sec_level_memu_el ).eq( sec_level_memu ).trigger( "click" );

        window.location.href = url;
    } else {
        alert( "您寻找的页面不存在或者您没有权限访问" );
    }
}