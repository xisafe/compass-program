//author:zhouyuan
//Date:2011-06-01
//function:用于top.cgi页面的js控制
//modify:2011-07-20

$(document).ready(function(){

    /* 用于左菜单的伸缩显示效果实现 */
    // $('dd:not(:first)').hide();
    // $('dt a').click(function(){
    //     if($(this).parent().next().css("display") == "block")
    //     {
    //         $(this).find("img").attr("src","/images/toggle-expand.png");
    //         $('dd:visible').slideUp('500');
    //     }else{
    //         $('dd:visible').slideUp('500');
    //         $('dt a span img').attr("src","/images/toggle-expand.png");
    //         $(this).find("img").attr("src","/images/toggle.png");
    //         $(this).parent().next().slideDown('500');
    //     }
    //     return false;
    // });
    /* 伸缩效果实现结束 */


    // $('dd ul li').click(function(){
    //     cgi_page = $(this).find("a").attr("href");
    //     $('dd ul li').removeClass("selected");
    //     $(this).addClass("selected");
    // });

});

function onclick_first_level_menu( e ){
    if( $( e ).parent().next().css("display") == "block"){
        $( e ).find("span").children("span:first-child").removeClass('carat_open').addClass('carat');
        $('dd:visible').slideUp('500');
    }else{
        $("a").parent("dt").find("span").children("span:first-child").removeClass('carat_open').addClass('carat');
        $('dd:visible').slideUp('500');
        $( e ).find("span").children("span:first-child").removeClass('carat').addClass('carat_open');
        $( e ).parent().next().slideDown('500');
    }
}

function onclick_sec_level_menu( e ) {
    $('dd ul li').removeClass("selected");
    $( e ).addClass("selected").parents('dd').prev('dt').addClass('sele_fir_menu').siblings('dt').removeClass('sele_fir_menu');
}