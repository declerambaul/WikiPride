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
import os, errno
import logging
logger = logging.getLogger('Report')

import utils
import settings

from data import userlists


class ReportItem():
    """
    A report consists of a collection of report items. A report item consists of a cohort instance and methods to generate the data and the plots.
    """
    def __init__(self, cohort, dest):

        self.cohort = cohort
        '''Cohort instance
        '''

        self.relDest = dest
        '''Relative path to the destination directory'''

    def createDirectory(self,base):
        '''Creates the directory if it doesn't exist already. The `base` directory is joined with the relative destination directory and returned.

        :arg base: base directory (e.g. settings.datadirectory or settings.wikipridedirectory)
        :returns: absolute path
        '''
        p = os.path.join(base,self.relDest)

        try:
            os.makedirs(p)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST:
                pass
            else: raise
        return p

    def loadData(self):
        '''Loads the data from disk if available
        '''    
        for varName in self.cohort.data_description.keys():  
            self.cohort.loadDataFromDisk(varName=varName,destination=os.path.join(REPORTDATA,self.relDest))

    def freeData(self):
        '''Frees the data in hope of reducing the memory usage of the process.        
        '''  
        for varName in self.cohort.data.keys():  
            del self.cohort.data[varName]
        



    def generateData(self):
        '''Generates and saves the cohort data. Calls the :meth:`.aggregateDataFromSQL` method from the :class:`.Cohort` instance passed as argument. The collected data matrices are stored in the :attr:`.Cohort.data` attribute. The data matrices are saved as txt files in the data destination directory.'''
        
        self.cohort.aggregateDataFromSQL(verbose=True)   
        
        dest = self.createDirectory(base=REPORTDATA)
        self.cohort.saveDataToDisk(destination=dest)

        
        self.freeData()


    def generateVisualizations(self,varNames, **kargs):
        '''For the variables names in `varNames`, produces the WikiPride graphs using :meth:`.wikiPride` (e.g. `added`, `editors`, ...).

        :arg varNames: list of str, containing the names of the variables for which wikipride should be produced.
        :arg **kargs: arguments passed directly to :meth:`.wikiPride`. E.g. `flip=True`, `percentage=False`
        '''
        
        self.loadData()

        dest = self.createDirectory(base=REPORTGRAPHS)

        for v in varNames:
            self.cohort.wikiPride(varName=v,dest=dest,**kargs)
        
        self.cohort.linePlots(dest=dest)

        self.freeData()


#Absolute path directories

REPORTDATA = os.path.join(settings.reportdirectory,'data')
REPORTGRAPHS = os.path.join(settings.reportdirectory,'graphs')
REPORTLISTS = os.path.join(settings.reportdirectory,'lists')


#Relative path directory tree for the report

COMMUNITY = "Community_roles" 

COHORTTREND =  "Cohort_trends"
AGE = os.path.join(COHORTTREND,"Age_cohorts")
ABS_AGE = os.path.join(COHORTTREND,"Absolute_age")
ABS_MORE1 = os.path.join(ABS_AGE,"More_than_1_edit")
ABS_MORE5 = os.path.join(ABS_AGE,"More_than_5_edits")
ABS_MORE100 = os.path.join(ABS_AGE,"More_than_100_edits")
ABS_LESS100 = os.path.join(ABS_AGE,"Less_than_100_edits")
REL_AGE = os.path.join(COHORTTREND,"Relative_age")
REL_MORE1 = os.path.join(REL_AGE,"More_than_1_edit")
REL_MORE5 = os.path.join(REL_AGE,"More_than_5_edits")
REL_MORE100 = os.path.join(REL_AGE,"More_than_100_edits")
REL_LESS100 = os.path.join(REL_AGE,"Less_than_100_edits")

NEWEDITORS = os.path.join(COHORTTREND,"New_editors")
HISTOGRAM = os.path.join(COHORTTREND,"Histogram_cohorts")
NAMESPACES = os.path.join(COHORTTREND,"Namespaces")

USERLISTS = "User_lists" 


# Report items
    
from cohorts import age
from cohorts import histogram
from cohorts import simple

