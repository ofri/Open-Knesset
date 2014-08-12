#!/bin/sh
if [ `pgrep -f PresenceManager.py` ]; then
kill `ps -ef | grep -v grep | grep "PresenceManager" | head -1 | awk '{print $2}'`
sleep 1s
fi
cd /oknesset_data/presence
python PresenceManager.py &
