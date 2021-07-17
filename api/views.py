from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response

class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer
    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guestCanPause = serializer.data.get('guestCanPause')
            votesToSkip = serializer.data.get('votesToSkip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guestCanPause = guestCanPause
                room.votesToSkip = votesToSkip
                self.request.session['roomCode'] = room.code
                room.save(update_fields=['guestCanPause','votesToSkip'])
            else:
                room = Room(host=host,guestCanPause=guestCanPause,votesToSkip=votesToSkip)
                room.save()
                self.request.session['roomCode'] = room.code

            return Response(RoomSerializer(room).data,status=status.HTTP_201_CREATED)
        return Response({"status":"Invalid"},status=status.HTTP_400_BAD_REQUEST)

class getRoom(APIView):
    serializer_class = RoomSerializer
    lookUpURL = 'code'
    def get(self,request,format=None):
        code = request.GET.get(self.lookUpURL)
        if code!=None:
            room = Room.objects.filter(code=code)
            if len(room)>0:
                data = RoomSerializer(room[0]).data
                data['isHost'] = self.request.session.session_key == room[0].host
                return Response(data,status=status.HTTP_200_OK)
            return Response({"status":"Invalid Code Room"},status=status.HTTP_404_NOT_FOUND)
        return Response({"status":"Code not found"},status=status.HTTP_404_NOT_FOUND)

class JoinRoom(APIView):
    def post(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        code = request.data.get("code")
        if code!=None:
            room = Room.objects.filter(code=code)
            if len(room)>0:
                self.request.session['roomCode'] = code
                return Response({"status":"Room Joined"},status=status.HTTP_200_OK)
            return Response({"status":"Invalid Code"},status=status.HTTP_404_NOT_FOUND)
        return Response({"status":"Failed to Join"},status=status.HTTP_404_NOT_FOUND)
class UserInRoom(APIView):
    def get(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        return JsonResponse({"code":self.request.session.get('roomCode')},status=status.HTTP_200_OK)
class LeaveRoom(APIView):
    def post(self,requst,format=None):
        if 'roomCode' in self.request.session:
            self.request.session.pop('roomCode')
            hostID = self.request.session.session_key
            room = Room.objects.filter(host=hostID)
            if len(room)>0:
                room=room[0]
                room.delete()
        return Response({"status":"Left Room"},status=status.HTTP_200_OK)

class UpdateView(APIView):
    serializer_class = UpdateRoomSerializer
    def patch(self,request,format=None):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guestCanPause = serializer.data.get("guestCanPause")
            votesToSkip = serializer.data.get("votesToSkip")
            code = serializer.data.get("code")
            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({"status":"Invalid Room"},status=status.HTTP_404_NOT_FOUND)
            room = queryset[0]
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response({"status":"Not Host"},status=status.HTTP_403_FORBIDDEN)
            room.guestCanPause = guestCanPause
            room.votesToSkip = votesToSkip
            room.save(update_fields=["guestCanPause","votesToSkip"])
            return Response(RoomSerializer(room).data,status=status.HTTP_200_OK)   
        return Response({"status":"Invalid data"},status=status.HTTP_400_BAD_REQUEST)    

