// JavaScript Document
function show_second_detail(){
   var first_node_name = document.getElementById('first-father').options[document.getElementById('first-father').selectedIndex].value;
   var obj = document.getElementById('second-father');
   obj.options.length = 0;
   obj.options.add(new Option('不选择',''));
   var obj2 = document.getElementById('third-father');
   obj2.options.length = 0;
   obj2.options.add(new Option('不选择',''));
   if(first_node_name=='')
   {
      return;
   }
   $.get('get_sub_node.cgi', {node_name:first_node_name}, function(data){
      if(data!='')
	  {
		 var sub_nodes = new Array();
		 sub_nodes = data.split(',');
		 for(var i=0;i<sub_nodes.length;i++)
		 {
		   if(sub_nodes[i] != '')
		   {
		      obj.options.add(new Option(sub_nodes[i],sub_nodes[i]));
		   }
		 }
	  }
     });
}

function show_third_detail(){
   var first_node_name = document.getElementById('first-father').options[document.getElementById('first-father').selectedIndex].value;
   var second_node_name = document.getElementById('second-father').options[document.getElementById('second-father').selectedIndex].value;
   if(first_node_name=='')
   {
      return;
   }
   var obj = document.getElementById('third-father');
   obj.options.length = 0;
   obj.options.add(new Option('不选择',''));
   if(second_node_name=='')
   {
      return;
   }
   var name = first_node_name + '/' + second_node_name;
   $.get('get_sub_node.cgi', {node_name:name}, function(data){
      if(data!='')
	  {
		 var sub_nodes = new Array();
		 sub_nodes = data.split(',');
		 for(var i=0;i<sub_nodes.length;i++)
		 {
		    if(sub_nodes[i] != '')
			{
		       obj.options.add(new Option(sub_nodes[i],sub_nodes[i]));
			}
		 }
	  }
     });
}

function show_detail(path)
{
    $.get('get_node_info.cgi', {path:path}, function(data){
		$("#pop-divs").remove();
		$("#pop-text-div").remove();
		var str = "<div id='pop-divs'></div>";
		str += "<div   id='pop-text-div' style='height:150px;min-height:0'><div id='pop-text-div-header'><img  id='pop-text-img' src='/images/delete.png  ' onclick='hide()' /></div><table width='100%' class='detail_table'  cellpadding='0' cellspacing='0' border='0'>";
		str += data;
		str += "</table></div>";
		$(str).appendTo("body");
	});
}

function hide()
{
	$("#pop-divs").remove();
	$("#pop-text-div").remove();
}