/*
 * 描述：更新网络状态
 *
 * 作者：王琳，245105947@qq.com
 * 公司：成都世纪顶点
 * 历史：
 *  2014.08.28 王琳创建
 *  2015.04.17 王琳修改
 */

$(document).ready(function(){
    var networkStatusManager = new NetworkStatusManager();
});

function NetworkStatusManager() {
    this.url = "/cgi-bin/network_status.cgi";
    this.tbody_id = "network_status_body";
    this.interface_status = {
        UP: "<font style='color: green;'><b>连接</b></font>",
        DOWN: "<font style='color: red;'>未连接</font>"
    }
    this.update_interval = 2000;

    /* 用于存放接口速率单元格的id */
    this.interface_rate_id = {};

    /* 用于存放当前下载的数据 */
    this.current_loaded_data = {};
    /* 用于存放前后两次数据包传送总数 */
    this.pre_RTX_data = {};
    this.current_RTX_data = {};

    /*第一次加载数据*/
    this.load_data();

    /* 初始化用于存放接口速率单元格的id */
    this.init_interface_rate_id( this.current_loaded_data );
    /* 存放第一次的数据包传送总数 */
    this.get_interface_RTX( this.current_loaded_data, this.pre_RTX_data );

    this.update_network_status();
}

NetworkStatusManager.prototype.update_network_status = function() {
    /*第一步，请求新数据*/
    var manager = this;
    manager.load_data();

    /*第二步，根据最近加载的数据，画出表格生成表*/
    manager.refresh_network_status();
    /*第三步，更新接口速率*/
    manager.refresh_interface_rate();
    /*第四步，拷贝数据*/
    manager.copy_RTX_store( manager.current_RTX_data, manager.pre_RTX_data );

    /*第三步，设置下次刷新*/
    window.setTimeout( function(){
        manager.update_network_status();
    }, manager.update_interval );
}

NetworkStatusManager.prototype.refresh_network_status = function() {
    var manager = this;
    var loaded_data = manager.current_loaded_data;
    var bond_regx = /^bond/;
    var table_body = '';
    for ( var i = 0; i < loaded_data.length; i++ ) {
        var area_item = loaded_data[i];
        var interface_area = area_item["Area"];
        var trs_content = new Array();
        /* 这里的ip_mask显示到一块，因为这里是桥接区域 */
        var area_rowspan = 0;
        for ( var j = 0; j < area_item["interface"].length; j++ ) {
            var bond_item = area_item["interface"][j];
            if ( bond_item.name.match( bond_regx ) ) {
                area_rowspan = area_rowspan + bond_item["interface"].length;
                for ( var k = 0; k < bond_item["interface"].length; k++ ) {
                    var eth_item = bond_item["interface"][k];
                    /* 访问到具体的接口,开始压栈每一行数据 */
                    var tr_content = '';
                    /* 如果是第一行，要添加bond接口信息 */
                    if ( k == 0 ) {
                        if ( interface_area == "WAN" || interface_area == "N/A" ) {
                            tr_content += '<td rowspan="' + bond_item["interface"].length + '">' + 
                                            bond_item.ip_mask.replace( /,/g, "<br/>&nbsp;" ) + '</td>';
                        }
                        tr_content += '<td rowspan="' + bond_item["interface"].length + '">' + bond_item.name + '</td>';
                    }
                    tr_content += '<td>' + eth_item.name + '</td>';
                    tr_content += '<td>' + eth_item.mac + '</td>';
                    tr_content += '<td>' + eth_item.speed + '</td>';
                    tr_content += '<td>' + manager.interface_status[eth_item.status] + '</td>';
                    tr_content += '<td id="' + manager.interface_rate_id[eth_item.name]["rx_rate_id"] + '"></td>';
                    tr_content += '<td id="' + manager.interface_rate_id[eth_item.name]["tx_rate_id"] + '"></td>';
                    trs_content.push( tr_content );
                }
            } else {
                area_rowspan += 1;
                /* 访问到具体的接口，开始压栈每一行数据 */
                var tr_content = '';
                if ( interface_area == "WAN" || interface_area == "N/A" ) {
                    tr_content += '<td>' + bond_item.ip_mask.replace( /,/g, "<br/>&nbsp;" ) + '</td>';
                }
                tr_content += '<td colspan="2">' + bond_item.name + '</td>';
                tr_content += '<td>' + bond_item.mac + '</td>';
                tr_content += '<td>' + bond_item.speed + '</td>';
                tr_content += '<td>' + manager.interface_status[bond_item.status] + '</td>';
                tr_content += '<td id="' + manager.interface_rate_id[bond_item.name]["rx_rate_id"] + '"></td>';
                tr_content += '<td id="' + manager.interface_rate_id[bond_item.name]["tx_rate_id"] + '"></td>';
                trs_content.push( tr_content );
            }
        }
        /* 每个接口信息已经压栈完成，开始组装整个区域信息 */
        for ( var j = 0; trs_content.length > 0; j++ ) {
            var tr_item = trs_content.shift();

            table_body += '<tr class="odd">';
            if ( j == 0 ) {
                /* 如果是本区域的第一行 */
                table_body += '<td rowspan="' + area_rowspan + '">' + interface_area + '</td>';
                if( interface_area == "LAN" || interface_area == "DMZ" ) {
                    /* 如果是内网，要整体显示ip_mask */
                    table_body += '<td rowspan="' + area_rowspan + '">' + area_item.ip_mask.replace( /,/g, "<br/>&nbsp;" ) + '</td>';
                }
            }
            table_body += tr_item;
            table_body += '</tr>';
        }
    }

    var table_body_id = "#" + manager.tbody_id;
    $( table_body_id ).html( table_body );
}

