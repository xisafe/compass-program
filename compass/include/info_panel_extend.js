/*
 * 描述: 信息面板使用实例文件
 *
 * 作者: WangLin，245105947@qq.com
 * 公司: capsheaf
 * 历史：
 *       2015.10.15 WangLin创建
 */

$(document).ready(function(){
    infoDisplayPanel.render();
    
    var dataItem = {
        assetName: "高级领导的PC",
        ipaddr: "192.168.4.177",
        mac: "ed-45-f6-a3-68-b2",
        confidentiality: "非常高",
        fragility: "低",
        integrality: "高",
        protectLevel: "非常高",
        physicalAsset: "$10000000000",
        physicalAddr: "川大基础教学楼",
        assetUser: '领导'
    };
    infoDisplayPanel.update_data(dataItem);
});

var infoDisplayPanelConf = {
    check_in_id: "display_panel",   /* ***必填***，确定面板挂载在哪里 */
    panel_name: "display_panel",    /* ==*可选*==，默认名字my_add_panel，当一个页面存在多个信息展示面板用于区分不同面板 */
    panel_title: "信息展示面板",    /* ===可选===，默认是“信息”，表示显示前面的 */
    is_panel_title_icon: true,      /* ===可选===，默认是“true”，表示标题前面的图标是否显示 */
    panel_title_icon: "info.png",   /* ===可选===，默认是“info.png”，is_panel_title_icon为true才有效 */
    is_panel_closable: false,       /* ===可选===，默认是false，控制面板是否可关闭，跟点击撤销按钮是一个效果 */
    is_modal: false,                /* ===可选===，默认是false，控制面板是否模态显示 */
    modal_config: {                 /* ===可选===，当想控制模块框大小层次等时创建，在is_modal为true时才生效 */
        modal_box_size: "m",        /* ===可选===，默认是l,有l、m、s三种尺寸的模态框 */
        modal_level: 10             /* ===可选===，默认是10，数字越大，模态框弹得越上层，可以在其他模态框之上 */
    },
    columns: 3,                     /* ===可选===，默认是2，表示信息展示的列数 */
    label_width: 1,                 /* ===可选===，默认是3，填写的是比例，必须是数字(整数类型和浮点类型) */
    value_width: 3,                 /* ===可选===，默认是7，填写的是比例，必须是数字(整数类型和浮点类型)，此处是1:3的比例 */
    items_list: [{
        label: "资产名称",
        name: "assetName",
        value: "领导的电脑"
    }, {
        label: "IP地址",
        name: "ipaddr",
        value: "192.168.4.188"
    }, {
        label: "MAC地址",
        name: "mac",
        value: "00-11-22-33-44-55"
    }, {
        label: "机密性",
        name: "confidentiality",
        value: "高"
    }, {
        label: "脆弱性",
        name: "fragility",
        value: "高"
    }, {
        label: "完整性",
        name: "integrality",
        value: "高"
    }, {
        label: "保护等级",
        name: "protectLevel",
        value: "高"
    }, {
        label: "物理资产",
        name: "physicalAsset",
        value: "10000元"
    }, {
        label: "物理位置",
        name: "physicalAddr",
        value: "一楼"
    }, {
        label: "资产用户",
        name: "assetUser",
        value: "艾磊"
    }] 
}

var infoDisplayPanel = new InfoDisplayPanel( infoDisplayPanelConf )