from pymorphy2 import MorphAnalyzer
from hmmtrigram import MostProbableTagSequence
from nltk import word_tokenize


class POStagger:
	def __init__(self, file_name):
		self.morph = MorphAnalyzer()
		self.mps = MostProbableTagSequence(file_name)
		self.end_of_sentence_markers = ['.', '!', '?', '\n']

	def parse(self, file_name):
		with open(file_name, 'r', encoding='UTF-8') as reader:
			txt_file = reader.read()
		tokenized_text = word_tokenize(txt_file)
		sentences = self.__sentence_divider(tokenized_text)
		parsed_sentences = self.__morphoanalyzer(sentences)
		most_probable_tags_sequence = self.__get_most_probable_pos_tag_sequence(parsed_sentences)
		return most_probable_tags_sequence, len(tokenized_text)

	def __sentence_divider(self, tokenized_text):
		sentences = []
		current_sentence = []
		for token in tokenized_text:
			current_sentence.append(token)
			if token in self.end_of_sentence_markers:
				sentences.append(current_sentence)
				current_sentence = []
		return sentences

	def __morphoanalyzer(self, sentences):
		parsed_sentences = []
		for sentence in sentences:
			parsed_sentence = []
			for token in sentence:
				parsed = self.morph.parse(token)
				parsed_sentence.append(parsed)
			parsed_sentences.append(parsed_sentence)
		return parsed_sentences

	def __get_most_probable_pos_tag_sequence(self, parsed_sentences):
		most_probable_tags_sequences = []
		for sentence in parsed_sentences:
			most_probable_tags_seq = self.mps.get_sequence(sentence)
			most_probable_tags_sequences.append(most_probable_tags_seq)
		return most_probable_tags_sequences


class Keywords(object):
	def __init__(self, file_name):
		self.rules_dict = {}
		with open(file_name) as file:
			for row in file:
				if len(row) > 3 and '#' not in row:
					rule = self.__validate_form(row)
					rule.append('END')
					key = ''
					for i,j in enumerate(rule):
						if len(rule)-1 > i:
							key = '{} {}'.format(key, j).strip()
							if key not in self.rules_dict.keys():
								self.rules_dict[key] = []
							r = rule[i+1].strip()
							if r not in self.rules_dict[key]:
								self.rules_dict[key].append(r)

	def __validate_form(self, row):
		rule = row.strip().split(' ')[::-1]
		composed = ['NOUN', 'ADJF', 'PRTF', 'NPRO', 'NUMR']
		simple = ['ADJS', 'COMP', 'VERB', 'INFN', 'PRTS', 'GRND', 'ADVB', 'PRED', 'PREP', 'CONJ', 'PRCL', 'INTJ']
		number = ['sing', 'plur']
		case = ['nomn', 'gent', 'datv', 'accs', 'ablt', 'loct', 'voct', 'gen1', 'gen2', 'acc2', 'loc1', 'loc2']
		for term in rule:
			if '_' in term:
				tag = term.split('_')
				if (len(tag) != 3) or (tag[0] not in composed or tag[1] not in number or tag[2] not in case):
					raise Exception('Invalid tag in rules. Please check: ',term)
			else:
				if term not in simple:
					raise Exception('Invalid tag in rules. Please check: ',term)
		return rule

	def __format_key(self, token):
		composed_pos = ['NOUN', 'ADJF', 'PRTF', 'NPRO', 'NUMR']
		pos = token.tag._POS
		if pos in composed_pos:
			key = '{}_{}_{}'.format(pos, token.tag.number, token.tag.case)
		else:
			key = pos
		return key

	def extract(self, tagged_text, token_count, threshold=0.001, weight_for_chunks=1):
		lemmas_count = {}
		keywords_in_text = []
		keylemmas_in_text = []
		print('\n')
		for sentence in tagged_text:
			keywords_in_sentence = []
			keylemmas_in_sentence = []
			reversed_sentence = sentence[::-1]
			sentence_length = len(reversed_sentence)
			i = 0
			while i < sentence_length:
				key = self.__format_key(reversed_sentence[i])
				word = reversed_sentence[i].word
				lemma = reversed_sentence[i].normal_form
				if lemma not in lemmas_count.keys():
					lemmas_count[lemma] = 0
				lemmas_count[lemma] += 1
				if key in self.rules_dict.keys():
					c = 1
					while key in self.rules_dict.keys():
						value = self.rules_dict[key]
						if 'END' in value:
							keywords_in_sentence.append(word)
							keylemmas_in_sentence.append(lemma)
						if i+c < sentence_length:
							next = self.__format_key(reversed_sentence[i+c])
							if next in value:
								word = '{} {}'.format(reversed_sentence[i+c].word, word)
								lemma = '{} {}'.format(reversed_sentence[i+c].normal_form, lemma)
								key = '{} {}'.format(key, next)
							else:
								break
						else:
							break
						c += 1
				i += 1
			if len(keywords_in_sentence) > 0:
				keywords_in_text.append(keywords_in_sentence)
				keylemmas_in_text.append(keylemmas_in_sentence)

		results = self.__set_weights(keywords_in_text, keylemmas_in_text, lemmas_count, token_count, threshold, weight_for_chunks)
		return results

	def __set_weights(self, keywords_in_text, keylemmas_in_text, lemmas_count, token_count, threshold, weight_for_chunks):
		weighted_chunks = {}
		for i, sentence in enumerate(keywords_in_text):
			for j, chunk in enumerate(sentence):
				weighted_chunks[keywords_in_text[i][j]] = 0
				chunk_elements = chunk.split(' ')
				for element in chunk_elements:
					if element in lemmas_count.keys():
						weighted_chunks[keywords_in_text[i][j]] += lemmas_count[element]
		for k,v in weighted_chunks.items():
			n_keywords_in_chunk = len(k.split(' '))
			#weighted_chunks[k] = (v / token_count) * (n_keywords_in_chunk ** weight_for_chunks)
			weighted_chunks[k] = (v * (n_keywords_in_chunk ** weight_for_chunks)) / token_count

		new_dict = {}
		for k,v in weighted_chunks.items():
			if v > threshold:
				new_dict[k] = v
		sorted_dict = {r: new_dict[r] for r in sorted(new_dict, key=new_dict.get, reverse=True)}

		return sorted_dict