NetworkStatusManager.prototype.refresh_interface_rate = function() {
    var manager = this;
    var pre_RTX_data = manager.pre_RTX_data;
    var current_RTX_data = manager.current_RTX_data;
    var interface_rate_id = manager.interface_rate_id;
    for ( var interface_name in interface_rate_id ) {
        var rx_speed = manager.get_average_speed( current_RTX_data[interface_name + "_RX_TMP"], 
                            pre_RTX_data[interface_name + "_RX_TMP"], 
                            current_RTX_data[interface_name + "_TIMESTAMP"] - pre_RTX_data[interface_name + "_TIMESTAMP"] );
        var tx_speed = manager.get_average_speed( current_RTX_data[interface_name + "_TX_TMP"], 
                            pre_RTX_data[interface_name + "_TX_TMP"], manager.update_interval );
        var rx_selector = "#" + interface_rate_id[interface_name]["rx_rate_id"];
        var tx_selector = "#" + interface_rate_id[interface_name]["tx_rate_id"];
        $( rx_selector ).html( rx_speed );
        $( tx_selector ).html( tx_speed );
    }

}

NetworkStatusManager.prototype.get_interface_RTX = function( loaded_data, RTX_store ) {
    var networkStatusManager = this;
    var bond_regx = /^bond/;
    for ( var i = 0; i < loaded_data.length; i++ ) {
        var area_item = loaded_data[i];
        for ( var j = 0; j < area_item["interface"].length; j++ ) {
            var bond_item = area_item["interface"][j];
            if ( bond_item.name.match( bond_regx ) ) {
                for ( var k = 0; k < bond_item["interface"].length; k++ ) {
                    var eth_item = bond_item["interface"][k];
                    /* 访问到具体的接口，提取RX_TMP和TX_TMP信息 */
                    RTX_store[eth_item.name + "_RX_TMP"] = eth_item.RX_TMP;
                    RTX_store[eth_item.name + "_TX_TMP"] = eth_item.TX_TMP;
                    RTX_store[eth_item.name + "_TIMESTAMP"] = eth_item.TIMESTAMP;
                }
            } else {
                /* 访问到具体的接口，提取RX_TMP和TX_TMP信息 */
                RTX_store[bond_item.name + "_RX_TMP"] = bond_item.RX_TMP;
                RTX_store[bond_item.name + "_TX_TMP"] = bond_item.TX_TMP;
                RTX_store[bond_item.name + "_TIMESTAMP"] = bond_item.TIMESTAMP;
            }
        }
    }
}

NetworkStatusManager.prototype.copy_RTX_store = function ( to_copy_store, copy_store ) {
    for ( var attr in to_copy_store ) {
        copy_store[attr] = to_copy_store[attr];
    }
}

/*
 * 传入 new_X, old_X为bit单位流量，interval为ms单位时间
 */
NetworkStatusManager.prototype.get_average_speed = function(new_X, old_X, interval) {
    var manager = this;
    var speed = manager.round( (new_X - old_X) / interval, 2 );
    if( speed > 1000 ) {
        speed = manager.round( speed / 1000, 2 );
        return speed + "MB/s"; //支持显示到MB
    } else {
        return speed + "KB/s";
    }
}

/*
 * 根据输入的e，返回保留位数值
 *  比如v是1.2456，e是2，返回1.25
 *  如果v是12456，e是-2，返回12500
 */
NetworkStatusManager.prototype.round = function(v,e){
    var t = 1;
    for (; e > 0; t *= 10, e--);
    for (; e < 0; t /= 10, e++);
    return Math.round( v * t ) / t;
}

NetworkStatusManager.prototype.load_data = function() {
    var manager = this;

    var sending_data = {
        ACTION: "load_data"
    };

    function ondatareceived(data) {
        manager.current_loaded_data = data;
        manager.get_interface_RTX( data, manager.current_RTX_data );
    }

    manager.request_for_json(sending_data, ondatareceived);
}

NetworkStatusManager.prototype.init_interface_rate_id = function( loaded_data ) {
    var networkStatusManager = this;
    var bond_regx = /^bond/;
    for ( var i = 0; i < loaded_data.length; i++ ) {
        var area_item = loaded_data[i];
        for ( var j = 0; j < area_item["interface"].length; j++ ) {
            var bond_item = area_item["interface"][j];
            if ( bond_item.name.match( bond_regx ) ) {
                for ( var k = 0; k < bond_item["interface"].length; k++ ) {
                    var eth_item = bond_item["interface"][k];
                    /* 访问到具体的接口，提取name信息 */
                    networkStatusManager.interface_rate_id[eth_item.name] = { rx_rate_id : eth_item.name + "_rx_rate_id",
                                                                              tx_rate_id: eth_item.name + "_tx_rate_id" };
                }
            } else {
                /* 访问到具体的接口，提取name信息 */
                networkStatusManager.interface_rate_id[bond_item.name] = { rx_rate_id : bond_item.name + "_rx_rate_id",
                                                                           tx_rate_id: bond_item.name + "_tx_rate_id" };
            }
        }
    }
}

NetworkStatusManager.prototype.request_for_json = function( sending_data, ondatareceived ) {
    var manager = this;
    var url = manager.url;
    $.ajax({
        type: 'POST',
        url: url,
        data: sending_data,
        dataType: 'json',
        async: false,
        error: function(request){
            //暂时不做任何处理
        },
        success: ondatareceived
    });
}