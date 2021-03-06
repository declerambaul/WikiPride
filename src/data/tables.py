"""This module holds the collection of SQL queries used for the preprocessing of the data
"""

import settings


CREATE_USER_DATABASE = 'CREATE DATABASE IF NOT EXISTS %s;'%settings.sqluserdb

USER_COHORT = "%s.%swiki_user_cohort"%(settings.sqluserdb,settings.language)
REV_LEN_CHANGED = "%s.%swiki_rev_len_changed"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH = "%s.%swiki_editor_centric_year_month"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH_NAMESPACE = "%s.%swiki_editor_centric_year_month_namespace"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH_NS0_NOREDIRECT = "%s.%swiki_editor_centric_year_month_ns0_noredirect"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH_DAY_NAMESPACE = "%s.%swiki_editor_centric_year_month_day_namespace"%(settings.sqluserdb,settings.language)
TIME_YEAR_MONTH_NAMESPACE ="%s.%swiki_time_centric_year_month_namespace"%(settings.sqluserdb,settings.language)
TIME_YEAR_MONTH_DAY_NAMESPACE = "%s.%swiki_time_centric_year_month_day_namespace"%(settings.sqluserdb,settings.language)


CREATE_USER_COHORTS = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    user_id,
    user_name,
    REPLACE(user_name, ' ', '_') as user_name_title,
    MIN(first_edit)         AS first_edit,
    YEAR(MIN(first_edit))   AS first_edit_year,
    MONTH(MIN(first_edit))  AS first_edit_month,
    MAX(first_edit)         AS last_edit
FROM
(
SELECT
    user_id,
    user_name,
    MIN(rev_timestamp)         AS first_edit,
    YEAR(MIN(rev_timestamp))   AS first_edit_year,
    MONTH(MIN(rev_timestamp))  AS first_edit_month,
    MAX(rev_timestamp)         AS last_edit
FROM %s.revision r
INNER JOIN %s.user u
    ON u.user_id = r.rev_user
GROUP BY user_id
UNION
SELECT
    user_id,
    user_name,
    MIN(ar_timestamp)         AS first_edit,
    YEAR(MIN(ar_timestamp))   AS first_edit_year,
    MONTH(MIN(ar_timestamp))  AS first_edit_month,
    MAX(ar_timestamp)         AS last_edit
FROM %s.archive a
INNER JOIN %s.user u
    ON u.user_id = a.ar_user
GROUP BY user_id
) AS whocares_doesntmatter
GROUP BY user_id, user_name;
"""%(USER_COHORT,settings.sqlwikidb,settings.sqlwikidb,settings.sqlwikidb,settings.sqlwikidb)
"""Query to create an augmented user table. Includes time stamp for first edit of user, also considering archived revisions. A detailed description is available `here <http://meta.wikimedia.org/wiki/WSoR_datasets/user_cohort>`_.
"""

INDEX_USER_COHORTS="""
CREATE INDEX /* SLOW_OK */ user_id on %s (user_id);
CREATE INDEX /* SLOW_OK */ user_title on %s (user_name_title);
"""%(USER_COHORT,USER_COHORT)



CREATE_REV_LEN_CHANGED = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    c.rev_id,
    c.rev_timestamp,
    YEAR(c.rev_timestamp)             AS rev_year,
    MONTH(c.rev_timestamp)            AS rev_month,
    DAY(c.rev_timestamp)              AS rev_day,
    c.rev_len,
    c.rev_user                        AS user_id,
    c.rev_user_text                   AS user_text,
    c.rev_page                        AS page_id,
    cp.page_namespace                 AS namespace,
    c.rev_parent_id                   AS parent_id,
    c.rev_len - IFNULL(p.rev_len, 0)  AS len_change
FROM %s.revision c
LEFT JOIN %s.revision p
    ON c.rev_parent_id = p.rev_id
INNER JOIN %s.page cp
    ON c.rev_page = cp.page_id;
"""%(REV_LEN_CHANGED,settings.sqlwikidb,settings.sqlwikidb,settings.sqlwikidb)

