'''The module defines Reverter cohorts.

.. todo
    Describe AbsoluteAgeReverts
    Describe AbsoluteAgeReverts

'''

import sys,logging


try:
    import numpy as N
except:
    logging.error('Numpy not installed')
    

import settings
import utils

from cohorts.base import Cohort

class Revert(Cohort):
    '''
    A revert action is one of the three:

    * A reverting action (the act of rolling back)
    * Reverted action (rolled back revision). Note that one reverting edit include multiple reverted edits
    * RevertedTo revision is the revision rolled back to.

    Cohort analyis can be done on all three types of revisions, the absract :class:`.Revert` class defines the different types.
    '''

    def __init__(self,reverttype,activation=1):
        '''
        arg reverttype: str, type of revert: 'reverting','reverted','revertedto'
        '''
        self.reverttype = reverttype

        self.activation = activation
        '''Minimum number of reverts by editor to be included'''

        Cohort.__init__(self)



    def initData(self):

        self.data['%s_edits'%self.reverttype] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['%s_editors'%self.reverttype] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()



    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        self.data_description['%s_edits'%self.reverttype] = {  'title' : 'Number of %s actions by editor age ( >%s reverts, %s, namespaces:All)'%(self.reverttype,(self.activation-1), 'no bots' if self.nobots else 'including bots'), \
                                            'ylabel': 'Reverts' }

        self.data_description['%s_editors'%self.reverttype] = { 'title' : 'Editor histogram for %s actions ( >%s reverts, %s, namespaces:All)'%(self.reverttype, self.activation-1, 'no bots' if self.nobots else 'including bots'), \
                                             'ylabel': 'Number of Editors' }

class AbsoluteAgeReverts(Revert):
    '''A cohort is the group of people that have started editing in the same month. Only reverting revisions are considered when aggregating the data.
    '''
    def __init__(self,reverttype,activation=1):

        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]
        '''Cohort definition
        '''                
        self.cohort_labels = ['%s / %s'%(settings.time_stamps[i][4:],settings.time_stamps[i][:4]) for i in self.cohorts]
        '''Cohort labels
        '''     
        
        self.sqlQuery = 'SELECT * FROM u_declerambaul.ptwiki_%s_editor_year_month;'%reverttype

        Revert.__init__(self,reverttype,activation)

    def processSQLrow(self,row):
        # try:
        editor_id = row['%s_user_id'%self.reverttype]

        if utils.checkBot(editor_id,ints=True):
            return

        year = row['%s_year'%self.reverttype]
        month = row['%s_month'%self.reverttype]

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        firstedit = '%d%02d'%(row['%s_first_edit_year'%self.reverttype],row['%s_first_edit_month'%self.reverttype])

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(fe_index)

        reverts = row['reverts']

        if reverts < self.activation:
            return

        self.data['%s_editors'%self.reverttype][cohorts_index,time_index] += 1
        
        self.data['%s_edits'%self.reverttype][cohorts_index,time_index] += reverts

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

        # too many dates are unreadable
        if nlabels > 15:
            nlabels = 15

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = ['%s / %s'%('1-6' if int(self.cohort_labels[i][:2])<=6 else '7-12',self.cohort_labels[i][-4:]) for i in skip]
            
        return ticks,labels


class RelativeAgeReverts(Revert):
    '''A cohort is the group of people that have the same age (e.g. are 3 month old). Only reverting revisions are considered when aggregating the data.

    .. todo
        'reverted_xxx' and 'reverting_xxx' is deterministic in processSQLrow, so only the query works only for one table
    '''
    def __init__(self,reverttype,activation=1):

        self.cohorts = [int(i) for i in range(0,len(settings.time_stamps))]        
        '''Cohort definition
        '''
        self.cohort_labels = ['%s month old'% i for i in self.cohorts]
        '''Cohort labels
        '''                        
        
        self.sqlQuery = 'SELECT * FROM u_declerambaul.ptwiki_%s_editor_year_month;'%reverttype


        Revert.__init__(self,reverttype,activation)


    def processSQLrow(self,row):
        # try:
        editor_id = row['%s_user_id'%self.reverttype]

        if utils.checkBot(editor_id,ints=True):
            return

        year = row['%s_year'%self.reverttype]
        month = row['%s_month'%self.reverttype]

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        firstedit = '%d%02d'%(row['%s_first_edit_year'%self.reverttype],row['%s_first_edit_month'%self.reverttype])

        fe_index = self.time_stamps_index.get(firstedit,None)
        if fe_index is None:
            return

        cohorts_index = self.getIndex(time_index, fe_index)

        reverts = row['reverts']

        if reverts < self.activation:
            return

        self.data['%s_editors'%self.reverttype][cohorts_index,time_index] += 1
        
        self.data['%s_edits'%self.reverttype][cohorts_index,time_index] += reverts

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

        # too many dates are unreadable
        if nlabels > 15:
            nlabels = 15

        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels) ]                
        labels = ['%s / %s'%('1-6' if int(self.cohort_labels[i][:2])<=6 else '7-12',self.cohort_labels[i][-4:]) for i in skip]
            
        return ticks,labels



