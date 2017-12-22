#!/usr/bin/python                                                                                                                                                                                                                  
#                                                                                                                                                                                                                                
#                                                                                                                                                                                                                                
#        +-----------------------------------------------------------------------------+                                                                                                                                         
#        | Endian Firewall                                                             |                                                                                                                                         
#        +-----------------------------------------------------------------------------+                                                                                                                                         
#        | Copyright (c) 2005-2009 Endian                                              | 
#        |         Endian GmbH/Srl                                                     |                                                                                                                                         
#        |         Bergweg 41 Via Monte                                                |                                                                                                                                         
#        |         39057 Eppan/Appiano                                                 |                                                                                                                                         
#        |         ITALIEN/ITALIA                                                      |                                                                                                                                         
#        |         info@endian.it                                                      |                                                                                                                                         
#        |                                                                             |                                                                                                                                         
#        | This program is free software; you can redistribute it and/or               |                                                                                                                                         
#        | modify it under the terms of the GNU General Public License                 |                                                                                                                                         
#        | as published by the Free Software Foundation; either version 2              |                                                                                                                                         
#        | of the License, or (at your option) any later version.                      |                                                                                                                                         
#        |                                                                             |                                                                                                                                         
#        | This program is distributed in the hope that it will be useful,             |                                                                                                                                         
#        | but WITHOUT ANY WARRANTY; without even the implied warranty of              |                                                                                                                                         
#        | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               |                                                                                                                                         
#        | GNU General Public License for more details.                                |                                                                                                                                         
#        |                                                                             |                                                                                                                                         
#        | You should have received a copy of the GNU General Public License           |                                                                                                                                         
#        | along with this program; if not, write to the Free Software                 |                                                                                                                                         
#        | Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA. |                                                                                                                                         
#        | http://www.fsf.org/                                                         |                                                                                                                                         
#        +-----------------------------------------------------------------------------+                                                                                                                                         
#                                                                                                                                                                                                                                

import cgi, cgitb
import endian.core.i18n
endian.core.i18n.UNICODE_WORKAROUND=True
from endian.core.widget import *

def buildPage():
    content = _("Loading Dashboard")
    baseTemplate = MainPageWidget(_("Dashboard"),'main_start.cgi')
    baseTemplate.setValue("TITLE",_("Dashboard"))
    baseTemplate.setValue("BODY", content)
    baseTemplate.addCSSInclude('/include/dashboard.css')
    baseTemplate.addJSInclude('/include/dashboard.js')
    baseTemplate.addJSInclude('/include/jquery.flot.js')
    baseTemplate.addJSInclude('/include/excanvas.js')
    baseTemplate.display()

cgitb.enable()
buildPage()
