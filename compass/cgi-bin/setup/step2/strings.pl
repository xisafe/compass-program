#
#        +-----------------------------------------------------------------------------+
#        | Endian Firewall                                                             |
#        +-----------------------------------------------------------------------------+
#        | Copyright (c) 2005-2006 Endian                                              |
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

%strings = (
  'nw_adsl_type' => _('ADSL type'),
  'nw_auth_method' => _('Authentication method'),
  'nw_automatic' => _('automatic'),
  'nw_blue_descr' => _('network segment for wireless clients (WIFI)'),
  'nw_blue' => _('BLUE'),
  'nw_chap' => _('CHAP'),
  'nw_concentrator_name' => _('Concentrator name'),
  'nw_description' => _('Description'),
  'nw_dhcp' => _('RFC1483 dhcp'),
  'nw_dial_telephone' => _('Phone number to dial'),
  'nw_dns_manual' => _('manual DNS configuration'),
  'nw_dns_quest' => _('DNS'),
  'nw_dns' => _('configure DNS resolver'),
  'nw_domainname' => _('Domainname'),
  'nw_encapsulation' => _('Encapsulation'),
  'nw_end_msg' => _('配置已保存，相关服务正在重启，请等待…'),
  'nw_field_blank' => _('This field may be blank.'),
  'nw_final_msg' => _('网络设置已经准备好,点击应用配置就可应用新的配置..'),
  'nw_gateway' => _('Default gateway'),
  'nw_green_changed_explain' => _('The IP address of GREEN has been changed. After relaunch (about 20 seconds) you can reach the webinterface on the new IP address by following the link'),
  'nw_green_changed_proxy' => _('Remember to check if IP address blocks of services are still configured as you wish. Mainly check the configuration of "Network based access control" of the HTTP Proxy.'),
  'nw_green_changed_link' => _('Web interface on the new address'),
  'nw_green_descr' => _('trusted, internal network (LAN)'),
  'nw_green' => _('GREEN'),
  'nw_hostname' => _('Hostname'),
  'nw_interface' => _('Interfaces'),
  'nr_interfaces' => _('Number of interfaces'),
  'hardware_information' => _('Hardware information'),

  'nw_ip' => _('IP address'),
  'nw_last' => _('应用配置'),
  'nw_link' => _('Link'),
  'nw_mac' => _('MAC'),
  'nw_manual' => _('manual'),
  'nw_mask' => _('network mask'),
  'nw_modemdriver' => _('Please select the driver of your modem'),
  'nw_mtu' => _('MTU'),
  'nw_next' => _('>>>'),
  'nw_cancel' => _('Cancel'),
  'nw_orange_descr' => _('network segment for servers accessible from internet (DMZ)'),
  'nw_orange' => _('ORANGE'),
  'nw_papchap' => _('PAP or CHAP'),
  'nw_pap' => _('PAP'),
  'nw_port' => _('Port'),
  'nw_pppoa' => _('PPPoA'),
  'nw_pppoe_plugin' => _('PPPoE plugin'),
  'nw_pppoe' => _('PPPoE'),
  'nw_prev' => _('<<<'),
  'nw_red_descr' => _('untrusted, internet connection (WAN)'),
  'nw_red_is_dhcp' => _('RED gets the data from DHCP.'),
  'nw_red' => _('RED'),
  'nw_static_gw' => _('Gateway'),
  'nw_static_ip' => _('Static ip'),
  'nw_static_netmask' => _('Netmask'),
  'nw_static' => _('RFC1483 static ip'),
  'nw_timeout' => _('Hang up after minutes of inactivity'),
  'nw_use_both_channels' => _('Use both B-Channels'),
  'nw_use_telephone' => _('Your phone number to be used to dial out'),
  'nw_vci' => _('VCI number'),
  'nw_vpi' => _('VPI number'),

  'nw_dns1' => _('DNS 1'),
  'nw_dns2' => _('DNS 2'),
  'password' => _('Password'),
  'service' => _('Service'),
  'username' => _('Username'),

  'nw_noautoconnect' => _('Do not automatically connect on boot'),
  'nw_mac_spoof' => 'MAC地址',
  'nw_additionalips' => _('Add additional addresses (one IP/Netmask or IP/CIDR per line)'),

  'nw_comport' => _('Please select the serial port of your modem'),
  'nw_modemtype' => _('Please select the modem type'),
  'nw_analog_modem' => _('Simple analog modem'),
  'nw_hsdpa_modem' => _('UMTS/HSDPA modem'),
  'nw_cdma_modem' => _('UMTS/CDMA modem'),
  'nw_speed' => _('Baud-rate'),
  'nw_apn' => _('Access Point Name'),
  'nw_device' => _('Device'),

  'nw_admin_mail' => _('管理员邮箱地址'),
  'nw_mail_from' => _('Sender email address'),
  'nw_mail_smarthost' => _('邮件中继主机地址'),
  
  'LDAP Connection Error' => _('LDAP连接错误'),
);

1;
