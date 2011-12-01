#!/bin/bash
# 
#  Usage:
#  ./runLanguages ja sv zh
# 

LANGUAGES="$@"
base=~/multiple_wp

mkdir -p $base
cd $base

for l in $LANGUAGES
do
	echo "[General]
language = "$l"
filterbots = True
startYM = 200401
endYM = 201106

[Directories]
cmapname = 'spectral'
basedirectory = "$base"
datadirectory = %(basedirectory)s/data
userlistdirectory = %(basedirectory)s/userlists
#reportdirectory = %(basedirectory)s/report
reportdirectory = ~/public_html/"$l"wp
wikipridedirectory = %(basedirectory)s/wikipride

[MySQL]
sqlhost = "$l"wiki-p.rrdb.toolserver.org
sqlwikidb = "$l"wiki_p
sqluserdb = u_declerambaul
sqlconfigfile = ~/.my.cnf
sqldroptables = False" > $l.config

python ~/WikiPride/wikipride.py -c $l.config preprocessing
python ~/WikiPride/wikipride.py -c $l.config data
python ~/WikiPride/wikipride.py -c $l.config report

done