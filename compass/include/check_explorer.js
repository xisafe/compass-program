function CheckBrowser()
{
  var app=navigator.appName;
  var verStr=navigator.appVersion;
  if (app.indexOf('Netscape') != -1) {
    return "firefox";
  }else if (app.indexOf('Microsoft') != -1) {
    if (verStr.indexOf("MSIE 3.0")!=-1 || verStr.indexOf("MSIE 4.0") != -1 || verStr.indexOf("MSIE 5.0") != -1 || verStr.indexOf("MSIE 5.1") != -1) {
      return "IE_old";

    } else { return "IE_new";}
  }
}