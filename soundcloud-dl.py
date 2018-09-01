import re
import requests
import urllib.request
import json
import codecs
import os
import sys
import argparse

import eyed3
import taglib

# btw, this is not my id
CLIENTID="Oa1hmXnTqqE7F2PKUpRdMZqWoguyDLV0"
API = "https://api.soundcloud.com/i1/tracks/{0}/streams?client_id={1}"

headers = {
    'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) '
        'Gecko/20100101 Firefox/55.0'
}

def get_id(html):

	"""
	Getting the ID of the song
	"""
	try:
		song_id = re.findall('soundcloud://sounds:(.*?)"', html)[0]
		return song_id
	except IndexError:
		print("\033[91m✘ Could not find song ID\033[0m")
		sys.exit()

def get_tags(html):

	"""
	Getting the tags so that we can put it into the 
	music file
	"""
	title = re.findall('"title":"(.*?)",', html)[0]
	title = codecs.getdecoder("unicode_escape")(title)[0]

	artist = re.findall('"username":"(.*?)",', html)[0]
	artist = codecs.getdecoder("unicode_escape")(artist)[0]

	genre = re.findall('"genre":"(.*?)",', html)[0]
	genre = codecs.getdecoder("unicode_escape")(genre)[0]

	return title, artist, genre


def get_album_art_url(html):
	"""
	Getting the album art url so that we can download it
	and add it to the music file later
	"""
	return re.findall('img src="(.*?)" width="500"', html)[0]


def tag(fname, title, artist, genre, arturl):
	"""
	Yes, I know I can do the tagging in a better way.
	But I dont know how to. So I would not mind some
	help :)
	"""
	
	song = taglib.File(fname)

	song.tags["ARTIST"] = [artist]
	song.tags["TITLE"] = [title]

	# Giving the album the same name as
	# the title beacause 
	# I cant find the album name
	song.tags["ALBUM"] = [title]
	song.tags["GENRE"] = [genre]
	song.save()

	song = eyed3.load(fname)

	imagename = str(title+"500x500.jpg")

	image = urllib.request.urlretrieve(arturl, imagename)
	print("\033[92m✔ Album art downloaded\033[0m")

	imagedata = open(imagename, "rb").read()

	song.tag.images.set(3, imagedata, "image/jpeg")

	song.tag.save()

	# Always leave the place better than you found it ;)
	os.remove(imagename)


def main():

	parser = argparse.ArgumentParser(description = "Download SoundCloud music at 128kbps with album art and tags")

	parser.add_argument('url', action="store", help="URL to the song")

	args = parser.parse_args()


	r = requests.get(args.url, headers=headers)
	print("\033[92m✔ Fetched needed data\033[0m")

	html = r.text

	song_id = get_id(html)
	title = get_tags(html)[0]
	artist = get_tags(html)[1]
	genre = get_tags(html)[2]
	arturl = get_album_art_url(html)

	json_url = API.format(song_id, CLIENTID)

	data = requests.get(json_url, headers=headers)
	data = json.loads(data.text)

	# Getting the file url with the best quality
	file_url = data["http_mp3_128_url"]

	# Example file name --> Adele - Hello.mp3
	fname = str(artist+" - "+title+".mp3")
 
	urllib.request.urlretrieve(file_url, fname)
	print("\033[92m✔ Downloaded:\033[0m {0} by {1}".format(title, artist))

	# Making the file beautiful
	tag(fname, title, artist, genre, arturl)

	print("\033[92m✔ Saved:\033[0m {}".format(fname))



if __name__=="__main__":
	main()
