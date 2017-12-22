#===============================================================================#
#
# DESCRIPTION: 获取文件的各种操作时间
#
# AUTHOR: 王琳 (WangLin), 245105947@qq.com
# COMPANY: capsheaf
# CREATED: 2014.04.25 - 09:00
#===============================================================================#

#============参数解释=============#
#
# 功能：获取文件最近访问时间(年月日)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件最近访问时间(年月日)
#   eg：传入‘-’, 返回 xxxx-xx-xx
#       传入‘/’, 返回 xxxx/xx/xx
#
#=================================#
sub get_file_atime_by_formatday($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatday = &get_time_by_formatday($atime, $format);
    return $formatday;
}

#============参数解释=============#
#
# 功能：获取文件最近修改时间(年月日)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件最近修改时间(年月日)
#   eg：传入‘-’, 返回 xxxx-xx-xx
#       传入‘/’, 返回 xxxx/xx/xx
#
#=================================#
sub get_file_mtime_by_formatday($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatday = &get_time_by_formatday($mtime, $format);
    return $formatday;
}

#============参数解释=============#
#
# 功能：获取文件创建时间(年月日)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件创建时间(年月日)
#   eg：传入‘-’, 返回 xxxx-xx-xx
#       传入‘/’, 返回 xxxx/xx/xx
#
#=================================#
sub get_file_ctime_by_formatday($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatday = &get_time_by_formatday($ctime, $format);
    return $formatday;
}

#============参数解释=============#
#
# 功能：获取文件最近访问时间(时分秒)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件最近访问时间(时分秒)
#   eg：传入‘-’, 返回 xx-xx-xx
#       传入‘/’, 返回 xx/xx/xx
#       传入‘:’, 返回 xx:xx:xx
#
#=================================#
sub get_file_atime_by_formatdaytime($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatdaytime = &get_time_by_formatdaytime($atime, $format);
    return $formatdaytime;
}

#============参数解释=============#
#
# 功能：获取文件最近修改时间(时分秒)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件最近修改时间(时分秒)
#   eg：传入‘-’, 返回 xx-xx-xx
#       传入‘/’, 返回 xx/xx/xx
#       传入‘:’, 返回 xx:xx:xx
#
#=================================#
sub get_file_mtime_by_formatdaytime($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatdaytime = &get_time_by_formatdaytime($mtime, $format);
    return $formatdaytime;
}

#============参数解释=============#
#
# 功能：获取文件创建时间(时分秒)
#
# 参数：filename -- 要获取时间的文件名
#       format -- 输出格式，任意字符
#
# 返回：文件创建时间(时分秒)
#   eg：传入‘-’, 返回 xx-xx-xx
#       传入‘/’, 返回 xx/xx/xx
#       传入‘:’, 返回 xx:xx:xx
#
#=================================#
sub get_file_ctime_by_formatdaytime($$) {
    my $filename = shift;
    my $format = shift;
    my ($atime, $mtime, $ctime) = &get_file_relevant_time_by_sec($filename);
    my $formatdaytime = &get_time_by_formatdaytime($ctime, $format);
    return $formatdaytime;
}

#====依次返回最近访问时间、最近修改时间和创建时间===#
sub get_file_relevant_time_by_sec($) {
    my $filename = shift;
    my ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blsize, $blocks);
    if( -e $filename ) {
        ($dev, $ino, $mode, $nlink, $uid, $gid, $rdev, $size, $atime, $mtime, $ctime, $blsize, $blocks) = stat($filename);
    } else {
        ($atime, $mtime, $ctime) = (0, 0, 0);
    }
    return ($atime, $mtime, $ctime);
}

sub get_time_by_ymdhmsw($) {
    my $timestamp = shift;
    my ($sec, $min, $hour, $mday, $mon, $year_off, $wday, $yday, $isdat) = gmtime($timestamp + 8 * 60 * 60);#针对我们地区，要加8小时
    my $test = $year_off."-".$mon."-".$mday."-".$hour."-".$min."-".$sec."-".$wday;
    return ($year_off + 1900, $mon + 1, $mday, $hour, $min, $sec, $wday + 1);
}

sub get_time_by_ymd($) {
    my $timestamp = shift;
    my ($year, $mon, $mday, $hour, $min, $sec, $wday) = &get_time_by_ymdhmsw($timestamp);
    return ($year, $mon, $mday);
}

sub get_time_by_hms($) {
    my $timestamp = shift;
    my ($year, $mon, $mday, $hour, $min, $sec, $wday) = &get_time_by_ymdhmsw($timestamp);
    return ($hour, $min, $sec);
}

sub get_time_by_week($) {
    my $timestamp = shift;
    my ($year, $mon, $mday, $hour, $min, $sec, $wday) = &get_time_by_ymdhmsw($timestamp);
    return ($wday);
}

sub get_time_by_formatday($$) {
    my $timestamp = shift;
    my $format = shift;
    my @times = &get_time_by_ymd($timestamp);
    #===第一步,将小于10的月、日前面加上0===#
    if($times[1] < 10) {
        $times[1] = "0".$times[1];
    }
    if($times[2] < 10) {
        $times[2] = "0".$times[2];
    }
    #===第二步,格式化日期,返回===#
    return join $format, @times;
}

sub get_time_by_formatdaytime($$) {
    my $timestamp = shift;
    my $format = shift;
    my @times = &get_time_by_hms($timestamp);
    #===第一步,将小于10数字前面加上0===#
    if($times[0] < 10) {
        $times[0] = "0".$times[0];
    }
    if($times[1] < 10) {
        $times[1] = "0".$times[1];
    }
    if($times[2] < 10) {
        $times[2] = "0".$times[2];
    }
    #===第二步,格式化日期,返回===#
    return join $format, @times;
}

return 1;
