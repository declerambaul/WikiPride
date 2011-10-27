'''
Creates a database connection to the slave replica on alpha and implements methods for querying the database
'''


import os
import settings
import logging


db = None
'''SQL connection instance
'''

def connect():
    """
    Connect to the MySQL database
    """
    try:
        import MySQLdb,MySQLdb.cursors
    except:
        logging.error("SQL module MySQLdb could not be imported.")    

    global db
    if db is None:
        db = MySQLdb.connect(db=settings.sqluserdb, host=settings.sqlhost, read_default_file=settings.sqlconfigfile)


def getSSDictCursor():
    """
    Returns a server-side dictionary cursor
    """

    connect()

    return db.cursor(MySQLdb.cursors.SSDictCursor)

def getSSCursor():
    """
    Returns a server-side  cursor
    """
    
    connect()

    return db.cursor(MySQLdb.cursors.SSCursor)

def getCursor():
    """
    Returns a normal cursor
    """

    connect()

    return db.cursor()

