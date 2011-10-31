'''
The aggregation of the cohort data requires that  :func:`data.preprocessing.process` has been executed and the data thus preprocessed. The :func:`data.cohortdata.process` method will create a directory structure that contains the data of the cohort defitintions described below. The data is saved in the form of `numpy` matrices.

* Community roles
    * User  
    * Administrators
    * .... other roles ....
* Cohort trends
    * Age Cohorts            
        * More than 1 edit 
        * More than 5 edit 
        * More than 100 edit 
        * Less than 100 edits 
    * New editors
    * Histogram cohorts
    * Namespaces
* User lists
    * Most active editors
    
            
            
'''

import os
import logging
logger = logging.getLogger('Cohort data')

import utils
import settings

from data.userlists import *


communityroles = os.path.join(settings.datadirectory,"Community roles")

cohorttrend = os.path.join(settings.datadirectory,"Cohort trends")
agecohorts = os.path.join(cohorttrend,"Age cohorts")
more1 = os.path.join(agecohorts,"More than 1 edit")
more5 = os.path.join(agecohorts,"More than 5 edits")
more100 = os.path.join(agecohorts,"More than 100 edits")
less100 = os.path.join(agecohorts,"Less than 100 edits")
neweditors = os.path.join(cohorttrend,"New editors")
histogramcohorts = os.path.join(cohorttrend,"Histogram cohorts")
namespaces = os.path.join(cohorttrend,"Namespaces")
userlists = os.path.join(settings.datadirectory,"User lists")


def createDirectories():
    """Create the directory structure of the report as described in :mod:`.cohortdata`.
    """
    try:        
        logger.info("Creating directory structure for cohort data")

        os.mkdir(cohorttrend)
        os.mkdir(agecohorts)
        os.mkdir(more1)
        os.mkdir(more5)
        os.mkdir(more100)
        os.mkdir(less100)
        os.mkdir(neweditors)
        os.mkdir(histogramcohorts)
        os.mkdir(namespaces)
        os.mkdir(userlists)
    except:
        logger.info('Failed to create directory structure')



def executeCommand(command,comment):
    """Executes a system command.

    :arg command: str, the command used to export the 
    :arg comment: str, comment for logging stream
    """
    try:        
        logger.info(comment)
        os.system(command) 
    except:
        logger.info('Failed executing command: %s'%comment)


def createCohorttrends():
    """Create the cohort trends data as described in :mod:`.cohortdata`.

    :arg command: str, the base directory in which the report structure is built
    """

    logger.info("Aggregating the Cohort Trend data")

    agecohorts 

    from cohorts import age

    


    '''
    more1 = os.path.join(agecohorts,"More than 1 edit")
    more5 = os.path.join(agecohorts,"More than 5 edits")
    more100 = os.path.join(agecohorts,"More than 100 edits")
    less100 = os.path.join(agecohorts,"Less than 100 edits")
    neweditors = os.path.join(cohorttrend,"New editors")
    histogramcohorts = os.path.join(cohorttrend,"Histogram cohorts")
    namespaces = os.path.join(cohorttrend,"Namespaces")
    '''


def process():
    """Aggregates the cohort data for a select set of cohort definitions, see :mod:`.cohortdata`.
    """

    logger.info('Aggregating the cohort data for %swiki'%settings.language)

    utils.setFilterBots(settings.filterbots,BOT_LIST_FILE)

    createDirectories()

    createCohorttrends()
    """
    create directory structure
    create 

    """


    





