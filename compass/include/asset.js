//author:zhouyuan
//Date:2012-03-09
//function:用于hirel.cgi页面的js控制
window.onload = function()
{
	count_content_height();
}

function count_content_height()
{
	 var content_height =(document.documentElement.clientHeight||window.innerHeight)-70;
	 var content_width  =(document.documentElement.clientWidth||window.innerWidth)*0.9-170;
	 $(".tree").css("height",content_height+"px");
	 $(".right_risk").css("height", (content_height-95)/2+"px");
	
}

function refresh(href,id,type)
{
	var values = document.getElementById(id).value;
	location.href = href+"?action="+type+"&&line="+values;
}

function get_error_node(err,container)
{
	var error_node = document.createElement("b");
	var txt = document.createTextNode(err);
	error_node.appendChild(txt);
	error_node.style.color = "red";
	container.appendChild(error_node);
}

function remove_error_node()
{
	var error = document.getElementsByTagName("b");
	while(error.length)
	{
		for(var h = 0;h<error.length;h++)
		{
			error[h].parentNode.removeChild(error[h]);
		}
		remove_error_node();
	}
}

function check_form(type)
{
	remove_error_node();
	if(type == "merge")
	{
		var merge = $(".merge_option");
		var merge_select = new Array();
		for(var i = 0;i<merge.size();i++)
		{
			if(merge.eq(i).attr("checked"))
			{
				merge_select.push(merge.eq(i));
			}
		}
	
		if(!merge_select.length)
		{
			get_error_node("请选择需要合并的节点！",document.getElementById("merge_node").parentNode);
		}else{
			for(var i = 1;i<merge_select.length;i++)
			{
				if(!check_brother(merge_select[i-1].parent(),merge_select[i].attr("value")))
					{
						get_error_node("所选合并的部门不属于兄弟节点，不能进行合并操作！",document.getElementById("merge_node").parentNode);
						break;
					}
				}
		}
		
		var merge_name = document.getElementById("merge_name").value;
		var r = /[\\~\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\?]+/g;
		if(!merge_name)
		{
			get_error_node("请输入合并后的部门名称！",document.getElementById("merge_name").parentNode);
		}else if(r.test(merge_name))
		{
			get_error_node("节合并后的部门名称含有非法字符！",document.getElementById("merge_name").parentNode);
		}
	}else if(type == "unmerge")
	{
		var select_obj = document.getElementById("unmerge_id");
		for(var i =0;i<select_obj.options.length;i++)
		{
			if(select_obj.options[i].style.display == "none")
			{
				select_obj.options[i].selected = true;
			}
		}
	}else if(type == "move")
	{
		var is_selected = 0;
		var select_obj = document.getElementById("move_host");
		for(var i =0;i<select_obj.options.length;i++)
		{
			if(select_obj.options[i].selected)
			{
				is_selected = 1;
			}
		}
		if(!is_selected)
		{
			get_error_node("没有选择待移动部门！",document.getElementById("move_host").parentNode);
		}
	}
	
	var error = document.getElementsByTagName("b");
	if(error.length>0)
	{
		return 0;
	}else{
		return 1;
	}
}

//检查是否为兄弟节点
function check_brother(node1,node2)
{
	var r = /^(.*)_\d+$/;
	if(r.test(node1))
	{
		var hit = RegExp.$1;
		var hit2 = "";
		if(r.test(node2))
		{
			var hit2 = RegExp.$1;
		}
		if(hit == hit2)
		{
			return 1;
		}else{
			return 0;
		}
	}
	return 0;
}

function show_hidden_child(evt)
{
	evt = evt|| window.event;
	var selected = evt.target||evt.srcElement;
	var father= selected.parentNode.parentNode.id;
	var r = /toggle.png$/;
	if(r.test(selected.src))
	{
		selected.src = "/images/toggle-expand.png";
	}else{
		selected.src = "/images/toggle.png";
	}
	$("#"+father+" > .UL").toggle();
}

function hide_host(evt)
{
	evt = evt|| window.event;
	var selected = evt.target||evt.srcElement;
	if(selected.value == "net")
	{
		document.getElementById("move_host").style.display="none";
		var move_host = document.getElementById("move_host");
		for(var i =0;i<move_host.options.length;i++)
		{
			move_host.options[i].selected = false;
		}
	}else{
		document.getElementById("move_host").style.display="block";
	}
}

function hide()
{
	document.getElementById("pop-divs").style.display ="none";
	document.getElementById("add_div").style.display ="none";
}

//生成分组
function add_group(evt)
{
	remove_error_node()
	var select_obj = document.getElementById("unmerge_id");
	var is_selected = 0;
	var is_all_selected = 1;
	var select_value = new Array();
	var select_text = new Array();
	var select_class = new Array();
	for(var i =0;i<select_obj.options.length;i++)
	{
		if(select_obj.options[i].selected)
		{
			is_selected++;
		}
	}
	
	var num =1;//记录当前的分组数
	var result = document.getElementById("unmerge_result");
	for(var i =0;i<result.childNodes.length;i++)
	{
		if(result.childNodes[i].tagName == "DIV")
		{
			num++;
		}
	}
	
	for(var i =0;i<select_obj.options.length;i++)
	{
		if(select_obj.options[i].selected)
		{
			select_value.push(select_obj.options[i].value);
			select_text.push(select_obj.options[i].text);
			select_class.push(select_obj.options[i].className);
			if(!(is_selected == 1 && select_class[0]=="net"))
			{
				select_obj.options[i].style.display = "none";
				select_obj.options[i].value = num+"="+select_obj.options[i].value;
				select_obj.options[i].selected = false;
			}
		}else{
			is_all_selected = 0;
		}
	}
	
	if(is_selected == 1 && select_class[0]=="net")
	{
		var result = document.getElementById("unmerge_result");
		get_error_node("当前所选已经是一个部门，不能继续分解为部门！",result.parentNode);
	}else if(is_selected>=1 && !is_all_selected)
	{
		var div = document.createElement("div");
		div.innerHTML += "<span class='note'>分组"+num+"成员为: </span><ul>";
		var temp = new Array();
		for(var j = 0;j<select_value.length;j++)
		{
			var values = select_value[j].split("=");
			div.innerHTML += "<li  value='"+select_value[j]+"'  style='text-indent:20px;' >"+select_text[j]+"</li>";
		}
		result.appendChild(div);
	}
	if(!is_selected){
		var result = document.getElementById("unmerge_result");
		get_error_node("没有选择任何节点！",result.parentNode);
	}

}