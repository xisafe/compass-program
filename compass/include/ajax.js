function createXMLHTTPRequestObject() {
  var resObject = null;
  try {
    resObject = new ActiveXObject("Microsoft.XMLHTTP");
  } catch (Error) {
    try {
      resObject = new ActiveXObject("MSXML2.XMLHTTP");
    } catch (Error) {
      try {
	resObject = new XMLHttpRequest();
      } catch (Error) {
	sleep(0);
      }
    }
  }
  return resObject;
}