INDEX_REV_LEN_CHANGED="""
CREATE INDEX /* SLOW_OK */ compound on %s (user_id,rev_year,rev_month,rev_day,namespace);
"""%REV_LEN_CHANGED
"""Query to create an augmented revision table. Includes namespace and change of the size of the articel `len_change`. Costly query, a detailed description is available `here <http://meta.wikimedia.org/wiki/WSoR_datasets/rev_len_changed>`_.
"""


CREATE_EDITOR_YEAR_MONTH = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    rlc.user_id,
    rlc.rev_year,
    rlc.rev_month,
    uc.first_edit,
    uc.first_edit_year,
    uc.first_edit_month,
    SUM(len_change = 0)                    AS noop_edits,
    SUM(len_change > 0)                    AS add_edits,
    SUM(len_change < 0)                    AS remove_edits,
    SUM(IF(len_change > 0, len_change, 0)) AS len_added,
    SUM(IF(len_change < 0, len_change, 0)) AS len_removed
FROM %s rlc
INNER JOIN %s uc USING(user_id)
GROUP BY
    rlc.user_id,
    rlc.rev_year,
    rlc.rev_month;
"""%(EDITOR_YEAR_MONTH,REV_LEN_CHANGED,USER_COHORT)
"""Query to editor centric table. For each user and each year/month, it contains the number of add/remove edits as well as number bytes added/removed.
"""


CREATE_EDITOR_YEAR_MONTH_NAMESPACE = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    rlc.user_id,
    rlc.namespace,
    rlc.rev_year,
    rlc.rev_month,
    uc.first_edit,
    uc.first_edit_year,
    uc.first_edit_month,
    SUM(len_change = 0)                    AS noop_edits,
    SUM(len_change > 0)                    AS add_edits,
    SUM(len_change < 0)                    AS remove_edits,
    SUM(IF(len_change > 0, len_change, 0)) AS len_added,
    SUM(IF(len_change < 0, len_change, 0)) AS len_removed
FROM %s rlc
INNER JOIN %s uc USING(user_id)
GROUP BY
    rlc.user_id,
    rlc.rev_year,
    rlc.rev_month,
    rlc.namespace;
"""%(EDITOR_YEAR_MONTH_NAMESPACE,REV_LEN_CHANGED,USER_COHORT)
"""Query to editor centric table. Same as `EDITOR_YEAR_MONTH` but including namespace. For each user and each year/month/namespace, it contains the number of add/remove edits as well as number bytes added/removed.
"""

# CREATE_EDITOR_YEAR_MONTH_NS0_NOREDIRECT = """
# CREATE TABLE IF NOT EXISTS %s
# SELECT /* SLOW_OK */
#     rlc.user_id,    
#     rlc.rev_year,
#     rlc.rev_month,
#     uc.first_edit,
#     uc.first_edit_year,
#     uc.first_edit_month,
#     SUM(len_change = 0)                    AS noop_edits,
#     SUM(len_change > 0)                    AS add_edits,
#     SUM(len_change < 0)                    AS remove_edits,
#     SUM(IF(len_change > 0, len_change, 0)) AS len_added,
#     SUM(IF(len_change < 0, len_change, 0)) AS len_removed
# FROM %s rlc
# INNER JOIN %s uc USING(user_id)
# INNER JOIN %s.page p
#     ON rlc.page_id = p.page_id;
# WHERE
#     p.page_namespace = 0 AND
#     p.page_is_redirect = 0
# GROUP BY
#     rlc.user_id,
#     rlc.rev_year,
#     rlc.rev_month;
# """%(EDITOR_YEAR_MONTH_NS0_NOREDIRECT,REV_LEN_CHANGED,USER_COHORT,settings.sqlwikidb)

