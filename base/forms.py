from django.forms import ModelForm
from .models import Room, User
from django.contrib.auth.forms import UserCreationForm #needed to use this after User model was overridden

#this class was made after User model was overridden
class OverriddenUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'bio'] #it works even if we don't add 'password1' and 'password2' fields

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants']
        # fields = ['name', 'description']

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'bio', 'avatar']