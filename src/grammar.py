import argparse
from sets import Set
import random
import operator

grammar = {
	'Sentenca': [
		['Complemento', 'Sentenca_1'],
		['Sentenca_1'],
		['Sentenca_2'],
	],
	'Sentenca_1': [
		['Sujeito', 'Verbo_Transitivo_Temporal', 'Objeto'],
		['Objeto', 'Sujeito', 'Verbo_Transitivo_Temporal'],
		['Sujeito', 'Verbo_Intransitivo_Temporal'],
		['Verbo_Intransitivo_Temporal', 'Sujeito'],
	],
	'Sentenca_2': [
		['Sujeito', 'Verbo_Transitivo_Atemporal', 'Objeto'],
		['Objeto', 'Sujeito', 'Verbo_Transitivo_Atemporal'],
	],
	'Complemento': [
		['Hoje'],
		['Ontem'],
		['Amanha'],
		['Passado'],
		['Futuro'],
		['Segunda-feira'],
		['Terca-feira'],
		['Quarta-feira'],
		['Quinta-feira'],
		['Sexta-feira'],
		['Sabado'],
		['Domingo'],
	],
	'Sujeito': [
		['Eu'],
		['Voce'],
		['El@'],
		['Sujeito_1'],
		['Sujeito_1', 'Modificador_Sujeito'],
	],
	'Sujeito_1': [
		['Homem'],
		['Mulher'],
	],
	'Modificador_Sujeito': [
		['Velh@'],
		['Amig@'],
		['Filh@'],
		['Bonit@'],
		['Fei@'],
		['Legal'],
		['Gord@'],
		['Magr@'],
		['Alt@'],
		['Calm@'],
		['Crianca'],
	],
	'Verbo_Intransitivo_Temporal': [
		['Estudar'],
		['Trabalhar'],
		['Cantar'],
		['Dormir'],
		['Comemorar'],
		['Namorar'],
		['Acordar'],
		['Brincar'],
		['Cozinhar'],
		['Esperar'],
		['Chorar'],
		['Rir'],
		['Viajar'],
	],
	'Verbo_Transitivo_Temporal': [
		['Comprar'],
		['Vender'],
		['Encontrar'],
		['Mostrar'],
		['Procurar'],
		['Ganhar'],
	],
	'Verbo_Transitivo_Atemporal': [
		['Gostar'],
		['Gostar-Nao'],
		['Amar'],
		['Ter'],
	],
	'Objeto': [
		['Substantivo'],
		['Substantivo', 'Adjetivo'],
	],
	'Substantivo': [
		['Livro'],
		['Casa'],
		['Carro'],
		['Mochila'],
		['Televisao'],
		['Pedra'],
		['Trem'],
		['Barco'],
		['Computador'],
		['Celular'],
		['Chapeu'],
		['Tenis'],
		['Oculos'],
		['Relogio'],
		['Camisa'],
	],
	'Adjetivo': [
		['Vermelh@'],
		['Verde'],
		['Azul'],
		['Amarel@'],
		['Pret@'],
		['Branc@'],
		['Bonit@'],
		['Fei@']
	],
}

terminals = Set()
num_expansions = {}

def populate_terminals():
	terminals = Set()
	for key, val in grammar.iteritems():
		for word_list in val:
			for word in word_list:
				if word not in grammar:
					terminals.add(word)
	return terminals

def calc_expansions(term):
	if term in num_expansions:
		return num_expansions[term]
	if term in terminals:
		num_expansions[term] = 1
	else:
		num_exp = 0
		for sntc in grammar[term]:
			curr = 1
			for t in sntc:
				curr *= calc_expansions(t)
			num_exp += curr
		num_expansions[term] = num_exp
	return num_expansions[term]

def count_expansions():
	num_expansions = {}
	calc_expansions('Sentenca')

def analyze_stats(sentences):
	counts = {}
	for sentence in sentences:
		for element in sentence.split():
			if element not in counts:
				counts[element] = 1
			else:
				counts[element] += 1

	# print stats
	sorted_counts = sorted(counts.items(), key = operator.itemgetter(1))
	for key, val in sorted_counts:
		print "%5d %s" % (val, key)

def generate_random_sentence(print_sentence = True):
	sentence = ['Sentenca']
	idx = 0
	while idx < len(sentence):
		if sentence[idx] in terminals:
			idx += 1
		else:
			choices = grammar[sentence[idx]]
			choice = random.choice(choices)
			sentence = sentence[:idx] + choice + sentence[idx+1:]
	sentence = " ".join([word.upper() for word in sentence])
	if print_sentence:
		print sentence
	return sentence

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='Grammar utils')
	parser.add_argument('--print_atoms', action='store_true',
                      help='Print atoms of the grammar')
  	parser.add_argument('--num_sentences', type=int, default=0,
                      help='The number of random sentences to generate.')
  	parser.add_argument('--include_atoms', type=bool, default=False,
  					  help='Wheather to include atoms or not.')

	args = parser.parse_args()

	terminals = populate_terminals()
	
  	if args.print_atoms:
  		for terminal in sorted(terminals):
			print terminal
		print '-----------------'
		print 'There are', len(terminals), 'terminals'

	sentences = []
	for i in range(args.num_sentences):
		sentences.append(generate_random_sentence(False))

	offset = 0
	if args.include_atoms:
		for terminal in sorted(terminals):
			print "%d. %s" % (offset+1, terminal.upper())
			offset += 1

	for i in range(len(sentences)):
		print "%d. %s" % (i+offset+1, sentences[i])