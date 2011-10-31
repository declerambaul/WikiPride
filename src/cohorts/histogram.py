'''This module implements histograms cohorts, e.g. EditsHistogram.
'''

import sys,logging



try:
    import numpy as N
except:
    logging.error('Numpy not installed')
    


import settings
import utils

from cohorts.base import Cohort

class EditsHistogram(Cohort):
    '''The cohorts are based on the number of edits they have done in a given month.
    '''
    def __init__(self):

        # We don't take into consideration people who have 0 edits as the data is coded sparse and we don't have
        # this information
        # Note that len(self.cohorts) has to be equal the number of bins in the numpy.array
        # self.cohorts = [1,3,5,7,10,20,40,60,80,100,200,500,1000,5000,10000,'>10000 edits']
        self.cohorts = [1,5,10,50,100,500,1000,'>1000 edits']
        '''Cohort definition
        '''
        self.cohort_labels = self.cohorts[:]
        self.cohort_labels[0] = '%s edit'%(self.cohort_labels[0])
        for i in range(1,len(self.cohorts)-1):
            self.cohort_labels[i] = '%s-%s edits'%(self.cohorts[i-1]+1,self.cohorts[i])
        # self.cohort_labels = ['<%s edits'%(e) for e in self.cohorts]
        '''Cohort labels
        '''                        
        Cohort.__init__(self)
    
    def getIndex(self, edits):
        '''
        Returns the index of the cohort 
        '''
        for i,e in enumerate(self.cohorts):
            if edits <= e:
                return i

        return len(self.cohorts)-1


    def processMongoDocument(self,editor):

        if 'edit_count' not in editor:        
            return

        editor_id = editor['user_id']


        if utils.isBot(editor_id):
            return

        for year,edity in editor['edit_count'].items():        
            for month,editm in edity.items():  
                # extract year and month 20xxxx  
                ym = '%s%02d'%(year,int(month))
                
                time_index = self.time_stamps_index.get(ym,None)
                if time_index is None:
                    continue

                # cohort index depends on the aggregate of the namespaces
                nedits = 0                        
                
                for ns,ecount in editm.items():                           
                                                                                    
                    if ns in self.NS:
                        # count edits
                        nedits +=  ecount
                
                if nedits > 0:
                    # Sparse representation. Only collecting >0 edits because it is possible that an editor has no edits in that namespace, but edits in other namespaces.
                    cohorts_index = self.getIndex(nedits)

                    # increment the histogram bin for that editor and month
                    # note: as the data is sparse, it means we don't count the number of people with zero edits in that month
                    self.data['editsHistogram'][cohorts_index,time_index] += 1

   
    def initData(self):

        self.data['editsHistogram'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()

    def initDataDescription(self):

        self.data_description['editsHistogram'] = {     'title' : 'Histogram of the number of edits', 
                                                        'ylabel' : 'Number of Editors'}


    def getColor(self, i):
        '''
        Returns a color based on the index of the cohort i
        '''
        return self.colors[i]

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]        
        labels = [self.cohort_labels[i] for i in skip]
            
        return ticks,labels


