function RestartService(startMess){
		if($('#notification-view').find('.content').attr("class") != 'content')
		{
				var viewport_width = $(window).width();
				var viewport_height = $(window).height();
				var document_width = $(document).width();
				var document_height = $(document).height();
				$overlay = $('<div></div>').attr('id', 'notification-overlay')
							 .css('width', document_width + 'px')
							 .css('height', document_height + 'px')
							 .css('opacity','0.0')
				$container = $('<div></div>').attr('id', 'notification-container')
				var left = Math.round((viewport_width - 516) / 2);
				var top = Math.round((viewport_height - 86) / 2);
				/* Centering the container */
				$container.css('top', top).css('left', left)
				$content = $('<div></div>').addClass("content");
				/* Inserting the content view into the container */
				$container.append($content)
				enconsole.log($container);
				enconsole.log($content);
				/* Inserting the container view into the body */
				$('body').append($overlay)
				$('#notification-view').append($container);
		}
		
		$('#notification-view').find('.content').html(startMess);
		
        $('#notification-overlay').show().fadeTo(500, 0.66, 
            function() {
               $('#notification-view').show().fadeTo(500, 1);
               $('#notification-container').show();
            });	
}
function endmsg(endMess){	
	$('#notification-view').find('.content').html(endMess);
		$('#notification-view').fadeTo(500, 1, function() {
            $('#notification-container').hide()
            $('#notification-overlay').fadeTo(500, 0.66, function() {
                $('#notification-overlay').hide();
                });
        });
}
	