import urllib2
from xml.etree.ElementTree import XML

class WeeServerError(Exception):
	def __init__(self, http_error=None, message='', *args, **kwargs):
		Exception.__init__(self, *args, **kwargs)
		self.http_error = http_error
		self.message = message

class WeeAuthError(Exception):
	pass

class WeeMonitor(object):
	username = ''
	key = ''
	headquarters_url = 'http://weewar.com/api1/headquarters'
	_opener = None

	def is_configured(self):
		return len(self.username) + len(self.key) > 0

	def set_auth_info(self, username, key):
		self.username = username
		self.key = key
		auth_handler = urllib2.HTTPBasicAuthHandler()
		auth_handler.add_password(
				realm='users',
				uri=self.headquarters_url,
				user=self.username,
				passwd=self.key
				)
		self._opener = urllib2.build_opener(auth_handler)

	def _get_xml_tree(self, url):
		try:
			hdl = self._opener.open(url)
		except urllib2.HTTPError, ex:
			if ex.code == 401:
				raise WeeAuthError()
			else:
				message=u"Game server is probably temporarily off."
				raise WeeServerError(http_error=ex, message=message)
		text = hdl.read()
		return XML(text)

	def user_games(self):
		tree = self._get_xml_tree(self.headquarters_url)
		games = {}
		for g in tree.findall('game'):
			gdata = {}
			for txtattr in ('id', 'name', 'state', 'link', 'since'):
				gdata[txtattr] = g.findall(txtattr)[0].text
			gdata['needs_attention'] = len(g.attrib.get('inNeedOfAttention', '')) > 0
			games[gdata['id']] = gdata
		return games
