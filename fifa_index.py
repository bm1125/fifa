from bs4 import BeautifulSoup
import pandas as pd
import requests

import unicodedata

class fifaIndex():

	
	global_link = 'https://www.fifaindex.com/teams/'
	_leagues = list()

	def __init__(self):
		self._versions = list()
		self.links = []
		self.teams = dict()

	def setVersions(self, *versions):
		self._versions = versions

	def mergeTeams(self, *args):
		for pair in args:
			assert len(pair) == 2, 'No pair given'
			self.teams[pair[0]].update(self.teams[pair[1]])
			del self.teams[pair[1]]

	def possibleDuplicates(self):
		l = list()
		for x in self.teams.keys():
			if len(self.teams[x]) != len(self._versions):
				l.append(x)
		return sorted(tuple(l))

	def __main(self, *versions):
		for v in versions:
			if len(str(v)) != 2:
				return
			temp = self.global_link + '/'+ str(v)
			self.links.append(temp)
		
	def getAvailableLeagues(self):
		l_list = list()
		html = requests.get('https://www.fifaindex.com/teams/fifa20/')
		page = BeautifulSoup(html.content, 'html.parser')

		leagues = page.find('select', attrs = {'name':'league', 'class':'form-control'})
		leagues = leagues.find_all('option')
		for league in leagues:
			l_list.append((league['value'], league.text))
		return l_list	

	def __scrapePage(self, page, version):
		page = BeautifulSoup(page.content, 'html.parser')
		main = page.find('div', class_='col-lg-8')
		main = main.find('tbody')
		teams = main.find_all('tr')
		for team in teams:
			league = team.find('td', attrs = {'data-title':'League'})
			name = team.find('td', attrs = {'data-title':'Name'})
			attack = team.find('td', attrs = {'data-title':'ATT'})
			midfield = team.find('td', attrs = {'data-title':'MID'})
			defense = team.find('td', attrs = {'data-title':'DEF'})
			overall = team.find('td', attrs = {'data-title':'OVR'})
			if name:
				output = {'defense':defense.text,'midfield':midfield.text,'attack':attack.text,'overall':overall.text}
				name = unicodedata.normalize('NFKD',name.text).encode('ascii','ignore').decode("utf-8")
				if name not in self.teams:
					self.teams[name] = {version:output}
				else:
					self.teams[name][version] = output


	def scrapeLeagues(self, *leagues):
		if not self._versions:
			print("Select fifa versions first")
			return
		for v in self._versions:
			link = 'https://www.fifaindex.com/teams/fifa' + str(v) + '/?'
			for x in leagues:
				link = link + 'league=' + str(x) + '&'
			self.__pagination(link, 1, v)

	def __pagination(self, link, page , v):
		temp_link = link[0:39] + str(page) + '/' + link[39:]
		main = requests.get(temp_link)
		if main.status_code == 200:
			print('scraping:\t',temp_link)
			self.__scrapePage(main , v)
			self.__pagination(link, page+1, v)

	def dataframe(self):
		if not self.teams:
			return
		return pd.DataFrame.from_dict({(i,j): self.teams[i][j] for i in self.teams.keys() for j in self.teams[i].keys()}, orient = 'index')


fifa = fifaIndex()
fifa.setVersions(17)
fifa.scrapeLeagues(13)

