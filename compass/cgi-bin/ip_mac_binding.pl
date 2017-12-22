#!/usr/bin/perl
use strict;
use warnings;

sub openaddbox($$$$@)
{
    my $linktext = shift;
    my $title = shift;
    my $show = shift;
    my $linkname = shift;
    my @errormessages = @_;
    #my @errormessages = $errormessages;
    my $disp_editor = "none";
    my $disp_link = "";
    if ($show eq "showeditor" || $#errormessages ne -1) {
        $disp_link = "none";
        $disp_editor = "";
    }

    if ($linktext ne "") {
        printf <<EOF
    <div id="add-div_ip" >

     <div id="add-div-header_ip">
<span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" />&nbsp;$linktext</span></div>
EOF
        ;
    }
    printf <<EOF
   <div id="add-div-content_ip"  style="display:$disp_editor">
EOF
;

    #if($title ne '') {
    #    printf <<EOF
    #    <div class="editortitle"><b>$title</b></div>
#EOF
    #    ;
    #}
    if ($#errormessages ne -1) {
        printf <<EOF
        <div class="editorerror" name="$linkname">
            <div>
                <ul style="padding-left: 20px">
EOF
        ;
        foreach my $errormessage (@errormessages) {
            printf <<EOF
                    <li style="color: red;">
                        <font color="red">$errormessage</font>
                    </li>
EOF
            ;
        }
        printf <<EOF
                </ul>
            </div>
            <hr size="1" color="#cccccc">
        </div>
EOF
        ;
    }
	printf <<EOF
        <form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' >
EOF
    ;
}
sub openotherbox($$$$@)
{
    my $linktext = shift;
    my $title = shift;
    my $show = shift;
    my $linkname = shift;
    my @errormessages = @_;
    #my @errormessages = $errormessages;
    my $disp_editor = "none";
    my $disp_link = "";
    if ($show eq "showeditor" || $#errormessages ne -1) {
        $disp_link = "none";
        $disp_editor = "";
    }

    if ($linktext ne "") {
        printf <<EOF
    <div id="add-div_ip1" >

     <div id="add-div-header_ip1">
<span style="display:block;float:left;margin:0px auto auto 5px;"><img src="/images/add.png" />&nbsp;$linktext</span></div>
EOF
        ;
    }
    printf <<EOF
   <div id="add-div-content_ip1"  style="display:$disp_editor">
EOF
;

    #if($title ne '') {
    #    printf <<EOF
    #    <div class="editortitle"><b>$title</b></div>
#EOF
    #    ;
    #}
    if ($#errormessages ne -1) {
        printf <<EOF
        <div class="editorerror" name="$linkname">
            <div>
                <ul style="padding-left: 20px">
EOF
        ;
        foreach my $errormessage (@errormessages) {
            printf <<EOF
                    <li style="color: red;">
                        <font color="red">$errormessage</font>
                    </li>
EOF
            ;
        }
        printf <<EOF
                </ul>
            </div>
            <hr size="1" color="#cccccc">
        </div>
EOF
        ;
    }
	printf <<EOF
        <form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}' onsubmit="var label=false;var file= document.getElementsByName('up_file')[0];if(file.value){label=true;}else{alert('请选择文件');} return label;">
EOF
    ;
}

sub closeaddbox
{
    my $submitvalue = shift;
    my $cancelvalue = shift;
    my $submitname = shift;
    my $cancelname = shift;
    my $cancellink = shift;
    
    if ($cancellink eq "") {
        $cancellink = "#$cancelname";
    }
    my $url = "https://".$ENV{'SERVER_ADDR'}.":10443". $ENV{'SCRIPT_NAME'};
    printf <<EOF
<table width="100%" cellpadding="0" cellspacing="0" style="font-size:12px;">
<tr class="add-div-footer"><td width="50%">
<input class='net_button' type='submit' name='$submitname' value='$submitvalue' style="display:block;float:right;color:black" />
</td><td width="50%">
<input class='net_button' type='button'  value='$cancelvalue' style="display:block;float:left;color:black" onclick="parent.window.document.getElementById('rightFrame').src='$url'"/>
<span  style="display:block;float:right;margin:3px 10px auto auto;">* 表示必填项</span>
<input type="hidden" class="form" name="color" value=""  /></td></tr>
</table>
   </form>     
    </div>  </div>	
EOF
    ;
}
sub closeotherbox
{
    my $submitvalue = shift;
    my $cancelvalue = shift;
    my $submitname = shift;
    my $cancelname = shift;
    my $cancellink = shift;
    
    if ($cancellink eq "") {
        $cancellink = "#$cancelname";
    }
    my $url = "https://".$ENV{'SERVER_ADDR'}.":10443". $ENV{'SCRIPT_NAME'};
    printf <<EOF
<input id="fuzhu" style="display:none;" type="text" value="scan_iface" />
   </form>     
    </div>  </div>	
EOF
    ;
}

1;