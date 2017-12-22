#!/bin/sh

for i in `find /var/log/ |grep -v httpd | grep -v rrd`;do if [ -f $i ];then cat /dev/null > $i;fi ;done
for i in `find /var/log/ |grep .gz`;do if [ -f $i ];then rm $i;fi ;done 
/usr/local/bin/restartsyslog.py --force >>/dev/null

exit 0
