'''
Starting with the Wikimedia SQL database schema, this module creates a set of tables that will be used to aggregate the cohort trends.
'''
import logging
logger = logging.getLogger('Preprocessing')


import settings

from data.tables import *
from db import sql


def dropTable(tablename):
    """Drops a SQL table in the user database

    :arg cur: MySQL cursor
    :arg tablename: str, name of the table
    """
    try:        
        logger.info('Dropping %s'%tablename)
        cur = sql.getCursor()
        cur.execute("DROP TABLE IF EXISTS %s;"%tablename)
    except:
        pass

def createTable(query,tablename):
    """Create a SQL table in the user database

    :arg tablename: str, name of the table
    :arg query: str, query to execute
    """
    try:        
        logger.info('Creating %s table'%tablename)
        cur = sql.getCursor()
        cur.execute(query)
        logger.info('Finished creating %s table'%tablename)
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

    

    # DROP TABLES 
    if settings.sqldroptables:
        
        dropTable(USER_COHORT)        
        dropTable(REV_LEN_CHANGED)
        dropTable(EDITOR_YEAR_MONTH)
        dropTable(EDITOR_YEAR_MONTH_NAMESPACE)
        dropTable(EDITOR_YEAR_MONTH_DAY_NAMESPACE)

    else:
        logger.info('No tables are being dropped! If they already exist nothing will be created in the next step.')



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