class EditorActivity(Cohort):
    '''The cohorts are based on the number of edits they have done in a given month. It uses a table where the values are aggregated for all namespaces.
    '''
    def __init__(self):

        # We don't take into consideration people who have 0 edits as the data is coded sparse and we don't have
        # this information
        # Note that len(self.cohorts) has to be equal the number of bins in the numpy.array
        self.cohorts = [1,5,50,100,500,1000,'>1000 edits']
        '''Cohort definition
        '''
        self.cohort_labels = self.cohorts[:]
        self.cohort_labels[0] = '%s edit'%(self.cohort_labels[0])
        for i in range(1,len(self.cohorts)-1):
            self.cohort_labels[i] = '%s-%s edits'%(self.cohorts[i-1]+1,self.cohorts[i])
        # self.cohort_labels = ['<%s edits'%(e) for e in self.cohorts]
        '''Cohort labels
        '''                        

        self.sqlQuery = 'SELECT * FROM u_declerambaul.ptwiki_editor_centric_year_month;'
        # query on the toolserver

        Cohort.__init__(self)
    
    def getIndex(self, edits):
        '''
        Returns the index of the cohort 
        '''
        for i,e in enumerate(self.cohorts):
            if edits <= e:
                return i

        return len(self.cohorts)-1

   
    def initData(self):

        self.data['added'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['removed'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['net'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['edits'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['editors'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()


    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with information used for plotting. 
        '''
        self.data_description['added'] = {  'title' : 'Megabytes added by editor activity ( %s, namespaces:All)'%('no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed by editor activity ( %s, namespaces:All)'%('no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed by editor activity ( %s, namespaces:All)'%('no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits by editor activity ( %s, namespaces:All)'%('no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Active editor histogram (%s, namespaces:All)'%('no bots' if self.nobots else 'including bots'), \
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


        edits = 0
        if row['add_edits'] is not None:
            edits += int(row['add_edits'])
        if row['remove_edits'] is not None:
            edits += int(row['remove_edits'])
        if row['noop_edits'] is not None:
            edits += int(row['noop_edits'])

        cohorts_index = self.getIndex(edits)

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

    def getColor(self, i):
        '''
        Returns a color based on the index of the cohort i
        '''
        return self.colors[i]

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]        
        labels = [self.cohort_labels[i] for i in skip]
            
        return ticks,labels


class NewEditorActivity(Cohort):
    '''The cohorts are based on the number of edits they have done in a given month.
    '''
    def __init__(self,period=3  ):

        # We don't take into consideration people who have 0 edits as the data is coded sparse and we don't have
        # this information
        # Note that len(self.cohorts) has to be equal the number of bins in the numpy.array
        # self.cohorts = [1,3,5,7,10,20,40,60,80,100,200,500,1000,5000,10000,'>10000 edits']
        self.cohorts = [1,5,10,50,100,500,1000,'>1000 edits']
        '''Cohort definition
        '''
        self.cohort_labels = self.cohorts[:]
        self.cohort_labels[0] = '%s edit'%(self.cohort_labels[0])
        for i in range(1,len(self.cohorts)-1):
            self.cohort_labels[i] = '%s-%s edits'%(self.cohorts[i-1]+1,self.cohorts[i])
        # self.cohort_labels = ['<%s edits'%(e) for e in self.cohorts]
        '''Cohort labels
        '''             
        self.period = period
        '''The number of month an editor is considered new
        '''
        self.old_user_id = None
        '''The user_id of the previously encountered editor as we iterate through the table
        '''
        self.lastym = None
        '''The ym at the end of the `period` months after the first edit of an editor 
        '''
        self.firstedit = None
        self.fe_index = None

        self.edits = 0
        self.added = 0
        self.removed = 0
        self.net = 0

        

        Cohort.__init__(self)
    
    def getIndex(self, edits):
        '''
        Returns the index of the cohort 
        '''
        for i,e in enumerate(self.cohorts):
            if edits <= e:
                return i

        return len(self.cohorts)-1

    def processSQLrow(self,row):
        # try:
        editor_id = row['user_id']

        if utils.isBot(editor_id):
            return


        if editor_id != self.old_user_id:
            '''When encountering a new editor, we extract the firstedit and the last ym of interest
            '''
            if self.old_user_id is not None:
                # we just finished aggregating information for an editor
                
                #getting bin of the number of edits the editor has done
                cohorts_index = self.getIndex(self.edits)

                self.data['editors'][cohorts_index,self.fe_index] += 1
                self.data['added'][cohorts_index,self.fe_index] = self.added
                self.data['removed'][cohorts_index,self.fe_index] = self.removed
                self.data['net'][cohorts_index,self.fe_index] = self.net
                self.data['edits'][cohorts_index,self.fe_index] = self.edits


            # initializing info for current editor
            self.old_user_id = editor_id

            year = row['first_edit_year']
            month = row['first_edit_month']

            self.firstedit = '%d%02d'%(year,month)
            self.fe_index = self.time_stamps_index.get(self.firstedit,None)

            if self.fe_index is None:
                return
            

            (m,y) = ((month+self.period)%12,year+(month+self.period)/12)
            self.lastym = '%d%02d'%(y,m)

            self.edits = 0
            self.added = 0
            self.removed = 0
            self.net = 0


        if self.fe_index is None:
            return

        year = row['rev_year']
        month = row['rev_month']

        ym = '%d%02d'%(year,month)

        if ym > self.lastym:
            return


        
        if row['add_edits'] is not None:
            self.edits += int(row['add_edits'])
        if row['remove_edits'] is not None:
            self.edits += int(row['remove_edits'])
        if row['noop_edits'] is not None:
            self.edits += int(row['noop_edits'])

        

        if row['len_added'] is not None:
            self.added += int(row['len_added'])
        if row['len_removed'] is not None:    
            self.removed += -int(row['len_removed'])
        if row['len_added'] is not None and row['len_removed'] is not None:
            self.net += int(row['len_added']) + int(row['len_removed'])
        

    def initData(self):

        self.data['added'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['removed'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['net'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['edits'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['editors'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()


    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with information used for plotting. 
        '''
        self.data_description['added'] = {  'title' : 'Megabytes added by new editor activity ( <%s months, %s, namespaces:All)'%(self.period, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }
        self.data_description['removed'] = {  'title' : 'Megabytes removed by new editor activity ( <%s months, %s, namespaces:All)'%(self.period, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['net'] = {  'title' : 'Megabytes Added-Removed by new editor activity ( <%s months, %s, namespaces:All)'%(self.period, 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Megabytes',\
                                            'ytickslabel' : lambda x : '%d'%(x/1e6) }

        self.data_description['edits'] = {  'title' : 'Number of edits by new editor activity ( <%s months, %s, namespaces:All)'%(self.period,'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Edits' }

        self.data_description['editors'] = {  'title' : 'Edits Histogram for the first %s month of an edit activity (%s, namespaces:All)'%(self.period, 'no bots' if self.nobots else 'including bots'), \
                                             'ylabel': 'Number of Editors' }
   



    def getColor(self, i):
        '''
        Returns a color based on the index of the cohort i
        '''
        return self.colors[i]

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]        
        labels = [self.cohort_labels[i] for i in skip]
            
        return ticks,labels




