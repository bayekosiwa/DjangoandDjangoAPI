from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
#above import no longer needed after User model was overridden
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, OverriddenUserCreationForm
# Create your views here.

# rooms = [
#     {'id':1, 'name':'Room1'},
#     {'id':2, 'name': 'Room2'},
#     {'id':3, 'name': 'Room3'}
# ]

def home(request):
    topics = Topic.objects.all()[0:5] #limit to 5
    q = request.GET.get('q') if request.GET.get('q')!= None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains = q) | Q(name__icontains = q) | Q(description__icontains = q))
    roomCount = rooms.count()
    #rooms.count works faster than python len()
    comments = Message.objects.filter(Q(room__topic__name__icontains=q))
    context={'rooms':rooms, 'topics':topics, 'roomCount':roomCount, 'comments':comments}
    return render(request, 'base/home.html', context)

def topics(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics=Topic.objects.filter(Q(name__icontains = q))
    context={'topics':topics}
    return render(request, 'base/topics.html', context)

def activity(request):
    comments = Message.objects.all()
    context={'comments':comments}
    return render(request, 'base/activity.html', context)

def profile(request,pk):
    user=User.objects.get(id=pk)
    rooms = user.room_set.all()
    comments = user.message_set.all()
    topics = Topic.objects.all()
    context={'user':user, 'rooms':rooms, 'comments':comments, 'topics':topics}
    return render(request, 'base/profile.html',context)

def room(request,pk):
    room = Room.objects.get(id=pk)
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room = i
    comments = room.message_set.all()
    # comments = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method=='POST':
        Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context={'room':room, 'comments':comments, 'participants':participants}        
    return render(request, 'base/room.html', context)

@login_required(login_url='/login')
def createRoom(request):
    form = RoomForm()
    topics=Topic.objects.all()
    if request.method == 'POST':
        # print(request.POST)
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            name=request.POST.get('name'),
            topic=topic,
            description=request.POST.get('description')
        )
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room=form.save(commit=False)
        #     room.host=request.user
        #     room.save()
        # if form.is_valid():
        #     form.save()      when host was allowed to be selected
        return redirect('home')

    context={'form':form,'topics':topics}
    return render(request, 'base/room_form.html', context)

def editRoom(request, pk):
    obj='edit'
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You can not do that')
    form = RoomForm(instance=room)
    if request.method=='POST':
        topic_name=request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save() 
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
        # how to return to url with /pk
    context = {'form':form, 'obj':obj, 'room':room}
    return render(request, 'base/room_form.html', context)

def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You can not do that')
    if request.method=='POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html' , {'obj':room})

def loginPage(request): #optional - replace username with email to present it more accurately as we are logging in with email now
    if request.user.is_authenticated:
        return redirect('home')
    page='login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, username=username, password=password)

        if user!=None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'username and password do not match')
    context={'page':page}
    return render(request, 'base/login.html', context)

def register(request):
    page='register'
    form = OverriddenUserCreationForm()
    context={'page':page, 'form':form}
    if request.method=='POST':
        form = OverriddenUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) #to freeze the credentials and clean them
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages(request, 'An error has occured')
    return render(request, 'base/login.html', context)

# @login_required(login_url='login') these two methods are as important as hiding the HTTP in templates 
# if request.user != user:           to prevent user from getting access by directly enter unauthorised urls
#         return HttpResponse('fuck off')

@login_required(login_url='login')
def editProfile(request,pk):
    user=User.objects.get(id=pk) 
    # or user = request.user
    if request.user != user:
        return HttpResponse('fuck off')
    form = UserForm(instance=user)
    # when we add instance in views, there is no need to add value in form fields in templates
    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES,instance=user) #request.FILES for image upload
        if form.is_valid():
            user = form.save(commit=False)
            user.username=user.username.lower()
            user.save()
            return redirect('profile', pk=user.id)
    context={'user':user, 'form':form}
    return render(request, 'base/edit-user.html', context)

def logoutPage(request):
    if request.method=='POST':
        logout(request)
        return redirect('home')
    return render(request, 'base/delete.html',)

# OR
# def logoutPage(request):
#     logout(request)
#     return redirect('home')

def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    room = message.room
    # if request.user != room.host:
    #     return HttpResponse('You can not do that')
    if request.method=='POST':
        message.delete()
        return redirect('room', pk=room.id)
    
# also we can add functionality to loop through all the messages if there is no single message left
# from a participant, so proceed to delete it from participants list

    return render(request, 'base/delete.html' , {'obj':message})

#request.user means the logged in user