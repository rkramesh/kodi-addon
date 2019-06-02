#!/bin/sh

diff -DVERSION1 /home/osmc/.kodi/addons/plugin.video.sendtokodi/service.py /media/H/sendkodi/service.py >/home/osmc/.kodi/addons/plugin.video.sendtokodi/service.py


cp /media/H/sendkodi/1mod_menuUtils.py /home/osmc/.kodi/addons/plugin.program.super.favourites/


rm /home/osmc/.kodi/addons/plugin.program.super.favourites/hot.py 

cp /media/H/sendkodi/hot.py /home/osmc/.kodi/addons/plugin.program.super.favourites/
cp /media/H/sendkodi/hot.py /tmp


