import pandas as pd 
import numpy as np
import re
import requests

class fifa():

	_df = pd.DataFrame()
	versions = ['players_16.csv','players_17.csv','players_18.csv','players_19.csv','players_20.csv']

	def __init__(self):
		self.__mergeVersions()


	@staticmethod
	def cleanData(df, v):
		data = df.iloc[:,0:10]
		ratings = df.loc[:,['sofifa_id','overall']]
		ratings = ratings.rename(columns={'overall':'overall_' + str(v)})
		return data, ratings


	def __mergeVersions(self):
		global_df = pd.DataFrame()
		global_rating = pd.DataFrame()
		for v in self.versions:
			temp_df, temp_rating = self.cleanData(pd.read_csv(v), re.findall('\d+', v)[0])
			if v != self.versions[0]:
				global_df = global_df.append(temp_df[~temp_df['sofifa_id'].isin(global_df['sofifa_id'])])
			else:
				global_df = temp_df
			global_df = pd.merge(global_df, temp_rating, left_on='sofifa_id', right_on='sofifa_id', how = 'left')
		self._df = global_df


	def toDict(self):
		fifa_dict = self._df.set_index('sofifa_id')
		return fifa_dict.to_dict(orient = 'index')

	def fifaDF(self):
		return self._df


class api():

	headers = {'x-rapidapi-key':'d2f0cce435mshe3d1fd9eac675dfp16e06fjsn8f7f976b50ea','x-rapidapi-host':'api-football-v1.p.rapidapi.com'}
	api_dict = {'leagues':'https://api-football-v1.p.rapidapi.com/v2/leagues/country/', 'teams':'https://api-football-v1.p.rapidapi.com/v2/teams/league/','lineups':'https://api-football-v1.p.rapidapi.com/v2/lineups/','squads':'https://api-football-v1.p.rapidapi.com/v2/players/squad/','league_fixtures':'https://api-football-v1.p.rapidapi.com/v2/fixtures/league/'}

	@staticmethod
	def checkStatus(response):
		if type(response) == requests.models.Response and response.status_code == '202' or '200':
			return True
		else:
			print("API error:",response.status_code)
			return False

	@staticmethod
	def checkResults(response, request_id):
		if response['api']['results'] == 0:
			print('No result for request:', request_id)
			return False
		return True

class SetUniverse(api):

	_fixtures = dict()

	def __init__(self):
		self._dict = dict()
		self._leagues_dict = dict()

	def addLeagues(self, country, season = None, keyword = None, neg_key = None):
		url = self.api_dict['leagues'] + str(country)
		if season:
			url = url + '/' + str(season)
		leagues = requests.get(url, headers = self.headers)
		if not self.checkStatus(leagues): # Validation
			return
		assert len(leagues.json()['api']['leagues']) != 0, 'No leagues found'
		leagues = leagues.json()['api']['leagues']
		print('The following leagues has been found and added:\n')
		for l in leagues:
			league_id = l['league_id']
			if league_id in self._leagues_dict:
				break
			league_name = l['name']
			league_season = l['season']
			season_start = l['season_start']
			season_end = l['season_end']
			country = l['country']
			string = str(league_id) + '\t' + country + '\t' + league_name + '\t' + str(league_season) + '\t' + season_start + '\t' + season_end
			if self.key(keyword, league_name) and self.key(neg_key, league_name, neg = True):
				temp = League(league_id, league_name, league_season, season_start, season_end, country)
				self._dict[league_id] = {'country':country,'league':league_name,'season':league_season,'start':season_start,'end':season_end}
				self._leagues_dict[league_id] = temp
				print(string)
			

	def LeaguesDF(self):
		return pd.DataFrame.from_dict(self._dict, orient = 'index')

	def removeLeague(self, *league_id):
		for i in league_id:
			del(self._dict[i])
			del(self._leagues_dict[i])

	def key(self, val, string, neg = False):
		if val == None:
			return True
		if neg and val not in string:
			return True
		if not neg and val in string:
			return True
		return False

	def addFixtures(self):
		for league in self._leagues_dict.keys():
			if not self._leagues_dict[league].has_matches:
				self._leagues_dict[league].retrieveFixtures()

	def FixturesDF(self):
		df = pd.DataFrame()
		for fix in self._fixtures.keys():
			df = df.append(self._fixtures[fix].df())
		df.columns = ['fix_id','league_id','home_team','away_team','home_score','away_score','season']
		df.set_index('fix_id', inplace = True)
		return df
		

	def fixtureDetail(self ,fixture_id):
		if fixture_id in self._fixtures:
			return self._fixtures[fixture_id].printFixture()



