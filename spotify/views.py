from django.shortcuts import render,redirect
from rest_framework.views import APIView
from requests import Request,post
from rest_framework import status
from rest_framework.response import Response
from .utils import *
from api.models import Room
from .models import Vote,PrevVote
from dotenv import load_dotenv
import os
import json
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
class AuthURL(APIView):
    def get(self,request,format=None):
        url = Request('GET','https://accounts.spotify.com/authorize',params={
            'scope': "user-read-playback-state user-modify-playback-state user-read-currently-playing",
            'response_type': 'code',
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url
        
        return Response({'url':url},status=status.HTTP_200_OK)

def spotify_callback(request,format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')
    response = post('https://accounts.spotify.com/api/token',data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()
    access_token = response.get('access_token')
    refresh_token = response.get('refresh_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    error = response.get('error')
    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create_user_tokens(request.session.session_key,access_token,refresh_token,token_type,expires_in)
    return redirect('frontend:')

class IsAuthenticated(APIView):
    def get(self,request,format=None):
       isAuth =  is_spotfy_authenticated(self.request.session.session_key)
       return Response({"status":isAuth},status=status.HTTP_200_OK)


class CurrentSong(APIView):
    def get(self,request,format=None):
        room_code = self.request.session.get("roomCode")
        room = Room.objects.filter(code =room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({},status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_call(host,endpoint,songuri=None)
        if 'error' in response or 'item' not in response:
            return Response({"status":"No song"},status=status.HTTP_204_NO_CONTENT)
        item = response.get("item")
        duration = item.get("duration_ms")
        progress = response.get("progress_ms")
        album_cover = item.get("album").get("images")[0].get("url")
        currently_playing = response.get("is_playing")
        song_id = item.get("id")
        artist_string = ""
        uri = item.get("uri")
        for i,artist in enumerate(item.get("artists")):
            if i> 0:
                artist_string += ", "
            artist_string += artist.get("name")
        votes = len(Vote.objects.filter(room=room,song_id=song_id))
        prevVote = len(PrevVote.objects.filter(room=room,song_id=song_id))
        ishost = host == self.request.session.session_key
        song = {"title":item.get("name"),"artist":artist_string,"duration":duration,"progress":progress,"image":album_cover,"current":currently_playing,"id":song_id,"votes":votes,"required_to_skip":room.votesToSkip,"prev_votes":prevVote,"uri":uri,"ishost":ishost}
        self.updateRoomSong(room,song_id)
        return Response(song,status=status.HTTP_200_OK)
    def updateRoomSong(self,room,song_id):
        current_song = room.current_song
        if current_song != song_id:
            response = execute_spotify_call(self.request.session.session_key,"/player/play",songuri=None)
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            vote = Vote.objects.filter(room=room).delete()
            prevvote = PrevVote.objects.filter(room=room).delete()

class PauseSong(APIView):
    def put(self,request,format=None):
        room_code = self.request.session.get('roomCode')
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key==room.host or room.guestCanPause:
            pause_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)
class PlaySong(APIView):
    def put(self,request,format=None):
        room_code = self.request.session.get('roomCode')
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key==room.host or room.guestCanPause:
            play_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)

class SkipSong(APIView):
    def post(self,request,format=None):
        room_code = self.request.session.get("roomCode")
        room = Room.objects.filter(code=room_code)[0]
        votes = Vote.objects.filter(room=room,song_id=room.current_song)
        votes_needed = room.votesToSkip
        if self.request.session.session_key == room.host or len(votes)+1 >= votes_needed:
            votes.delete()
            skip_song(room.host)
        else:
            vote = Vote(user = self.request.session.session_key, room=room, song_id=room.current_song)
            vote.save()
        return Response({},status=status.HTTP_204_NO_CONTENT)

class PrevSong(APIView):
    def post(self,request,format=None):
        room_code = self.request.session.get("roomCode")
        room = Room.objects.filter(code=room_code)[0]
        votes = PrevVote.objects.filter(room=room,song_id=room.current_song)
        votes_needed = room.votesToSkip
        if self.request.session.session_key == room.host or len(votes)+1 >= votes_needed:
            votes.delete()
            prev_song(room.host)
        else:
            vote = PrevVote(user = self.request.session.session_key, room=room, song_id=room.current_song)
            vote.save()
        return Response({},status=status.HTTP_204_NO_CONTENT)


class UserSong(APIView):
    def post(self,request,format=None):
        room_code = self.request.session.get("roomCode")
        #uri = request.get("uri")
        body = request.body.decode('utf-8')
        body = json.loads(body)
        uri = body['songuri']
        room = Room.objects.filter(code=room_code)[0]
        if self.request.session.session_key != room.host:
            play_host_song(self.request.session.session_key,uri)
            return Response({},status=status.HTTP_204_NO_CONTENT)



