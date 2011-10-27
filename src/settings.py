'''
Settings used for cohort analysis. Many of these settings can be overwritten in the cohort class __init__ calls.
'''

import utils
import logging

# Configure logging
logging.basicConfig( level=logging.DEBUG, format='%(asctime)s - %(name)s: %(message)s', datefmt='%b-%d %H:%M')


###
### General
###
language = None
'''The language of the Wikipedia (e.g. 'en','pt')
'''

nobots = None
'''Filter out known bots?
'''
botfile = None
'''Path to the file containing all known bot user_ids
'''


''' MOVE INTO COHORT DEFINITIONS WHERE NEEDED!
NS = ( '-2','-1','0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '100', '101','108','109')
# NS = ( '4', '5' )
# NS = ( '0' )
Filter for namespaces
'''

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
ncolors = None
'''The number of colors to use in colormap. None defaults to the number
of colors defined by the cohorts, usually equal to the number of cohorts
'''
wikiprideDirectory = '../wikipride'
'''Path to wikipride visualizations (no / at the end!)
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
'''The name of the database on db host where the Mediawiki database is stored. On the toolserver, this is for example 'ptwiki_p'
'''
sqluserdb = None
'''The name of the database on db host where the aggregated tables will be stored. On the toolserver, this is the username prepended by a 'u_', e.e. 'u_delcerambaul'
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



def readConfig(configfile):
	'''
	Reads the configuration from `ConfigParser` instance into the runtime settings.

	:arg configfile: A file that can be read by a `ConfigParser` instance
	'''

	global language,nobots,botfile,basedirectory,datadirectory,reportdirectory,wikipridedirectory,sqlhost,sqlwikidb,sqluserdb,sqlconfigfile,sqldroptables


	import ConfigParser

	config = ConfigParser.ConfigParser()
	config.read(configfile)


	import os

	# general settings
	language = config.get('General','language') 
	nobots = config.get('General','nobots')
	botfile = config.get('General','botfile')
	utils.setFilterBots(nobots,botfile)
	
	(time_stamps,time_stamps_index) = utils.create_time_stamps_month(fromym='200401',toym='201106')

	if language == 'None':
		language = None


	# directories
	basedirectory = config.get('Directories','basedirectory')
	datadirectory = config.get('Directories','datadirectory')
	reportdirectory = config.get('Directories','reportdirectory')
	wikipridedirectory = config.get('Directories','wikipridedirectory')

	if not os.path.isdir(basedirectory):
		print basedirectory
		logging.warning("%s not a valid basedirectory"%basedirectory)
	if not os.path.isdir(datadirectory):
		print datadirectory
		logging.warning("%s not a valid datadirectory"%datadirectory)
	if not os.path.isdir(reportdirectory):
		logging.warning("%s not a valid reportdirectory"%reportdirectory)
	if not os.path.isdir(wikipridedirectory):
		logging.warning("%s not a valid wikipridedirectory"%wikipridedirectory)


	# sql
	sqlhost = config.get('MySQL','sqlhost')
	sqlwikidb = config.get('MySQL','sqlwikidb')
	sqluserdb = config.get('MySQL','sqluserdb')
	sqlconfigfile = config.get('MySQL','sqlconfigfile')	
	sqldroptables = config.getboolean('MySQL','sqldroptables')	

	# the default config sqlhost host is set to LANUAGEwiki-p.rrdb.toolserver.org	
	if 'LANUAGE' in sqlhost and language is not None:
		sqlhost = sqlhost.replace('LANUAGE',language)

	sqlconfigfile = os.path.expanduser(sqlconfigfile)
	if not os.path.isfile(sqlconfigfile):
		logging.warning("%s sql config file not found"%sqlconfigfile)
		


	# mongo db

	# not implemented at this point. if needed in the future (again), extract config settings here.