class RevertsByEditorType(Cohort):
    '''
    A Cohort is defined as a group of editors having the same function (administrators, bureaucrats, hugglers, ...). 
    '''
    def __init__(self,activation=1):


        # editor_types = ['Administrator','Bureaucrat','Eliminator','Huggler','Bot','Multiple','Other']
        editor_types = ['Administrator','Huggler','Bot','Admin & Huggle','Other']

        self.editor_types_dict = {a : i for i,a in enumerate(editor_types)}
        '''Dictionary mapping editory type to numpy.array matrix
        '''
        self.cohorts = [int(i) for i in range(0,len(editor_types))]
        '''Cohort definition
        '''                
        self.cohort_labels = editor_types
        '''Cohort labels
        '''     

        #initialize helper structures
        try:
            from db import sql

            cur = sql.getSSCursor()

            # administrators
            cur.execute("select user_id from ptwiki_p.user u join ptwiki_p.user_groups ug on (u.user_id=ug.ug_user) where ug.ug_group='sysop';")
            self.administrators = set(i[0] for i in cur)
            # bureaucrat
            cur.execute("select user_id from ptwiki_p.user u join ptwiki_p.user_groups ug on (u.user_id=ug.ug_user) where ug.ug_group='bureaucrat';")
            self.bureaucrats = set(i[0] for i in cur)
            # eliminators
            cur.execute("select user_id from ptwiki_p.user u join ptwiki_p.user_groups ug on (u.user_id=ug.ug_user) where ug.ug_group='eliminator';")
            self.eliminators = set(i[0] for i in cur)
            # hugglers
            cur.execute("select user_id from u_declerambaul.ptwiki_huggle;")
            self.hugglers = set(i[0] for i in cur)
            # bots
            cur.execute("select user_id from u_declerambaul.ptwiki_bots;")
            self.bots = set(i[0] for i in cur)
            

            self.sqlQuery = 'SELECT * FROM u_declerambaul.ptwiki_%s_editor_year_month;'%reverttype

        except:
            logging.error("Could not establish SQL connection to initialize RevertsByEditorType.")

        Cohort.__init__(self)

    def initData(self):

        self.data['reverts'] = N.zeros((len(self.cohorts), len(self.time_stamps)))
        self.data['reverters'] = N.zeros((len(self.cohorts), len(self.time_stamps)))

        self.initDataDescription()



    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        self.data_description['reverts'] = {  'title' : 'Number of reverts by editor type (namespaces:All)', \
                                            'ylabel': 'Reverts' }

        self.data_description['reverters'] = {  'title' : 'Reverter histogram by editor type (namespaces:All)', \
                                             'ylabel': 'Number of Reverters' }

    def processSQLrow(self,row):
        # try:
        editor_id = row['reverting_user_id']

        
        year = row['reverting_year']
        month = row['reverting_month']

        ym = '%d%02d'%(year,month)

        time_index = self.time_stamps_index.get(ym,None)
        if time_index is None:
            return

        cohorts_index = self.getIndex(editor_id)

        reverts = row['reverts']

        self.data['reverters'][cohorts_index,time_index] += 1
        
        self.data['reverts'][cohorts_index,time_index] += reverts

        # except:
        #     raise Exception('row:\n%s'%row)
   
    def getIndex(self, editor_id):
        '''
        Returns the index of the cohort, which is identical to the time index of the first edit 
        '''
        
        c_id = None
        if editor_id in self.administrators:
            c_id = self.editor_types_dict['Administrator']
        # if editor_id in self.bureaucrats:
        #     if c_id is not None:
        #         return self.editor_types_dict['Multiple']
        #     c_id = self.editor_types_dict['Bureaucrat']
        # if editor_id in self.eliminators:
        #     if c_id is not None:
        #         return self.editor_types_dict['Multiple']            
        #     c_id = self.editor_types_dict['Eliminator']
        if editor_id in self.hugglers:
            if c_id is not None:
                return self.editor_types_dict['Admin & Huggle']            
            c_id = self.editor_types_dict['Huggler']
        if editor_id in self.bots:
            # if c_id is not None:
            #     return self.editor_types_dict['Multiple']            
            c_id = self.editor_types_dict['Bot']
        
        if c_id is None:
            return self.editor_types_dict['Other']

        return c_id

        

    def colorbarTicksAndLabels(self,ncolors):
        '''Returns ticks and labels for the colorbar of a WikiPride visualization
        '''

        nlabels = ncolors


        ticks = N.linspace(0, (1.-1./nlabels), nlabels) +0.5/nlabels
        # skip = [ int(i) for i in N.linspace(0,len(self.cohorts)-1,nlabels+1) ]                
        # labels = [self.cohort_labels[i] for i in skip]
        labels = self.cohort_labels

        return ticks,labels
