'''Cohorts designed to replicate Erik Zachte's report card metrics. The cohorts use the XXwiki_editor_centric_year_month_ns0_noredirect table.

'''

import sys,logging
logger = logging.getLogger('Report Card Cohorts')

try:
    import numpy as N
except:
    logger.error('Numpy not installed')
    

import settings
import utils

from cohorts.base import Cohort
from data import tables


class EditorTrends(Cohort):
    '''A cohort corresponds to an activity level. The reportcard currently features 5+ and 100+ as active editor category. 

    .. warning:
        The wikipride plots for this cohort definition is useless. It doesn't make sense to have a stacked bar chart as the 100+ editors are a subset of the 5+ editors (one editor can be assigned to multiple cohorts for one time unit). See the :meth:`.linePlots` method instead.
    '''
    def __init__(self,activitylevels=[5,10,100]):

        self.cohorts = activitylevels
        '''Cohort definition
        '''                
        self.cohort_labels = ['%s+ edits'%l for l in self.cohorts]
        '''Cohort labels
        '''     
        
        self.sqlQuery = 'SELECT *,(noop_edits+add_edits+remove_edits) as total_edits FROM %s;'%tables.EDITOR_YEAR_MONTH_NS0_NOREDIRECT
        '''The SQL query returns edit information for each editor for each ym she has edited.'''

        # self.ncolors = utils.numberOfMonths(settings.time_stamps[0],settings.time_stamps[-1])/6
        '''
        Number of visible colors in the wikipride plots. 
        '''

        Cohort.__init__(self)


    def initData(self):

        self.data['added'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['removed'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['net'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['edits'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['editors'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()



    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''        

        self.data_description['added'] = {  'title' : 'Megabytes added by editor activity ( no redirects, excl. bots, namespace 0)', \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed by editor activity ( no redirects, excl. bots, namespace 0)', \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed by editor activity ( no redirects, excl. bots, namespace 0)', \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits by editor activity ( no redirects, excl. bots, namespace 0)', \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Active editor histogram ( no redirects, excl. bots, namespace 0)', \
                                             'ylabel': 'Editors' }

    def processSQLrow(self,row):
        # try:
        editor_id = row['user_id']

        if utils.isBot(editor_id):
            return

        year = row['rev_year']
        month = row['rev_month']

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        totaledits = int(row['total_edits'])
        for i,al in enumerate(self.cohorts):
            # for each activity level al

            if totaledits >= al:
                self.data['edits'][i,time_index] += totaledits
                self.data['editors'][i,time_index] += 1
                self.data['added'][i,time_index] += int(row['len_added'])
                self.data['removed'][i,time_index] += -int(row['len_removed'])
                self.data['net'][i,time_index] += int(row['len_added']) + int(row['len_removed'])
   
    def getIndex(self, fe):
        '''
        Returns the index of the cohort, which is identical to the time index of the first edit 
        '''
        raise Exception("NO. EditorTrends is a hacky cohort - the mapping between editor and cohort must not be unique (a +100 editor is also a +5 editor)")

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors+1

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = ['%s-%s'%('1-6' if int(self.cohort_labels[i][:2])<=6 else '7-12',self.cohort_labels[i][-4:]) for i in skip]
            
        return ticks,labels

    def __repr__(self):
        '''String representation of cohort.
        '''        
        return "Editor trend cohort (%s)"%self.cohorts


class ProjectSpaceCohorts(Cohort):
    '''A cohort that is comprised of active editors that started editing in a given year. Only the contributions to the Wikipedia namespaces 4&5 are considered.
    '''
    def __init__(self,activation=5):


        self.activation =  activation

        self.NS = ( '4', '5' )

        ts,ts_i = utils.create_time_stamps_month(fromym='200401',toym='201012')
        self.time_stamps = ts 
        self.time_stamps_index = ts_i
        '''Only take time_stamps starting with self.year
        '''

        self.cohorts = range(2004,2011)
        '''Cohort definition
        '''
        self.cohort_labels = ['%s cohort'% i for i in self.cohorts]
        '''Cohort labels
        '''

        # self.sqlQuery = 'SELECT * FROM fabian WHERE namespace IN (4,5) AND add_edits > %s AND first_edit_year in (%s)'%(self.activation,','.join([str(c) for c in self.cohorts]))


        Cohort.__init__(self)

   
    def initData(self):

        self.data['added'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['removed'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['net'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['edits'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        # self.data['size'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()

    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        self.data_description['added'] = {  'title' : 'Megabytes added to Project namespaces, >%s edits/month'%(self.activation), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        # self.data_description['removed'] = {  'title' : '%s Cohort, >%s edits/month - Megabytes removed (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
        #                                     'ylabel': 'Megabytes',\
        #                                     'ytickslabel' : lambda x : '%d'%(x/1e6) }

        # self.data_description['net'] = {  'title' : '%s Cohort, >%s edits/month - Megabytes Added-Removed (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
        #                                     'ylabel': 'Megabytes',\
        #                                     'ytickslabel' : lambda x : '%d'%(x/1e6) }

        # self.data_description['edits'] = {  'title' : '%s Cohort, >%s edits/month - Number of edits (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
        #                                     'ylabel': 'Edits' }


    def processSQLrow(self,row):

        editor_id = row['user_id']

        if utils.isBot(editor_id):
            return

        year = row['rev_year']
        month = row['rev_month']
        ns = str(row['namespace'])

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        cohorts_index = self.getIndex(row['first_edit_year'])

        if ns in self.NS:
            self.data['added'][cohorts_index,time_index] += int(row['len_added'])
            self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
            self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
            self.data['edits'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])

   
    def getIndex(self, y):
        '''
        Returns the index of the cohort, given the year of the first edit
        '''
        return self.cohorts.index(y)

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors+1

        # too many dates are unreadable
        if nlabels > 15:
            nlabels = 15

        ticks = N.linspace(0, 1., nlabels) #  +1./(nlabels-1)*1/2
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = [self.cohort_labels[i] for i in skip]

        return ticks,labels

class NameSpaces(Cohort):
    '''The namespaces themselves are cohorts
    '''
    def __init__(self):


        self.cohorts = ('0', '1', '2', '3', '4', '5','other')
        '''Cohort definition
        '''
        self.cohort_labels = ['%s namespace'% i for i in self.cohorts]
        '''Cohort labels
        '''
                

        self.cohort_index = {'0':0, '1':1, '2':2, '3':3, '4':4, '5':5}

        self.sqlQuery = 'SELECT * FROM %s;'%tables.EDITOR_YEAR_MONTH_NAMESPACE
        '''The SQL query returns edit information for each editor for each ym she has edited.'''


        Cohort.__init__(self)

   
    def initData(self):

        self.data['added'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['removed'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['net'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['edits'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        # self.data['size'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()

    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        self.data_description['added'] = {  'title' : 'Megabytes added to namespaces (%s)'%('excluding bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed from namespaces (%s)'%('excluding bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['net'] = {  'title' : 'Megabytes added-removed to namespaces (%s)'%('excluding bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }                                                                                                

        self.data_description['edits'] = {  'title' : 'Number of edits to namespaces (%s)'%('excluding bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Edits' }


    def processSQLrow(self,row):

        editor_id = row['user_id']

        if utils.isBot(editor_id):            
            return
        
        year = row['rev_year']
        month = row['rev_month']
        ns = str(row['namespace'])

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        cohorts_index = self.getIndex(ns)

        if row['len_added'] is not None:
            self.data['added'][cohorts_index,time_index] += int(row['len_added'])
        if row['len_removed'] is not None:    
            self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
        if row['len_removed'] is not None and row['len_removed'] is not None:
            self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
        if row['len_removed'] is not None and row['remove_edits'] is not None:
            self.data['edits'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])

   
    def getIndex(self, ns):
        '''
        Returns the index of the cohort, given the year of the first edit
        '''
        return self.cohort_index.get(ns,6)
        

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors


        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        # skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels+1) ]                
        # labels = [self.cohort_labels[i] for i in skip]
        labels = self.cohort_labels

        return ticks,labels


class NewEditors(Cohort):
    '''There is just one cohort, which contains the number of of editors who started contributing in any given month. The sql query aggregates the counts::

        SELECT  
    first_edit_year, 
    first_edit_month, 
    count(*) AS recruits
FROM
    xxx.xxwiki_user_cohort
GROUP BY
    first_edit_year,
    first_edit_month;

    :meth:`.NewEditors.linePlot` creates a line plot.
    '''
    def __init__(self):


        self.cohorts = ['New Editors']
        '''Cohort definition
        '''
        self.cohort_labels = self.cohorts
        '''Cohort labels
        '''
                

        self.sqlQuery = """SELECT  
            first_edit_year, 
            first_edit_month, 
            count(*) AS recruits
        FROM
            %s
        GROUP BY
            first_edit_year,
            first_edit_month;"""%tables.USER_COHORT
        '''The SQL query returns the new editor count for each ym.'''

        Cohort.__init__(self)

   
    def initData(self):

        self.data['editors'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        # self.data['size'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()

    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        self.data_description['editors'] = {  'title' : 'Number of new editors (first edit)', \
                                            'ylabel': '# Editors' }


    def processSQLrow(self,row):

        firstedit = '%d%02d'%(row['first_edit_year'],row['first_edit_month'])

        fe_index = self.time_stamps_index.get(firstedit,None)

        if fe_index is None:
            return

        # there is only one cohort
        cohorts_index = 0

        self.data['editors'][cohorts_index,fe_index] += row['recruits']
        

   
    def getIndex(self, ns):
        '''
        Not needed in this cohort!
        '''
        raise Exception("NO!")
        

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors


        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        # skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels+1) ]                
        # labels = [self.cohort_labels[i] for i in skip]
        labels = self.cohort_labels

        return ticks,labels

    def linePlots(self,dest):
        '''Creates a line plot for the number of new editors and saves it to disk.

        :arg dest: str, destination directory
        '''
        logger.info('Creating line plots for New editors cohort.')

        fig = self.addLine(self.data['editors'][0,:])
        
        self.saveFigure(name='line', fig=fig, dest=dest, title=self.data_description['editors']['title'],ylabel=self.data_description['editors']['ylabel'])


