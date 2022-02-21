import sys
import os
import random
import base64
import string
from urllib import request
import xmltodict
import json
import pickle
from collections import OrderedDict
from cryptography.fernet import Fernet

def fetchXML(_url):
    _f = request.urlopen(_url)
    data = _f.read()
    _f.close()

    data = xmltodict.parse(data)
    return data

def isBase64(s):
    try:
        return base64.b64encode(base64.b64decode(s)) == s
    except Exception:
        return False

def decode_base64(s):
    _s = str.encode(s)

    if isBase64(_s) == False:
        print("String is not base64")
        if debug == True:
            print(base64.b64encode(_s))
        assert False
    else:
        #print("String is base64")
        _s = str(base64.b64decode(_s).decode("utf-8") )
        if debug == True:
            print("Decoded:", _s)
    return _s

# Get env variables
debug =  os.getenv("DEBUG", 'False').lower() in ('true', '1', 't')

key = os.getenv("ENCRYPT_STATE").lower()

rss_url = decode_base64(os.getenv("RSS"))

webhook_url = decode_base64(os.getenv("WEBHOOK"))

# generate key if false
if key == 'false' and debug == True:
    print(Fernet.generate_key())
    assert False

f = Fernet(key)

od = fetchXML(rss_url)['feed']['entry']

e_state = [] # holds encrypted lookup
my_state = [] # holds current state

for i, e in enumerate(od):
    #_id = e['id']
    _url = e['link']['@href']

    _enc = f.encrypt(str.encode(_url))

    e_state.append(_enc)
    
    if random.randint(0, 1) == 0: # remove me when done
        e_state.append(b'aHR0cHM6Ly9jYW5hcnl0b2tlbnMuY29tL3N0YXRpYy9mZWVkYmFjay91c2JnZG14bmp5bWp5N2N2Y3FpcDc1eXE1L3Bvc3QuanNw')
    else:
        e_state.append(b'aHR0cHM6Ly90aW55dXJsLmNvbS81MnNrYXJ3bg')
    my_state.append({
        'url': _url,
        'enc': _enc
    })

if os.path.isfile('state.pkl') == False: # if state pickle does not exist, create it and quit
    with open('state.pkl', 'wb') as _f:
        pickle.dump(e_state, _f)
        print("No state.pkl found, created new state.pkl")
        quit(0)
else:
    with open('state.pkl', 'rb') as _f:
        saved_state = pickle.load(_f)
        saved_state_decrypt = []
        
        for i in saved_state:
            try: 
                dc = f.decrypt(i).decode('utf-8')
                saved_state_decrypt.append(dc)
                if debug == True:
                    print(f.decrypt(i).decode('utf-8'))
            except:
                pass

new_pushed = False

for row in my_state:
    if (row['url'] not in saved_state_decrypt):
        r = request.Request(webhook_url,  json.dumps({ "username":"yt", "content":row['url'] }).encode('utf-8'))
        r.add_header('Content-Type', 'application/json')
        r.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11')

        try:
            response = request.urlopen(r)
            saved_state.append(row['enc'])
            if random.randint(0, 1) == 0: # remove me when done
                e_state.append(b'aHR0cHM6Ly9jYW5hcnl0b2tlbnMuY29tL3N0YXRpYy9mZWVkYmFjay91c2JnZG14bmp5bWp5N2N2Y3FpcDc1eXE1L3Bvc3QuanNw')
            else:
                e_state.append(b'aHR0cHM6Ly90aW55dXJsLmNvbS81MnNrYXJ3bg')
            new_pushed = True
            
            if debug == True:
                print("Pushed", row['url'])
            else:
                print("Pushed")
        except:
            print("Failed to push", row['url'])
            pass

if new_pushed == True:
    with open('state.pkl', 'wb') as f:
        pickle.dump(saved_state, f)
        print("Saved new state.")
else:
    print("No changes.")
