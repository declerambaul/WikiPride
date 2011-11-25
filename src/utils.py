'''
A set of utility methods that are used in different parts of the framework.
'''

import logging


# Set of bots read from a bot tsv file
bots = None
filterBots = False
def setFilterBots(fb,botfile):
    global filterBots,bots
    
    if fb:
        try:
            bots = set(long(bot) for bot in open(botfile,'r'))

            filterBots = fb
        except:
            logging.error("Botlist (%s) could not be loaded, Bots will not be filtered"%botfile)
            
def isBot(u_id):
    '''
    Returns true if we filter for bots and  u_id is a known bot.

    :arg ints: Boolean, if True compares u_id as int (default is False)    
    '''       
    if filterBots:
        if u_id in bots:
            return True
    return False        


def create_time_stamps_month(fromym='200101',toym='201012'):
    '''
    Helper data structures for time stamps
    List of all time unites, i.e. every month. yyyymm
    '''
    time_stamps = []
    # A dictionary that serves as a lookup for the index of atime stamp
    time_stamps_index = {}

    min_year = fromym[:-2]
    min_month = fromym[-2:]
    max_year = toym[:-2]
    max_month = toym[-2:]

    i = 0 
    #add remaining months in the first year
    for m in range(int(min_month),13):
        ts = '%s%02d'%(min_year,m)
        time_stamps.append(ts)
        time_stamps_index[ts] = i
        i += 1
    #add intermediate years
    for y in range(int(min_year)+1,int(max_year)):
        for m in range(1,13):
            ts = '%s%02d'%(y,m)
            time_stamps.append(ts)
            time_stamps_index[ts] = i
            i += 1
    #last year
    for m in range(1,int(max_month)+1):
        ts = '%s%02d'%(max_year,m)
        time_stamps.append(ts)
        time_stamps_index[ts] = i
        i += 1

    return (time_stamps,time_stamps_index)

def create_time_stamps_day(fromymd='20010101',toymd='20101231'):
    '''
    Helper data structures for time stamps
    List of all time unites, i.e. every month. yyyymm
    '''

    import calendar

    time_stamps = []
    # A dictionary that serves as a lookup for the index of atime stamp
    time_stamps_index = {}

    min_year = int(fromymd[:4])
    min_month = int(fromymd[4:6])
    min_day = int(fromymd[6:8])
    max_year = int(toymd[:4])
    max_month = int(toymd[4:6])
    max_day = int(toymd[6:8])
    i = 0 
    #add remaining months in the first year
    for m in range(min_month,13):
        # calender.monthrange returns a tuple (day of the week, number of days in the month)
        nds = calendar.monthrange(min_year,m)[1]
        for d in range(min_day,nds+1):
            ts = '%s%02d%02d'%(min_year,m,d)
            time_stamps.append(ts)
            time_stamps_index[ts] = i
            i += 1
    #add intermediate years
    for y in range(min_year+1,max_year):
        for m in range(1,13):
            # calender.monthrange returns a tuple (day of the week, number of days in the month)
            nds = calendar.monthrange(y,m)[1]            
            for d in range(1,nds+1):
                ts = '%s%02d%02d'%(y,m,d)
                time_stamps.append(ts)
                time_stamps_index[ts] = i
                i += 1
    #to last month
    for m in range(1,max_month):
        nds = calendar.monthrange(max_year,m)[1]
        for d in range(1,nds+1):
            ts = '%s%02d%02d'%(max_year,m,d)
            time_stamps.append(ts)
            time_stamps_index[ts] = i
            i += 1
    #to last day
    for d in range(1,max_day+1):
        ts = '%s%02d%02d'%(max_year,max_month,d)
        time_stamps.append(ts)
        time_stamps_index[ts] = i
        i += 1


    return (time_stamps,time_stamps_index)
    
    
def computeMonthStartEndtime(ym):
    '''
    Returns the starting and end datetime object for the yyyymm passed. I.e. the first and last day of the month

    :arg ym: str, 'yyyymm' format
    :returns: tuple of datetime objects
    '''
    from datetime import datetime
    import calendar

    
    y = int(ym[:4])
    m = int(ym[4:])

    start = datetime(y, m, 1)
    # days in the given month 
    # calender.monthrange returns a tuple (day of the week, number of days in the month)
    d = calendar.monthrange(y,m)[1]

    end = datetime(y, m, d)

    return (start,end)

def numberOfMonths(ymStart,ymEnd):
    '''Returns the number of months between the parameters.

    :arg ymStart: str, 'yyyymm' format
    :arg ymEnd: str, 'yyyymm' format
    :returns: int, number of month
    '''
    months = 0
    months += (int(ymEnd[:4])-(int(ymStart[:4])+1)) * 12
    if int(ymEnd[:4])==int(ymStart[:4]):
        #same year
        months += (int(ymEnd[4:])-int(ymStart[4:]))+1
    else:
        months += 12-int(ymStart[4:])+1
        months += int(ymEnd[4:])

    return months


def cmap_discretize(cmapName, N):
    """
    From http://www.scipy.org/Cookbook/Matplotlib/ColormapTransformations
    
    :arg cmap: colormap instance, eg. cm.jet.
    :arg N: Number of colors.

    :returns: a discrete colormap from the continuous colormap cmap.
    """
    
    try:
        from numpy import array, linspace, zeros, interp
        import matplotlib 
        from matplotlib import pyplot as plt
    except:
        logging.error('matplotlib or numpy not installed')
        logging.error("cmap_discretize() returns invalid cmap; you can't plot without these packages anyways")
        return cmapName


    if cmapName is None:
        cmap = plt.cm.spectral
    else:
        cmap = plt.cm.get_cmap(cmapName)
    


    # try: 
    #     from scipy import interpolate
    # except:
    #     logging.error('scipy not installed')
    #     logging.info("cmap_discretize() can't interpolate the colormap, returns cmap %s unchanged"%cmapName)
    #     return cmap


    cdict = cmap._segmentdata.copy()
    # N colors
    colors_i = linspace(0,1.,N)
    # N+1 indices
    indices = linspace(0,1.,N+1)
    for key in ('red','green','blue'):
        # Find the N colors
        D = array(cdict[key])
        
        # using scipy 
        # I = interpolate.interp1d(D[:,0], D[:,1])
        # colors = I(colors_i)
        
        # using numpy
        colors = interp(colors_i,D[:,0], D[:,1])

        # Place these colors at the correct indices.
        A = zeros((N+1,3), float)
        A[:,0] = indices
        A[1:,1] = colors
        A[:-1,2] = colors
        # Create a tuple for the dictionary.
        L = []
        for l in A:
            L.append(tuple(l))
        cdict[key] = tuple(L)
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap('colormap',cdict,1024)


def movingAverage(array, WINDOW=5):
    try:
        import numpy as N
    except:
        logging.warning("Moving average can't be computed (Numpy not installed)")
        return
    
    
    weightings = N.repeat(1.0, WINDOW) / WINDOW
    return N.convolve(array, weightings)[WINDOW-1:-(WINDOW-1)]    


