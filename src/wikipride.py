'''
Main entry point into the wikipride framework
'''
import os
import argparse
import utils
import logging

import settings



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
		type=bool,
		default=None, 
		help='if True, all SQL tables will be dropped before being created',
	)

	parser.add_argument(
		'workstep',
		type=str, 
		choices=['all','data','report'],
		help="""the part of the workflow to be executed. all: data and report.
		data: aggregate the required MediaWiki SQL tables into a analytic-friendly format. 
		report: create a set of standard reports (data must have been run on the same language wiki before)."""
	)

	args = parser.parse_args()
	
	# read default config file
	# config = ConfigParser.ConfigParser()
	# config.read('default.config')

	# settings.readConfig(config)


	# read config passed as argument
	if args.config is not None:
		if os.path.isfile(args.config): 
			settings.readConfig(args.config)			
		else:
			logging.warning('Config file is not a File: %s'%args.config)

	if args.droptables is not None:
		settings.droptables = args.droptables
	
	if args.workstep == 'all':
		pass
	elif args.workstep == 'data':
		from data import preprocessing
		preprocessing.process()		
	elif args.workstep == 'report':	
		pass

	
	# for row in map(args.dump, args.processor.process, noop=args.noop, threads=args.threads):
	# 	print('\t'.join(encode(v) for v in row))

if __name__ == "__main__":
	main()