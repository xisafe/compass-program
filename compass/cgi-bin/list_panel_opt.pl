#!/usr/bin/perl
#==============================================================================#
#
# 描述: 列表翻页类页面头文件,主要用于数据的增删改查
#
# 作者: 王琳 (WangLin), 245105947@qq.com
# 公司: capsheaf
# 历史:
#   2014.08.05 WangLin创建
#
#==============================================================================#

require '/var/efw/header.pl';

# $DEBUG  = "ON";#等于其他值不打印debug信息
$DEBUG  = "OFF";

$READ_OPEN_ERROR    = "读取数据时，打开文件失败";
$WRITE_OPEN_ERROR   = "写入数据时，打开文件失败";

$NONE_READ_ERROR    = "未读取数据";
$NONE_WRITE_ERROR   = "未写入数据";
$NONE_CHANGE_ERROR  = "数据没有变化";

$READ_SUCCEEDED     = "读取数据成功";
$WRITE_SUCCEEDED    = "写入数据成功";

$FILE_NOT_FOUND     = "文件不存在";

#==================================================#
#
# 功能: 打印调试信息
#
# 参数：debug_info -- 打印的消息
#
# 返回: 无
#
#==================================================#
sub debug($) {
    my $debug_info = shift;

    if( $DEBUG eq "ON" ) {
        print "$debug_info\n";
    }
}

#author:PT 
sub debug2file($$){ 
        # return false;
        my $str = shift; 
        my $filepath = shift; 
        if (!$filepath){ $filepath = '/var/efw/debug.log';} 
        open(FILE, ">>$filepath") or die "Cant append to $filepath: $!"; 
                print FILE $str ; 
                print FILE "\n"; 
        close(FILE); 
} 



#==================================================#
#
# 功能: 输入以splitor分割的字符串，返回键和值一样的hash
#
# 参数：keys -- 以splitor分割的字符串，
#               类似“1&2&5”之类的字符串
#       splitor -- key值之间的分隔符
#
# 返回: 储存key值的hash
#
# 例子：调用get_record_keys_hash( “6|7|8”, “\|”)，输出
#       (
#           6 => 6,
#           7 => 7,
#           8 => 8,
#       ) 
#       的哈希
#
#==================================================#
sub get_record_keys_hash($$) {
    my $keys = shift;
    my $splitor = shift;

    my %keys_hash;
    my @keys_array = split( $splitor, $keys );
    foreach my $key ( @keys_array ) {
        chomp( $key );
        $keys_hash{$key} = $key;
    }

    return %keys_hash;
}

#==================================================#
#
# 功能: 读取文件中的每行数据存储在指定的数组中
#
# 参数：filename -- 读取数据的文件名
#       lines_ref -- 存储读取到的数据的数组引用
#
# 返回: status -- 读取成功与否，0表示成功
#       mesg -- 相关错误消息
#       total_num -- 总共的记录数
#
#==================================================#
sub read_config_lines($$) {
    my $filename = shift;
    my $lines_ref = shift;
    my ( $status, $mesg, $total_num ) = ( -1, $NONE_READ_EERROR, 0 );

    #===第一步，检查文件是否存在===#
    &debug( "检查文件($filename)是否存在..." );
    if( !-e $filename ) {
        return ( $status , $FILE_NOT_FOUND, $total_num );
    }

    #===第二步，检查文件是否能打开读===#
    &debug( "准备打开文件($filename)..." );
    open( FILE, "<$filename" ) or return ( $status, $READ_OPEN_ERROR, $total_num );
    &debug( "正在读取文件($filename)内容..." );
    foreach my $record ( <FILE> ) {
        $record =~ s/[\r\n]//g;#去掉末尾的换行符
        push( @$lines_ref, $record );
        &debug( "\t读取文件($filename)数据$record..." );
    }
    close FILE;
    &debug( "读取文件($filename)内容完毕!" );

    $status = 0;
    $mesg = $READ_SUCCEEDED;
    $total_num = scalar( @$lines_ref );
    return ( $status, $mesg, $total_num );
}

