"""This module holds the collection of SQL queries used for the preprocessing of the data
"""

import settings

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
mysql -h %swiki-p.rrdb.toolserver.org -e 'select user_id from %s;' > %s;
sed -i '1d' %s
"""%(settings.userlistdirectory,settings.language,BOT_LIST,BOT_LIST_FILE,BOT_LIST_FILE)





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

