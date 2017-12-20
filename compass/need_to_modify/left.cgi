#!/usr/bin/perl
require '/var/efw/header.pl';
my %menuhash = ();
my $menu = \%menuhash;
my $useFlavour = 'main';
my %settings = ();
my $systemconfig = "${swroot}/systemconfig/settings";
my %system_settings;
my $system_title;

sub read_config(){
    if ( -f $systemconfig ) {
       &readhash( "$systemconfig", \%system_settings );
    }
    $system_title = $system_settings{'SYSTEM_TITLE'};
}

sub getselected($) {
    my $root = shift;
    if (!$root) {
    return 0;
    }

    foreach my $item (%$root) {
    if ($root->{$item}{'selected'}) {
        return $root->{$item};
    }
    }
}

#显示一级和二级菜单
sub show_all_menu()
{
    printf <<EOF
    <div id="menu-top">
        <ul>
EOF
    ;
    foreach my $k1 ( sort keys %$menu ) {
        if (! $menu->{$k1}{'enabled'}) {
            next;
        }

        my $link = getlink($menu->{$k1});
        if ($link eq '') {
            next;
        }
        if (! is_menu_visible($link)) {
            next;
        }
        if ($menu->{$k1}->{'selected'}) {
            print '<li class="selected">';
        } else {
            print '<li>';
        }

        printf <<EOF
            <div class="rcorner">
                <a href="$link">$menu->{$k1}{'caption'}</a>
            </div>
        </li>
EOF
        ;
    }

    printf <<EOF
        </ul>
    </div>
EOF
    ;

}


#将框架分html写入
sub left_html()
{
    &read_config();
    printf <<EOF
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        <title>$system_title</title>
        <link rel="shortcut icon" href="/images/shortcut.ico" />
        <link rel="stylesheet" type="text/css" href="/include/main.css" />
        <script language="javascript" type="text/javascript" src="/include/jquery.js"></script>
        <script language="javascript" type="text/javascript" src="/include/left-menu.js"></script>
        <script type="text/javascript" src="/include/for_iE6_png.js"></script>
    </head>
    <body id="left-body">
        <div class="left-menu">
            <div id="left-menu-header">
                <span class="arrow">
                    <img src='/images/menu.png' style="margin: 0px 3px -3px 22px;"/>
                </span>%s
            </div>
            <div id="menu-content">
                <dl>
EOF
    ,'管理控制台'
    ;

    showmenu_frame();

    printf <<EOF
                </dl>
            </div>
        </div>
    </body>
</html>
EOF
    ;
}

showhttpheaders();
left_html();