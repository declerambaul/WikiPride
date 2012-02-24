'''
Settings used for cohort analysis. Many of these settings can be overwritten in the cohort class __init__ calls.
'''

import utils
import logging

# Configure logging
format='%(asctime)s - %(name)s: %(message)s'
logging.basicConfig( level=logging.DEBUG, format=format, datefmt='%b-%d %H:%M',filename='wikipride.log')
# Log to file and in console
console = logging.StreamHandler()
formatter = logging.Formatter(format)
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


logger = logging.getLogger('Settings')



###
### General
###
language = None
'''The language of the Wikipedia (e.g. 'en','pt')
'''

filterbots = None
'''Filter out known bots?
'''
#TODO REMOVE FILTER BOTS FROM SETTINGS!!!
#legacy
@property
def nobots():
	return filterbots


time_stamps = None
'''List containing all YM (e.g. '200401' for January 2004) that we want to analyze
'''
time_stamps_index = None
'''A dictionary mapping each YM in `time_stamps` to its array index (used to access numpy arrays)
'''


###
### WikiPride visualizations
###
cmapName = 'spectral'
'''Colormap to use. Has to be a valid name in matplotlib.pyplot.cm.datad
'''


###
### Directories
###
basedirectory = None
'''Path to base directory for the wikipride project
'''
datadirectory = None
'''Path to directory for cohort data
'''
userlistdirectory = None
'''Path to directory for user lists
'''
reportdirectory = None
'''Path to store report 
'''
wikipridedirectory = None
'''Path to store wikipride visualizations of user defined cohorts
'''


###
### Database configuration
###


# SQL
sqlhost = None
'''The host name of the MySql server
'''
sqlwikidb = None
'''The name of the database on db host where the Mediawiki database is stored. On the toolserver, this is for example `ptwiki_p`
'''
sqluserdb = None
'''The name of the database on db host where the aggregated tables will be stored. On the toolserver, this is the username prepended by a `u_`, e.e. `u_delcerambaul`
'''
sqlconfigfile = None
'''
The path to the MySQL configuration for logging into the server, e.g. '~/.my.cnf'
'''
sqldroptables = None
'''
If `True`, all tables that we attempt to create will be dropped if they exist already. If `False`, only tables don't exist already will be created
'''

'''  MOVE INTO COHORT DEFINITIONS WHERE NEEDED!
sqlquery = 'SELECT *  FROM ptwiki_editor_centric_year_month;'
The SQL query that is used to aggregate the data
'''


# Mongo DB (Legacy code so far, only using MySQL at the moment)
mongodb = 'wikilytics'
'''The name of the db
'''
mongocol = 'enwiki_editors_dataset'
'''The name of the collection 
'''
mongoQueryVars = None
'''The Mongo query variables used to aggregate the data.
'''

def setTimeStamps(startYM,endYM):
	global time_stamps,time_stamps_index
	(time_stamps,time_stamps_index) = utils.create_time_stamps_month(fromym=startYM,toym=endYM)


def readConfig(configfile):
	'''
	Reads the configuration from `ConfigParser` instance into the runtime settings.

	:arg configfile: A file that can be read by a `ConfigParser` instance
	'''

	global language,filterbots,time_stamps,time_stamps_index,botfile,basedirectory,datadirectory,userlistdirectory,reportdirectory,wikipridedirectory,sqlhost,sqlwikidb,sqluserdb,sqlconfigfile,sqldroptables

	import os
	import ConfigParser

	config = ConfigParser.ConfigParser()
	config.read(configfile)

	# general settings
	language = config.get('General','language') 
	if len(language) != 2:
		raise Exception('Language code should be two characters (%s)'%language)

	filterbots = config.get('General','filterbots')	
	
	startYM = config.get('General','startYM') 
	endYM = config.get('General','endYM') 
	(time_stamps,time_stamps_index) = utils.create_time_stamps_month(fromym=startYM,toym=endYM)
	
	# directories	
	basedirectory = os.path.expanduser(config.get('Directories','basedirectory'))
	datadirectory = os.path.expanduser(config.get('Directories','datadirectory'))
	userlistdirectory = os.path.expanduser(config.get('Directories','userlistdirectory'))
	reportdirectory = os.path.expanduser(config.get('Directories','reportdirectory'))
	wikipridedirectory = os.path.expanduser(config.get('Directories','wikipridedirectory'))

	# if not os.path.isdir(basedirectory):
	# 	import errno
	# 	try:
	# 	    os.makedirs(p)
	# 	except OSError as exc: # Python >2.5
	# 	    if exc.errno == errno.EEXIST:
	# 	        pass
	# 	    else: raise

	# sql
	sqlhost = config.get('MySQL','sqlhost')
	sqlwikidb = config.get('MySQL','sqlwikidb')
	sqluserdb = config.get('MySQL','sqluserdb')
	sqlconfigfile = config.get('MySQL','sqlconfigfile')	
	sqldroptables = config.getboolean('MySQL','sqldroptables')	

	sqlconfigfile = os.path.expanduser(sqlconfigfile)
	if not os.path.isfile(sqlconfigfile):
		logger.warning("%s sql config file not found"%sqlconfigfile)
		


	# mongo db

	# not implemented at this point. if needed in the future (again), extract config settings here.
