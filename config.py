import os

class Config(object):
	_filename = None

	def get_file_name(self):
		if self._filename:
			return self._filename
		try:
			return os.path.join(os.environ['HOME'], '.weewar-monitor')
		except KeyError:
			return os.path.join(os.getcwd(), 'weewar-monitor.cfg')

	def _read(self, name):
		try:
			cfg = file(name, 'r')
			username, api_key, interval = cfg.readline().split(':')
			self.username = username
			self.api_key = api_key
			self.interval = int(interval)
			cfg.close()
		except (IOError, ValueError):
			cfg = file(name, 'wb')
			cfg.close()
			self.username = ''
			self.api_key = ''
			self.interval = 30

	def save(self):
		cfg = file(self.get_file_name(), 'wb')
		cfg.write('%s:%s:%d' % (self.username, self.api_key, self.interval))
		cfg.close()

	def __init__(self):
		self._read(self.get_file_name())
