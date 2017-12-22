#!/usr/bin/perl

require '/var/efw/header.pl';

my $name        = "资源配置";
my $extraheader 	= "<link rel='stylesheet' type='text/css' href='/extjs/resources/css/ext-all.css'>
					<link rel='stylesheet' type='text/css' href='/include/resourceset.css'>
					<script type='text/javascript' src='/extjs/ext-debug.js'></script>
					<script language='javascript' type='text/javascript' src='/include/resourceset_manage.js'></script>
					<script language='javascript' type='text/javascript' src='/include/resourceset_list.js'></script>";



showhttpheaders();
openpage($name, 1, $extraheader);
&display_add_resg();
&display_add_res();
&list_res();
closepage();

sub display_add_resg(){
	#添加资源组
	printf <<EOF
<div id="add-div-resg" >
	<div id="add-div-header-resg">
		<span style="display:block;float:left;margin:0px auto auto 10px;"><img src="/images/add.png" /><span>添加资源组</span></span>
	</div>
	<div id="add-div-content-resg"  style="display:none">
		<form name="USER_FORM_RESG" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
			<!--此table是为了消除Firefox中内容漂移问题-->
			<table></table>
			<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
				<tbody>
					<tr class="env">
						<td class="add-div-type need_help">资源组名称*</td>
						<td>
							<input type="text" MaxLength="50" id="resg_name" name="resg_name" value=""/>
						</td>
					</tr>
					<tr class="odd" >
						<td class="add-div-type need_help">描述</td>
						<td >
							<textarea id="resg_description" style="height:150px;width:400px;" name="resg_description" ></textarea>
						</td>
					</tr>
					<tr class="env hidden">
						<td class="add-div-type need_help">是否启用</td>
						<td>
							<input type="checkbox" id="resg_enable" name="orgz_enable" style="vertical-align:middle;padding:0px;margin:0px;" checked>
							<label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
						</td>
					</tr>	   
				</tbody>
			</table>
			<table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
				<tr class="add-div-footer">
					<td width="50%">
						<input class='net_button' type='button' id="resg_submit" value='添加' style="display:block;float:right;color:black" />
					</td>
					<td width="50%">
						<input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEditResg();"/>
						<span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
						<input type="hidden" class="form" name="color" value=""  />
					</td>
				</tr>
			</table>
		</form> 
	</div>
</div>
EOF
;
}

sub display_add_res(){
	
	##添加或者编辑资源控件
	printf <<EOF
<div id="add-div" >
	<div id="add-div-header">
		<span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" /><span>添加资源</span></span>
	</div>
	<div id="add-div-content"  style="display:none">
		<form name="USER_FORM_RESOURCE" enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
			<!--此table是为了消除Firefox中内容漂移问题-->
			<table></table>
			<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed">
				<tbody>
					<tr class="env">
						<td class="add-div-type need_help">资源名称*</td>
						<td>
							<input type="text" MaxLength="50" id="resource_name" name="resource_name" value=""/>
						</td>
					</tr>
					<tr class="odd" >
						<td class="add-div-type need_help">描述</td>
						<td >
							<textarea id="resource_description" style="height:150px;width:400px;" name="resource_description" ></textarea>
						</td>
					</tr>
					<tr class="env">
						<td class="add-div-type need_help">访问方式*</td>
						<td>
							<select id="access_method" name="access_method" onchange="change()" style="width:136px">
							  <option  value="web">WEB访问</option>
							  <option  value="other">其他访问</option>
							</select>
						</td>
					</tr>
					<tr class="odd" >
						<td class="add-div-type need_help">IP地址*</td>
						<td >
							<input type="text" MaxLength="50" id="ip_addr" name="ip_addr" value=""/>
						</td>
					</tr>
					<tr class="env">
						<td class="add-div-type need_help">协议*</td>
						<td>
							<select id="protocol" name="protocol" onchange="" style="width:136px">
							  <option  value="tcp" >TCP</option>
							  <option  value="udp">UDP</option>
							</select>
						</td>
					</tr>
					<tr class="odd" >
						<td class="add-div-type need_help">端口*</td>
						<td >
							<input type="text" MaxLength="50" id="port" name="port" value=""/>
						</td>
					</tr>
					<tr class="env" id="hreftr" style="display:table-row;">
						<td class="add-div-type need_help">URL地址*</td>
						<td>
							<input type="text" MaxLength="50" id="url_addr" name="url_addr" value=""/>
						</td>
					</tr>
					<tr class="odd" >
						<td class="add-div-type need_help">所属资源组</td>
						<td >
							<input type="text" MaxLength="50" id="resource_grep" name="resource_grep" readonly onClick="createTreeWindow('resource_grep')"/>
						</td>
					</tr>
					<tr class="env">
						<td class="add-div-type need_help">是否启用</td>
						<td>
							<input type="checkbox" id="resource_enable" name="orgz_enable" style="vertical-align:middle;padding:0px;margin:0px;" checked>
							<label style="vertical-align:middle;display:inline-block;text-indent:3px;font-weight:normal;padding:0px;">启用</label>
						</td>
					</tr>	   
				</tbody>
			</table>
			<table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
				<tr class="add-div-footer">
					<td width="50%">
						<input class='net_button' type='button' id="resource_submit" value='添加' style="display:block;float:right;color:black" />
					</td>
					<td width="50%">
						<input class='net_button' type='button'  value='撤销' style="display:block;float:left;color:black" onclick="cancelAddOrEditResource();"/>
						<span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
						<input type="hidden" class="form" name="color" value=""  />
					</td>
				</tr>
			</table>
		</form> 
	</div>
</div>
EOF
;
}

##资源列表将挂载在这里
sub list_res() {
printf <<EOF
	<div id='resource_list'></div>
EOF
;
}
