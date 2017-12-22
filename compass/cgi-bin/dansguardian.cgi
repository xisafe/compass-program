#!/usr/bin/perl

require '/home/httpd/cgi-bin/proxy.pl';
require 'netwizard_tools.pl';
require '/var/efw/header.pl';
# -------------------------------------------------------------
# some definitions
# -------------------------------------------------------------
my $blackdir    = "/etc/dansguardian/blacklists";
my $phrasedir   = "/etc/dansguardian/phraselists";

my $havpfile = "/var/efw/dansguardian/enable_havp";
my $startingfile = "/var/efw/dansguardian/STARTING";
my $dansguardian_dir = "/var/efw/dansguardian/";
my $exceptionsitelist_file = "${swroot}/dansguardian/exceptionsitelist";
my $exceptioniplist_file = "${swroot}/dansguardian/exceptioniplist";
my $bannedsitelist_file = "${swroot}/dansguardian/bannedsitelist";
my $bannediplist_file = "${swroot}/dansguardian/bannediplist";

my $name        = _('Content filter');
my %checked     = ( 0 => '', 1 => 'checked', 'on' => 'checked');
my $title = _("添加配置");
my %conf;

my %par;

my %conf_blacklist;
my %conf_phraselist;

my $exceptionsitelist = '';
my $exceptioniplist = '';
my $bannedsitelist = '';
my $bannediplist = '';
my $bannedphraselist = '';#新增变量 by wl 2014.04.14
my $bannedregexpurllist= '';#新增变量 by wl 2014.04.14

my @blacklist;
my @phraselist;
my $scripts = '<script type="text/javascript" src="/include/serviceswitch.js"></script>
                <script type="text/javascript" src="/include/waiting.js"></script>
                <script type="text/javascript" src="/include/category.js"></script>
                <script type="text/javascript" src="/include/dansguardian.js"></script>
                <script type="text/javascript" src="/include/serviceswitch.js"></script>
                <script type="text/javascript" src="/include/waiting.js"></script>';
my $errormessage = "";
my $warnmessage = "";
my $notemessage = "";
my @errormessages;
my $edit_line = "";
######zhouyuan 2011-09-27  添加帮助信息##########
my $help_hash1 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-配置文件名","-10","10","down");

my $help_hash2 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-因特网内容平台","-10","10","down");

my $help_hash3 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-短语最大得分","-10","10","down");

my $help_hash4 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-页面过滤包含以下策略","-10","10","down");

my $help_hash5 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-过滤页面包含以下分类(URL黑名单)","-10","10","down");

my $help_hash6 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-定制黑白名单","-10","10","down");

my $help_hash7 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-定制黑白名单-允许以下站点","-10","10","down");

my $help_hash8 = read_json("/home/httpd/help/dansguardian_help.json","dansguardian.cgi","代理-HTTP-内容过滤-生成配置-定制黑白名单-禁止以下站点","-10","10","down");

#################################################

##########程序主体部分###########################
&validateUser();
&getcgihash(\%par);
&do_action();
my ($default_proxy_conf_ref, $proxy_conf_ref) = reload_par();
my %proxy_conf = %$proxy_conf_ref;
&showhttpheaders();
openpage(_("HTTP Configuration"), 1, $scripts);
&showapplybox(\%proxy_conf); 
&openbigbox($errormessage, $warnmessage, $notemessage);
&display_add();
&display_list();
&check_form();
&closepage();
################################################

sub check_hosts($) { #check if the checkhosts are valid
    my $name = shift;
    my $error = "";
    if($par{$name} ne ""){
        my @temp = split(/\n/,$par{$name});
        
        foreach my $line (@temp){
            $line =~ s/^\s+//g;
            $line =~ s/\s+$//g;
            
            if ($line) {
            
                if($line =~ /^\d+\.\d+\.\d+\.\d+$/){
                    if(!check_ip($line, "255.255.255.0")){
                        $error .= _($line."不是一个有效的IP地址")."<br />";
                    }
                }
                else{
                    if (!validdomainname($line)) {
                        $error .= _($line."不是一个有效的域名")."<br />";
                    }
                }
            }
        }
        
    return $error;

    }
}


