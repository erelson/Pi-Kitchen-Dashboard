#!/bin/bash

firefox $HOME/repos/Pi-Kitchen-Dashboard/index.html &
while [ ! "$(DISPLAY=:0 wmctrl -l | grep Kitchen)" ]; do
    sleep 3
done
DISPLAY=:0 wmctrl -a Kitchen
xdotool key F11 mousemove 0 320
