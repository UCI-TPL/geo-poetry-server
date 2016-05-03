import sys
import re

class Parser:
	SENTENCE_START_SYMBOL = '^'
	SENTENCE_END_SYMBOL = '$'

	def __init__(self, name, db, sentence_split_char = '\n'):
		self.name = name
		self.db   = db
		self.sentence_split_char = sentence_split_char
		# In addition to alphanumeric and underscore characters, ' and - are part of a word,
		#  but only if they don't occur at the beginning or end of a word.
		self.word_regex = re.compile("\\b[\\w'-/]+\\b")

	def parse(self, txt):
		sentences = txt.split(self.sentence_split_char)
		self.parse_list(sentences)

	def parse_list(self, sentences):
		depth = self.db.get_depth()
		i = 0

		for sentence in sentences:
			list_of_words = self.word_regex.findall(sentence)

			words = [Parser.SENTENCE_START_SYMBOL] * (depth - 1) + list_of_words + [Parser.SENTENCE_END_SYMBOL] * (depth - 1)
			
			for n in range(0, len(words) - depth + 1):
				self.db.add_word(words[n:n+depth])

			self.db.commit()
			i += 1
			if i % 1000 == 0:
				print i
				sys.stdout.flush()