sub save_dg_profile($) {
    my $id = shift;
    
    my ($exceptionsitelist_file, $bannedsitelist_file, $bannedphraselist_file, $bannedregexpurllist_file)= ("", "", "", "");
    my $cpfile;

    if ($id eq "content1") {
        $exceptionsitelist_file = "$dg_dir/exceptionsitelist";
        $bannedsitelist_file = "$dg_dir/bannedsitelist";
        $bannedphraselist_file = "$dg_dir/bannedphraselist";
        $bannedregexpurllist_file = "$dg_dir/bannedregexpurllist";
        $cpfile = "$dg_dir/settings";
        open (OUT, ">$dg_dir/settings"); 
        print OUT "ENABLE_DANSGUARDIAN=$conf{'ENABLE_DANSGUARDIAN'}\n";
    }
    else {
        if (! -d "$dg_profiledir") {
            system("mkdir $dg_profiledir");
        }
        if (! -d "$dg_profiledir/$id") {
            system("mkdir $dg_profiledir/$id");
        }
        
        $exceptionsitelist_file = "$dg_profiledir/$id/exceptionsitelist";
        $bannedsitelist_file = "$dg_profiledir/$id/bannedsitelist";
        $bannedphraselist_file = "$dg_profiledir/$id/bannedphraselist";
        $bannedregexpurllist_file = "$dg_profiledir/$id/bannedregexpurllist";
        $cpfile = "$dg_profiledir/$id/settings";
        open (OUT, ">$dg_profiledir/$id/settings");
    }
    print OUT "NAME=$conf{'NAME'}\n";
    print OUT "HAVP=$conf{'HAVP'}\n";
    print OUT "PICS_ENABLE=$conf{'PICS_ENABLE'}\n";
    print OUT "PORT=$conf{'PORT'}\n";
    print OUT "NAUGHTYNESSLIMIT=$conf{'NAUGHTYNESSLIMIT'}\n";
    print OUT "BLACKLIST=$conf{'BLACKLIST'}\n";
    print OUT "PHRASELIST=$conf{'PHRASELIST'}\n";
    close OUT;
    
    open (OUT, ">$exceptionsitelist_file");
    print OUT $conf{'EXCEPTIONSITELIST'};
    close OUT;
    open (OUT, ">$bannedsitelist_file");
    print OUT $conf{'BANNEDSITELIST'};
    close OUT;
    open (OUT, ">$bannedphraselist_file");
    print OUT $conf{'BANNEDPHRASELIST'};
    close OUT;
    open (OUT, ">$bannedregexpurllist_file");
    print OUT $conf{'BANNEDREGEXPURLLIST'};
    close OUT;
    system("touch $proxyreload");
    system("sudo fmodify $dg_profiledir/$id/settings");
    system("sudo fmodify $exceptionsitelist_file");
    system("sudo fmodify $bannedsitelist_file");
    system("sudo fmodify $bannedphraselist_file");
    system("sudo fmodify $bannedregexpurllist_file");
}

