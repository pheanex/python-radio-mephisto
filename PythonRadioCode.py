#!/usr/bin/python
# -*- encoding: utf-8 -*-

import posix, os, sys, time, string, struct, fcntl, subprocess
import random
from mx.DateTime import *
from mpd import MPDClient


# Die wesentliche Funktion
def get_file_to_play(zeit):
    # log("Suche Datei fuer " + str(zeit))
    f = open(player_config, "r")
    lines = f.readlines()
    f.close()
    for x in lines:
        cfg = string.split(x)
        if cfg[0] == "%04d" % zeit.year:
            if cfg[1] == "%02d" % zeit.month:
                if cfg[2] == "%02d" % zeit.day:
                    if cfg[3] == "%02d" % zeit.hour:
                        if cfg[4] == "W":
                            break
                        if cfg[4] == "V":
                            break
    else:
        return get_endlosband()

    # log("Eintrag gefunden: %s %s %s %s" % (cfg[5], cfg[6], cfg[7], cfg[8]))

    # Vorproduktion: Datei abspielen
    if cfg[4] == "V":
        # log("Spiele vorproduzierte Datei: " + cfg[5])
        return "/opt/dserv/data/vorprod/%s" % (cfg[5])

    else:
        # Wiederholung: zu Wiederholende Datei suchen
        # finde die letzte passende Datei:
        # pdt = DateTime(2000, 8, 14, 18, 0, 0)
        pdt = DateTime(string.atoi(cfg[5], 10), string.atoi(cfg[6], 10), string.atoi(cfg[7], 10), string.atoi(cfg[8], 10), zeit.minute, zeit.second)
        # log("Suche Datei fuer: " + str(pdt))
        while pdt >= DateTime(string.atoi(cfg[5], 10), string.atoi(cfg[6], 10), string.atoi(cfg[7], 10), string.atoi(cfg[8], 10), 0, 0):
            filename = "/opt/dserv/data/%s/%s/%s" % (cfg[5], cfg[6], cfg[7])
            filename += "/%s-%02d-%02d.mp3" % (cfg[8], pdt.minute, pdt.second)
            if os.path.exists(filename):
                # log("Datei gefunden: " + filename)
                return filename
            pdt = pdt - RelativeDateTime(seconds=1)

    # log("Keine Datei für den Eintrag gefunden! Spiele Endlosband")
    return get_endlosband()


def get_endlosband():
    global last_endlosband_hour, endlosband, last_playing
    endlosband_now = now()
    endlosband_hour = endlosband_now.hour
    if endlosband_hour != last_endlosband_hour:
        last_endlosband_hour = endlosband_hour
        return get_random_file(endlosband)

    return last_playing


def get_random_file(directory):
    result = directory + "/" + random.choice(os.listdir(directory))
    log("Setze zufälliges Endlosband: " + result)
    return result


log_file = "/var/log/doku/doku-player.log"
player_config = "/var/doku/player.conf"
# endlosband = "/opt/dserv/data/endlos.mp3"
last_playing = ""
endlosband = "/opt/dserv/data/endlos"
timed_play = "/opt/doku/bin/timed_play"
player_control_file = "/var/doku/computer-ist-auf-sendung"


# Meine Funktion:
def create_playlist():
    client.connect(**mpd_server)
    client.clear()
    client.add(get_file_to_play(zeit))
    client.close()

# Auführen:
create_playlist()
