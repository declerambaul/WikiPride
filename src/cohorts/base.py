"""This module defines the abstract class :class:`.Cohort`
"""

import logging




try:
    import numpy as N
except:
    logging.error('Numpy not installed')
    raise Exception('Numpy is a requirement')



import settings



# (time_stamps,time_stamps_index) = create_time_stamps(fromym='200101',toym='201101')

class Cohort:
    '''
    Abstract class that defines common properties of cohorts, which are defined in the :mod:`cohorts` modules
    '''
    def __init__(self):

        # cohorts and cohort_labels should be defined by now as this is an abstract class
        if self.cohorts is None or self.cohort_labels is None:
            logging.error("self.cohorts or self.cohort_labels not properly defined")
            # raise Exception("self.cohorts or self.cohort_labels not properly defined")
        

        self.data = {}
        '''Dictionary that contains the data. {name : numpy.array }. Different aggregates 
        can be saved; for example 'bytesadded','edits','bytesremovedPerEditor'
        '''
        self.data_description = {}
        '''Dictionary that holds descriptive information about self.data. For example, an
        'addedBytes' data description might be:

        self.data_description['addedBytes'] = { title}
        '''
        if 'NS' not in self.__dict__:
            self.NS = settings.NS
        '''
        Set of namesspaces that we are interested in
        '''
        self.nobots = settings.nobots
        '''
        True if the bots are filtered from the cohort
        '''
        if 'time_stamps' not in self.__dict__:
            self.time_stamps = settings.time_stamps
        '''
        List of timestamps
        '''
        if 'time_stamps_index' not in self.__dict__:
            self.time_stamps_index = settings.time_stamps_index
        '''
        Hash from time_stamp to index in self.time_stamps
        '''
        
        # self.ncolors = settings.ncolors if ('ncolors' in settings.__dict__ and settings.ncolors is not None)  else len(self.cohorts)
        # '''
        # Number of colors in the colormap
        # '''
        # self.cmap = None
        # '''
        # Colormap used for wikipride visualization
        # '''
        # self.colors = None
        # '''
        # Hash from cohort index to a color of the colormap 
        # '''
        

        self.saveData = settings.saveData
        '''If True, saves the aggregated data to disk using self.dataToDisk()
        '''
        if 'sqlQuery' not in self.__dict__:
            self.sqlQuery = None
        '''The sql query used to aggregate the data. If None, the sql query from the settings will be used
        '''
        self.mongoQueryVars = 'settings' # {'user_id':1,'edit_count':1}
        '''The Mongo query variables used to aggregate the data. If None, all fields will be returned by mongo. If 'settings', the mongoQueryVars from the settings will be used
        '''
                
    def getFileName(self,varName,destination=None,ftype='data'):
        '''Generates the path and file name that is used for data files as well as visualizations

        :arg varName: name of the self.data variable
        :arg destination: str, destination directory. If None, settings will be used
        :arg ftype: str, 'data' or 'wikipride'
        :returns: A filename without file format
        '''   

        if destination is None: 
            if ftype=='data':
                destination = settings.dataDirectory
            elif ftype=='wikipride':
                destination = settings.wikiprideDirectory
        
             
        desc = [self.__class__.__name__]
        if self.nobots:
            desc.append('nobots')
        else:
            desc.append('bots')
        if len(self.NS) < 16:
            desc.append('NS-'+ '-'.join(self.NS))
        
        desc = '_'.join(desc)

        fn = '%s/%s_%s'%(destination,varName,desc)

        return fn

        
    def dataToDisk(self):
        '''Saves the aggregated numpy.arrays to file. There is one file for each collected variable, the names 
        is uniquely constructed from the properties of the variable and cohort.
        '''
        for n,d in self.data.items():
            fn = self.getFileName(n)
            N.savetxt('%s.txt'%fn,d)


    def loadDataFromDisk(self,varName):
        '''Loads the data from disk. It will populate self.data with {names[i] : numpy.array}.
        An error is raised if there is no corresponding datafile stored

        :args varName: variable name
        '''
        fn = self.getFileName(varName,ftype='data')
        self.data[varName] = N.loadtxt('%s.txt'%fn)

        self.initDataDescription()
        


    def aggregateDataFromSQL(self):
        '''Iterates over the SQL data and calls self.processSQLrow() which needs to be implemented by the parent cohort class
        '''

        logging.info('Aggregating data from SQL')
        

        from db import sql

        cur = sql.getSSDictCursor()
        # try:
        #     from db import sql
        # except:
        #     logging.error("Couldn't connect to SQL")
        #     raise Exception("SQL connection needed!")
        

        if self.sqlQuery is None:
            if 'sqlquery' in settings.__dict__:
                if settings.sqlquery!='' and settings.sqlquery is not None:
                    self.sqlQuery = settings.sqlquery
            else:
                logging.error("No valid SQL query has been supplied.")     
                raise Exception("SQL query needed!")
                   
        self.initData()

        logging.info("SQL query: %s"%self.sqlQuery)     

        cur.execute(self.sqlQuery)

        for count,row in enumerate(cur):
            self.processSQLrow(row)

            if count%1000000==0:
                logging.info('Processed %s million SQL rows'%(count/1000000))


    def processSQLrow(self,row):
        '''Processes a row of the SQL result set
        '''
        raise Exception("Cohort subclass should implement this me!")

    def aggregateDataFromMongo(self):
        logging.info('Aggregating data from Mongo DB')
        

        try:
            from db import mongo
        except:
            logging.error("Couldn't connect to Mongo db")
            raise Exception("Mongo connection needed!")
        
        mongo.connect()

        if self.mongoQueryVars == 'settings':
            if 'mongoQueryVars' in settings.__dict__:
                self.mongoQueryVars = settings.mongoQueryVars
            else:
                logging.error("No valid query variables have been supplied. Returning all variables instead.")     
                self.mongoQueryVars = None
                                   
        self.initData()

        for count,document in enumerate(mongo.col.find({},self.mongoQueryVars)):
            self.processMongoDocument(document)

            if count%1000000==0:
                logging.info('Processed %s million Mongo documents'%(count/1000000))



    def processMongoDocument(self):
        '''Processes a document of the Mogo DB result set
        '''
        raise Exception("Cohort subclass should implement this method!")
        
    def initData(self):
        '''Initialize the self.data dictionary with the appropriate variable names and numpy.arrays
        '''
        raise Exception("Cohort subclass should implement this method!")
    def initDataDescription(self):
        '''Initialize the self.data_description dictionary with additional information
        '''
        raise Exception("Cohort subclass should implement this method!")


    def finalizeData(self):
        '''This method should is called at the of an aggregateDataFromXXX() method. It allows to manipulate
        the time series data in self.data. E.g. and 'addedBytes' could be divided by 'edits' to create a new 
        variable 'addedPerEdit'.
        '''
        logging.info("No manipulations after the data aggregation is implemented for %s"%(self.__class__.__name__))     

    

    def setColorbar(self):
        raise Exception("Cohort subclass should implement this method!")

    def getIndex(self, edits):
        '''
        Returns the index of the cohort 
        '''
        raise Exception("Cohort subclass should implement this method!")        


    def wikiPride(self, varName,varDesc=None, normal=True, percentage=True, colorbar=True, ncolors=None, flip=False, pdf=True,dest=None):
        '''
        Plots the cohort trends using the famous WikiPride stacked bar chart!

        If `normal` is True, the absolute values are visualized

        If `percentage` is True, the relative values are visualized (i.e. the percentages)

        If `flip` is True, the numpy.array is flipped upside down. This results in the bars
        added in reverse order. The order of the cohort labels is also reversed as a result.

        :arg varName: str, the name of the numpy.array in self.data to visualize
        :arg varDesc: str. Alternative name for the data description. If None, `varName' will be used.
        :arg normal: Boolean. Visualize absolute values.
        :arg percentage: Boolean. Visualize percentages.
        :arg colorbar: Boolean. Add color bar legend.
        :arg pdf: Boolean. If True, save plot as pdf
        :arg dest: str. Path to directory on where to save the plot. If None, the path in settings.py will be used
        :arg flip: Boolean. N.flipud() the numpy.array

        '''
        try:
            if pdf:
                from matplotlib import use
                use('PDF')

            from matplotlib import pyplot as plt
            from matplotlib import mpl
        except:
            logging.error("matplotlib not installed, no plotting possible")
            return


        from utils import cmap_discretize    

        # configure the color map    
        if ncolors is None:
            ncolors = settings.ncolors if ('ncolors' in settings.__dict__ and settings.ncolors is not None)  else len(self.cohorts)                                                

        cmapName = settings.cmapName if 'cmapName' in settings.__dict__  else 'spectral'
        cmap = cmap_discretize(cmapName,ncolors)
        colors = cmap(N.linspace(0,1,len(self.cohorts)))   
        
        # the data to plot
        self.initDataDescription()
        data = self.data[varName]
        data_description = {}
        if varDesc is not None:
            data_description = self.data_description[varDesc] if varDesc in self.data_description else {}
        else:
            data_description = self.data_description[varName] if varName in self.data_description else {}

        # x axis
        # xt = N.arange(data.shape[1])
        xt = N.arange(len(self.time_stamps))

        if flip:
            data = N.flipud(data)
            self.cohort_labels.reverse()


        if normal and percentage:
            #figure contains both plots
            size = (3*11,2*8.5)
            fig = plt.figure(figsize=size)    
            axN = fig.add_axes([0.05,0.55,0.85,0.4],frame_on=False)    
            axP = fig.add_axes([0.05,0.05,0.85,0.4],frame_on=False)    
            
        elif normal:
            size = (3*11,8.5)
            fig = plt.figure(figsize=size)
            axN = fig.add_axes([0.05,0.1,0.85,0.8],frame_on=False)
        elif percentage:
            size = (3*11,8.5)
            fig = plt.figure(figsize=size)
            axP = fig.add_axes([0.05,0.1,0.85,0.8],frame_on=False)
        else:
            logging.error('No plots to plot while plotting!')
            return


        for i in range(data.shape[0]):

            logging.info("Plotting cohort %s"%self.cohort_labels[i]) 

            if normal:
                b = data[0:i,:].sum(axis=0)
                axN.bar(xt,data[i,:],bottom=b,color=colors[i],linewidth=0)     
                
                # rectpatches = axN.patches
                # pcol = mpl.collections.PatchCollection(rectpatches, match_original=False)
                # axN.add_collection(pcol) 
                # axN.patches = []

            if percentage:       
                # scale to 1 
                t = data.sum(axis=0) + 1
                b = data[0:i,:].sum(axis=0) / t
                axP.bar(xt,data[i,:]/t,bottom=b,color=colors[i],linewidth=0)
            
            

        
        xtskip = [ int(i) for i in N.linspace(0,xt.shape[0]-1,(xt.shape[0]-1)/5)]
        xtlabels = ['%s / %s'%(self.time_stamps[i][4:],self.time_stamps[i][:4]) for i in xtskip]

        if normal:
            # axN.set_title('Net contributions of cohorts (namespace 0, bots filtered)')
            title = data_description.get('title','')
            axN.set_title(title)

            if 'ylim' in data_description:
                axN.set_ylim(data_description['ylim'])

            ylabel = data_description.get('ylabel','')
            axN.set_ylabel(ylabel)

            if 'ytickslabel' in data_description:
                func = data_description['ytickslabel']
                axN.set_yticklabels(map(func, axN.get_yticks()),size='small')
            
            # x ticks / labels
            axN.set_xticks(xtskip)
            axN.set_xticklabels(xtlabels,rotation=20,verticalalignment='top')#,size='small')


        if percentage:

            axP.set_ylim(0,1)
            axP.set_ylabel('Percentage')   
            axP.twinx()
        
            title = data_description.get('title','')
            axP.set_title('Percentage - %s'%title)            

            # x ticks / labels
            axP.set_xticks(xtskip)
            axP.set_xticklabels(xtlabels,rotation=20,verticalalignment='top')#,size='small')


        if colorbar:        
            # color bar axes
            cba = fig.add_axes([0.92,0.1,0.02,0.8])
            # color bar
            cb = mpl.colorbar.ColorbarBase(cba, cmap=cmap, orientation='vertical')
            # getting cohort specific ticks and labels
            ticks,labels = self.colorbarTicksAndLabels(ncolors)

            cb.set_ticks(ticks)   
            cb.set_ticklabels(labels)
        
        
        
        if percentage and normal:                           
            fig.set_size_inches(33,2*8.5)
        else:
            fig.set_size_inches(33,8.5)
            
        # save figure
        fn = self.getFileName( varName, destination=dest)

        fig.savefig('%s.%s'%(fn,'pdf' if pdf else 'png'))
        fig.clear()


        # reverse cohort_labels back if data has been flipped
        if flip: 
            self.cohort_labels.reverse()