absMore1 = ReportItem(cohort=age.AbsoluteAgeAllNamespaces(minedits = 1), dest=ABS_MORE1)
absMore5 = ReportItem(cohort=age.AbsoluteAgeAllNamespaces(minedits = 5), dest=ABS_MORE5)
absMore100 = ReportItem(cohort=age.AbsoluteAgeAllNamespaces(minedits = 100), dest=ABS_MORE100)
absLess100 = ReportItem(cohort=age.AbsoluteAgeAllNamespaces(minedits = 1,maxedits = 100), dest=ABS_LESS100)


relMore1 = ReportItem(cohort=age.RelativeAgeAllNamespaces(minedits = 1), dest=REL_MORE1)
relMore5 = ReportItem(cohort=age.RelativeAgeAllNamespaces(minedits = 5), dest=REL_MORE5)
relMore100 = ReportItem(cohort=age.RelativeAgeAllNamespaces(minedits = 100), dest=REL_MORE100)
relLess100 = ReportItem(cohort=age.RelativeAgeAllNamespaces(minedits = 1,maxedits = 100), dest=REL_LESS100)


editorActivity = ReportItem(cohort=histogram.EditorActivity(), dest=HISTOGRAM)

nsCohort = ReportItem(cohort=simple.NameSpaces(), dest=NAMESPACES)
newEditors = ReportItem(cohort=simple.NewEditors(), dest=NEWEDITORS)


    
def processData():
    '''The aggregation of the cohort data requires that  :func:`data.preprocessing.process` has been executed and the data thus preprocessed. The :func:`data.cohortdata.processData` method will use the report definition in :mod:`.report` to create a directory structure that contains the data of the cohort defitintions described below. The data is stored in the form of `numpy` matrices.                
    '''
    logger.info('Aggregating the cohort data for %swiki'%settings.language)

    utils.setFilterBots(settings.filterbots,userlists.BOT_LIST_FILE)

    # aggregate and save cohort data
    absMore1.generateData()
    absMore5.generateData()
    absMore100.generateData()
    absLess100.generateData()
    
    relMore1.generateData()
    relMore5.generateData()
    relMore100.generateData()
    relLess100.generateData()

    editorActivity.generateData()

    nsCohort.generateData()
    
    newEditors.generateData()


def processCSV():
    '''The aggregation of the cohort data requires that  :func:`data.preprocessing.process` has been executed and the data thus preprocessed. The :func:`data.cohortdata.processData` method will use the report definition in :mod:`.report` to create a directory structure that contains the data of the cohort defitintions described below. The data is stored in the form of `numpy` matrices.                
    '''
    logger.info('Aggregating the cohort data for %swiki'%settings.language)

    utils.setFilterBots(settings.filterbots,userlists.BOT_LIST_FILE)

    # aggregate and save cohort data
    absMore1.generateCSV()
    absMore5.generateCSV()
    absMore100.generateCSV()
    absLess100.generateCSV()
    
    relMore1.generateData()
    relMore5.generateData()
    relMore100.generateData()
    relLess100.generateData()

    editorActivity.generateData()

    nsCohort.generateData()
    
    newEditors.generateData()




def processReport():
    '''Creates a set of graphs which requires that :func:`data.report.processData` has been executed and the data thus aggregated. The data is loaded from disk.
    '''    

    stdVars = ['added','edits','editors']

    absMore1.generateVisualizations(varNames=stdVars)
    absMore5.generateVisualizations(varNames=stdVars)
    absMore100.generateVisualizations(varNames=stdVars)
    absLess100.generateVisualizations(varNames=stdVars)

    relMore1.generateVisualizations(varNames=stdVars, flip=True)
    relMore5.generateVisualizations(varNames=stdVars, flip=True)
    relMore100.generateVisualizations(varNames=stdVars, flip=True)
    relLess100.generateVisualizations(varNames=stdVars, flip=True)

    editorActivity.generateVisualizations(varNames=stdVars)

    nsCohort.generateVisualizations(varNames=['added','edits'])

    newEditors.generateVisualizations(varNames=['editors'], percentage=False,colorbar=False)