class League(SetUniverse):

	_fixtures_dict = dict()
	#_fixtures = dict()

	def __init__(self, league_id, desc, season, start, end, country):
		self.has_matches = False
		self.league_id = league_id
		self.desc = desc
		self.season = season
		self.start = start
		self.end = end
		self.country = country

	def getTeams(self):
		url = self.api_dict['teams'] + str(self.league_id)
		teams = requests.get(url, headers = self.headers)
		if not self.checkStatus(teams) or not self.checkResults(teams, 'retrieving teams'):
			return
		teams = teams.json()['api']['teams']

	def retrieveFixtures(self):
		url = self.api_dict['league_fixtures'] + str(self.league_id)
		fixtures = requests.get(url, headers = self.headers)
		if not self.checkStatus(fixtures):
			return
		fixtures = fixtures.json()['api']['fixtures']
		assert len(fixtures) != 0, ('No fixtures found for league: {%S}', self.league_id)
		self.has_matches = True
		for fix in fixtures:
			fix_id = fix['fixture_id']
			date = fix['event_date']
			venue = fix['venue']
			referee = fix['referee']
			home_id = fix['homeTeam']['team_id']
			home = fix['homeTeam']['team_name']
			away_id = fix['awayTeam']['team_id']
			away = fix['awayTeam']['team_name']
			home_score = fix['goalsHomeTeam']
			away_score = fix['goalsAwayTeam']
			ht_score = fix['score']['halftime']
			et = fix['score']['extratime']
			penalty = fix['score']['penalty']
			fixture = Fixture(self.league_id, self.country, self.season, fix_id, date, home_id, home, away_id, away, home_score, away_score, ht_score, et, penalty, referee, venue )
			self._fixtures[fix_id] = fixture
			self._fixtures_dict[fix_id] = {'league_id':self.league_id,'home_id':home_id,'home_team':home,'away_id':away_id,'away':away,'home_score':home_score,'away_score':away_score}
	
	def fixturesDf(self):
		return pd.DataFrame.from_dict(self._fixtures_dict, orient = 'index')

	def fixtureDetail(self, fix_id):
		return self._fixtures[fix_id].printFixture()

class Fixture(League):

	def __init__(self, league_id, country, season, fix_id, date, home_id, home, away_id, away, home_score, away_score, ht_score, et, penalty,referee, venue):
		self.league_id = league_id
		self.country = country
		self.season = season
		self.fix_id = fix_id
		self.date = date
		self.home_id = home_id
		self.home = home
		self.away_id = away_id
		self.away = away
		self.home_score = home_score
		self.away_score = away_score
		self.ht_score = ht_score
		self.et = et
		self.penalty = penalty
		self.referee = referee
		self.venue = venue

	def retrieveFixtureStats(self):
		pass

	def printFixture(self):
		fixture = {self.fix_id:{'league_id':self.league_id,'country':self.country,'season':self.season,'date':self.date,'home_id':self.home_id,'home': self.home,'away_id':self.away_id,'away':self.away,'home_score':self.home_score,'away_score':self.away_score,'ht_score':self.ht_score,'extra_time':self.et,'penalty':self.penalty,'referee':self.referee,'venue':self.venue}}
		return fixture 

	def df(self):
		return pd.DataFrame([[self.fix_id, self.league_id, self.home, self.away, self.home_score, self.away_score, self.season]])


