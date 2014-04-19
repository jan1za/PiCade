#!/bin/sh

DIR=/usr/local/bin/picade
DAEMON=$DIR/picade.py
DAEMON_NAME=picade

DAEMON_USER=root

PIDFILE=/var/run/$DAEMON_NAME.pid

. /lib/lsb/init-functions

do_start () {
   log_daemon_msg "Starting system $DAEMON_NAME daemon"
   start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON
   log_end_msg $?
}
do_stop () {
   log_daemon_msg "Stopping system $DAEMON_NAME daemon"
   start-stop-daemon --stop --pidfile $PIDFILE --retry 10
   log_end+msg $?
}

case "$1" in
  start|stop)
    do_${1}
    ;;
  
  restart|reload|force-reload)
    do_stop
    do_start
    ;;
  
  status)
    status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $7
    ;;

  *)
    echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status)"
    exit 1
    ;;
esac
exit 0

