#!/usr/bin/python
# -*- coding: utf-8; mode: python -*-

'''
Pablo Palomino Gomez
Aplicaciones Distribuidas en Internet
Universidad de Castilla-La Mancha
'''

from flask import Flask, request, redirect, url_for, flash, render_template
from flask_oauthlib.client import OAuth

app = Flask(__name__)
oauth = OAuth()
mySession=None
currentUser=None

app.secret_key = 'development'


twitter = oauth.remote_app('twitter',
    base_url='https://api.twitter.com/1.1/',
    request_token_url='https://api.twitter.com/oauth/request_token',
    access_token_url='https://api.twitter.com/oauth/access_token',
    authorize_url='https://api.twitter.com/oauth/authenticate',
    consumer_key='5oTLu98Ku6s2fuQBdz2RR27X6',
    consumer_secret='30NW13waVeERUdEZ6CsHYzcYcdHJ57l8J8AyBEvO4KxkAsHCFW'
)


# Obtener token para esta sesion
@twitter.tokengetter
def get_twitter_token(token=None):
    global mySession

    if mySession is not None:
        return mySession['oauth_token'], mySession['oauth_token_secret']


# Limpiar sesion anterior e incluir la nueva sesion
@app.before_request
def before_request():
    global mySession
    global currentUser

    currentUser = None
    if mySession is not None:
        currentUser = mySession


# Pagina principal
@app.route('/')
def index():
    global currentUser

    info = None
    tweets = []
    if currentUser is not None:
        resp = twitter.request('statuses/home_timeline.json')
        if resp.status == 200:
            info = resp.data
            for tweet in info:
                tweets.append(str(tweet['id'])+" - "+tweet['user']['name']+":  "+tweet['text'])
        else:
            flash('Imposible acceder a Twitter.')

    return render_template('index.html', user=currentUser, tweets=tweets)


# Get auth token (request)
@app.route('/login')
def login():
    callback_url=url_for('oauthorized', next=request.args.get('next'))
    return twitter.authorize(callback=callback_url or request.referrer or None)


# Eliminar sesion
@app.route('/logout')
def logout():
    global mySession

    mySession = None
    return redirect(url_for('index'))


# Callback
@app.route('/oauthorized')
def oauthorized():
    global mySession

    resp = twitter.authorized_response()
    if resp is None:
        flash('You denied the request to sign in.')
    else:
        mySession = resp
    return redirect(url_for('index'))




# Operaciones
@app.route('/deleteTweet', methods=['POST'])
def deleteTweet():
    global currentUser

    if currentUser is not None:
        tweetid = request.form['tweetID']
        resp = twitter.post('statuses/destroy/'+tweetid+'.json')
        if resp.status == 200:
            flash ('Tweet Deleted','success')
        else:
            flash ('An error has occurred. Not Deleted','success')
    else:
        flash ('You must be authenticate!', 'success')
    return redirect(url_for('index'))



@app.route('/retweet', methods=['POST'])
def retweet():
    global currentUser

    if currentUser is not None:
        tweetid = request.form['tweetID']
        resp = twitter.post('statuses/retweet/'+tweetid+'.json')
        if resp.status == 200:
            flash ('Tweet Retweeted','success')
        else:
            flash ('An error has occurred. Not Retweeted','success')
    else:
        flash ('You must be authenticate!', 'success')
    return redirect(url_for('index'))

@app.route('/favorite', methods=['POST'])
def favorite():
    global currentUser

    if currentUser is not None:
        tweetid = request.form['tweetID']
        resp = twitter.post('favorites/create.json', {'id': tweetid})
        if resp.status == 200:
            flash ('Tweet added to Favorites','success')
        else:
            flash ('An error has occurred. Not added to favorites','success')
    else:
        flash ('You must be authenticate!', 'success')
    return redirect(url_for('index'))


@app.route('/follow', methods=['POST'])
def follow():
    global currentUser

    if currentUser is not None:
        userid = request.form['userID']
        username = request.form['username']
        if len(userid) == 0:
            resp = twitter.post('friendships/create.json',{'screen_name': username})
        else:
            resp = twitter.post('friendships/create.json',{'user_id': userid})

        if resp.status == 200:
            flash ('User Followed', 'success')
        else:
            flash ('Not Followed. An error has occured', 'success')
    else:
        flash ('You must be authenticate!', 'success')
    return redirect(url_for('index'))



@app.route('/tweet', methods=['POST'])
def tweet():
    # Paso 1: Si no estoy logueado redirigir a pagina de /login
               # Usar currentUser y redirect
    global currentUser

    if currentUser is not None:
    # Paso 2: Obtener los datos a enviar
                       # Usar request (form)
        tweet = request.form['tweetText']
    # Paso 3: Construir el request a enviar con los datos del paso 2
   # Utilizar alguno de los metodos de la instancia twitter (post, request, get, ...)

        resp = twitter.post('statuses/update.json', {'status': tweet })
    # Paso 4: Comprobar que todo fue bien (no hubo errores) e informar al usuario
       # La anterior llamada devuelve el response, mirar el estado (status)
        if resp.status == 200:
            flash ('Tweet Published','success')
        else:
            flash ('An error has occurred. Not Published','success')
    else:
        flash ('You must be authenticate!', 'success')
    return redirect(url_for('index'))

    flash ('Tweet Published','success')
    # Paso 5: Redirigir a pagina principal (hecho)
    return redirect(url_for('index'))




if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=7000)
