from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd 
import re

#MAKING CSV FILE
with open('fifateamratings.csv', 'w') as csv:
	csv.write("league, team, overall, attack, midfield, defense, year\n")

#SELENIUM DRIVER
driver = webdriver.Chrome("/usr/local/bin/chromedriver")

def scrapeTeams(link, year):

	if 'https://sofifa.com' not in link:
		link = 'https://sofifa.com' + link
	driver.get(link)
	content = driver.page_source
	soup = BeautifulSoup(content, 'lxml')

	tbody = soup.find('tbody')
	tr = tbody.find_all('tr')
	next_page = soup.find('div', class_='pagination')
	pagination_text = next_page.find('span', class_='bp3-button-text')

	with open('fifateamratings.csv', 'a') as csv:
		for team in tr:
			name = team.find('td', class_ = 'col-name-wide')
			overall = team.find('td', attrs= {'data-col':'oa'}).text
			attack = team.find('td', attrs = {'data-col':'at'}).text
			mid = team.find('td', attrs={'data-col':'md'}).text
			df = team.find('td', attrs={'data-col':'df'}).text
			team = name.find_all('div', class_='bp3-text-overflow-ellipsis') #IMPORT TEAM NAME AND LEAGEU
			team_name = team[0].text
			league = team[1].text
			league = re.sub('\s\(\d+\)', '', league)
			string = str(league[1:] + ',' + team_name + ',' + overall + ',' + attack + ',' + mid + ',' + df + ',' + str(year) + '\n')
			csv.write(string)

	if next_page is not None and pagination_text.text == 'Next':
		scrapeTeams(str(next_page.a['href']), year)


#Different years has different address
scrapeTeams('/teams?type=all&lg%5B%5D=13&lg%5B%5D=16&lg%5B%5D=19&lg%5B%5D=31&lg%5B%5D=53', 2020)
scrapeTeams('/teams?type=all&lg%5B%5D=13&lg%5B%5D=16&lg%5B%5D=19&lg%5B%5D=31&lg%5B%5D=53&r=190075&set=true', 2019)
