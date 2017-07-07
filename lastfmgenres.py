#
# http://www.last.fm/api/show/geo.getTopTracks
#
import urllib.request
import urllib.parse
import urllib.error
import time
import sys
try:
	import json
except ImportError:
	import simplejson as json

MIN_PLAYCOUNT = 3

lastfm_errors = {
		1  : "This error does not exist",
		2  : "Invalid service -This service does not exist",
		3  : "Invalid Method - No method with that name in this package",
		4  : "Authentication Failed - You do not have permissions to access the service",
		5  : "Invalid format - This service doesn't exist in that format",
		6  : "Invalid parameters - Your request is missing a required parameter",
		7  : "Invalid resource specified",
		8  : "Operation failed - Most likely the backend service failed. Please try again.",
		9  : "Invalid session key - Please re-authenticate",
		10 : "Invalid API key - You must be granted a valid key by last.fm",
		11 : "Service Offline - This service is temporarily offline. Try again later.",
		12 : "Subscribers Only - This station is only available to paid last.fm subscribers",
		13 : "Invalid method signature supplied",
		14 : "Unauthorized Token - This token has not been authorized",
		15 : "This item is not available for streaming.",
		16 : "The service is temporarily unavailable, please try again.",
		17 : "Login: User requires to be logged in",
		18 : "Trial Expired - This user has no free radio plays left. Subscription required.",
		19 : "This error does not exist",
		20 : "Not Enough Content - There is not enough content to play this station",
		21 : "Not Enough Members - This group does not have enough members for radio",
		22 : "Not Enough Fans - This artist does not have enough fans for for radio",
		23 : "Not Enough Neighbours - There are not enough neighbours for radio",
		24 : "No Peak Radio - This user is not allowed to listen to radio during peak usage",
		25 : "Radio Not Found - Radio station not found",
		26 : "API Key Suspended - This application is not allowed to make requests to the web services",
		27 : "Deprecated - This type of request is no longer supported",
		29 : "Rate Limit Exceded - Your IP has made too many requests in a short period, exceeding our API guidelines"
		}

def lastfm_error(error_code):
	return lastfm_errors[int(error_code)]

class LastFM:
	def __init__(self ):
		self.API_URL = "https://ws.audioscrobbler.com/2.0/"
		self.API_KEY = "a79472b2278b802963f190166498c59d"
	
	def send_request(self, args, **kwargs):
		#Request specific args
		kwargs.update( args )
		#Global args
		kwargs.update({
		  "api_key":  self.API_KEY,
		  "format":   "json"
		})
		try:
			sys.stdout.flush()
			#Create an API Request
			url = self.API_URL + "?" + urllib.parse.urlencode(kwargs)
			#Send Request and Collect it
			data = urllib.request.urlopen( url )
			result = data.read().decode('utf-8')
			#Close connection
			data.close()
			time.sleep(1) # Not to excide request per second limit (which is 1).

			response_data = json.loads( result )
			if "error" in response_data:
				print(lastfm_error(response_data["error"]));
				return None
			return response_data
		except urllib.error.HTTPError as e:
			print("HTTP error: {0}".format(e.code))
		except urllib.error.URLError as e:
			print("Network error: {0}".format(e.reason.args[1]))

	def get_library_artists(self, username):
		args = {
				"method":	'library.getartists',
				"user": username,
				"page": 1
				}
		total_page_count = 1
		artists = []
		while args["page"] <= total_page_count:
			response_data = self.send_request( args )
			if response_data is None:
				print('Retrieving page {0} of artist library for user {1} failed.'.format(args["page"], username))
				return []
			total_page_count = int(response_data["artists"]["@attr"]["totalPages"])
			print("Fetched page {0} out of {1}".format(args["page"], total_page_count))
			args["page"] += 1
			for artist in response_data["artists"]["artist"]:
				if int(artist["tagcount"]) == 0 and int(artist["playcount"]) >= MIN_PLAYCOUNT:
					artists.append(artist)

		return [artist["name"] for artist in artists]
	
	def get_artist_top_tags(self, artist):
		args = {
				"method":	'artist.gettoptags',
				"artist": artist
				}
		response_data = self.send_request( args )
		if response_data is None:
			print('Retrieving top tags for artist {1} failed.'.format(artist))
			return []
		tags = response_data["toptags"]
		if "tag" not in tags:
			return []
		tags = tags["tag"]
		if type(tags) is dict:
			return[tags["name"]]
		return [tag["name"] for tag in tags]

def main():
	if len(sys.argv) < 2:
		print("Usage: lastfmgenres.py <username>")
		return
	username = sys.argv[1]
	lastfm = LastFM()
	artists = lastfm.get_library_artists(username)
	current, total = 0, len(artists)
	if total <= 0:
		print('No artists to tag.')
		return
	print('Fetching...', end='')
	with open(username + '.txt', 'w') as f:
		f.write('# The format is: "<artist>":<tag>,<tag>,...\n')
		f.write('# It should not be changed.\n')
		f.write('# You can safely remove any artist (as whole line) or any tag.\n')
		f.write('# Of course, you can add new tags (and even artists).\n')
		f.write('# Just remember that tags are separated by commas and each new line represents separate artist.\n')
		for artist in artists:
			tags = lastfm.get_artist_top_tags(artist)
			f.write('"{0}":{1}\n'.format(artist, ','.join(tags)))
			print('\rArtist {0} of {1}.'.format(current + 1, total), end='')
			current += 1
	print('\rNow go edit file {0}.txt'.format(username))
	

if __name__ == "__main__":
	main()