sub read_dg_profile($) {
    my $id = shift;
    
    my ($exceptionsitelist_file, $bannedsitelist_file, $bannedphraselist_file, $bannedregexpurllist_file)= ("", "", "", "");
    
    if ($id eq "") {
        %conf = ();
        if (-e $dg_conf_default) {
            readhash($dg_conf_default, \%conf);
        }
    }
    elsif ($id eq "content1") {
        if (-e $dg_conf_default) {
            readhash($dg_conf_default, \%conf);
        }
        if (-e $dg_conf) {
            readhash($dg_conf, \%conf);
        }
        
        $exceptionsitelist_file = "$dg_dir/exceptionsitelist";
        $bannedsitelist_file = "$dg_dir/bannedsitelist";
        $bannedphraselist_file = "$dg_dir/bannedphraselist";
        $bannedregexpurllist_file = "$dg_dir/bannedregexpurllist";
        
        $conf{'NAME'} = _("Default Profile");
    }
    else {
        %conf = ();
        if (-e $dg_conf_default) {
            readhash($dg_conf_default, \%conf);
        }
        if (-e "$dg_profiledir/$id/settings") {
            readhash("$dg_profiledir/$id/settings", \%conf);
        }
        
        $exceptionsitelist_file = "$dg_profiledir/$id/exceptionsitelist";
        $bannedsitelist_file = "$dg_profiledir/$id/bannedsitelist";
        $bannedphraselist_file = "$dg_profiledir/$id/bannedphraselist";
        $bannedregexpurllist_file = "$dg_profiledir/$id/bannedregexpurllist";
    }
    
    $conf{'ID'} = $id;
    
    if (-e "$blackdir/categories") {
        readhash("$blackdir/categories", \%blackcategories);
    }
    else {
        %blackcategories = ();
    }
    
    if (-e "$phrasedir/categories") {
        readhash("$phrasedir/categories", \%phrasecategories);
    }
    else {
        %phrasecategories = ();
    }
        
    @blacklist  = split(/\n/, `ls $blackdir | grep -v CATEGORIES | grep -v blacklists.info `);
    @phraselist = split(/\n/, `ls $phrasedir`);

    %conf_blacklist = ();
    foreach my $item (split(/;/, $conf{'BLACKLIST'})) {
        $conf_blacklist{"BL_" . $item} = 'on';
    }

    %conf_phraselist = ();
    foreach my $item (split(/;/, $conf{'PHRASELIST'})) {
        $conf_phraselist{"PH_" . $item} = 'on';
    }
    
    if ( -e $exceptionsitelist_file) {
        $exceptionsitelist = `cat $exceptionsitelist_file 2>/dev/null`;
        $conf{'EXCEPTIONSITELIST'} = $exceptionsitelist;
    }
    if (-e $bannedsitelist_file) {
        $bannedsitelist = `cat $bannedsitelist_file 2>/dev/null`;
        $conf{'BANNEDSITELIST'} = $bannedsitelist;
    }
    if (-e $bannedphraselist_file) {
        $bannedphraselist = `cat $bannedphraselist_file 2>/dev/null`;
        $conf{'BANNEDPHRASELIST'} = $bannedphraselist;
    }
    if (-e $bannedregexpurllist_file) {
        $bannedregexpurllist = `cat $bannedregexpurllist_file 2>/dev/null`;
        $conf{'BANNEDREGEXPURLLIST'} = $bannedregexpurllist;
    }
}

sub delete_dg_profile() {
    $profile_used = "false";
    if ( $profile_used eq "false" ) {
        $rmdir = "$dg_profiledir/$par{'PROFILE'}";
        system("rm -R \"$rmdir\"");
        system("touch $proxyreload");
        system("sudo fdelete $rmdir");
    }
}

sub check_form()
{
    #表单检查代码添加-2012-08-30-zhouyuan
    #===Modified by wl 2014.04.14===#
    printf <<EOF
    <script>
    var object = {
       'form_name':'DANSGUARDIAN_FORM',
       'option'   :{
            'BANNEDPHRASELIST':{
               'type':'textarea',
               'required':'0',
               'check':'other|',
               'other_reg':'!/^\$/',
               'ass_check':function(eve){
                    var my_value = eve._getCURElementsByName('BANNEDPHRASELIST','textarea',"DANSGUARDIAN_FORM")[0].value;
                    var values = my_value.split("\\n");
                    var regex = new RegExp("\^\<\.\*\>\$");
                    for(var i = 0; i < values.length; i++) {
                        if(!regex.test(values[i])) {
                            return "关键字书写不正确,应放在\<\>中";
                        }
                    }
                }
            },
            'BANNEDREGEXPURLLIST':{
               'type':'textarea',
               'required':'0',
               'check':'other|',
               'other_reg':'!/^\$/',
               'ass_check':function(eve){
                    
                }
            },
            'NAME':{
               'type':'text',
               'required':'0',
               'check':'name|',
            },
            'NAUGHTYNESSLIMIT':{
               'type':'text',
               'required':'1',
               'check':'num|',
               "ass_check":function(eve){
                    var max = eve._getCURElementsByName('NAUGHTYNESSLIMIT','input',"DANSGUARDIAN_FORM")[0].value;
                    var msg = "";
                    if(max<50 || max>300){
                        msg="最大短语得分应该在50-300之间！";
                    }
                    return msg;
                }
            },
            'EXCEPTIONSITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'ip|domain|',
            },
            'BANNEDSITELIST':{
               'type':'textarea',
               'required':'0',
               'check':'ip|domain|',
            },
        }
    }
    var check = new  ChinArk_forms();
    check._main(object);
    //check._get_form_obj_table("DANSGUARDIAN_FORM");
    </script>
EOF
    ;
}

