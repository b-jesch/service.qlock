import os
import xbmcaddon
import xbmc
import xbmcvfs
from xbmcgui import Window
from xml.dom import minidom
from datetime import datetime, timedelta

__addon__ = xbmcaddon.Addon()
__scriptname__ = __addon__.getAddonInfo('id')
__cwd__ = __addon__.getAddonInfo('path')
__layoutDir__ = xbmcvfs.translatePath(os.path.join(__cwd__, 'resources', 'layout'))

Mon = xbmc.Monitor()
WINDOW = Window(10000)


def getLanguage():
    lang = "English"
    if xbmc.getLanguage() in (os.listdir(__layoutDir__)): lang = xbmc.getLanguage()

    __layoutFile__ = os.path.join(__layoutDir__, lang, 'layout.xml')
    xml = minidom.parse(__layoutFile__)
    data = xml.getElementsByTagName("background")[0]
    backplate = data.getAttribute("all").split(",")
    return backplate, xml, lang


def drawQlock(backplate, xml, now, lang):
    log('Draw Qlock (%s)' % lang)
    for i in range(len(backplate)): WINDOW.setProperty("Qlock.%i.Background" % (i + 1), backplate[i])
    for i in range(1, 111):
        WINDOW.clearProperty("Qlock.%i.Highlight" % i)

    times = xml.getElementsByTagName("time")[0]
    minute = "m%.2d" % ((now.minute // 5) * 5)

    to = 0
    try:
        if now.minute > 19:
            to = int(times.getAttribute("shiftOn20"))
            if now.minute > 34: to += int(times.getAttribute("shiftOnHalfHour"))
            if now.minute > 24: to += int(times.getAttribute("shiftOn25"))
    except (AttributeError, ValueError) as e:
        log(str(e), level=xbmc.LOGERROR)

    if now.hour >= 12: hour = "h%.2d" % (now.hour - 12 + to + int(times.getAttribute("shiftHour")))
    else: hour = "h%.2d" % (now.hour + to + int(times.getAttribute("shiftHour")))

    if hour == "h00": hour = "h12"

    if xbmc.getLanguage() == "German" and hour == "h01" and minute == "m00":  # German only, at one o'clock
        highlight = ["1", "2", "4", "5", "6", "45", "46", "47", "108", "109", "110"]
    else:
        highlight = times.getAttribute(minute).split(",") + \
                    times.getAttribute("all").split(",") + times.getAttribute(hour).split(",")

    for letter in highlight:
        WINDOW.setProperty("Qlock.%s.Highlight" % letter.replace(" ", ""), backplate[int(letter) - 1])


def log(msg, level=xbmc.LOGDEBUG):
    xbmc.log("[%s]: %s" % (__scriptname__, msg,), level=level)


while not Mon.abortRequested():
    cron_timetuple = datetime(*datetime.now().timetuple()[:5])
    background, dom, lang = getLanguage()
    drawQlock(background, dom, datetime.now(), lang)
    cron_timetuple += timedelta(minutes=1)
    if 1 < (cron_timetuple - datetime.now()).seconds + 1 < 59:
        Mon.waitForAbort((cron_timetuple - datetime.now()).seconds + 1)
    else:
        Mon.waitForAbort(30)

log('QLock finished')
