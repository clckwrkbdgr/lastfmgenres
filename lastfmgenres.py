#
# http://www.last.fm/api/show/geo.getTopTracks
#
from pprint import pprint
import urllib.request
import urllib.parse
import urllib.error
import inspect
try:
	import json
except ImportError:
	import simplejson as json

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
		self.API_URL = "http://ws.audioscrobbler.com/2.0/"
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
			#Create an API Request
			url = self.API_URL + "?" + urllib.parse.urlencode(kwargs)
			#Send Request and Collect it
			data = urllib.request.urlopen( url )
			result = data.read().decode('utf-8')
			data.close()
			#Print it
			response_data = json.loads( result )
			if "error" in response_data:
				print(lastfm_error(response_data["error"]));
				return None
			#Close connection
			return response_data
		except urllib.error.HTTPError as e:
			print("HTTP error: {0}".format(e.code))
		except urllib.error.URLError as e:
			print("Network error: {0}".format(e.reason.args[1]))

	def get_top_artists(self, method, dict ):
		#find the key		  
		args = {
			"method":	method,
			"limit":	3
		}
		for key in dict.keys():
			args[key] = dict[key]
		
		response_data = self.send_request( args )
		if response_data is None:
			return
		
		print("~~~~~~~~~~~~~~" + str( args["method"] ) + "~~~~~~~~~~~~~~")
		
		#Get the first artist from the JSON response and print their name
		for artist in response_data["topartists"]["artist"]:
			print(artist["name"])
		
	def get_hyped_artists(self, method ):
		args = {
				"method":	method,
				"limit":	3
				}
		response_data = self.send_request( args )
		if response_data is None:
			return
		print("~~~~~~~~~~~~~~" + str( args["method"] ) +"~~~~~~~~~~~~~~")
		#Get the first artist from the JSON response and print their name
		for artist in response_data["artists"]["artist"]:
			print(artist["name"])
		
	def get_similar_tracks(self, method, dict ):
		args = {
		  "method":	method,
		  "limit":	3
		}
		for key in dict.keys():
			args[key] = dict[key]
			print(key, dict[key])
		
		response_data = self.send_request( args )
		if response_data is None:
			return
		print("~~~~~~~~~~~~~~" + str( args["method"] ) +"~~~~~~~~~~~~~~")
		#Get the first artist from the JSON response and print their name

		for artist in response_data["similartracks"]["track"]:
			print(artist["name"], artist["artist"]["name"])

def main():
	last_request = LastFM()
	last_request.get_top_artists( "tag.gettopartists", { "tag": "rock" } )
	last_request.get_top_artists( "geo.gettopartists", { "country": "spain" } )
	last_request.get_hyped_artists( "chart.getHypedArtists" )
	last_request.get_similar_tracks( "track.getsimilar", {
									"track": "Ray of Light",
									"artist": "Madonna"})

if __name__ == "__main__": main()
