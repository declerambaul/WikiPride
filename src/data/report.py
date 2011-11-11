"""This module defines the content of a report, which consists of the following at the moment. 

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


"""
import os
import logging
logger = logging.getLogger('Report')

import utils
import settings


from data import userlists


REPORTDATA = os.path.join(settings.reportdirectory,'data')
REPORTGRAPHS = os.path.join(settings.reportdirectory,'graphs')
REPORTLISTS = os.path.join(settings.reportdirectory,'lists')

# Directories

COMMUNITY = "Community_roles" # os.path.join(settings.datadirectory,"Community_roles")

COHORTTREND =  "Cohort_trends" # os.path.join(settings.datadirectory,"Cohort_trends")
AGE = os.path.join(COHORTTREND,"Age_cohorts")
ABS_AGE = os.path.join(COHORTTREND,"Absolute_Age")
ABS_MORE1 = os.path.join(ABS_AGE,"More_than_1_edit")
ABS_MORE5 = os.path.join(ABS_AGE,"More_than_5_edits")
ABS_MORE100 = os.path.join(ABS_AGE,"More_than_100_edits")
ABS_LESS100 = os.path.join(ABS_AGE,"Less_than_100_edits")
REL_AGE = os.path.join(COHORTTREND,"Relative_Age")
REL_MORE1 = os.path.join(REL_AGE,"More_than_1_edit")
REL_MORE5 = os.path.join(REL_AGE,"More_than_5_edits")
REL_MORE100 = os.path.join(REL_AGE,"More_than_100_edits")
REL_LESS100 = os.path.join(REL_AGE,"Less_than_100_edits")

NEWEDITORS = os.path.join(COHORTTREND,"New_editors")
HISTOGRAM = os.path.join(COHORTTREND,"Histogram_cohorts")
NAMESPACES = os.path.join(COHORTTREND,"Namespaces")

USERLISTS = "User_lists" # os.path.join(settings.datadirectory,"User_lists")


# Cohort instances that are part of the report

from cohorts import age

absMore1 = age.AbsoluteAgeAllNamespaces(minedits = 1)
absMore5 = age.AbsoluteAgeAllNamespaces(minedits = 5)
absMore100 = age.AbsoluteAgeAllNamespaces(minedits = 100)
absLess100 = age.AbsoluteAgeAllNamespaces(minedits = 1,maxedits = 100)

relMore1 = age.RelativeAgeAllNamespaces(minedits = 1)
relMore5 = age.RelativeAgeAllNamespaces(minedits = 5)
relMore100 = age.RelativeAgeAllNamespaces(minedits = 100)
relLess100 = age.RelativeAgeAllNamespaces(minedits = 1,maxedits = 100)



def getDirectory(base,reporttype):
    """Joins the base directory with the specific report type directory

    :arg base: base directory (e.g. settings.datadirectory or settings.wikipridedirectory)
    """
    return os.path.join(base,reporttype)


def createDirectories(base):
    """Create the directory structure of the report as described in :mod:`.cohortdata`.

    :arg base: base directory (e.g. settings.datadirectory or settings.wikipridedirectory)
    """
    # try:        
    #     logger.info("Creating directory structure for cohort data")

    os.system('rm -Rf %s'%base)
    os.system('mkdir -p %s'%base)

    os.mkdir(getDirectory(base, COHORTTREND))
    os.mkdir(getDirectory(base, ABS_AGE))
    os.mkdir(getDirectory(base, ABS_MORE1))
    os.mkdir(getDirectory(base, ABS_MORE5))
    os.mkdir(getDirectory(base, ABS_MORE100))
    os.mkdir(getDirectory(base, ABS_LESS100))

    os.mkdir(getDirectory(base, REL_AGE))
    os.mkdir(getDirectory(base, REL_MORE1))
    os.mkdir(getDirectory(base, REL_MORE5))
    os.mkdir(getDirectory(base, REL_MORE100))
    os.mkdir(getDirectory(base, REL_LESS100))

    # os.mkdir(getDirectory(base, NEWEDITORS))
    # os.mkdir(getDirectory(base, HISTOGRAM))
    # os.mkdir(getDirectory(base, NAMESPACES))

    # except:
    #     logger.info('Failed to create report directory structure (directories already exists?)')