sub do_action() {
    #check_for_errors();

    if ($par{'ACTION'} eq 'apply'){
        &log(_('Apply proxy settings'));
        &applyaction();
    }

    my $is_edit = $par{'is_edit'};
    if ( $par{'ACTION'} eq "save") {
        
        # TODO: check error return code from restartscripts
        # TODO: check the log to see if this does not take too long!
        #
        if ($par{'PROFILE'} eq "") {
            my $tmpdir = "$dg_profiledir/content";
            my $i = 2;
            my $dir = "$tmpdir$i";
            $par{'PROFILE'} = "content$i";
            while ( -d "$dir" ) {
                $dir = "$tmpdir$i";
                $par{'PROFILE'} = "content$i";
                $i++;
            }
            mkdir($dir);
        }
        
        my $id = $par{'PROFILE'};
        my $is_true = 1;
        read_dg_profile($id);
        
        my $logid = "$0 [" . scalar(localtime) . "]";
        
        my $name = $par{'NAME'};
        
        my $havp = 'off';
        if ($par{'HAVP'} eq 'on') {
            $havp = 'on';
        }
        
        my $pics_enable = 'off'; 
        if ($par{'PICS_ENABLE'} eq 'on') {
            $pics_enable = 'on';
        }

        if ($par{'NAUGHTYNESSLIMIT'} !~ /^\d+$/) {   
            $errormessage = _("最大短语得分含有非法字符");
            $is_true = 0;
        }elsif ($par{'NAUGHTYNESSLIMIT'} < 50) {   
            $errormessage = _("Max. score for phrases is no valid");
            $is_true = 0;
        }elsif ($par{'NAUGHTYNESSLIMIT'} > 300) {
            $errormessage = _("Max. score for phrases is no valid");
            $is_true = 0;
        }
            
        my $save_phraselist="";
        foreach my $item (@phraselist) {
            chomp;
                if ($par{'PH_'.$item} eq 1) {
                $save_phraselist .= "$item;"; 
            }
        }
        
        my $save_blacklist="";
        foreach my $item (@blacklist) {
            chomp;
            if ($par{'BL_'.$item} eq 1) {
                $save_blacklist .= "$item;"; 
            }
        }
        $errormessage .= check_hosts("EXCEPTIONSITELIST");
        
        $errormessage .= check_hosts("BANNEDSITELIST");
        
        if(!$errormessage && $is_true){
            if ( ($conf{'NAME'} ne $name) ||
                 ($conf{'HAVP'} ne $havp) ||
                 ($conf{'PICS_ENABLE'} ne $pics_enable) ||
                 ($conf{'PORT'} != $par{'PORT'}) ||
                 ($conf{'NAUGHTYNESSLIMIT'} != $par{'NAUGHTYNESSLIMIT'}) ||
                 ($conf{'PHRASELIST'} ne $save_phraselist) ||
                 ($conf{'BLACKLIST'} ne $save_blacklist) ||
                 ($conf{'EXCEPTIONSITELIST'} ne $par{'EXCEPTIONSITELIST'}) ||
                 ($conf{'BANNEDSITELIST'} ne $par{'BANNEDSITELIST'}) ||
                 ($conf{'BANNEDPHRASELIST'} ne $par{'BANNEDPHRASELIST'}) ||
                 ($conf{'BANNEDREGEXPURLLIST'} ne $par{'BANNEDREGEXPURLLIST'})
             ) {
                print STDERR "$logid: writing new configuration file\n";
                
                $conf{'NAME'} = $name;
                $conf{'HAVP'} = $havp;
                $conf{'PICS_ENABLE'} = $pics_enable;
                $conf{'PORT'} = $par{'PORT'};
                $conf{'NAUGHTYNESSLIMIT'} = $par{'NAUGHTYNESSLIMIT'};
                $conf{'PHRASELIST'} = $save_phraselist;
                $conf{'BLACKLIST'} = $save_blacklist;
                $conf{'EXCEPTIONSITELIST'} = $par{'EXCEPTIONSITELIST'};
                $conf{'BANNEDSITELIST'} = $par{'BANNEDSITELIST'};
                $conf{'BANNEDPHRASELIST'} = $par{'BANNEDPHRASELIST'};
                $conf{'BANNEDREGEXPURLLIST'} = $par{'BANNEDREGEXPURLLIST'};
                
                save_dg_profile($id);
                $notemessage = _("操作成功");
            }
        }
        else{
            if($is_edit ne 'y'){delete_dg_profile()};
        }
    }
    if ( $par{'ACTION'} eq "delete" ) {
        delete_dg_profile();
        $notemessage = _("Config successfully deleted.");
    }

    if ( $par{'ACTION'} eq "edit") {
        #create profile -> now rules can be added on begin
        #require 'dansguardian-profile.pl';
        read_dg_profile($par{'PROFILE'});
        $button = _("Update profile");
        $show = "showeditor";
        $title = "编辑配置";
        
    }
    else {
        read_dg_profile("");
        $button = _("Create profile");
        $show = "";
    }
}

