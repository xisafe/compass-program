$(document).ready(function() {
	$('input[name="submit"]').on('click', function() {
		if (!$('input[name="ENABLED"]')[0].checked) {
            object2.option.server_ip.required = '0';
         }
	});
});

Ext.require([
    'Ext.data.TreeStore',
    'Ext.tree.Panel',
	'Ext.window.Window'
]);
Ext.define('OpenvpnuserGroup', {
    extend: 'Ext.data.Model',
    fields: [
       {name: 'text'},
       {name: 'leaf'},
       {name: 'type'},
       {name: 'desc'},
       {name: 'state'},
	   {name: 'expanded'},
       {name: 'full_name'},
	   {name: 'children'},
       {name: 'res'},
	   {name: 'users'}
    ],
    idProperty: 'openvpnusergroup'
});

function createTreeWindow(inputID){
	var groups_store = Ext.create('Ext.data.TreeStore', {
		model: 'OpenvpnuserGroup',
		proxy: {
            type: 'ajax',
            url: '/cgi-bin/sslvpn_users_ctree.cgi',
			actionMethods:{
				read: 'POST'
			}
        },
		autoLoad: true,
        sorters: [{
            property: 'leaf',
            direction: 'ASC'
        }, {
            property: 'text',
            direction: 'ASC'
        }],
		listeners: {
			beforeload: function(store){
				var sync_name = document.getElementsByName('sync_name')[0].value;
				var params ={
					sync_name: sync_name
				};
				Ext.apply(store.proxy.extraParams, params);
			}
		}
	});

	var groups_tree = Ext.getCmp('openvpnusersctreepanel');
	if(!groups_tree){
		groups_tree = Ext.create('Ext.tree.Panel', {
			//width: 200,
			id: 'openvpnusersctreepanel',
			closeAction: 'hide',
			width: document.body.clientWidth*0.37,
			height: 480,
			rootVisible: true,
			root: {
				text: '所有用户',
				id: '所有用户',
				full_name: '所有用户',
				type: 'org',
				desc: '这是根组织结构',
				expanded: true,
				checked: false
			},
			store: groups_store,
			listeners: {
				checkchange:function(node,checked){
					if(checked){
						node.eachChild(function (child) { 
							chd(child,true);
						});
					}else{
						node.eachChild(function (child) {
							chd(child,false);
						});
					}
					//进行父级选中操作
					parentnode(node); 
				}
			}
		});
	}
	
	var groups_tree_window = Ext.getCmp('openvpnusersctreewindow');
	if(!groups_tree_window){
		groups_tree_window = Ext.create('Ext.window.Window', {
			title: '选择用户组',
			id: 'openvpnusersctreewindow',
			closeAction: 'hide',
			height: 500,
			modal: true,
			width: document.body.clientWidth*0.37,
			layout: 'fit',
			items: { 
				xtype: groups_tree
			},
			buttons:[
				{
					text: '确定',
					handler: function(me){
						var nodes = me.up('window').down('treepanel').getChecked();
						var str = "";
						var i = 0;
						var array = new Array();
						for( i = 0; i < nodes.length; i++ ){
							if(nodes[i].data.type == "ug"){
								array.push(nodes[i].data.full_name);
							}
						}
						str = array.join(';');
						var element = document.getElementById(inputID);
						element.value = str;
						me.up('window').close();
					}
				},{
					text: '取消',
					handler: function(me){
						me.up('window').close();
					}
				}
			]
		});
	}
	groups_tree_window.show();
}

function toggleModel(inputID){
	var elems = document.getElementById("sync_policy");
	var tr = document.getElementById("server_ip_tr");
	var service_div = document.getElementById("service_div");
	if(elems.value == "service"){
		tr.style.display = "none";
		service_div.style.display = "block";
	}else if(elems.value == "client"){
		tr.style.display = "table-row";
		service_div.style.display = "none";
	}
}
