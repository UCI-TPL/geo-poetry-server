from db import Db
from gen import Generator
from parse import Parser
from sql import Sql
from rnd import Rnd
import sqlite3

SENTENCE_SEPARATOR = '.'
WORD_SEPARATOR = ' '
DB_NAME = 'name'  #value here doesn't matter, only used in command line (markov.py script)

def markov_gen(sentence_list, depth, db_filepath):
	"""Generator function that generates new sentences from a list of sentences.
	Arguments:
		sentence_list		List of strings, each being a single sentence to learn from
		depth				Depth of analysis at which to build the Markov chain
		db_filepath			Path to file where sqlite database will be stored"""
	db = Db(sqlite3.connect(db_filepath), Sql())
	db.setup(depth)

	parser = Parser(DB_NAME, db, SENTENCE_SEPARATOR).parse_list(sentence_list)
	generator = Generator(DB_NAME, db, Rnd())
	while True:
		yield generator.generate(WORD_SEPARATOR)
