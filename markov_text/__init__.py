from db import Db
from gen import Generator
from parse import Parser
from sql import Sql
from rnd import Rnd
import sqlite3

SENTENCE_SEPARATOR = '.'
WORD_SEPARATOR = ' '
DB_NAME = 'name'  #value here doesn't matter, only used in command line (markov.py script)

def MarkovGenerator(sentence_list, depth, db_filepath, db = None, rnd = None):
	"""Generator that generates new sentences from a list of sentences.
	Arguments:
		sentence_list		List of strings, each being a single sentence to learn from
		depth				Depth of analysis at which to build the Markov chain
		db_filepath			Path to file where sqlite database will be stored
		db (optional)		Db object (for mocking in unit tests)
		rnd (optional)		Rnd object (for mocking in unit tests)"""
	if not db:
		db = Db(sqlite3.connect(db_filepath), Sql())
		db.setup(depth)
	if not rnd:
		rnd = Rnd()

	parser = Parser(DB_NAME, db, SENTENCE_SEPARATOR).parse_list(sentence_list)
	generator = Generator(DB_NAME, db, rnd)
	while True:
		sentence = generator.generate(WORD_SEPARATOR).strip()
		if len(sentence) == 0:
			continue # avoid generating the empty string
		else:
			yield sentence
