import tweepy
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

from pymongo_get_database import get_database

def calcDifference(old, new):
  old = old.replace(",", ".")
  new = new.replace(",", ".")
  difference = float(new) - float(old)

  if (difference < 0):
    return '📈 {}%'.format(round(difference, 2))
  else:
    return '📉 +{}%'.format(round(difference, 2))

consumer_key = os.environ.get('consumer_key')
consumer_secret = os.environ.get('consumer_secret')
access_token = os.environ.get('access_token')
access_secret = os.environ.get('access_secret')

auth=tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_secret)
api=tweepy.API(auth)
while True:
  print('running task {}'.format(datetime.now()))
  URL = "https://resultados.tse.jus.br/oficial/ele2022/545/dados-simplificados/br/br-c0001-e000545-r.json"
  r = requests.get(url = URL)
  data = r.json()

  if (data['cand'][0]['n'] == "13"):
    lula_data = data['cand'][0]
    bolsonaro_data = data['cand'][1]
  else:
    lula_data = data['cand'][1]
    bolsonaro_data = data['cand'][0]

  dbname = get_database()
  collection_name = dbname["percentage"]
  item_details = collection_name.find_one({},{})

  stored_lula_percentage = item_details['candidate_1_percentage']
  stored_bolsonaro_percentage = item_details['candidate_2_percentage']

  if (stored_lula_percentage != lula_data['pvap'] or stored_bolsonaro_percentage != bolsonaro_data['pvap']):
    difference_candidate1 = calcDifference(str(stored_lula_percentage), lula_data['pvap'])
    difference_candidate2 = calcDifference(str(stored_bolsonaro_percentage), bolsonaro_data['pvap'])

    collection_name.update_one({'_id':"1"}, {"$set": {"candidate_1_percentage": lula_data['pvap'] }}, upsert=False)
    collection_name.update_one({'_id':"1"}, {"$set": {"candidate_2_percentage": bolsonaro_data['pvap'] }}, upsert=False)
    tweet_text='🔴🔴ATENÇÃO! Novo resultado parcial: \n \n {} 🔴 {}% ({}) \n {} 🟢 {}% ({}) \n \n Última atualização: {} {} \n Porcentagem atual apurada: {}%. \n \n #Eleições2022 #Parcial'.format(lula_data['nm'], lula_data['pvap'], difference_candidate1, bolsonaro_data['nm'], bolsonaro_data['pvap'],  difference_candidate2, data['dg'], data['hg'], data['pst'])
    api.update_status(tweet_text)
  time.sleep(30)
