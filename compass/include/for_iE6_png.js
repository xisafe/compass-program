//author:zhouyuan
//Date:2011-10-08
//function:用于系统所有页面的png图片的白边处理

if (navigator.platform == "Win32" && navigator.appName == "Microsoft Internet Explorer"&& window.attachEvent) 
{
	var app=navigator.appName;
    var verStr=navigator.appVersion;
	if (verStr.indexOf("MSIE 3.0")!=-1 || verStr.indexOf("MSIE 4.0") != -1 || verStr.indexOf("MSIE 5.0") != -1 || verStr.indexOf("MSIE 5.1") != -1 || verStr.indexOf("MSIE 6.0") != -1) {
		window.attachEvent("onload", correctPNG);
		window.attachEvent("onload", alphaBackgrounds);
	}
}

function correctPNG()
{
	for(var i=0; i<document.images.length; i++)
	{
		var img = document.images[i]
		var imgName = img.src.toUpperCase()
		var img_height = img.height;

		if ((imgName.substring(imgName.length-3, imgName.length) == "PNG") && (imgName.substring(imgName.length-14, imgName.length) != "SWITCH-OFF.PNG") && (imgName.substring(imgName.length-13, imgName.length) != "SWITCH-ON.PNG" ) && (imgName.substring(imgName.length-7, imgName.length) != "ADD.PNG" ) && (imgName.substring(imgName.length-7, imgName.length) != "DEL.PNG" ) && (imgName.substring(imgName.length-11, imgName.length) != "REFRESH.PNG") && (imgName.substring(imgName.length-7, imgName.length) != "CUT.PNG") )
		{
			var imgID = (img.id) ? "id='" + img.id + "' " : ""
			var imgClass = (img.className) ? "class='" + img.className + "' " : ""
			var imgTitle = (img.title) ? "title='" + img.title + "' " : "title='" + img.alt + "' "
			var imgStyle = ""
			imgStyle = "display:inline-block;" + img.style.cssText
			if (img.align == "left") imgStyle = "float:left;" + imgStyle
			if (img.align == "right") imgStyle = "float:right;" + imgStyle
			if (img.parentElement.href) imgStyle = "cursor:hand;" + imgStyle
			var strNewHTML = "<span " + imgID + imgClass + imgTitle+ " style=\"" + "width:" + img.width + "px; height:" 							+ img_height  + "px;margin-bottom:-5px;" + imgStyle
							 + ";"
							 + "filter:progid:DXImageTransform.Microsoft.AlphaImageLoader"
							 + "(src=\'" + img.src + "\', sizingMethod='crop');\"></span>"
			img.outerHTML = strNewHTML
			i = i-1
		}
	}
}


function alphaBackgrounds()
{
	var rslt = navigator.appVersion.match(/MSIE (d+.d+)/, '');
	var itsAllGood = (rslt != null && Number(rslt[1]) >= 5.5);
	for (i=0; i<document.all.length; i++)
	{
		var bg = document.all[i].currentStyle.backgroundImage;
		if (bg)
		{
			if (bg.match(/.png/i) != null)
			{
				var mypng = bg.substring(5,bg.length-2);
				document.all[i].style.filter ="progid:DXImageTransform.Microsoft.AlphaImageLoader(src='"+mypng+"',sizingMethod='crop')";
				document.all[i].style.backgroundImage = "url('')";
			}
		}
	}
}