'''
Main entry point into the wikipride framework
'''

import os,io
import argparse

import utils
import settings

import logging
logger = logging.getLogger('WikiPride Main')


def main():
	parser = argparse.ArgumentParser(
		description="""WikiPride analytics framework. 
		"""
	)

	parser.add_argument(
		'-c', '--config',
		metavar="",
		type=str, 
		default=None,
		help='<path> to the config file'
	)
	parser.add_argument(
		'-l', '--language',
		metavar='',
		type=str, 
		help='the language of the wiki project to analyze',
	)
	parser.add_argument(
		'-d', '--droptables',
		metavar='',
		action='store_true',
        dest='droptables', 		
		help='if True, all SQL tables will be dropped before being created',
	)

	parser.add_argument(
		'workstep',
		type=str, 
		choices=['all','preprocessing','data','report'],
		help="""the part of the workflow to be executed. all: preprocessing, data and report. 
		preprocessing: aggregate mediawiki SQL tables into analytic-friendly auxialiary tables.
		data: compute the cohort analysis data (prerequisite: preprocessing workstep)
		report: create a set of standard reports (prerequisite: data workstep)."""
	)

	args = parser.parse_args()
	
	# read config passed as argument

	if os.path.isfile(args.config): 
		settings.readConfig(args.config)
	else:
		logger.warning('Invalid config file: %s'%args.config)
		return

	if args.droptables is not None:
		settings.droptables = args.droptables
	
	if args.workstep == 'all':
		from data import preprocessing
		from data import report
		preprocessing.process()
		report.processData()
		report.processReport()
	elif args.workstep == 'preprocessing':
		from data import preprocessing
		preprocessing.process()	
	elif args.workstep == 'data':
		from data import report
		report.processData()
	elif args.workstep == 'report':	
		from data import report
		report.processReport()	

	
if __name__ == "__main__":
	main()