CREATE_EDITOR_YEAR_MONTH_NS0_NOREDIRECT = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    rlc.user_id,    
    rlc.rev_year,
    rlc.rev_month,
    SUM(len_change = 0)                    AS noop_edits,
    SUM(len_change > 0)                    AS add_edits,
    SUM(len_change < 0)                    AS remove_edits,
    SUM(IF(len_change > 0, len_change, 0)) AS len_added,
    SUM(IF(len_change < 0, len_change, 0)) AS len_removed
FROM %s rlc
INNER JOIN %s.page p
    ON rlc.page_id = p.page_id
WHERE
    p.page_namespace = 0 AND
    p.page_is_redirect = 0
GROUP BY
    rlc.user_id,
    rlc.rev_year,
    rlc.rev_month;
"""%(EDITOR_YEAR_MONTH_NS0_NOREDIRECT,REV_LEN_CHANGED,settings.sqlwikidb)
"""Query to editor centric table. Same as `EDITOR_YEAR_MONTH` but including only for namespace 0 (main) and only for pages that are no redirects. For each user and each year/month, it contains the number of add/remove edits as well as number bytes added/removed.
"""

CREATE_EDITOR_YEAR_MONTH_DAY_NAMESPACE = """
CREATE TABLE IF NOT EXISTS %s
SELECT /* SLOW_OK */
    rlc.user_id,
    rlc.namespace,
    rlc.rev_year,
    rlc.rev_month,
    rlc.rev_day,
    uc.first_edit,
    uc.first_edit_year,
    uc.first_edit_month,
    SUM(len_change = 0)                    AS noop_edits,
    SUM(len_change > 0)                    AS add_edits,
    SUM(len_change < 0)                    AS remove_edits,
    SUM(IF(len_change > 0, len_change, 0)) AS len_added,
    SUM(IF(len_change < 0, len_change, 0)) AS len_removed
FROM %s rlc
INNER JOIN %s uc USING(user_id)
GROUP BY
    rlc.user_id,
    rlc.rev_year,
    rlc.rev_month,
    rlc.rev_day,
    rlc.namespace;
"""%(EDITOR_YEAR_MONTH_DAY_NAMESPACE,REV_LEN_CHANGED,USER_COHORT)

CREATE_TIME_YEAR_MONTH_NAMESPACE = """
CREATE TABLE %s
SELECT /* SLOW_OK */ 
    edc.rev_year,
    edc.rev_month,    
    edc.namespace,
    COUNT(edc.user_id)  AS editors,
    SUM(noop_edits)     AS noop_edits,
    SUM(add_edits)      AS add_edits,
    SUM(remove_edits)   AS remove_edits,
    SUM(len_added)      AS len_added,
    SUM(len_removed)    AS len_removed
FROM %s as edc
GROUP BY
    edc.rev_year,
    edc.rev_month,
    edc.namespace;
"""%(TIME_YEAR_MONTH_NAMESPACE,EDITOR_YEAR_MONTH_NAMESPACE)
"""Query to time centric table. For each year/month, it contains the number of editors, the number of add/remove edits as well as number bytes added/removed.
"""

CREATE_TIME_YEAR_MONTH_DAY_NAMESPACE = """
CREATE TABLE %s
SELECT /* SLOW_OK */ 
    edc.rev_year,
    edc.rev_month,
    edc.rev_day,
    edc.namespace,
    COUNT(edc.user_id)  AS editors,
    SUM(noop_edits)     AS noop_edits,
    SUM(add_edits)      AS add_edits,
    SUM(remove_edits)   AS remove_edits,
    SUM(len_added)      AS len_added,
    SUM(len_removed)    AS len_removed
FROM %s as edc
GROUP BY
    edc.rev_year,
    edc.rev_month,
    edc.rev_day,
    edc.namespace;
"""%(TIME_YEAR_MONTH_DAY_NAMESPACE,EDITOR_YEAR_MONTH_DAY_NAMESPACE)
"""Query to time centric table. Same as `TIME_YEAR_MONTH_NAMESPACE` but including namespace. For each year/month, it contains the number of editors, the number of add/remove edits as well as number bytes added/removed.
"""

