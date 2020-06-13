# Using EA FIFA team rankings to predict football matches

I wanted to try and train a neural network to predict football matches in LaLiga (Spanish first league). So to do so I needed to scrape the FIFA team rankings from http://fifaindex.com (also possible from http://sofifa.com , I have attached to this repository a scraper I've built), and laliga results from the last years.

## The model

At first I thought I will just use as much data as possible to train the network but I believe it is really hard to asses teams across different leagues even for a company such as EA. To my belief, each of the five big leagues in europe are slightly different than the other. Also, teams from different leagues only play against each other in cup competitions or just friendly games after the season ends. Both cases, it is different than regular league.

## football data

I decided to use an api service of https://api-football.com .  Anyone who signs up for a free account can get up to 75 calls a day (maybe 50, not sure). Anyway I paid for the premium account so I can have more calls in case I decided to extend my project (which so far I haven't.. but I may). Anyway, for this kind of project , https://football-data.co.uk should be more than enough and maybe even better at the end because their datasets also store odds information which is very important when evaluating football models.

I did built a special package for the api-football service. It is available on my github and just need to insert api key for it to work. I tried to make it as easy as possible to use so in the future if I had any ideas of improving I could just load it and download the data.

I wrote a detailed explanation on how to use the package I wrote for the api-football. Everything is in the notebook file (Football Prediction.ipnyb) that I have uploaded to this repository. I also wrote a script that will scrape data from fifa-index. Explantaion with examples also available in the notebook.


I got the fixtures data from http://api-football.com and

I came across this article https://towardsdatascience.com/predicting-premier-league-odds-from-ea-player-bfdb52597392 and wanted to reproduce the results.

I encountered some problems with fifa players dataset that is available on kaggle so for now I decided to scrape myself team rankings (def, mid, att, overall) and see if a neural network predictions could be valuable. Later on I plan on adding more paremeters to each team and maybe building my own players dataset and using it in the same way as in the article above.

I've built two packages to make it easier for me handling the data on jupyter notebook. In the notebook I have uploaded here there's detailed explanation about each package and its methods.




```python

class Universe(api):

  def __init__(self):
    self.set = True

```

# Heading1
