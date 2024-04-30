import re
import json 
import requests
import os
import xml.etree.ElementTree as ET  # Import ElementTree module
import feedparser
from dateutil import parser, tz
import datetime
import os.path
import urllib.request

def simplifized_url(stringUrl):
    prefixes = ["http://www.", "https://www.", "http://", "https://"]
    for prefix in prefixes:
        if stringUrl.startswith(prefix):
            stringUrl = stringUrl[len(prefix):]
    return re.sub(r'[^a-zA-Z0-9]', '_', stringUrl)

def current_timestamp():
    ct = datetime.datetime.now()
    return int(ct.timestamp())

def save_json(jsonObject, filePath):
    with open(filePath, 'w') as json_file:
        json.dump(jsonObject, json_file, indent=4)
        print(f"> Saved {filePath}")

def load_json(filePath):
    with open(filePath, 'r') as json_file:
        data = json.load(json_file)
    return data

def load_json_from_url(url):
    with urllib.request.urlopen(url) as url:
        data = json.load(url)
        print(f"> Loaded json from: {url}")
    return data

def load_txt_lines(filePath):
    with open(filePath, 'r') as file:
        data = file.read().splitlines()
        print(f"> Loaded txt from: {filePath}")
    return data

def custom_tzinfos(tzname, tzoffset):
    if tzname == "PDT":
        return tz.tzoffset(None, -25200)  # Pacific Daylight Time offset in seconds (-7 hours)
    elif tzname == "PST":
        return tz.tzoffset(None, -28800)  # Pacific Standard Time offset in seconds (-8 hours)
    elif tzname == "EDT":
        return tz.tzoffset(None, -14400)  # Eastern Daylight Time offset in seconds (-4 hours)
    elif tzname == "EST":
        return tz.tzoffset(None, -18000)  # Eastern Standard Time offset in seconds (-5 hours)
    elif tzname == "CDT":
        return tz.tzoffset(None, -18000)  # Central Daylight Time offset in seconds (-5 hours)
    elif tzname == "CST":
        return tz.tzoffset(None, -21600)  # Central Standard Time offset in seconds (-6 hours)
    elif tzname == "MDT":
        return tz.tzoffset(None, -21600)  # Mountain Daylight Time offset in seconds (-6 hours)
    elif tzname == "MST":
        return tz.tzoffset(None, -25200)  # Mountain Standard Time offset in seconds (-7 hours)
    elif tzname == "AKDT":
        return tz.tzoffset(None, -28800)  # Alaska Daylight Time offset in seconds (-8 hours)
    elif tzname == "AKST":
        return tz.tzoffset(None, -32400)  # Alaska Standard Time offset in seconds (-9 hours)
    elif tzname == "HAST":
        return tz.tzoffset(None, -36000)  # Hawaii-Aleutian Standard Time offset in seconds (-10 hours)
    elif tzname == "HST":
        return tz.tzoffset(None, -36000)  # Hawaii Standard Time offset in seconds (-10 hours)
    # Add more timezone abbreviations as needed
    return None