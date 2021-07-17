from django.urls import path
from .views import RoomView,CreateRoomView,getRoom,JoinRoom,UserInRoom,LeaveRoom,UpdateView

urlpatterns = [

    path('room',RoomView.as_view()),
    path('create-room',CreateRoomView.as_view()),
    path('get-room',getRoom.as_view()),
    path('join-room',JoinRoom.as_view()),
    path('checkRoom',UserInRoom.as_view()),
    path('leaveroom',LeaveRoom.as_view()),
    path('updateroom',UpdateView.as_view())
]
