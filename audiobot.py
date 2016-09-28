#!/usr/bin/python
import telepot
from pydub import *
import urllib2
import time
import json


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv


def audio_to_text():
    language = 'pt-br'
    audio_pieces = list()   # might need to divide audio into smaller pieces
    song = AudioSegment.from_ogg('./audio.ogg')    # load audio as python variable
    if len(song) > 20 * 1000:   # divide audio into smaller pieces of 20 seconds each 
        for i in range(0, len(song), 20 * 1000):
            audio_pieces.append(song[i:i + 20 * 1000])
    else:
        audio_pieces.append(song)
    for song in audio_pieces:
        song.export('audio.flac', format="flac", bitrate="48000")   # convert to FLAC since google expects it
        flac_file = open('./audio.flac', 'rb')
        flac_data = flac_file.read()
        flac_file.close()
        audio = flac_data
        header = {"Content-Type": "audio/x-flac; rate=48000"}
        keys = ["AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw"]  # Default key of
        # https://github.com/Uberi/speech_recognition/blob/master/speech_recognition/__init__.py
        response = ''
        while True:
            try:
                url = "https://www.google.com/speech-api/v2/recognize?output=json&lang=%s&key=%s" % (language, keys[0])
                data = urllib2.Request(url, audio, header)
                post = urllib2.urlopen(data)
                response = post.read().split('\n')
                break
            except Exception as exception:
                print
                print "EXCEPTION:"
                print exception
                print "When sending to google"
                print "Trying again!"
                time.sleep(2)
        if len(response) < 2:
            print 'NOTHING'
            return

        response = json.loads(response[1], object_hook=_decode_dict)
        best_response = response['result'][0]['alternative'][0]['transcript']
        print best_response
        bot.sendMessage(user, best_response)


def save_audio(audio):
    global user
    if 'chat' in audio:
        if 'id' in audio.get('chat'):
            user = audio.get('chat').get('id')
    if 'voice' not in audio:
        print 'Not an audio file'
        return
    print ('Got audio!')
    key = audio['voice'].get('file_id')
    bot.download_file(key, './audio.ogg')
    print ('Downloaded audio!')
    audio_to_text()


if __name__ == '__main__':
    global bot
    global user
    bot = telepot.Bot('225272590:AAH47dvt1W6_xiXeENY6XLqX7UHXrpPEKfc')
    bot.getMe()    # register bot
    bot.message_loop(save_audio)    # call back when messages arrive
    while 1:
        time.sleep(0.1)    # prevent script from quitting 




