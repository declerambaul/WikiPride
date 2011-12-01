'''This module implements age cohorts, AbsoluteAge and RelativeAge.
'''

import sys,logging
logger = logging.getLogger('Age cohorts')

try:
    import numpy as N
except:
    logger.error('Numpy not installed')
    


import settings
import utils


from cohorts.base import Cohort
from data import tables


class Age(Cohort):
    '''A abstract class for for an age cohort.
    '''
    def __init__(self):

        if self.cohorts is None or self.cohort_labels is None:
            logger.error("self.cohorts or self.cohort_labels not properly defined")
            # raise Exception("self.cohorts or self.cohort_labels not properly defined")
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
        self.data_description['added'] = {  'title' : 'Megabytes added ( %s, namespaces:%s)'%('no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed ( %s, namespaces:%s)'%('no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed ( %s, namespaces:%s)'%('no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits ( %s, namespaces:%s)'%('no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Number of editors active ( %s, namespaces:%s)'%('no bots' if self.nobots else 'including bots', ','.join(self.NS) if len(self.NS)<16 else 'all'), \
                                                                                  'ylabel': 'Editors' }



class AbsoluteAgePerMonth(Age):
    '''A cohort is the group of people that have started editing in the same month.
    '''
    def __init__(self):

        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]
        '''Cohort definition
        '''                
        self.cohort_labels = ['%s / %s'%(settings.time_stamps[i][4:],settings.time_stamps[i][:4]) for i in self.cohorts]
        '''Cohort labels
        '''         
        
        self.old_user_id = None
        '''The user_id of the previously encountered editor as we iterate through the table
        '''
                       
        Age.__init__(self)



    def processSQLrow(self,row):
        try:

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

                if row['len_added'] is not None:
                    self.data['added'][cohorts_index,time_index] += int(row['len_added'])
                if row['len_removed'] is not None:    
                    self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
                if row['len_removed'] is not None and row['len_removed'] is not None:
                    self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
                if row['len_removed'] is not None and row['remove_edits'] is not None:
                    self.data['edits'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])


                if editor_id != self.old_user_id:
                    #counting the editor we encountered
                    self.data['editors'][cohorts_index,time_index] += 1

                    self.old_user_id = editor_id



        except:
            raise Exception('row:\n%s'%row)
   
    def getIndex(self, fe):
        '''
        Returns the index of the cohort, which is identical to the time index of the first edit 
        '''
        return fe

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



class RelativeAgePerMonth(Age):
    '''A cohort is the group of people that have the same age at the time of an edit. During the first month of editing, a contributor will be in the 1-month old cohort, then he switches to the 2-month cohort and so forth.
    '''
    def __init__(self):


        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]        
        '''Cohort definition
        '''
        self.cohort_labels = ['%s month old'% i for i in self.cohorts]
        '''Cohort labels
        '''                   
        self.old_user_id = None
        '''The user_id of the previously encountered editor as we iterate through the table
        '''

             
        Age.__init__(self)

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

        cohorts_index = self.getIndex(time_index, fe_index)

        if ns in self.NS:

            if row['len_added'] is not None:
                self.data['added'][cohorts_index,time_index] += int(row['len_added'])
            if row['len_removed'] is not None:    
                self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
            if row['len_removed'] is not None and row['len_removed'] is not None:
                self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
            if row['len_removed'] is not None and row['remove_edits'] is not None:
                self.data['edits'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])


            if editor_id != self.old_user_id:
                #counting the editor we encountered
                self.data['editors'][cohorts_index,time_index] += 1

                self.old_user_id = editor_id

   


    def getIndex(self,ti,fe):
        '''
        Returns the index of the cohort (i.e. the relative age of the editor) from the time index of the edit and time index of the first edit
        '''
        return ti-fe


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


