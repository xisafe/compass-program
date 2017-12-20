/*向上遍历父结点*/      
function nodep(node){
	var bnode=true;
	Ext.Array.each(node.childNodes,function(v){
		if(!v.data.checked){     
			bnode=false;      
			return;        
		}    
	 });      
	 return bnode;
}

function parentnode(node){ 
	if(node.parentNode != null){
		if(nodep(node.parentNode)){
			node.parentNode.set('checked', true);
		}else{
			node.parentNode.set('checked', false);
		}       
		parentnode(node.parentNode);
	}
}
/*遍历子结点 选中 与取消选中操作*/
function chd(node,check){
	node.set('checked',check);
	if(node.isNode){
		node.eachChild(function (child) {
			chd(child,check);
		});
	} 
}