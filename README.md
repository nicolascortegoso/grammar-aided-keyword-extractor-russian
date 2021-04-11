# grammar-aided-keyword-extractor-russian
A grammar-aided keyword extractor for Russian

1. Introduction
The extraction algorithm relies on what the user defines based on empirical, methodological or theoretical evidence as suitable grammatical patterns to find keywords. Patterns are indicated as a sequence of part-of-speech (POS) tags in a grammar.
Since the extracting algorithm searches the text for user-defined POS sequences, it requires a prior morphological analysis. Words are parsed using pymorphy2 and disambiguated by an algorithm that provides the most probable sequence of tags in the context of the sentence. 
The extracted keywords are n-grams that meet what the user defined as a valid POS tag sequence in the grammar. The keywords are ranked and sorted in descending order of their scores.

2. The grammar
The grammar is provided externally as a separate txt file. Each line in the file must describe only one pattern of n POS tags (one pattern per line). Empty and commented lines are completely ignored (comments are entered with the "#" character) and the tags are verified to conform to the format described in the rest of this section.
Since the extracting algorithm is build on the top of the morphological analysis of pymorphy2, its nomenclature is used unchanged.

Part-of-speech tags: 
    • 'NOUN': noun
    • 'ADJF': full adjective
    • 'ADJS': short adjective
    • 'COMP: comparative
    • 'VERB': verb (personal form)
    • 'INFN': verb (infinitive)
    • 'PRTF': full participle
    • 'PRTS': short participle
    • 'GRND': adverb
    • 'NUMR': numeral
    • 'ADVB': adverb
    • 'NPRO': pronoun-noun
    • 'PRED': predicative
    • 'PREP': preposition
    • 'CONJ': conjunction
    • 'PRCL': particle
    • 'INTJ': interjection

Number:
    • 'sing': singular
    • 'plur': plural

Cases:
    • 'nomn': nominative
    • 'gent': genitive
    • 'datv': dative case
    • 'accs': accusative case
    • 'ablt': instrumental
    • 'loct': prepositional case
    • 'voct': vocative case
    • 'gen1': first genitive
    • 'gen2': second genitive (partitive case)
    • 'acc2': second accusative
    • 'loc1': first prepositional case
    • 'loc2': second prepositional (locative case)

In principle, part-of-speech tags can be combined in any order, although, of course, ungrammatical sequences are less likely to be found in texts. For words classes with case declensions (nouns, full adjectives and participles, pronouns and numerals) it is mandatory to indicate number and case after the corresponding part-of-speech (in that order) separated by the symbol “_”. For example, a singular noun in the nominative case:

NOUN_sing_nomn

If the tag in the grammar does not strictly follow this format, it will be considered invalid and the code will throw and exception. The rest of the word classes that do not take case declensions are referenced only by the part-of-speech. For example:

PREP

Each sequence of tags must be expressed, on the same line, in the intended order and with the tags separated by a space. For example, the sequence of a preposition followed by an singular adjective and a singular noun, both in the locational case, has the following format:

PRED ADJF_sing_loct NOUN_sing_loct

Example grammar:
```
NOUN_sing_nomn
ADJF_sing_nomn NOUN_sing_nomn
PRED ADJF_sing_loct NOUN_sing_loct NOUN_sing_gent
```

Where the first line defines as possible candidate for a keyword a singular noun in the nominative case; the second a singular noun in the nominative case preceded by and adjective with the same number and case; and the third line a singular adjective and a noun in the locative case, introduced by a preposition and followed by a singular noun in the negative case.

3. The metric
The extracted candidate keywords are ranked according to a metric that takes into account the length of the n-gram and the number of times that the lemmatized forms of the words that make up the keyword appear in the text:

score(k) = (c(l) len(k)^w) / c(t)

where:
c(l) is the sum of all the frequencies in the text for the lemmatized forms of the words that make up the keyword;
len(k) is the number of elements (words) that the keyword contains. For single-word keywords, the value is 1. For n-word keywords, the value is n.
w is a value the user passes as an argument. It is intended to have an impact on the length of the keywords. Keywords with more than one word tend to obtain higher scores than unigrams. When the weight is a positive value less than 1, it will smooth the difference in scores between keywords of different lengths. A weight with a positive value greater than 1, will increase the scores of the keywords based on their length. Conversely, a negative number weight will penalize keywords accordingly to their length. A weight of 1 or 0 will have no effect.
c (t) is the number of tokens that the text contains. It's just a normalization value, so keywords get proportional scores regardless of the length of their source texts.

4. Implementation example
The script requires python3 and pymorphy2 to be installed. The  disambiguation process after the morphological parsing is based on the probabilities in the file “transition_probabilities.json”, so this is also a requirement. The user must provide the algorithm with the file that contains the grammar, written according to the formatting rules described in section 2.

Example code:
```
from kw_extractor import POStagger, Keywords #1
tagger = POStagger('trainstion_probabilities.json') #2
keywords = Keywords('rules.txt') #3
filename = 'text.txt' #4
tagged_text, token_count = tagger.parse(filename) #5
keywords.extract(tagged_text, token_count, 0.01, 0.4) #6
```
where:
#1 imports the classes “POStagger” and “Keywords” from the file “kw_extractor.py”;
#2 the object “tagger” is initialized from the class “POStagger” with the file that contains the transition probabilities as argument;
#3 the object “keywords” is initialized from the class “Keywords” with the txt file that contains the grammar as argument;
#4 path to the text file to process
#5 the “parse” method of the object “tagger” takes the text to process as input and returns the tagged text and the number of tokens it contains.
#6 the “extract” method of the object “keywords” takes 4 arguments. The first argument is the tagged text and the second one, the number of tokens that text has. These two arguments are mandatory. The third argument is a threshold that will filter for keywords with scores lower than the given value. By default, this value is set to “0.001”. The fourth and last argument is the weight that is used to penalize or reward the score of the keywords based on their number of words. By default, the number is set to 1 (no effect).


5. References
Korobov M. (2015), Morphological Analyzer for Russian and Ukrainian Languages. In: Analysis of Images, Social Networks and Texts, pp 320-332.