sub display_add() {
    openeditorbox($title, _("Profile editor"), $show, "addrule", @errormessages);
    printf <<EOF
    </form>
    <form name="DANSGUARDIAN_FORM" method="post" ACTION="$ENV{'SCRIPT_NAME'}" >
        <table width="100%">
            <tr class="env">
                <td class="add-div-type need_help">%s $help_hash1</td>
EOF
    ,_('Profile Name'),
    ;
    my $disabled = "";
    if ($conf{'ID'} eq "content1") {
        $disabled="disabled";
    }
    printf <<EOF
                <td>
                    <input type='text' name='NAME' $disabled value='$conf{'NAME'}'/>
                    <input type='hidden' name='PROFILE' value='$conf{'ID'}'/>
                    <input type="hidden" name="is_edit" value= "$par{'is_edit'}" />
                    <input type='hidden' name='ACTION' value='save'/>
                </td>
            </tr>

            <!-- NAUGHTYNESSLIMIT, PICS, SAVE  -->

            <tr class="odd">
                <td  class="add-div-type">%s </td>
                <td> <input type='checkbox' name='HAVP' $checked{$conf{'HAVP'}} />
                </td>
            </td>
            <tr class="env">
                <td  class="add-div-type need_help">%s $help_hash2</td><td>
                 <input type='checkbox' name='PICS_ENABLE' $checked{$conf{'PICS_ENABLE'}} />
                </td>

            </tr>

            <tr class="odd">
                <td  class="add-div-type need_help">%s* $help_hash3</td>
                <td><input type='text' name='NAUGHTYNESSLIMIT' value='$conf{'NAUGHTYNESSLIMIT'}' size='3'/>
                </td>
            </tr>
        </table>
EOF
    ,
    _('Activate antivirus scan'),
    _('Platform for Internet Content Selection'),
    _('最大短语得分'),
    ;

    printf <<EOF
    <div class="phraselist">
        %s
EOF
    ,get_folding("PHRASELIST", "start", '基于页面关键字列表的过滤', "", "<img class=\"statusall\" name=\"phraselist\" src=\"/images/accept.png\" />"),
    ;

    my $uncategorized = "";
    my %tmp = %phrasecategories;
    %phrasecategories = ();

    my $uncategorized = "";
    foreach my $b (@phraselist) {
        my $found = 0;
        if ($b eq "categories") {
            next;
        }
        foreach my $c (keys %tmp) {
            foreach my $cb (split(/\|/, $tmp{$c})) {
                if ($b eq $cb) {
                    $found = 1;
                    $phrasecategories{$c} .= "$b|";
                    last;
                }
            }
            if ($found eq 1) {
                last;
            }
        }
        if ($found eq 0) {
            $uncategorized .= "$b|";
        }
    }

    $phrasecategories{'uncategorized'} = $uncategorized;

    my $catcount = scalar(keys %phrasecategories);
    my $count = 0;
        print "<table>";
    foreach my $cat (sort(keys %phrasecategories)) {
        if ($cat eq "categories" || $phrasecategories{$cat} eq "") {
            next;
        }
        undef %is_in_cat;
        my $countchecked = 0;
        my $countnotchecked = 0;
        for (split(/\|/, $phrasecategories{$cat})) {
            if ($_ eq "categories") {
                next;
            }
            $is_in_cat{$_} = 1;
            if ($conf_phraselist{"PH_" . $_} ne "on") {
                $countnotchecked++;
            }
            else {
                $countchecked++;
            }
        }

        my $allchecked = "none";

        if ($countnotchecked eq 0) {
            $allchecked = "all";
        }
        elsif ($countchecked ne 0) {
            $allchecked = "some";
        }

        my $catname = $cat;
        $catname =~ s/_/ /g;

        if ($count % 2 == 0) {
            print "<tr class=\"categorytable\" ><td style=\"width:50%;\"  vlign=\"top\">";
        }
        else {
            print "<td style=\"width:50%;\" vlign=\"top\">";
        }
        
        my %subcategories = ();
        
        for my $item (@phraselist) {
            if ($item eq "categories") {
                next;
            }
            if ($is_in_cat{$item} eq 1) {
                $subcategories{"PH_$item"} = _(ucfirst($item));
            }
        }
        get_category("phrase_$cat", _(ucfirst($catname)), $allchecked, \%subcategories, \%conf_phraselist);
        
        if ($count % 2 == 0) {
            print "</td>";
        }
        else {
            print "</td></tr>";
        }
        
        $count++;
    }
    print "</table>";
    printf <<EOF
        %s
    </div>
    <div>
        %s
        <table border="0" cellspacing="0" cellpadding="0" width="100%">
            <tr class="odd">
                <td class="add-div-type need_help">自定义关键字</td>
                <td>
                    <textarea name="BANNEDPHRASELIST" style="width: 300px; height: 100px;">$bannedphraselist</textarea>
                    (每行一个)
                </td>
                
            </tr>
        </table>
        %s
    </div>
EOF
    ,get_folding()
    ,get_folding("CUSTOMLIST", "start", "基于页面自定义关键字列表的过滤")
    ,get_folding()
    ;
    printf <<EOF
    <div class="blacklist">
        %s
EOF
    ,
    get_folding("BLACKLIST", "start", '基于页面关键字分类的URL过滤（URL黑名单）', "", "<img class=\"statusall\" name=\"blacklist\" src=\"/images/accept.png\" />"),
    ;

    my %tmp = %blackcategories;
    %blackcategories = ();

    my $uncategorized = "";
    foreach my $b (@blacklist) {
        my $found = 0;
        if ($b eq "categories") {
            next;
        }
        foreach my $c (keys %tmp) {
            foreach my $cb (split(/\|/, $tmp{$c})) {
                if ($b eq $cb) {
                    $found = 1;
                    $blackcategories{$c} .= "$b|";
                    last;
                }
            }
            if ($found eq 1) {
                last;
            }
        }
        if ($found eq 0) {
            $uncategorized .= "$b|";
        }
    }

    $blackcategories{'uncategorized'} = $uncategorized;

    my $catcount = scalar(keys %blackcategories);
    if (($catcount % 2) == 0) {
        $catcount++;
    }
    my $count = 0;
    print "<table>";
    foreach my $cat (sort(keys %blackcategories)) {
        if ($cat eq "categories" || $blackcategories{$cat} eq "") {
            next;
        }
        undef %is_in_cat;
        my $countchecked = 0;
        my $countnotchecked = 0;
        for (split(/\|/, $blackcategories{$cat})) {
            if ($_ eq "categories") {
                next;
            }
            $is_in_cat{$_} = 1;
            if ($conf_blacklist{"BL_" . $_} ne "on") {
                $countnotchecked++;
            }
            else {
                $countchecked++;
            }
        }

        my $allchecked = "none";

        if ($countnotchecked eq 0) {
            $allchecked = "all";
        }
        elsif ($countchecked ne 0) {
            $allchecked = "some";
        }

        my $catname = $cat;
        $catname =~ s/_/ /g;
        
        if ($count % 2 == 0) {
            print "<tr class=\"categorytable\" ><td style=\"width:50%;\">";
        }
        else {
            print "<td style=\"width:50%;\">";
        }
        
        my %subcategories = ();
        
        for my $item (@blacklist) {
            if ($item eq "categories") {
                next;
            }
            if ($is_in_cat{$item} eq 1) {
                $subcategories{"BL_$item"} = _(ucfirst($item));
            }
        }
        get_category("black_$cat", _(ucfirst($catname)), $allchecked, \%subcategories, \%conf_blacklist);
        
        
        if ($count % 2 == 0) {
            print "</td>";
        }
        else {
            print "</td></tr>";
        }
        
        $count++;
    }
    print "</table>";
    printf <<EOF
        %s
    </div>
    <div>
        %s
        <table border="0" cellspacing="0" cellpadding="0" width="100%">
            <tr class="odd">
                <td class="add-div-type need_help">自定义关键字</td>
                <td>
                    <textarea name="BANNEDREGEXPURLLIST" style="width: 300px; height: 100px;">$bannedregexpurllist</textarea>
                    (每行一个)
                </td>
                
            </tr>
        </table>
        %s
    </div>
EOF
    ,get_folding()
    ,get_folding("CUSTOMLIST", "start", "基于页面自定义关键字分类的URL过滤（URL黑名单）")
    ,get_folding()
;
    printf <<EOF
    <div>
        %s
EOF
    ,
    get_folding("CUSTOMLIST", "start", _('定制黑白名单'));
    
    printf <<EOF
    
        <table border="0" cellspacing="0" cellpadding="0" width="100%">
            <tr class="odd">
                <td class="add-div-type need_help">%s $help_hash7</td>
                <td>
                    <textarea style="width: 300px; height: 100px;" name="EXCEPTIONSITELIST">$exceptionsitelist</textarea>
                </td>
                
            </tr>
            <tr class="odd">
               <td class="add-div-type need_help">%s $help_hash8</td>
                <td>
                    <textarea style="width: 300px; height: 100px;" name="BANNEDSITELIST">$bannedsitelist</textarea>
                </td>
            </tr>
        </table>
        %s
    </div>
EOF
    ,
    _('Allow the following sites'),
    _('Block the following sites'),
    get_folding(),
    ;
    my $allow = _("categories are accepted");
    my $partial = _("some categories are blocked");
    my $deny = _("categories are blocked");
    my $legend = "<br/><table><tr><td><img src=\"/images/accept.png\"/></td><td>$allow</td></tr>
                  <tr><td><img src=\"/images/partial.png\"/></td><td>$partial</td></tr>
                  <tr><td><img src=\"/images/deny.png\"/></td><td>$deny</td></tr></table>";
    closeeditorbox($button, _("Cancel"), "rulebutton", "addrule", "$ENV{'SCRIPT_NAME'}", $legend);
}

