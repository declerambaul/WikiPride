'''
Starting with the Wikimedia SQL database schema, this module creates a set of tables that will be used to aggregate the cohort trends.
'''

import os
import logging
logger = logging.getLogger('Preprocessing')


import settings

from data.tables import *
from data.userlists import *
from db import sql


def dropTable(tablename):
    """Drops a SQL table in the user database

    :arg tablename: str, name of the table
    """
    try:        
        logger.info('Dropping %s'%tablename)
        cur = sql.getCursor()
        cur.execute("DROP TABLE IF EXISTS %s;"%tablename)
    except:
        pass

def tableExists(tablename):
    """Returns True if the table exists in the user database

    :arg tablename: str, name of the table
    """
    cur = sql.getCursor()
    cur.execute("show tables from %s like '%s';"%(settings.sqluserdb, tablename.split('.')[1]))
    
    if cur.fetchone()  is None:
        return False
    else:
        return True


def createTable(query,tablename):
    """Create a SQL table in the user database

    :arg tablename: str, name of the table
    :arg query: str, query to execute
    """
    try:
        if settings.sqldroptables:
            dropTable(tablename)
        else:
            # logger.info('Table %s not dropped.'tablename)    
            pass
        
        if not tableExists(tablename):
            cur = sql.getCursor()
            logger.info('Creating %s table'%tablename)
            cur.execute(query)
            logger.info('Finished creating %s table'%tablename)
        else:
            logger.info('Table %s exists already! Do nothing'%tablename)
    except:
        logger.exception("Could not create table %s"%tablename)



def createIndex(query,tablename):
    """Create an index on a SQL table in the user database

    :arg tablename: str, name of the table
    :arg query: str, query to execute
    """
    try:  
        cur = sql.getCursor()          
        cur.execute(query)
        logger.info("Created indexes on %s"%tablename)
    except:
        logger.warning("Could not create index on %s. Possibly it already exists"%tablename)

def executeCommand(command,comment):
    """Exports a SQL table into a file

    :arg command: str, the command used to export the 
    :arg comment: str, comment for logging stream
    """
    try:        
        logger.info(comment)
        os.system(command)        
    except:
        logger.info('Failed executing command: %s'%command)



def process():
    """Creates the auxiliary SQL tables on the user database.

    .. warning:
        This can take a long time. Especially for larger Wikipedias. For the English Wikipedia, it will take over a week :(
    """

    if settings.language in ['en','de']:
        logger.warning('YOU ARE ATTEMPTING TO RUN THE PREPROCESSING ON THE ENGLISH OR GERMAN WIKIPEDIA. HOPEFULLY YOU ARE PATIENT, THIS WILL TAKE A WHILE!')
    else:
        logger.warning('Be patient, this can take a long time. I hope you used the screen command...')
    
    logger.info('Preprocessing data for %swiki'%settings.language)

    

    # CREATE TABLES AND INDEXES    
    
    createTable(CREATE_USER_COHORTS,USER_COHORT)
    createIndex(INDEX_USER_COHORTS,USER_COHORT)    

    createTable(CREATE_REV_LEN_CHANGED,REV_LEN_CHANGED)
    createIndex(INDEX_REV_LEN_CHANGED,REV_LEN_CHANGED)

    createTable(CREATE_EDITOR_YEAR_MONTH,EDITOR_YEAR_MONTH)
    createTable(CREATE_EDITOR_YEAR_MONTH_NAMESPACE,EDITOR_YEAR_MONTH_NAMESPACE)

    # not creating the 'day' table, it can be used for time series analysis, it is not useful for cohort visualizations.
    # createTable(CREATE_EDITOR_YEAR_MONTH_DAY_NAMESPACE,EDITOR_YEAR_MONTH_DAY_NAMESPACE)

    createTable(CREATE_TIME_YEAR_MONTH_NAMESPACE,TIME_YEAR_MONTH_NAMESPACE)

    
    # not creating the 'day' table, it can be used for time series analysis, it is not useful for cohort visualizations.
    # createTable(CREATE_TIME_YEAR_MONTH_DAY_NAMESPACE,TIME_YEAR_MONTH_DAY_NAMESPACE)

    createTable(CREATE_BOT_LIST,BOT_LIST)
    createIndex(INDEX_BOT_LIST,BOT_LIST)

    
    executeCommand(EXPORT_BOT_LIST,'Exporting bot list for cohort analysis')








