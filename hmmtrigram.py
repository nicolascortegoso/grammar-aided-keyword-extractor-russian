import json

class MostProbableTagSequence:
	def __init__(self, transition_probabilities):
		with open(transition_probabilities) as json_file:
			self.data = json.load(json_file)

	def get_transition_probabilities(self, tag, previous_tag):
		try:
			probability = self.data[tag][previous_tag]
			return probability
		except:
			return 'Один из тегов имеет неправильную форму'

	def __pymorphy2_parse(self, pymorphy2_parse):
		sentence = []
		for token in pymorphy2_parse:
			token_info = [token, []]
			for i in token:
				lemma = i.normal_form
				score = i.score
				pos = i.tag.POS
				if pos is None:
					pos = i.tag._POS
				case = i.tag.case
				l = [lemma, score]
				if case is None:
					pos_case = pos
				else:
					pos_case = '{} {}'.format(pos, case)
				info = [lemma, score, str(pos_case), str(i.tag)]
				token_info[1].append(info)
			sentence.append(token_info)
		return sentence

	def __separate_punctuation_marks(self, sentence):
		sentence_without_punctuation_marks = []
		punctuation_marks_positions = {}
		for i, token in enumerate(sentence):
			if token[1][0][2] == 'PNCT':
				punctuation_marks_positions[i] = token
			else:
				sentence_without_punctuation_marks.append(token)
		return sentence_without_punctuation_marks, punctuation_marks_positions

	def get_sequence(self, pymorphy2_analysis):
		tagged_tokens = self.__pymorphy2_parse(pymorphy2_analysis)
		sentence_without_punctuation_marks, punctuation_marks_positions = self.__separate_punctuation_marks(tagged_tokens)
		error_in_desambiguation_process = False
		desambiguated_sentence = []
		token_counter = 1
		end_of_sentence = ['конец предложения', [['<E>',1, '<E>']]]
		sentence_without_punctuation_marks.append(end_of_sentence)
		previous_states = [{'<S>': [1, '<*>']}]
		for token in sentence_without_punctuation_marks:
			current_states = []
			dict_pos = {}
			token_counter += 1
			for pos in token[1]:
				t = pos[2]
				dict_pos[t] = [0, 'UNKN']
				for key,value in previous_states[-1].items():
					previous_state_prob = value[0]
					emission_prob = pos[1]
					u_v = '{}_{}'.format(value[1],key)
					transition_prob = self.data[t][u_v]
					probability = previous_state_prob * emission_prob * transition_prob
					if probability > dict_pos[t][0]:
						dict_pos[t][0] = probability
						dict_pos[t][1] = key
			previous_states.append(dict_pos)

		highest_score = '<E>'
		desambiguated_tag_list = []
		for i in previous_states[::-1]:
			try:
				highest_score = i[highest_score][1]
				desambiguated_tag_list.append(highest_score)
			except:
				pymorphy2_most_probable = []
				for token in tagged_tokens:
					pymorphy2_most_probable.append(token[0][0])
				return pymorphy2_most_probable
				#error_in_desambiguation_process = True

		desambiguated_tag_list_reversed = desambiguated_tag_list[::-1][2:]
		desambiguated_sentence = []
		punctuation_marks_counter = 0
		for i, token in enumerate(tagged_tokens):
			if i in punctuation_marks_positions.keys():
				punct_mark_list = (punctuation_marks_positions[i][0])#, punctuation_marks_positions[i][1], None, None, None)
				desambiguated_sentence.append(punct_mark_list[0])
				punctuation_marks_counter += 1
			else:
				desambiguated_pos = desambiguated_tag_list_reversed[i-punctuation_marks_counter]
				alternatives = tagged_tokens[i][1]
				for j, alternative in enumerate(alternatives):
					if alternative[2] == desambiguated_pos:
						desambiguated_sentence.append(tagged_tokens[i][0][j])
						break
		if error_in_desambiguation_process:
			return False
		else:
			return desambiguated_sentence
