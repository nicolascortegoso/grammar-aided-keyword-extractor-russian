from kw_extractor import POStagger, Keywords

tagger = POStagger('transition_probabilities.json')
keywords = Keywords('rules.txt')

filename = '' # path to the text file to process

tagged_text, token_count = tagger.parse(filename)
results = keywords.extract(tagged_text,
									 token_count,
									  0.001,			# threshold that will filter for keywords with scores lower than the given value
									  1				# weight that is used to penalize or reward the score of the keywords based on their number of words  
									)
print(filename, results)
