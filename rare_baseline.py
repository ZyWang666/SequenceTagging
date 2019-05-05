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
				textToReplace = '_RARE_'
			temp.write(line.replace(textToSearch, textToReplace,1)) 
		print("count: ", count)
		temp.close()

	def emission_para(self,x,y):
		num = 0
		denum = 0
		if y == 'O':
			denum = self.oTagCount
		else:
			denum = self.geneTagCount
		s = y + ' ' + x
		if 'O ' + x not in self.myDic and 'I-GENE '+ x not in self.myDic:
			s = y + ' ' + '_RARE_'
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

a = BaseLine()
print('start modifying rare words...')
a.handle_data('gene.counts')
import os
print('starting predicting words...')
os.system("python count_freqs.py rare.train > rare.counts")
a.handle_data('rare.counts')
a.output()
os.system('python eval_gene_tagger.py gene.key gene_dev.p1.out')