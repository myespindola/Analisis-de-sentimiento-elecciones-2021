from tweepy import Stream #API de twitter que nos permite obtener la informacion de twitter
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json 
import sqlite3#Es una base de datos SQL que viene integrada en Python
from unidecode import unidecode
import time
import re
import nltk
from textblob import TextBlob #Permite hacer analisis de sentimiento en texto
nltk.download('stopwords') #Stopwords


# Ingresamos las credenciales para la API de Twitter
ckey='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
csecret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
atoken='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
asecret='XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

# Establecemos la coneccion con la base de datos en SQLite
conn = sqlite3.connect('twitter.db')
c = conn.cursor()

# Creamos una tabla en la cual se almacenaran los tweets
def create_table():
    try:
        c.execute("CREATE TABLE IF NOT EXISTS sentiment(unix REAL, tweet TEXT,teewtlimpio TEXT, sentiment REAL)")
        c.execute("CREATE INDEX fast_unix ON sentiment(unix)")
        c.execute("CREATE INDEX fast_tweet ON sentiment(tweet)")
        c.execute("CREATE INDEX fast_sentiment ON sentiment(sentiment)")
        c.execute("CREATE INDEX fast_teewtlimpio ON sentiment(teewtlimpio)")
        conn.commit()
    except Exception as e:
        print(str(e))
create_table()

#Definimos funciones para eliminar palabras vacias y limpiar el texto
def quita_palabras_vacias(tweet):
    palabras_vacias = nltk.corpus.stopwords.words('spanish')
    letra_limpia = ' '.join([palabra for palabra in tweet.split(' ') if palabra not in palabras_vacias])
    return letra_limpia

def limpiar_tweet(tweet):
    tweet= re.sub(r"http\S+", "", tweet) #Elimina links
    tweet= re.sub(r"RT", "", tweet) #Elimina Retweets
    tweet= re.sub(r":", "", tweet) 
    tweet=tweet.lower() # Pasamos el texto a minuscula

    return tweet

#Creamos una clase la cual leera el streming de tweets y los ira almacenando en la base de datos
class listener(StreamListener):

    def on_data(self, data):
        try:
            data = json.loads(data)
            if "extended_tweet" in data: #Si el tweet es largo, obntenenmos el campo extended_tweet.full_text
                tweet = unidecode(data['extended_tweet']['full_text'])      
            elif ('retweeted_status' in data) and ('extended_tweet' in data["retweeted_status"]): #Si el tweet fue retwitteado, obtenemos el campo retweeted_status.extended_tweet.full_text
                tweet = unidecode(data["retweeted_status"]["extended_tweet"]['full_text'])
            else:
                if not data['text'].endswith('…'):
                    tweet = unidecode(data['text']) #Si es un tweet normal y esta completo, obtenemos solo el campo text
            
            tweet_limpio=limpiar_tweet(tweet) #Hacemos la limpieza
            tweet_limpio=quita_palabras_vacias(tweet)
            time_ms = data['timestamp_ms'] #Obtenemos la hora del tweet
            sentiment = TextBlob(tweet_limpio).translate(to='en').polarity #Obtenemos el sentimiento del tweet, para esto primero traducimos el tweet limpio a ingles
            print(time_ms, tweet,tweet_limpio, sentiment)
            c.execute("INSERT INTO sentiment (unix, tweet,teewtlimpio, sentiment) VALUES (?, ?, ?, ?)", #Cargamos esta informacion en la base de datos
                  (time_ms, tweet,tweet_limpio, sentiment))
            conn.commit()

        except KeyError as e: #En caso de error simplemente pasamos la excepcion
            print(str(e))
        return(True)

    def on_error(self, status): # En caso de un error lo catcheamos para evitar la sancion de twitter por exeder el limite de solicitud de accesos
        print(status)


while True: #Corremos el Twitter stream listener en un bucle

    try:
        auth = OAuthHandler(ckey, csecret)
        auth.set_access_token(atoken, asecret)
        twitterStream = Stream(auth, listener()) #Buscamos tweets que mencionen a alguno de los partidos, o algo relacionado con las elecciones de Mexico 2021
        twitterStream.filter(track=['Partido Morena','Partido PAN','Partido PRI','Partido Movimiento Ciudadano','Partido Partido Verde Rcologista','Partido PES','Partido Juntos Haremos Historia','Partido PRD','Partido PT','Elecciones2021Mx'], languages=["es"])

    except Exception as e:
        print(str(e))
        time.sleep(5)

# Este archivo de python lo corremos en una terminal, y lo dejamos en segundo plano
