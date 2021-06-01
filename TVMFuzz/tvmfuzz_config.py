from configparser import ConfigParser
from ast import literal_eval
from os.path import dirname, realpath, join

config_parser = ConfigParser()
config_path = join(dirname(realpath(__file__)), "tvmfuzz_settings.ini")
config_parser.read(config_path)

class TVMFuzzConfig(object):
	def __init__(self,parameters):
		for name,value in parameters.items():
			setattr(TVMFuzzConfig,name,literal_eval(value))

parameters = {}
for section in config_parser.sections():
	for option in config_parser.options(section):
		parameters[option] = config_parser.get(section,option)

TVMFuzzConfig(parameters)
