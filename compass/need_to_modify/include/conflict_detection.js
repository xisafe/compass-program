// JavaScript Document
function warning_box(message){
	$("<div id='infoDiv'></div><div id='cover'></div>").appendTo("body");
		$("#infoDiv").empty();
		var viewport_width = $(window).width();
		var viewport_height = $(window).height();
		var Bwidth=$(document).width();
		var Bheight=$(document).height();
		var width=0.6*Bwidth;
		var height=0.6*Bheight;
		var left = Math.round((viewport_width - width) / 2);
		var top = 100;
		$("#cover").css({display:'block',top:'0px',left:0,width:Bwidth,height:Bheight});
		$("#infoDiv").css({display:'block',left:left,top:top,width:width});
		var startMess = message;
		var endMess = "扫描完成!";
		if($('#notification-view').find('.content').attr("class") != 'content')
		{
				var viewport_width = $(window).width();
				var viewport_height = $(window).height();
				var document_width = $(document).width();
				var document_height = $(document).width();
				$overlay = $('<div></div>').attr('id', 'notification-overlay')
							 .css('width', document_width + 'px')
							 .css('height', document_height + 'px')
							 .css('opacity','0.0');
				$container = $('<div></div>').attr('id', 'notification-container_elvis')
							  .css('width', '50%')
							 .css('min-height', '80px')
							 .css('position', 'fixed')
							 .css('z-index', '4001')
							 .css('display', 'none')
							 .css('text-align','center')
							 .css('padding','10px')
							 .css('background-color','#fff')
							 .css('border','3px solid #fcb214');
				var left = Math.round((viewport_width) / 4);
				var top = Math.round((viewport_height - 80) / 2);
				/* Centering the container */
				$container.css('top', top).css('left', left)
				$content = $('<div></div>').addClass("content1");
				/* Inserting the content view into the container */
				$container.append($content)
				enconsole.log($container);
				enconsole.log($content);
				/* Inserting the container view into the body */
				$('body').append($overlay)
				$('#notification-view').append($container);
		}
		startMess = "<br />" + "<span style='font-size:13px' ><b>" + startMess + "</n></span>";
		startMess += '<br /><br /><input class="net_button" type="submit" name="save" value="我知道了" onclick="hide()">';
		$('#notification-view').find('.content1').html(startMess);
		
        $('#notification-overlay').show().fadeTo(500, 0.66, 
            function() {
               $('#notification-view').show().fadeTo(500, 1);
               $('#notification-container_elvis').show();
            });
	}
function hide(){	
		$('#notification-view').fadeTo(500, 1, function() {
            $('#notification-container_elvis').hide()
            $('#notification-overlay').fadeTo(500, 0.66, function() {
                $('#notification-overlay').hide();
                });
        });
}