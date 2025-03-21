from django.shortcuts import render
# from django.contrib.auth.hashers import make_password
def index(request):
    return render(request, 'users/index.html')
def register(request):
    # hashed_password = make_password(password)
    # user = User.objects.create(username=username, password=hashed_password)
    return render(request, 'users/register.html')