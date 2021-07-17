from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from requests import post,put,get
from dotenv import load_dotenv
import os
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
BASE_URL = "https://api.spotify.com/v1/me/"

def get_user_tokens(session_id):
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens:
        return user_tokens[0]
    else:
        return None

def update_or_create_user_tokens(session_id,access_token,refresh_token,token_type,expires_in):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token','refresh_token','expires_in','token_type'])
    else:
        tokens = SpotifyToken(user=session_id,access_token=access_token,refresh_token=refresh_token,token_type=token_type,expires_in=expires_in)
        tokens.save()

def is_spotfy_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiredate = tokens.expires_in
        if expiredate <= timezone.now():
            renew_spotify_token(session_id)
        return True
    return False


def renew_spotify_token(session_id):
    refresh_token =  get_user_tokens(session_id).refresh_token
    response = post('https://accounts.spotify.com/api/token',data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': CLIENT_ID,
        'client_secret' : CLIENT_SECRET

    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    update_or_create_user_tokens(session_id,access_token,refresh_token,token_type,expires_in)

def execute_spotify_call(session_id,endpoint,songuri,post_=False,put_=False):
    tokens = get_user_tokens(session_id)
    if post_:
        post(BASE_URL+endpoint,headers = {"Content-Type":"application/json","Authorization":"Bearer "+tokens.access_token})
    if put_:
        put(BASE_URL+endpoint,headers = {"Content-Type":"application/json","Authorization":"Bearer "+tokens.access_token})
    response = get(BASE_URL+endpoint,{},headers = {"Content-Type":"application/json","Authorization":"Bearer "+tokens.access_token})
    if songuri!=None:
        post(BASE_URL+endpoint+songuri,headers = {"Content-Type":"application/json","Authorization":"Bearer "+tokens.access_token})
    try:
        return response.json()
    except:
        return {"Error":"Failed to send request"}

def play_song(session_id):
    return execute_spotify_call(session_id,"player/play",songuri=None,put_=True)

def pause_song(session_id):
    return execute_spotify_call(session_id,"player/pause",songuri=None,put_=True)

def skip_song(session_id):
    return execute_spotify_call(session_id,"player/next",songuri=None,post_=True)

def prev_song(session_id):
    return execute_spotify_call(session_id,"player/previous",songuri=None,post_=True)

def play_host_song(session_id,songuri):
    execute_spotify_call(session_id,"player/queue",songuri="?uri="+songuri,put_=True)
    return skip_song(session_id)


#add to queue then skip track