#!/usr/bin/env python
from random import randint
from vocab import *

# grammar:
#
# haiku := r1 r2 r3
#
# r1 := [adverb] [artref] adjective* noun
#
# r2 := [artref] adjective* noun
#     | artref noun verb [adverb_place] article [adjective] noun
#
# r3 := artref adjective* noun
# 	  | exclamation noun adverb
#
# adverb := adverb_place | adverb_time
#
# artref := article | referent

def pick(words, maxsyl=None, exclude=[]):
	if maxsyl is not None or len(exclude) > 1:
		words = [word for word in words if word not in exclude and nsyllables[word] <= maxsyl]
	if len(words) != 0:
		return words[randint(0, len(words) - 1)]

def pick_multiple(wordlists, maxsyl):
	minpossible = sum(min(nsyllables[word] for word in words) for words in wordlists)
	if minpossible > maxsyl:
		raise RuntimeError('cannot pick words with only %d syllables!' % maxsyl)
	
	picks = [pick(words) for words in wordlists]
	while syllables(picks) > maxsyl: # or len(set(picks)) != len(wordlists):
		picks = [pick(words) for words in wordlists]
	return picks
	
def syllables(line):
	return sum(nsyllables[word] for word in line)

def flipcoin():
	return randint(0, 1) == 1

def haiku():
	color1 = randint(0, 1)
	color2 = randint(0, 1)
	color3 = 1 - color1 if color1 == color2 else randint(0, 1)
	r1 = make_r1(color1)
	r2 = make_r2(color2)
	r3 = make_r3(color3)
	return ' '.join(r1) + '\n' + ' '.join(r2) + '\n' + ' '.join(r3)

def pick_if_fits(line, maxsyl, index, words):
	syl = syllables(line)
	if syl < maxsyl:
		word = pick(words, maxsyl - syl)
		if word is not None:
			line.insert(index, word)
			return True
	return False

def make_r1(color):
	try:
		line = [pick(nouns[color])]
		if randint(0, 9) < 8:
			pick_if_fits(line, 5, -1, adverbs_place + adverbs_time)
		if randint(0, 9) < 2:
			pick_if_fits(line, 5, -1, articles + referents)
		while syllables(line) < 5:
			assert pick_if_fits(line, 5, -1, adjectives[color])
		return line
	except AssertionError:
		return make_r1(color)

def make_r2(color):
	try:
		if flipcoin():
			line = [pick(nouns[color])]

			if randint(0, 9) < 2:
				pick_if_fits(line, 7, -1, articles + referents)

			while syllables(line) < 7:
				assert pick_if_fits(line, 7, -1, adjectives[color])

			return line
		else:
			# artref noun verb [adverb_place] article [adjective] noun
			artref = pick(articles + referents)
			article = pick(articles)
			space_left = 7 - syllables([artref, article])
			noun1, verb, noun2 = pick_multiple([nouns[color], verbs[color], nouns[color]], space_left)
			line = [artref, noun1, verb, article, noun2]
			if flipcoin():
				pick_if_fits(line, 7, 3, adverbs_place)
			while syllables(line) < 7:
				assert pick_if_fits(line, 7, -1, adjectives[color])
			return line
	except AssertionError:
		return make_r2(color)

def make_r3(color):
	try:
		if flipcoin():
			# artref adjective* noun
			line = [pick(articles + referents), pick(nouns[color])]
			while syllables(line) < 5:
				assert pick_if_fits(line, 5, -1, adjectives[color])
			return line
		else:
			# exclamation noun adverb
			line = pick_multiple([exclamations[color], nouns[color], verbs[color]], 5)
			while syllables(line) < 5:
				assert pick_if_fits(line, 5, -2, adjectives[color])
			return line
	except AssertionError:
		return make_r3(color)

if __name__ == '__main__':
	print haiku()