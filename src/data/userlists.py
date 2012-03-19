"""This module holds the collection of SQL queries used for the preprocessing of the data
"""
import logging
logger = logging.getLogger('User lists')


import os,sys
from datetime import datetime,timedelta
import settings


### Bots

BOT_LIST = "%s.%swiki_bots"%(settings.sqluserdb,settings.language)

CREATE_BOT_LIST = """
CREATE TABLE IF NOT EXISTS %s
SELECT  
	u.user_id, 
	u.user_name
FROM %s.user u 
JOIN %s.user_groups ug ON (u.user_id=ug.ug_user)
WHERE   ug.ug_group = 'bot'
"""%(BOT_LIST,settings.sqlwikidb,settings.sqlwikidb)


INDEX_BOT_LIST="""
CREATE INDEX user_id on %s (user_id);
"""%(BOT_LIST)


BOT_LIST_FILE = "%s/%swiki_bots.tsv"%(settings.userlistdirectory,settings.language)
EXPORT_BOT_LIST = """
mkdir -p %s;
mysql -h %s -e 'select user_id from %s;' > %s;
sed -i '1d' %s
"""%(settings.userlistdirectory,settings.sqlhost,BOT_LIST,BOT_LIST_FILE,BOT_LIST_FILE)



INSERT_BOT_LIST = """
INSERT INTO %s (user_id,user_name) 
SELECT 
	user_id, 
	user_name 
FROM
	%s.user 
WHERE 
	%s in (%s);
"""


### Autoconfirmed users

TEMPDIR = '/a/datasets/fabian/auto_confirmed/'

def createAutoConfirmedUserTable():
	'''This is a function rather than a SQL query because a script is used to create the dataset which is then imported back into the MySQL database '''

	from db import sql

	tempfile = os.path.join(TEMPDIR,'user_autoconfirmed.tsv')
	output = open(tempfile, 'a')

	fourdays = timedelta(days=4)

	curSS = sql.getSSCursor()

	logger.info('Creating temp file to store autoconfirmation date of all users')

	curSS.execute('''SELECT 
	                    u.user_id, 
	                    u.user_name,
	                    u.user_registration,
	                    (SELECT rev_timestamp FROM %s.revision WHERE rev_user=u.user_id ORDER BY rev_timestamp ASC LIMIT 9, 1) AS tenthedit
	                    FROM %s.user u;'''%(settings.sqlwikidb,settings.sqlwikidb)) 


	for i,res in enumerate(curSS):
	    u_id = res[0]
	    u_text = res[1]

	    tenedits = res[3]

	    ins = (u_id,u_text,0,'NULL')
	    
	    if tenedits:
	        # an editors has to have ten edits to be auto-confirmed
	        tenedits = datetime.strptime(tenedits,'%Y%m%d%H%M%S')
	        reg_time = res[2] 

	        reg_plus_four = None
	        if reg_time:
	            reg_plus_four = datetime.strptime(reg_time,'%Y%m%d%H%M%S') + fourdays
	            # print 'four days after:',reg_plus_four

	            if reg_plus_four>tenedits:
	                # 10 edits in less than 4 days, auto-confirmed after 4 days
	                # print '-> auto-confirmed after four days'
	                auto = datetime.strftime(reg_plus_four,'%Y%m%d%H%M%S')
	                # ins = '"%s","%s",1,"%s"'%(u_id,u_text,auto)
	                ins = (u_id,u_text,1,auto)
	            else:
	                # 10th edit after than 4 days, auto-confirmed after 10 edits
	                # print '-> auto-confirmed after 10 edits'
	                auto = datetime.strftime(tenedits,'%Y%m%d%H%M%S')
	                # ins = '"%s","%s",1,"%s"'%(u_id,u_text,auto)
	                ins = (u_id,u_text,1,auto)
	        
	        else:
	            # no registration time, just use 10 edits (there are only few like that)
	            auto = datetime.strftime(tenedits,'%Y%m%d%H%M%S')
	            # ins = '"%s","%s",1,"%s"'%(u_id,u_text,auto)
	            ins = (u_id,u_text,1,auto)
	            
	    
	    output.write('\t'.join(str(v) for v in ins)+'\n')

	    if i%100==0:          
	        if i%3000==0:
	            sys.stdout.write('\n.')
	        else:   
	            sys.stdout.write('.')

	        sys.stdout.flush() 

	curSS.close()
	output.close()


	cur = sql.getCursor()

	cur.execute('''DROP TABLE %s.user_autoconfirmed;
		CREATE TABLE IF NOT EXISTS %s.%s_user_autoconfirmed
		    (user_id int(5) unsigned,
		    user_name varchar(255),
		    auto_confirmation tinyint(1) unsigned,
		    confirmation_timestamp char(14));
		'''%(settings.sqluserdb,settings.sqluserdb,settings.sqlwikidb))


	cur.close()

	logger.info('Importing auto_confirmation data into MySQL')

	os.system('mysqlimport --local %s %s'%(settings.sqluserdb,tempfile))


	logger.info('Creating index on user_autoconfirmed table')
	cur = sql.getCursor()
	cur.execute("CREATE INDEX user_id ON %s.user_autoconfirmed  (user_id);"%settings.sqluserdb)
	

