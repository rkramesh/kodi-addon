import xbmcaddon
import xbmcgui
import xbmc,os
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')
 
line1 = "Hello World!"
line2 = "We can write anything we want here"
line3 = "Using Python"
 
xbmcgui.Dialog().ok(addonname, line1, line2, line3)
os.system("sh /home/osmc/rk.sh")