#==================================================#
#
# 功能: 从指定的数组将数据覆盖写入到文件中
#
# 参数：filename -- 要覆盖写入数据的文件名
#       lines_ref -- 储存要写入的数据的数组引用
#
# 返回: status -- 写入成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub write_config_lines($$) {
    my $filename = shift;
    my $lines_ref = shift;
    my ( $status, $mesg ) = ( -1, $NONE_WRITE_ERROR );

    #===第一步，检查文件是否存在===#
    &debug( "检查文件($filename)是否存在..." );
    if( !-e $filename ) {
        return ( $status , $FILE_NOT_FOUND );
    }

    #===第二步，检查文件是否能打开写===#
    &debug( "准备打开文件($filename)..." );
    open( FILE, ">$filename" ) or return ( $status, $WRITE_OPEN_ERROR );
    &debug( "正在向文件($filename)写入内容..." );
    foreach my $record ( @$lines_ref ) {
        if ($record ne "") {#去掉空行
            print FILE "$record\n";
            &debug( "\t向文件($filename)写入数据$record..." );
        }
    }
    close FILE;
    &debug( "向文件($filename)写入内容完毕!" );

    $status = 0;
    $mesg = $WRITE_SUCCEEDED;
    return ( $status, $mesg );
}

#==================================================#
#
# 功能: 将字符串数据追加到文件末尾
#
# 参数：filename -- 追加字符串数据的文件名
#       record -- 追加的字符串
#
# 返回: status -- 追加成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub append_one_record($$) {
    my $filename = shift;
    my $record = shift;

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    #===添加数据===#
    push( @lines, $record );
    &debug( "\t在第最后一行插入数据$record..." );

    ( $status, $mesg ) = &write_config_lines( $filename, \@lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 将字符串插入到指定行
#
# 参数：filename -- 要插入字符串的文件名
#       line -- 要插入的行号(0到文件中所有行的长度)
#       record -- 要插入的字符串
#
# 返回: status -- 插入功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub insert_one_record($$$) {
    my $filename = shift;
    my $line = shift;
    my $record = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    if ( $line < 0 ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    if ( $line >= $len ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    #===插入数据===#
    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {
        if( $i == $line ) {
            push( @new_lines, $record );
            &debug( "\t在第<$i>行插入数据$record..." );
        }
        push( @new_lines, $lines[$i] );
    }

    ( $status, $mesg ) = &write_config_lines( $filename, \@new_lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 删除文件中指定行的数据
#
# 参数：filename -- 要删除数据的文件名
#       line -- 要删除的数据的行号(0到文件中所有行的长度)
#
# 返回: status -- 删除功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub delete_one_record($$) {
    my $filename = shift;
    my $line = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    if ( $line < 0 ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    if ( $line >= $len ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    #===删除数据===#
    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {
        if( $i != $line ) {
            push( @new_lines, $lines[$i] );
            &debug( "\t保留第<$i>行数据$lines[$i]..." );
        } else {
            &debug( "\t删除第<$i>行数据$lines[$i]..." );
        }
    }

    ( $status, $mesg ) = &write_config_lines( $filename, \@new_lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 删除文件中指定行的数据
#
# 参数：filename -- 要删除数据的文件名
#       line_nums -- 要删除的数据的多个行号，
#                    0到文件中所有行的长度，
#                    多个行号用‘&’隔开
#
# 返回: status -- 删除功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub delete_several_records($$) {
    my $filename = shift;
    my $line_nums = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my %line_hash = &get_record_keys_hash( $line_nums, "&" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    #===删除数据===#
    my @new_lines = ();
    for ( my $i = 0; $i < $len; $i++ ) {
        if( $line_hash{$i} eq $i ) {
            &debug( "\t删除第<$i>行数据$lines[$i]..." );
        } else {
            push( @new_lines, $lines[$i] );
            &debug( "\t保留第<$i>行数据$lines[$i]..." );
        }
    }
    ( $status, $mesg ) = &write_config_lines( $filename, \@new_lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 删除文件中指定id的数据
#
# 参数：filename -- 要删除数据的文件名
#       id --       要删除的数据的id
#
# 返回: status -- 删除功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub delete_several_records_by_id($$) {
    my $filename = shift;
    my $ids = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my %id_hash = &get_record_keys_hash( $ids, "&" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $maxid =int(`cat $filename`);
    my $len = scalar(@lines);
    
    #===删除数据===#
    my @new_lines = ();
    for ( my $i = 0; $i <$len; $i++ ) {
        my @del_arr=split(",",$lines[$i]);
        if( exists $id_hash{$del_arr[0]} ) {
            &debug( "\t删除第<$i>行数据$lines[$i]..." );
        } else {
            push( @new_lines, $lines[$i] );
            &debug( "\t保留第<$i>行数据$lines[$i]..." );
        }
    }

    ( $status, $mesg ) = &write_config_lines( $filename, \@new_lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 获取文件中指定行的数据
#
# 参数：filename -- 要获取数据的文件名
#       line -- 要获取的数据的行号(0到文件中所有行的长度)
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#       record -- 返回指定的数据
#
#==================================================#
sub get_one_record($$) {
    my $filename = shift;
    my $line = shift;
    my ( $status, $mesg, $record ) = ( -1, $NONE_READ_EERROR, "" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg , $record);
    }

    my $len = scalar( @lines );

    if ( $line < 0 ) {
        return ( $status, $NONE_READ_EERROR, $record );
    }

    if ( $line >= $len ) {
        return ( $status, $NONE_READ_EERROR, $record );
    }

    #===读取指定行数据===#
    $record = $lines[$line];

    return ( $status, $mesg, $record );#不管成功与否，都要返回
}
#==================================================#
#
# 功能: 获取文件中指定id的数据
#
# 参数：filename -- 要获取数据的文件名
#       id -- 要获取的数据的行号(0到文件中所有行的长度)
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#       record -- 返回指定的数据
#
#==================================================#
sub get_one_record_by_id($$) {
    my $filename = shift;
    my $id = shift;
    my ( $status, $mesg, $record ) = ( -1, $NONE_READ_EERROR, "" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg , $record);
    }

    my $len = scalar( @lines );
    for ( my $i = 0; $i < $len; $i++ ) {
        my $temp_id = (split(',',$lines[$i]))[0];
        if( $temp_id eq  $id) {
            &debug( "\t装载第<$i>行数据$lines[$i]..." );
            $record = $lines[$i];
            last;
        }
    }
    #===读取指定匹配数据===#
    

    return ( $status, $mesg, $record );#不管成功与否，都要返回
}
#==================================================#
#
# 功能: 获取文件中指定多行的数据
#
# 参数：filename -- 要获取数据的文件名
#       line_nums -- 要获取的数据的多个行号，
#                    0到文件中所有行的长度，
#                    多个行号用‘&’隔开,
#       lines_ref -- 存储读取到的数据的数组引用
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub get_several_records($$$) {
    my $filename = shift;
    my $line_nums = shift;
    my $lines_ref = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my %line_hash = &get_record_keys_hash( $line_nums, "&" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    #===装载数据===#
    for ( my $i = 0; $i < $len; $i++ ) {
        if( $line_hash{$i} eq "$i" ) {
            &debug( "\t装载第<$i>行数据$lines[$i]..." );
            push( @$lines_ref, $lines[$i] );
        }
    }

    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 获取文件中指定多个id的数据
#
# 参数：filename -- 要获取数据的文件名
#       id_nums -- 要获取的数据的多个id号，
#                    多个id号用‘&’隔开,
#       lines_ref -- 存储读取到的数据的数组引用
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub get_several_records_by_ids($$$) {
    my $filename = shift;
    my $id_nums = shift;
    my $lines_ref = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my %line_hash = &get_record_keys_hash( $id_nums, "&" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    #===装载数据===#
    for ( my $i = 0; $i < $len; $i++ ) {
        my $id = (split(',',$lines[$i]))[0];
        if( $line_hash{$id} eq $id) {
            &debug( "\t装载第<$i>行数据$lines[$i]..." );
            push( @$lines_ref, $lines[$i] );
        }
    }

    return ( $status, $len );#不管成功与否，都要返回
}
#==================================================#
#
# 功能: 获取文件中指定行的数据
#
# 参数：filename -- 要获取数据的文件名
#       page_size -- 要获取的数据的页大小
#       page_number -- 获取第几页
#       lines_ref -- 存储读取到的数据的数组引用
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#       total_num -- 一共有多少条记录
#
#==================================================#
sub get_one_page_records($$$$) {
    my $filename = shift;
    my $page_size = shift;
    my $page_number = shift;
    my $lines_ref = shift;
    my ( $status, $mesg, $total_num ) = ( -1, $NONE_READ_EERROR, 0 );

    my $from_num = ( $page_number - 1 ) * $page_size;
    my $to_num = $page_number * $page_size;

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg, $total_num );
    }

    $total_num = scalar( @lines );
    if( $total_num < $to_num ) {
        $to_num = $total_num;
    }

    for ( my $i = $from_num; $i < $to_num; $i++ ) {
        push( @$lines_ref, $lines[$i] );
    }

    return ( $status, $mesg, $total_num );#不管成功与否，都要返回
}
#==================================================#
#
# 功能: 获取文件中指定行的数据，并对数据进行筛选
#
# 参数：filename -- 要获取数据的文件名
#       page_size -- 要获取的数据的页大小
#       page_number -- 获取第几页
#       lines_ref -- 存储读取到的数据的数组引用
#       search -- 所有筛选条件的组合
#
# 返回: status -- 获取功与否，0表示成功
#       mesg -- 相关错误消息
#       total_num -- 一共有多少条记录
#
#==================================================#
sub get_one_page_records_better($$$$$) {
    my $filename = shift;           #文件内容
    my $page_size = shift;          #要获取的数据的页的大小
    my $page_number = shift;        #获取第几页
    my $lines_ref = shift;          #存储读取到的数据的数组引用
    my $search = shift;             #筛选条件

    my ( $status, $mesg, $total_num ) = ( -1, $NONE_READ_EERROR, 0 );

    #===第一步，检查文件是否存在===#
    &debug( "检查文件($filename)是否存在..." );
    if( !-e $filename ) {
        return ( $status , $FILE_NOT_FOUND, $total_num );
    }
    
    my $from_num = ( $page_number - 1 ) * $page_size;
    my $to_num = $page_number * $page_size;

    my @lines = ();
    # my $src_lines = `$search_cmd |head $filename -n $to_num | tail -n $page_size `;
    my $src_lines = `$search |head -n $to_num | tail -n $page_size `;
    # print "$search |head -n $to_num | tail -n $page_size";
    @lines = split(/\n/,$src_lines);

    $total_num = `$search| wc -l  | cut -d ' '  -f 1`;

    for ( my $i = 0; $i <= scalar(@lines); $i++ ) {
    # print "i:$i line:$lines[$i]";
        push( @$lines_ref, $lines[$i] );
    }

    return ( $status, $mesg, $total_num );#不管成功与否，都要返回
}


#==================================================#
#
# 功能: 更新指定行号的数据
#
# 参数：filename -- 要更新数据的文件名
#       line -- 要更新的数据的行号(0到文件中所有行的长度)
#       record -- 要更新的数据(字符串)
#
# 返回: status -- 更新成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub update_one_record($$$) {
    my $filename = shift;
    my $line = shift;
    my $record = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    if ( $line < 0 ) {
        $status = -1;
        return ( $status, $NONE_WRITE_ERROR );
    }

    if ( $line >= $len ) {
        $status = -1;
        return ( $status, $NONE_WRITE_ERROR );
    }

    #===更新数据===#
    $lines[$line] = $record;

    ( $status, $mesg ) = &write_config_lines( $filename, \@lines );
    return ( $status, $mesg );#不管成功与否，都要返回
}
#==================================================#
#
# 功能: 更新指定id的数据
#
# 参数：filename -- 要更新数据的文件名
#       id -- 要更新的数据的id
#       record -- 要更新的数据(字符串)
#
# 返回: status -- 更新成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub update_one_record_by_id($$$) {
    my $filename = shift;
    my $id = shift;
    my $record = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    my $len = scalar( @lines );

    if ( $line < 0 ) {
        $status = -1;
        return ( $status, $NONE_WRITE_ERROR );
    }

    if ( $line >= $len ) {
        $status = -1;
        return ( $status, $NONE_WRITE_ERROR );
    }

    #===更新数据===#
    foreach(my $i = 0 ;$i < $len;$i++){
        my @arr=split(",",$lines[$i]);
        if( $arr[0] eq $id){
             $lines[$i] = $record;
             ( $status, $mesg ) = &write_config_lines( $filename, \@lines );
            last;
        }
    }
   
    return ( $status, $mesg );#不管成功与否，都要返回
}

#==================================================#
#
# 功能: 将指定行号的数据向上或者向下移动一行
#
# 参数：filename -- 要移动数据的文件名
#       line -- 要移动的行号
#       direction -- 移动方向(-1是往上，1往下)
#
# 返回: status -- 移动成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub move_one_record($$$) {
    my $filename = shift;
    my $line = shift;
    my $direction = shift;
    my ( $status, $mesg ) = ( -1, $NONE_READ_EERROR );

    #===控制只移动一行===#
    if( $direction > 0 ) {
        $direction = 1;
    } elsif ( $direction < 0 ) {
        $direction = -1;
    } else {
        return ( -1, $NONE_CHANGE_ERROR );
    }

    my $newline = $line + $direction;

    my @lines = ();
    ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg );
    }

    if ( $newline < 0 ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    if ( $newline >= scalar( @lines ) ) {
        return ( $status, $NONE_WRITE_ERROR );
    }

    #===交互顺序===#
    my $temp = $lines[$line];
    $lines[$line] = $lines[$newline];
    $lines[$newline] = $temp;
    &debug( "\t调换第<$line>行和第<$newline>数据..." );

    ( $status, $mesg ) = &write_config_lines( $filename, \@lines );
    return ( $status, $mesg );
}

#==================================================#
#
# 功能: 获取请求的查询键值对
#
# 参数：query_ref -- 要储存查询键值对的哈希引用
#
# 返回: status -- 移动成功与否，0表示成功
#       mesg -- 相关错误消息
#
#==================================================#
sub get_query_hash($){
    my $query_ref = shift;
    my $query_string = $ENV{'QUERY_STRING'};

    if ( $query_string eq '' ) {
        return;
    }

    my @key_values = split( "&", $query_string );
    foreach my $key_value ( @key_values ) {
        my ( $key, $value ) = split( "=", $key_value );
        $query_ref->{ $key } = $value;
        #===对获取的值进行一些处理===#
        $query_ref->{ $key } =~ s/\r//g;
        $query_ref->{ $key } =~ s/\n//g;
        chomp( $query_ref->{ $key } );
    }

    return;
}

#==================================================#
#
# 功能: 查找字段值在文件中的位置
#
# 参数：filename -- 要查找字段的文件名
#       splitor -- 文件内容中字段的分割符
#       index -- 一条记录中，第几个字段
#       field -- 要查找的完全匹配的字段值
#       
#
# 返回: status -- 查找成功与否，0表示成功
#       mesg -- 相关错误消息
#       line_num -- 如果查找的，返回第一次匹配的行号，
#       没有返回空串
#
#==================================================#
sub where_is_field($$$$) {
    my $filename = shift;
    my $splitor = shift;
    my $index = shift;
    my $field = shift;
    my ( $status, $mesg, $line_num ) = ( -1, $NONE_READ_EERROR, "" );

    my @lines = ();
    my ( $status, $mesg ) = &read_config_lines( $filename, \@lines );
    if( $status != 0 ) {
        return ( $status, $mesg, $line_num );
    }

    my $len = scalar( @lines );

    for ( my $i = 0; $i < $len; $i++ ) {
        my @fields = split( $splitor, $lines[$i] );
        if ( $fields[$index] eq $field ) {
            $mesg = "找到了字段$field在第$i行";
            $line_num = $i;
            last;
        } else {
            &debug( "\t正在检查$lines[$i],取到的值为$fields[$index]" );
        }
    }

    if ( $line_num eq "" ) {
        $mesg = "一切正常，未找到已存在的$field";
    }

    return ( $status, $mesg, $line_num );
}
#==================================================#
#
# 功能: 置顶或置底
#
# 参数：derection -- 要查找字段的文件名
#       line -- 文件内容中字段的分割符
#       conf_file -- 一条记录中，第几个字段
#       
#
# 返回: status -- 查找成功与否，0表示成功
#       mesg -- 相关错误消息
#       line_num -- 如果查找的，返回第一次匹配的行号，
#       没有返回空串
#
#==================================================#
sub change_arrangement($$$) {
    my $derection = shift;
    my $line = shift;
    my $conf_file = shift;
    my $reload = 0;
    my ( $status, $error_mesg, $total_num ) = ( -1, "未读取数据", 0);
    my @content_array;

    my ( $status, $error_mesg, $total_num ) =  &read_config_lines( $conf_file, \@content_array);#读取配置文件的数据;
    
    my ($min, $max) = (0,$total_num - 1); 
    if($line < $total_num && $line >= 0){
        

        if($derection eq 'top' && $line != $min){
            my @temp = splice @content_array , $line , 1;
            unshift @content_array, @temp;
            ( $status, $error_mesg) =  &write_config_lines($conf_file,\@content_array);
            
        }elsif( $derection eq 'bottom' && $line != $max){
            my @temp = splice @content_array , $line , 1;
            push @content_array, @temp;
            ( $status, $error_mesg) = &write_config_lines($conf_file,\@content_array);

        }elsif($derection eq 'up' && $line != $min){
            my $temp_up = $content_array[$line-1];
            $content_array[$line-1] = $content_array[$line];
            $content_array[$line] = $temp_up;
            ( $status, $error_mesg) =  &write_config_lines($conf_file,\@content_array);
            
        }elsif( $derection eq 'down' && $line != $max){
                my $temp_down = $content_array[$line + 1];
                $content_array[$line + 1] = $content_array[$line];
                $content_array[$line] = $temp_down;
           
                ( $status, $error_mesg) = &write_config_lines($conf_file,\@content_array);
        }else{
                   
            ( $status, $error_mesg) = (-1,"非法换行"); 
        }

    }else{
        ( $status, $error_mesg ) = (-1,"非法换行,行号无效"); 
    }
    if ($error_mesg eq '写入数据成功') {
        $error_mesg = '';   
        $reload = 1;     
    }
    return ($status, $reload, $error_mesg);
}
# &test();
# sub test(){
#     my $filename = "/var/efw/objects/urllist/urlconfig";
#     my ( $status, $mesg ,$res)  = ( -1, "none" ,"");
#     if( $ARGV[0] eq "-g" ){
#         ( $status, $mesg ) = &get_several_records_by_ids( $filename, $ARGV[1] ,$ARGV[2] );
#     } 
#     print "$status: $mesg\nres:$res";

# }
# sub test() {
#     my $filename = "/var/efw/idps_console/rule_libraries/config";
#     my ( $status, $mesg ) = ( -1, "none" );

#     if ( $ARGV[0] eq "-a" ) {
#         ( $status, $mesg ) = &append_one_record( $filename, $ARGV[1] );
#     }
#     elsif ( $ARGV[0] eq "-i" ) {
#         ( $status, $mesg ) = &insert_one_record( $filename, $ARGV[1], $ARGV[2] );
#     }
#     elsif ( $ARGV[0] eq "-m" ) {
#         ( $status, $mesg ) = &move_one_record( $filename, $ARGV[1], $ARGV[2] );
#     }
#     elsif ( $ARGV[0] eq "-d" ) {
#         ( $status, $mesg ) = &delete_one_record( $filename, $ARGV[1] );
#     }
#     elsif ( $ARGV[0] eq "-ds" ) {
#         ( $status, $mesg ) = &delete_several_records( $filename, $ARGV[1] );
#     }
#     elsif ( $ARGV[0] eq "-c" ) {
#         ( $status, $mesg, $line_num ) = &where_is_field( $filename, $ARGV[1], $ARGV[2], $ARGV[3] );
#     }

#     print "$status: $mesg\n";
# }

1;
