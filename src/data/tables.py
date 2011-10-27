"""This module holds the collection of SQL queries used for the preprocessing of the data
"""

import settings

USER_COHORT = "%s.%swiki_user_cohort"%(settings.sqluserdb,settings.language)
REV_LEN_CHANGED = "%s.%swiki_rev_len_changed"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH = "%s.%swiki_editor_centric_year_month"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH_NAMESPACE = "%s.%swiki_editor_centric_year_month_namespace"%(settings.sqluserdb,settings.language)
EDITOR_YEAR_MONTH_DAY_NAMESPACE = "%s.%swiki_editor_centric_year_month_day_namespace"%(settings.sqluserdb,settings.language)




CREATE_USER_COHORTS = """
CREATE TABLE IF NOT EXISTS %s
SELECT
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


INDEX_USER_COHORTS="""
CREATE INDEX user_id on %s (user_id);
CREATE INDEX user_title on %s (user_name_title);
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
CREATE INDEX compound on %s (user_id,rev_year,rev_month,rev_day,namespace);
"""%REV_LEN_CHANGED



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
