'''For simple cohorts :) 


'''

import sys,logging


try:
    import numpy as N
except:
    logging.error('Numpy not installed')
    

import settings
import utils

from cohorts.base import Cohort
from data import tables


class OneYearCohort(Cohort):
    '''A cohort that is comprised of active editors that started editing in a given year.
    '''
    def __init__(self,year,activation=5,overall=False):

        self.year = year
        '''The year the cohort started.
        '''
        self.activation = activation
        '''Minimum number of edits per month to be included in the cohort
        '''
        self.overall = overall

        ts,ts_i = utils.create_time_stamps_month(fromym='%s01'%self.year,toym='201012')
        self.time_stamps = ts 
        self.time_stamps_index = ts_i
        '''Only take time_stamps starting with self.year
        '''

        self.cohorts = [self.year,'others']
        '''Cohort definition
        '''
        self.cohort_labels = ['%s cohort'% i for i in self.cohorts]
        '''Cohort labels
        '''

        if self.overall:
            self.sqlQuery = "SELECT *  FROM fabian WHERE user_id IN (SELECT user_id FROM fabian WHERE first_edit_year=%s GROUP BY user_id HAVING SUM(add_edits)>%s);"%(self.year,self.activation)
        else:
            self.sqlQuery = 'SELECT *  FROM fabian WHERE add_edits > %s AND first_edit_year=%s'%(self.activation,self.year)

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
        self.data_description['added'] = {  'title' : '%s Cohort, >%s edits/month - Megabytes added (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : '%s Cohort, >%s edits/month - Megabytes removed (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : '%s Cohort, >%s edits/month - Megabytes Added-Removed (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : '%s Cohort, >%s edits/month - Number of edits (%s, namespaces:%s)'%(self.year,self.activation,'no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
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

        firstedit = '%d%02d'%(row['first_edit_year'],row['first_edit_month'])

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(fe_index)

        if ns in self.NS:
            self.data['added'][cohorts_index,time_index] += int(row['len_added'])
            self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
            self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
            self.data['edits'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])

   
    def getIndex(self, fe):
        '''
        Returns the index of the cohort, which is identical to the time index of the first edit 
        '''
        return 0

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
        self.sqlQuery = 'SELECT * FROM declerambaul.project_namespaces_nosandbox WHERE add_edits > %s AND first_edit_year in (%s)'%(self.activation,','.join([str(c) for c in self.cohorts]))


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


