//重写了Date对象的prototype,扩展了增加日期的方法

Date.prototype.Format = function(fmt) 
{
   
    var o =
     { 
        "M+" : this.getMonth() + 1, //月份 
        "d+" : this.getDate(), //日 
        "h+" : this.getHours(), //小时 
        "m+" : this.getMinutes(), //分 
        "s+" : this.getSeconds(), //秒 
        "q+" : Math.floor((this.getMonth() + 3) / 3), //季度 
        "S" : this.getMilliseconds() //毫秒 
     }; 
    if (/(y+)/.test(fmt)) 
         fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length)); 
    for (var k in o) 
        if (new RegExp("(" + k + ")").test(fmt)) 
             fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length))); 
    return fmt; 
}

Date.prototype.addHours = function(d)
{
	var date = this;
    date.setHours(date.getHours() + d);
    return date;
};

Date.prototype.subductionHours = function(d)
{	var date = this;
    date.setHours(date.getHours() - d);
     return date;
};
Date.prototype.addDays = function(d)
{
	var date = this;
    date.setDate(date.getDate() + d);
    return date;

};

Date.prototype.subductionDays = function(d)
{
    var date = this;
    date.setDate(date.getDate() - d);
    return date;

};

Date.prototype.addWeeks = function(w)
{
    var date = this;
    date.addDays(w * 7);
    return date;

};

Date.prototype.subductionWeeks = function(w)
{
    var date = this;
    date.subductionDays(w * 7);
    return date;

};

Date.prototype.addMonths= function(m)
{
    var date = this;
    var d = date.getDate();
    date.setMonth(date.getMonth() + m);

    if (date.getDate() < d)
        date.setDate(0);
    return date;

};
Date.prototype.subductionMonths= function(m)
{
   var date = this;
    var d = date.getDate();
    date.setMonth(date.getMonth() - m);

    if (date.getDate() < d)
      {date.setDate(0);} 
    return date;

};

Date.prototype.addYears = function(y)
{
    var date = this;
    var m = date.getMonth();
    date.setFullYear(date.getFullYear() + y);

    if (m < date.getMonth()) 
     {
        date.setDate(0);
     }
     return date;
};
Date.prototype.subductionYears = function(y)
{
    var date = this;
    var m = date.getMonth();
    date.setFullYear(date.getFullYear() - y);

    if (m < date.getMonth()) 
     {
        date.setDate(0);
     }
     return date;

};
// var now = new Date();
// now.addDays(1);//加减日期操作
// alert(now.Format("yyyy-MM-dd"));