def processCohortData(cohort,destination):
    """Calls the :meth:`.aggregateDataFromSQL` method from the :class:`.Cohort` instance passed as argument. The collected data matrices are stored in the :attr:`.Cohort.data` attribute. The data matrices are saved as txt files in the `destination` directory.

    :arg cohort: :class:`.Cohort` instance
    :arg destination: destination directory for saved data
    """
    cohort.aggregateDataFromSQL(verbose=True)    
    cohort.dataToDisk(destination=destination)

    
def processData():
    '''The aggregation of the cohort data requires that  :func:`data.preprocessing.process` has been executed and the data thus preprocessed. The :func:`data.cohortdata.processData` method will use the report definition in :mod:`.report` to create a directory structure that contains the data of the cohort defitintions described below. The data is stored in the form of `numpy` matrices.                
    '''
    logger.info('Aggregating the cohort data for %swiki'%settings.language)

    utils.setFilterBots(settings.filterbots,userlists.BOT_LIST_FILE)

    createDirectories(REPORTDATA)

    # aggregate and save cohort data
    processCohortData(cohort=absMore1,destination=getDirectory(REPORTDATA,ABS_MORE1))
    processCohortData(cohort=absMore5,destination=getDirectory(REPORTDATA,ABS_MORE5))
    processCohortData(cohort=absMore100,destination=getDirectory(REPORTDATA,ABS_MORE100))
    processCohortData(cohort=absLess100,destination=getDirectory(REPORTDATA,ABS_LESS100))

    processCohortData(cohort=relMore1,destination=getDirectory(REPORTDATA,REL_MORE1))
    processCohortData(cohort=relMore5,destination=getDirectory(REPORTDATA,REL_MORE5))
    processCohortData(cohort=relMore100,destination=getDirectory(REPORTDATA,REL_MORE100))
    processCohortData(cohort=relLess100,destination=getDirectory(REPORTDATA,REL_LESS100))




def produceWikiPrideGraphs(cohort,destination,flip=False):
    '''Produces the `added`, `edits`, `editors` WikiPride graphs using :meth:`.wikiPride`.

    :arg cohort: :class:`.Cohort` instance
    :arg destination: str, destination directory for plots
    :arg flip: bool, see :meth:`.Cohort.wikiPride`
    '''

    pdf = False
    verbose = True

    cohort.wikiPride(varName='added',dest=destination,pdf=pdf,flip=flip,verbose=verbose)
    cohort.wikiPride(varName='edits',dest=destination,pdf=pdf,flip=flip,verbose=verbose)
    cohort.wikiPride(varName='editors',dest=destination,pdf=pdf,flip=flip,verbose=verbose)



def produceGraphs():
    '''
    Given all the cohort data, this method produces a set of visualizations and stores them in a directory structure
    '''

    createDirectories(REPORTGRAPHS)
    produceWikiPrideGraphs(cohort=absMore1,destination=getDirectory(REPORTGRAPHS,ABS_MORE1))
    produceWikiPrideGraphs(cohort=absMore5,destination=getDirectory(REPORTGRAPHS,ABS_MORE5))
    produceWikiPrideGraphs(cohort=absMore100,destination=getDirectory(REPORTGRAPHS,ABS_MORE100))
    produceWikiPrideGraphs(cohort=absLess100,destination=getDirectory(REPORTGRAPHS,ABS_LESS100))

    produceWikiPrideGraphs(cohort=relMore1,flip=True,destination=getDirectory(REPORTGRAPHS,REL_MORE1))
    produceWikiPrideGraphs(cohort=relMore5,flip=True,destination=getDirectory(REPORTGRAPHS,REL_MORE5))
    produceWikiPrideGraphs(cohort=relMore100,flip=True,destination=getDirectory(REPORTGRAPHS,REL_MORE100))
    produceWikiPrideGraphs(cohort=relLess100,flip=True,destination=getDirectory(REPORTGRAPHS,REL_LESS100))
    

def report():
    '''Executes the `report` step. I.e. both the `data` and the `graphs` work flow step.
    '''    
    processData()
    produceGraphs()






