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
        
        self.sqlQuery = 'SELECT * FROM %s;'%tables.EDITOR_YEAR_MONTH_NS0_NOREDIRECT
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

        totaledits = 0
        if row['add_edits'] is not None:
            totaledits += int(row['add_edits'])
        if row['remove_edits'] is not None:
            totaledits += int(row['remove_edits'])
        if row['noop_edits'] is not None:
            totaledits += int(row['noop_edits'])
        
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

