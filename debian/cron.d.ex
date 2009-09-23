#
# Regular cron jobs for the apt-offline package
#
0 4	* * *	root	[ -x /usr/bin/apt-offline_maintenance ] && /usr/bin/apt-offline_maintenance
