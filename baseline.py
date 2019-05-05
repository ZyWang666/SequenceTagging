rare_model = input("enter the rare model(normal/improved) you want to evaluate:\n")
mode = input("enter the function(handle/evaluate) you want to run:\n")
class BaseLine:
	def parseData(self,fname):
		for l in open(fname, 'r'):
			yield l

	def handle_data(self, filename):
		data = list(self.parseData(filename))
		for d in data:
			d = d.rstrip().split(' ')
			if d[1] == 'WORDTAG':
				if d[2] == 'O':
					self.oTagCount += int(d[0])
				else:
					self.geneTagCount += int(d[0])
				self.myDic[d[2] + ' ' + d[3]] = int(d[0])
				if filename == 'gene.counts':
					if d[3] in self.wordsDic:
						self.wordsDic[d[3]] += int(d[0])
					else:
						self.wordsDic[d[3]] = int(d[0])
		if filename == 'gene.counts':
			self.wordsDic = [(k, int(self.wordsDic[k])) for k in sorted(self.wordsDic, key=self.wordsDic.get)]
			lowWords = []
			for p in self.wordsDic:
				if p[1] >= 5:
					break
				else:
					lowWords.append(p[0])
			self.replace(lowWords)

	def replace(self,lowWords):
		import os
		import sys
		import fileinput
		file = open('gene.train', 'r')
		temp = open('rare.train', 'w')
		count = 0
		for line in open('gene.train', 'r'):
			count += 1
			if len(line.split(' ')) != 2:
				if len(line.split(' ')) != 1:
					print(len(line.split(' ')))
				temp.write(line)
				continue
			textToSearch = line.split(' ')[0] 
			textToReplace = textToSearch
			if textToSearch in lowWords:
				if rare_model == 'normal':
					textToReplace = '_RARE_'
				elif rare_model == 'improved':
					textToReplace = self.checkWordType(textToSearch)
			temp.write(line.replace(textToSearch, textToReplace,1)) 
		temp.close()

	def checkWordType(self, word):
		#type1: has numbers 
		if self.hasNumbers(word):
			return 'ContainNumber'
		elif self.hasUppers(word):
			return 'ContainUpper'
		else:
			return '_RARE_'

	def hasNumbers(self,s):
 		return any(char.isdigit() for char in s)
	
	def hasUppers(self,s):
		return any(char.isupper() for char in s)

	def emission_para(self,x,y):
		num = 0
		denum = 0
		if y == 'O':
			denum = self.oTagCount
		else:
			denum = self.geneTagCount
		s = y + ' ' + x
		if 'O ' + x not in self.myDic and 'I-GENE '+ x not in self.myDic:
			if rare_model == 'normal':
				s = y + ' ' + '_RARE_'
			elif rare_model == 'improved':
				s = y + ' ' + self.checkWordType(x)
		if s in self.myDic:
			num = self.myDic[s]
		return float(num)/float(denum)

	def output(self):
		dev = open('gene.dev', 'r')
		res = open('gene_dev.p1.out', 'w')
		for w in dev:
			if w == '\n':
				res.write(w)
			else:
				w =  w.rstrip() 
				score1 = self.emission_para(w, 'O')
				score2 = self.emission_para(w, 'I-GENE')
				s = 'O'
				if score1 < score2:
					s = 'I-GENE'
				res.write(w + ' ' + s + '\n')
		res.close()

	def __init__(self):
		self.geneTagCount = 0
		self.oTagCount = 0
		self.myDic = {}
		self.wordsDic= {}

if rare_model != 'normal' and rare_model != 'improved':
	print("wrong input")
	exit()
if mode != 'handle' and mode != 'evaluate':
	print("Wrong input")
	exit()

import os
a = BaseLine()
if mode == 'handle':
	os.system('python count_freqs.py gene.train > gene.counts')
	print('modifying gene.train to rare.train...')
	a.handle_data('gene.counts')
	os.system("python count_freqs.py rare.train > rare.counts")

elif mode == 'evaluate':
	print('predicting words using rare.counts...')
	a.handle_data('rare.counts')
	a.output()
	os.system('python eval_gene_tagger.py gene.key gene_dev.p1.out')