class RelativeAgePerDay(Age):
    '''A cohort is the group of people that have the same age at the time of an edit.
    '''
    def __init__(self):

        ts_month,ts_month_index = utils.create_time_stamps_month()

        self.cohorts = [int(i) for i in range(0,len(ts_month))]        
        '''Cohort definition
        '''
        self.cohort_labels = ['%s days old'% i for i in self.cohorts]
        '''Cohort labels
        '''                        
        Age.__init__(self)

    def processSQLrow(self,row):

        editor_id = row['user_id']

        if utils.isBot(editor_id):
            return

        year = row['rev_year']
        month = row['rev_month']
        day = row['rev_day']
        ns = str(row['namespace'])

        ymd = '%d%02d%02d'%(year,month,day)

        time_index = self.time_stamps_index.get(ymd,None)
        if time_index is None:
            return

        fe = str(row['first_edit_year'])
        firstedit = fe[:8]
        # time.strptime(fe,"%Y%m%d%H%M%S")
        # firstedit = '%d%02d%02d'%(fe[0:4],fe[4:6],fe[6:8])
        

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(time_index, fe_index)

        if ns in self.NS:

            self.data['addedPerDay'][cohorts_index,time_index] += int(row['len_added'])
            self.data['removedPerDay'][cohorts_index,time_index] += -int(row['len_removed'])
            self.data['netPerDay'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
            self.data['editsPerDay'][cohorts_index,time_index] += int(row['add_edits'])+int(row['remove_edits'])

   


    def getIndex(self,ti,fe):
        '''
        Returns the index of the cohort (i.e. the relative age of the editor) from the time index of the edit and time index of the first edit
        '''
        i = (ti-fe)%30

        if i > len(self.cohorts)-1:
            return len(self.cohorts)-1
        
        return i



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



                                 
class AbsoluteAgeAllNamespaces(Cohort):
    '''A cohort is the group of people that have started editing in the same month. 
    '''
    def __init__(self,minedits=1,maxedits=None):

        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]
        '''Cohort definition
        '''                
        self.cohort_labels = ['%s / %s'%(settings.time_stamps[i][4:],settings.time_stamps[i][:4]) for i in self.cohorts]
        '''Cohort labels
        '''     
        
        self.sqlQuery = 'SELECT * FROM %s;'%tables.EDITOR_YEAR_MONTH
        '''The SQL query returns edit information for each editor for each ym she has edited.'''

        self.minedits = minedits
        '''Minimum number of edits by editor in a given month to be included'''

        self.maxedits = maxedits
        '''Maximum number of edits by editor in a given month to be included'''

        self.ncolors = utils.numberOfMonths(settings.time_stamps[0],settings.time_stamps[-1])/6
        '''
        Number of visible colors in the wikipride plots. E.g. one color for every six month for wikipride plots
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
        editspan = "%s<edits%s"%(self.minedits,'<%s'%self.maxedits if self.maxedits is not None else '')

        self.data_description['added'] = {  'title' : 'Megabytes added by editor activity ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed by editor activity ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed by editor activity ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits by editor activity ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Active editor histogram ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                             'ylabel': 'Number of Editors' }

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

        firstedit = '%d%02d'%(row['first_edit_year'],row['first_edit_month'])

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(fe_index)

        edits = 0
        if row['add_edits'] is not None:
            edits += int(row['add_edits'])
        if row['remove_edits'] is not None:
            edits += int(row['remove_edits'])
        if row['noop_edits'] is not None:
            edits += int(row['noop_edits'])

        if edits < self.minedits or (edits > self.maxedits and self.maxedits is not None):                        
            return

        self.data['editors'][cohorts_index,time_index] += 1

        if row['len_added'] is not None:
            self.data['added'][cohorts_index,time_index] += int(row['len_added'])
        if row['len_removed'] is not None:    
            self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
        if row['len_added'] is not None and row['len_removed'] is not None:
            self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
        
        self.data['edits'][cohorts_index,time_index] += edits

        # except:
        #     raise Exception('row:\n%s'%row)
   
    def getIndex(self, fe):
        '''
        Returns the index of the cohort, which is identical to the time index of the first edit 
        '''
        return fe

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors+1

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = ['%s / %s'%('1-6' if int(self.cohort_labels[i][:2])<=6 else '7-12',self.cohort_labels[i][-4:]) for i in skip]
            
        return ticks,labels

    def __repr__(self):
        '''String representation of cohort.
        '''
        editspan = "%s<edits%s"%(self.minedits,'<%s'%self.maxedits if self.maxedits is not None else '')
        return "Absolute Age Cohort (%s)"%editspan


class RelativeAgeAllNamespaces(Cohort):
    '''A cohort is the group of people that have the same age at the time of an edit. During the first month of editing, a contributor will be in the 1-month old cohort, then he switches to the 2-month cohort and so forth.
    '''
    def __init__(self,minedits=1,maxedits=None):

        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]        
        '''Cohort definition
        '''
        self.cohort_labels = ['%s month old'% i for i in self.cohorts]
        '''Cohort labels
        '''                   
        
        self.sqlQuery = 'SELECT * FROM %s;'%tables.EDITOR_YEAR_MONTH
        '''The SQL query returns edit information for each editor for each ym she has edited.'''

        self.minedits = minedits
        '''Minimum number of edits by editor in a given month to be included'''

        self.maxedits = maxedits
        '''Maximum number of edits by editor in a given month to be included'''

        self.ncolors = utils.numberOfMonths(settings.time_stamps[0],settings.time_stamps[-1])/6
        '''
        Number of visible colors in the wikipride plots. E.g. one color for every six month for wikipride plots
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
        editspan = "%s<edits%s"%(self.minedits,'<%s'%self.maxedits if self.maxedits is not None else '')

        self.data_description['added'] = {  'title' : 'Megabytes added ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Number of active editors ( %s, %s, all namespaces)'%(editspan, 'no bots' if self.nobots else 'including bots'), \
                                             'ylabel': 'Number of Editors' }

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

        firstedit = '%d%02d'%(row['first_edit_year'],row['first_edit_month'])

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(time_index, fe_index)


        edits = 0
        if row['add_edits'] is not None:
            edits += int(row['add_edits'])
        if row['remove_edits'] is not None:
            edits += int(row['remove_edits'])
        if row['noop_edits'] is not None:
            edits += int(row['noop_edits'])

        if edits < self.minedits or (edits > self.maxedits and self.maxedits is not None):                        
            return

        self.data['editors'][cohorts_index,time_index] += 1

        if row['len_added'] is not None:
            self.data['added'][cohorts_index,time_index] += int(row['len_added'])
        if row['len_removed'] is not None:    
            self.data['removed'][cohorts_index,time_index] += -int(row['len_removed'])
        if row['len_added'] is not None and row['len_removed'] is not None:
            self.data['net'][cohorts_index,time_index] += int(row['len_added']) + int(row['len_removed'])
        
        self.data['edits'][cohorts_index,time_index] += edits

        # except:
        #     raise Exception('row:\n%s'%row)
   
    def getIndex(self,ti,fe):
        '''
        Returns the index of the cohort (i.e. the relative age of the editor) from the time index of the edit and time index of the first edit
        '''
        return ti-fe

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors+1

        ticks = N.linspace(0, 1., nlabels) +1./(nlabels-1)*1/2
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = ['%s-%s months old'%(self.cohorts[skip[i+1]],self.cohorts[skip[i]+1]) for i in range(0,len(skip)-2)]
        labels.append('%s-%s months old'%(self.cohorts[-1],self.cohorts[skip[-2]+1]))
        return ticks,labels

    def __repr__(self):
        '''String representation of cohort.
        '''
        editspan = "%s<edits%s"%(self.minedits,'<%s'%self.maxedits if self.maxedits is not None else '')
        return "Relative Age Cohort (%s)"%editspan

    def linePlots(self,dest):
        '''Graphs for relative age cohorts include

        * Bytes added per edit (new vs. old editors)
        * Contribution percentage of bytes added for each one year cohort
        * Editor percentage for each one year cohort        

        
        '''
        logger.info('Creating line plots for %s'%self)

        editspan = "%s<edits%s"%(self.minedits,'<%s'%self.maxedits if self.maxedits is not None else '')

        # Bytes added per edit (new vs. old editors)

        added = self.data['added']
        edits = self.data['edits']
        editors = self.data['editors']

        six = added[0:6,:].sum(axis=0)/(edits[0:6,:].sum(axis=0)+1)
        moresix = added[7:,:].sum(axis=0)/(edits[7:,:].sum(axis=0)+1)

        six = utils.movingAverage(array=six, WINDOW=3)
        moresix = utils.movingAverage(array=moresix, WINDOW=3)

        fig = self.addLine(data=six,label='new editors (0-6 months active)')
        fig = self.addLine(data=moresix,fig=fig,label='older editors (>6 months active)')        

        # l = 12  
        # fig = None      
        # for i in range(0,(added.shape[1]/l)*l,l):
        #     e = edits[(i):(i+l-1),:].sum(axis=0)
        #     e[e==0] = 1
        #     data = added[(i):(i+l-1),:].sum(axis=0)/e
        #     fig = self.addLine(data=data,fig=fig,label='%s-%s months active'%(i,(i+l-1)))

       
        self.saveFigure(name='bytes_per_edit_new_vs_old', fig=fig, dest=dest, title='Bytes added per edit (new vs. old editors, %s)'%editspan,ylabel='Bytes', legendpos=1)


        # Contribution percentage of bytes added for each one year cohort
        total = added.sum(axis=0)
        total[total==0] = 1

        l = 12  
        fig = None      
        for i in range(0,(added.shape[1]/l)*l,l):
            data = added[(i):(i+l-1),:].sum(axis=0)/total
            fig = self.addLine(data=data,fig=fig,label='%s-%s months active'%(i,(i+l-1)))


        self.saveFigure(name='percentage_added_line', fig=fig, dest=dest, title='Contribution percentage of bytes added for editors with %s'%editspan,ylabel='Percentage', legendpos=1)

        # Editor percentage for each one year cohort
        total = editors.sum(axis=0)
        total[total==0] = 1

        l = 12  
        fig = None      
        for i in range(0,(added.shape[1]/l)*l,l):
            data = editors[(i):(i+l-1),:].sum(axis=0)/total
            fig = self.addLine(data=data,fig=fig,label='%s-%s months active'%(i,(i+l-1)))


        self.saveFigure(name='percentage_editor_line', fig=fig, dest=dest, title='Editor age percentage for editors with %s'%editspan,ylabel='Percentage', legendpos=1)







