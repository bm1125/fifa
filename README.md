# Using EA FIFA team rankings to predict football matches

I wanted to try and train a neural network to predict football matches in LaLiga (Spanish first league). So to do so I needed to scrape the FIFA team rankings from http://fifaindex.com (also possible from http://sofifa.com , I have attached to this repository a scraper I've built), and laliga results from the last years.

## general idea

At first I thought I will just use as much data as possible to train the network but I believe it is really hard to asses teams across different leagues even for a company such as EA. To my belief, each of the five big leagues in europe are slightly different than the other. Also, teams from different leagues only play against each other in cup competitions or just friendly games after the season ends. Both cases, it is different than regular league.

## football data

I decided to use an api service of https://api-football.com .  Anyone who signs up for a free account can get up to 75 calls a day (maybe 50, not sure). Anyway I paid for the premium account so I can have more calls in case I decided to extend my project (which so far I haven't.. but I may). Anyway, for this kind of project , https://football-data.co.uk should be more than enough and maybe even better at the end because their datasets also store odds information which is very important when evaluating football models.

I did built a special package for the api-football service. It is available on my github and just need to insert api key for it to work. I tried to make it as easy as possible to use so in the future if I had any ideas of improving I could just load it and download the data.

I wrote a detailed explanation on how to use the package I wrote for the api-football. Everything is in the notebook file (Football Prediction.ipnyb) that I have uploaded to this repository. I also wrote a script that will scrape data from fifa-index. Explantaion with examples also available in the notebook.

Following the instructions on the notebook will lead you to have the final dataframe as the following:

|fix_id |  result|	defense_h|	midfield_h|	attack_h|	overall_h|	defense_a|	midfield_a|	attack_a|	overall_a|
|-------|--------|---------|--------|	-------|--------|---------|--------|-------|--------|								
|9887|	0|	74|	75|	74|	75|	74|	75|	77|	75|
|9886|	0|	80|	80|	80|	80|	75|	74|	77|	75|
|9884|	1|	75|	76|	79|	75|	83|	82|	85|	83|
|9883|	1|	79|	80|	80|	79|	76|	78|79	|78|
|9882|	1|	78|	79|	81|	79|	75|	74|	75|	74|
|...||||||||||


# The model

I am not really familiar with neural networks algroithms. I know the basics of how neural networks works but actually traning a model is something I haven't done before and at first I felt blind actually trying to figure how many layers I should use, how many nodes and what parameters I should set. After a lot of trial and error I set the model as follows:

```python
def setModel(dropout, first_layer, second_layer):

    global model
    model = Sequential()
    n_features = X_train.shape[1]

    model.add(Dense(8, input_shape = (n_features,)))
    model.add(Dense(first_layer))
    model.add(Dropout(dropout))
    model.add(Dense(second_layer))
    model.add(Dense(3, activation = 'softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='Adam', metrics = ['accuracy'])

    #model.summary()
```

```python
def testModel(epochs, patience):
    early_stopping = keras.callbacks.EarlyStopping(monitor='accuracy', min_delta = 0, patience = patience)
    model.fit(X_train, y_train, verbose = 0, epochs = epochs, batch_size = 1, callbacks = [early_stopping])
    return model.evaluate(X_test, y_test)
```

I managed to get best result (accuracy) with 8 and 6 nodes, 0.5 dropout rate, 1000 epochs and setting early stopping to 15.

```python
setModel(0.5, 8,6)
testModel(1000, 15)

2/2 [==============================] - 0s 1ms/step - loss: 0.9124 - accuracy: 0.5957
```

# Results

Looking at the expected results one thing immediately pops out is the fact that the model never predict a draw! This is also a shotcoming of the classical poisson model that has been developed in 82.
It also seems to me that the model overestimate the home advantage. When there is equally skilled teams (ie alaves - athletic club or espanyol - valencia) I think the probabilities are a bit off.
Clearly, I'll have to think of new ways of training the model in order to predict draws better. 8/47 matches ended in draw. Also I'll have to find a way to adjust home advantage bias.

After comparing the predictions to pinnacle closing odds, I can say that this model also underestimate big teams (Barcelona, Real Madrid..) and giving them less chance than they actually has.


