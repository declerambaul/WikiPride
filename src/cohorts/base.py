"""This module defines the abstract class :class:`.Cohort`. All cohort definitions must inherit this class.

.. inheritance-diagram:: cohorts.base.Cohort
"""

import sys
import logging
logger = logging.getLogger('Cohort core')



try:
    import numpy as N
except:
    logger.error('Numpy not installed')
    raise Exception('Numpy is a requirement')

try:
    # if pdf:
    #     from matplotlib import use
    #     use('PDF')
    from matplotlib import pyplot as plt
    from matplotlib import mpl
except:
    logger.error("Matplotlib not installed, no plotting possible")



import settings



# (time_stamps,time_stamps_index) = create_time_stamps(fromym='200101',toym='201101')

class Cohort:
    '''
    Abstract class that defines common properties of cohorts, which are defined in the :mod:`cohorts` modules
    '''
    def __init__(self):

        # cohorts and cohort_labels should be defined by now as this is an abstract class
        if self.cohorts is None or self.cohort_labels is None:
            logger.error("self.cohorts or self.cohort_labels not properly defined")
            raise Exception("Cohorts or cohort labels not properly defined for %s"%self.__name__)
        

        self.data = {}
        '''Dictionary that contains the data. {name : numpy.array }. Different aggregates 
        can be saved; for example 'bytesadded','edits','bytesremovedPerEditor'
        '''
        self.data_description = {}
        '''Dictionary that holds descriptive information about self.data. For example, an
        'addedBytes' data description might be:

        self.data_description['addedBytes'] = { title}
        '''

        # TODO : REMOVE
        # if 'NS' not in self.__dict__:
        #     self.NS = settings.NS
        # '''
        # Set of namesspaces that we are interested in
        # '''
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
        
        if 'ncolors' not in self.__dict__:
            self.ncolors = len(self.cohorts)                                                
            '''The number of colors used for the wikipride graphs. If required, it should be defined in the child class definition.
            '''
        
        self.mongoQueryVars = 'settings' # {'user_id':1,'edit_count':1}
        '''The Mongo query variables used to aggregate the data. If None, all fields will be returned by mongo. If 'settings', the mongoQueryVars from the settings will be used
        '''

        # initialize the data description (not the data itself)
        self.initDataDescription()
                
    def getFileName(self,varName,destination=None,ftype='data'):
        '''Generates the path and file name based on properties of the cohort. Additional identifying features might be used in file names by overwriting this method in subclasses of the base :class:`.Cohort` class. 

        If no `destination` argument is passed, the method uses the `ftype` argument to determine which base directory should be used. Only the name of the data feature (e.g. 'added') and the cohort name (e.g. `AbsoluteAgePerMonth`) is used in the basic method.

        :arg varName: name of the self.data variable
        :arg destination: str, destination directory. If None, settings will be used
        :arg ftype: str, 'data' or 'wikipride'
        :returns: A path without file format
        '''   
        import os 

        if destination is None: 
            if ftype=='data':
                destination = settings.datadirectory
            elif ftype=='wikipride':
                destination = settings.wikipridedirectory
        
             
        desc = [varName, self.__class__.__name__]
        # if self.nobots:
        #     desc.append('nobots')
        # else:
        #     desc.append('bots')
        # if len(self.NS) < 16:
        #     desc.append('NS-'+ '-'.join(self.NS))
        
        desc = '_'.join(desc)

        fn = os.path.join(destination,desc)

        return fn

        
    def dataToDisk(self,destination=settings.datadirectory):
        '''Saves the aggregated numpy.arrays to file. There is one file for each collected variable, the names 
        is uniquely constructed from the properties of the variable and cohort.
        '''
        for name,data in self.data.items():
            fn = '%s.txt'%self.getFileName(varName=name,destination=destination)            
            N.savetxt(fn,data)


    def loadDataFromDisk(self,varName,destination=None):
        '''Loads the data from disk. It will populate self.data with {names[i] : numpy.array}.
        An error is raised if there is no corresponding datafile stored

        :args varName: variable name
        :arg destination: str, destination directory. If None, settings will be used

        '''
        fn = None
        if destination is None:
            fn = self.getFileName(varName,ftype='data')
        else:
            fn = self.getFileName(varName,destination=destination)

        self.data[varName] = N.atleast_2d(N.loadtxt('%s.txt'%fn))

        self.initDataDescription()        


    def aggregateDataFromSQL(self,verbose=False):
        '''Iterates over the SQL data and calls self.processSQLrow() which needs to be implemented by the parent cohort class

        :arg verbose: bool, display progress on stdout
        '''

        logger.info('Aggregating data from SQL for %s'%self)
        

        from db import sql

        cur = sql.getSSDictCursor()
        # try:
        #     from db import sql
        # except:
        #     logger.error("Couldn't connect to SQL")
        #     raise Exception("SQL connection needed!")
        

        if self.sqlQuery is None:
            logger.error("No valid SQL query has been supplied.")     
            raise Exception("SQL query needed!")
                   
        self.initData()

        if verbose:
            logger.info("SQL query: %s"%self.sqlQuery)
            # logger.info("Progress (every `.` is 10000 rows)")     

        cur.execute(self.sqlQuery)

        for count,row in enumerate(cur):
            self.processSQLrow(row)
            
            if verbose:            
                if count%10000==0:
                    sys.stdout.write('.')                    
                    sys.stdout.flush() 
                    # print '.',
                    # logger.info('Processed %s million SQL rows'%(count/1000000))
        
        if verbose:
            sys.stdout.write('\n')                    
            sys.stdout.flush()  



    def processSQLrow(self,row):
        '''Processes a row of the SQL result set
        '''
        raise Exception("Cohort subclass should implement this method!")

    def aggregateDataFromMongo(self):
        logger.info('Aggregating data from Mongo DB')
        

        try:
            from db import mongo
        except:
            logger.error("Couldn't connect to Mongo db")
            raise Exception("Mongo connection needed!")
        
        mongo.connect()

        if self.mongoQueryVars == 'settings':
            if 'mongoQueryVars' in settings.__dict__:
                self.mongoQueryVars = settings.mongoQueryVars
            else:
                logger.error("No valid query variables have been supplied. Returning all variables instead.")     
                self.mongoQueryVars = None
                                   
        self.initData()

        for count,document in enumerate(mongo.col.find({},self.mongoQueryVars)):
            self.processMongoDocument(document)



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
        logger.info("No manipulations after the data aggregation is implemented for %s"%(self.__class__.__name__))     

    

    def setColorbar(self):
        raise Exception("Cohort subclass should implement this method!")

    def getIndex(self, edits):
        '''
        Returns the index of the cohort 
        '''
        raise Exception("Cohort subclass should implement this method!")        


    def __repr__(self):
        '''String representation of cohort, abstract :class:`.Cohort` returns the name of the class only.
        '''
        return self.__class__.__name__

    def wikiPride(self, varName,varDesc=None, normal=True, percentage=True, colorbar=True, ncolors=None, flip=False, pdf=False,dest=None,verbose=False):
        '''
        Plots the cohort trends using the famous WikiPride stacked bar chart! If `normal` is True, the absolute values are visualized. If `percentage` is True, the relative values are visualized (i.e. the percentages). If `flip` is True, the numpy.array is flipped upside down. This results in the bars added in reverse order. The order of the cohort labels is also reversed as a result.

        :arg varName: str, the name of the numpy.array in self.data to visualize
        :arg varDesc: str. Alternative name for the data description. If None, `varName` will be used.
        :arg normal: Boolean. Visualize absolute values.
        :arg percentage: Boolean. Visualize percentages.
        :arg colorbar: Boolean. Add color bar legend.
        :arg pdf: Boolean. If True, save plot as pdf
        :arg flip: Boolean. N.flipud() the numpy.array which inverses the order the boxes are added
        :arg dest: str. Path to directory on where to save the plot. If None, the path in settings.py will be used
        :arg verbose: Boolean. Displays information about the graphing progress.
        '''

        from utils import cmap_discretize    

        logger.info('Creating WikiPride graph for %s - %s'%(varName,self))

        # configure the color map    
        if ncolors is not None:
            self.ncolors = ncolors 

        cmapName = settings.cmapName if 'cmapName' in settings.__dict__  else 'spectral'
        cmap = cmap_discretize(cmapName,self.ncolors)
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
            self.cohorts.reverse()


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
            logger.error('No plots to plot while plotting!')
            return

        
        for i in range(data.shape[0]):

            if verbose:
                sys.stdout.write('.')                    
                sys.stdout.flush() 
                # print '.',
                # logger.info("Plotting cohort %s"%self.cohort_labels[i]) 

            if normal:
                b = data[0:i,:].sum(axis=0)
                axN.bar(xt,data[i,:],bottom=b,color=colors[i],linewidth=0)     
                
                # rectpatches = axN.patches
                # pcol = mpl.collections.PatchCollection(rectpatches, match_original=False)
                # axN.add_collection(pcol) 
                # axN.patches = []

            if percentage:       
                # scale to 1 
                t = data.sum(axis=0)
                t[t==0] = 1
                b = data[0:i,:].sum(axis=0) / t

                # print 'cohort '+self.cohort_labels[i]
                # print 'total \n%s'%t
                # print 'bottom \n%s'%b
                # print 'box \n%s'%(data[i,:]/t)

                axP.bar(xt,data[i,:]/t,bottom=b,color=colors[i],linewidth=0)
            
        if verbose:
                sys.stdout.write('\n')                    
                sys.stdout.flush()  

        
        xtskip = [ int(i) for i in N.linspace(0,xt.shape[0]-1,(xt.shape[0]-1)/5)]
        xtlabels = ['%s / %s'%(self.time_stamps[i][4:],self.time_stamps[i][:4]) for i in xtskip]

        if normal:
            # axN.set_title('Net contributions of cohorts (namespace 0, bots filtered)')
            title = '%s_WP - %s'%(settings.language.upper() ,data_description.get('title',''))
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
        
            title = '%s_WP - %s'%(settings.language.upper() ,data_description.get('title',''))
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
            ticks,labels = self.colorbarTicksAndLabels(self.ncolors)

            cb.set_ticks(ticks)   
            cb.set_ticklabels(labels)
        
        
        
        if percentage and normal:                           
            fig.set_size_inches(33,2*8.5)
        else:
            fig.set_size_inches(33,8.5)
            
        # save figure
        fn = None
        if dest is None:
            fn = self.getFileName( varName, ftype='wikipride')
        else:
            fn = self.getFileName( varName, destination=dest)

        if verbose:
            logger.info('Saving WikiPride plot')
        fig.savefig('%s.%s'%(fn,'pdf' if pdf else 'png'))
        # fig.clear()
        plt.close(fig)



        # reverse cohort_labels back if data has been flipped
        if flip: 
            self.cohort_labels.reverse()
            self.cohorts.reverse()

    def linePlots(self, dest):
        '''This method allows to produce line plots using the cohort data stored in `self.data`. Usually line plots illustrate interesting trends/ratios that depend on the cohort definition. Thus this method in the base cohort definition does nothing and should be overwritten in the cohort class itself.'''
        logging.warning("linePlots() is called on a cohort instance (%s) for which no line plots have been defined."%self.__class__.__name__)
        pass

    def addLine(self, data,fig=None, label=''):
        '''Adds a line to the matplotlib figure passed as argument. The dimension the data has to match the length of the `time_stamps`. It is assumed that the figure contains only one axes.

        :arg data: numpy.array of same length as `time_stamps`
        :arg fig: matplotlib figure. If none, a new figure is created.
        :arg label: str, label for the legend. Defaults to an empty string.

        :returns: matplotlib figure

        '''
        # the axis
        ax=None
        if fig is None:
            size = (3*11,8.5)
            fig = plt.figure(figsize=size)
            ax = fig.add_axes([0.05,0.1,0.85,0.8],frame_on=False)
        else:
            ax = fig.axes[0]
        
        ax.plot(range(data.shape[0]),data,label=label)    

        return fig
        

    def saveFigure(self, name, fig, dest,title='',ylabel='',xlabel=None,ylog=False,legendpos=None,pdf=False):
        """Saves a matplotlib figure to disk.

        :arg name: str, name of resulting file
        :arg fig: matplotlib figure to be saved.
        :arg dest: str, destination folder.
        :arg title: str, plot title. Defaults to an empty string.        
        :arg ylabel: str, plot y axis label. Defaults to an empty string.
        :arg xlabel: str, plot x axis label. If none, time stamps xticks will be used.
        :arg ylog: If True the log scale is used for the y-axis, default is False. 
        :arg legendpos: int, the position of the legend. If None, no legend will be displayed.
        :arg pdf: If True the file will be saved as pdf, otherwise as png.

        """

        ax = fig.axes[0]

        
        ax.set_title('%s_WP - %s'%(settings.language.upper() ,title))
        ax.set_ylabel(ylabel)

        if xlabel is not None:
            ax.xlabel(xlabel)
        else:            
            # x ticks / labels
            xt = N.arange(len(self.time_stamps))
            xtskip = [ int(i) for i in N.linspace(0,xt.shape[0]-1,(xt.shape[0]-1)/5)]
            xtlabels = ['%s / %s'%(self.time_stamps[i][4:],self.time_stamps[i][:4]) for i in xtskip]
            
            ax.set_xticks(xtskip)
            ax.set_xticklabels(xtlabels,rotation=20,verticalalignment='top')#,size='small')

        
        if ylog:
            ax.set_yscale('log')

        if legendpos is not None:
            ax.legend(loc=legendpos)



        fn = self.getFileName( name, destination=dest)
        fig.savefig('%s.%s'%(fn,'pdf' if pdf else 'png'))
        # fig.clear()
        plt.close(fig)



