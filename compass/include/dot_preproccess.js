/*
 * 当前时间 current_time
 * 获得的点集 s
 * 应有的点数 n
 *      一个月 43200
 *      一周   10080
 *      一天   1440
 *      一小时 60
 */

function preprocess( n, set_pre ) {
    var times = 1000;
    var current_time = set_pre[0].time * times; //获取当前时间的函数，自己实现，以秒为单位, 
    var time_interval = 60 * times; // 60s

    var real_dots = new Array();

    var j = 0, i = 0;

    for ( i = 0; i < n; i++ ) {
        if ( j >= set_pre.length ) {
            break;
        }
        
        var dot_time = current_time - i * time_interval;
        var item = set_pre[j];
        var time_item = item.time * times;
        if ( time_item >= dot_time - 30 * times && time_item < dot_time + 30 * times ) {
            // 合法的点,后台传的数据和前台计算时间合上,这个点被使用了，j++
            real_dots.push({ value: item.value, time: dot_time });
            j++;
            for ( ; j < set_pre.length; j++ ) {
                item = set_pre[j];
                if ( item.time * times >= dot_time - 30 * times && item.time * times < dot_time + 30 * times ) {
                    //落在上一点相同区间，不要此点j++
                    j++;
                } else {
                    break;
                }
            }
        } else {
            
            real_dots.push({ value: "-", time: dot_time });
        }
        
    }

    for ( var k = i; k < n; k++ ) {
        var dot_time = current_time - k * time_interval;
        real_dots.push({ value: "-", time: dot_time });
    }

    return real_dots;
}

function get_current_time(){
    var myDate = new Date();
    var current_time_seconds = myDate.getTime();
    return current_time_seconds;
}