sub display_list() {
    printf <<EOF
    <table class="ruleslist" width="100%" cellspacing="0" cellpadding="0">
        <tr class='odd'>
            <td class="boldbase" width="5%">#</td>
            <td class="boldbase" width="55%">%s</td>
            <td class="boldbase" width="40%">%s</td>
        </tr>
EOF
    ,
    _('Profile Name'),
    _('Actions')
    ;

    $count = 0;
    foreach my $id (@{get_dg_profiles()}) {
        if ( $count % 2 eq 1 ) {
            print "<tr class='env'>";
        }
        else {
            print "<tr class='odd'>";
        }
        $count++;
        printf <<EOF
            <td>$id</td>
            <td>%s</td>
            <td class="actions">
                <form enctype='multipart/form-data' method='post' action='$ENV{SCRIPT_NAME}'>
                    <input type='hidden' name='ACTION' value='edit' />
                    <input type='hidden' name='PROFILE' value='$id' />
                    <input type='hidden' name='is_edit' value='y' />
                    <input class="imagebutton" type='image' name='submit' src='$EDIT_PNG' alt='%s' title='%s' />
                </form>
EOF
        ,
        get_dg_profile_info($id),
        _("Edit"),
        _("Edit profile"),
        ;
        if ($id ne "content1") {
            printf <<END
            <form enctype="multipart/form-data" method="post" onsubmit="return confirm('%s');" action="$ENV{SCRIPT_NAME}">
                <input type="hidden" name="ACTION" value="delete" />
                <input type="hidden" name="PROFILE" value="$id" />
                <input class="imagebutton" type="image" name="submit" src="$DELETE_PNG" alt="%s" title="%s" />
            </form>
END
            ,_("确认删除?"),
            _("Remove"),
            _("Remove profile")
            ;
        }
        printf <<EOF
            </td>
        </tr>
EOF
            ;
    }
    printf <<EOF
    </table>
    <table  class="list-legend" cellpadding="0" cellspacing="0" >
        <tr>
            <td>&nbsp; <b>%s:</b>
            <img src='$EDIT_PNG' alt="%s" />
            %s
            <img src="$DELETE_PNG" alt="%s" />
            %s</td>
        </tr>
    </table>
    <br /><br /><br /><br /><br />
EOF
    ,
    _('Legend'),
    _('Edit'),
    _('Edit profile'),
    _('Delete'),
    _('删除')
    ;
}