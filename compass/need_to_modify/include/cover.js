// JavaScript Document
function position(){
var current_width = document.documentElement.scrollWidth||document.body.scrollWidth;
current_width = current_width/2;
var obj2 = document.getElementById('detail_div');
var div_width = obj2.style.width;
var new_width = '';
for(var i = 0; i < div_width.length; i++)
{
	if(div_width.charAt(i) == 'p'||div_width.charAt(i) =='x' )
	{
	}
	else {
		new_width += div_width.charAt(i);
	}
}
new_width = current_width - new_width/2;
new_width += 'px';
obj2.style.left= new_width;

obj2 = document.getElementById('protocol_div');
div_width = obj2.style.width;
new_width = '';
for(var i = 0; i < div_width.length; i++)
{
	if(div_width.charAt(i) == 'p'||div_width.charAt(i) =='x' )
	{
	}
	else {
		new_width += div_width.charAt(i);
	}
}
new_width = current_width - new_width/2;
new_width += 'px';
obj2.style.left= new_width;
}

function remove_cover(){
    var obj1 = document.getElementById("cover_div");
   	var obj2 = document.getElementById("detail_div");
	var obj3 = document.getElementById("protocol_div");
   	obj1.style.display = "none";
   	obj2.style.display = "none";
	obj3.style.display = "none";
}

function display_protocol(){
    position();
	var obj1 = document.getElementById("cover_div");
   	var obj2 = document.getElementById("detail_div");
	var obj3 = document.getElementById("protocol_div");
	obj1.style.display = "block";
	obj2.style.display = "none";
	obj3.style.display = "block";
}

function display_detail(){
    position();
	var obj1 = document.getElementById("cover_div");
   	var obj2 = document.getElementById("detail_div");
	var obj3 = document.getElementById("protocol_div");
	obj1.style.display = "block";
   	obj2.style.display = "block";
	obj3.style.display = "none";
}
document.getElementById("confirm_button").onmouseover=function(){
    this.style.color="white";
	this.style.background="url(../images/confirm_hover.png)";
    var obj = document.getElementById("cancel_button");
	obj.style.background="url(../images/confirm.png)";
	obj.style.color="black";
}

document.getElementById("confirm_button").onmouseout=function(){
    this.style.color="black";
	this.style.background="url(../images/confirm.png)";
    var obj = document.getElementById("cancel_button");
	obj.style.background="url(../images/confirm_hover.png)";
	obj.style.color="white";
}

document.getElementById("confirm_button2").onmouseover=function(){
    this.style.color="white";
	this.style.background="url(../images/confirm_hover.png)";
}

document.getElementById("confirm_button2").onmouseout=function(){
    this.style.color="black";
	this.style.background="url(../images/confirm.png)";
}

document.getElementById("cancel_button").onmouseover=function(){
    this.style.color="black";
	this.style.background="url(../images/confirm.png)";
    var obj = document.getElementById("confirm_button");
	obj.style.background="url(../images/confirm_hover.png)";
	obj.style.color="white";
}

document.getElementById("cancel_button").onmouseout=function(){
    this.style.color="white";
	this.style.background="url(../images/confirm_hover.png)";
    var obj = document.getElementById("confirm_button");
	obj.style.background="url(../images/confirm.png)";
	obj.style.color="black";
}