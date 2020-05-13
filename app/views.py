from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse,Http404
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from PIL import Image
import cv2
from CloudAndGridREC.recognize import recognize
from CloudAndGridREC.extract_embeddings import extract_embeddings
from CloudAndGridREC.train_model import train_model
import datetime
#from EmoPy.EmoPy.src.fermodel import FERModel
from .forms import LoginForm
from .models import Educator
import requests
import base64, numpy, json, io
from django.core.files.base import ContentFile
# Create your views here.


def empty_view(request):
    return HttpResponseRedirect('/login/')


def login_view(request):
    form = LoginForm(request.POST or None)
    print("Login form created", request.POST, form.is_valid())
    if request.POST and form.is_valid():
        user = form.login(request)
        if user:
            login(request, user)
            return render(request, 'app/main_page/client.html', {'username': user.username})
    return render(request, 'app/main_page/login.html', {'form': form})


def logout_view(request):
   logout(request)
   return HttpResponseRedirect('/login/')


@login_required(login_url='/login/', redirect_field_name='/make_recognition/')
def make_recognition(request):

    if request.method=="POST":
        dict = json.loads(request.body.decode('utf-8'))
        data = dict['image']
        #image = cv2.imread("./CloudAndGridREC/images/emcka.jpg")
        #image.save(response, "JPEG")

        format, imgstr = data.split(';base64,')
        file_bytes = base64.b64decode(imgstr)
        image = Image.open(io.BytesIO(file_bytes))
        print(image)
        image = cv2.cvtColor(numpy.array(image), cv2.COLOR_RGB2BGR)
        image = recognize(image)
        image = cv2.cvtColor(numpy.array(image), cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="JPEG")
        img_str = base64.b64encode(img_buffer.getvalue())

        from django.http import JsonResponse
        return JsonResponse({'image': img_str.decode('utf-8')})



@login_required(login_url='/login/', redirect_field_name='/extract_and_train/')
def extract_and_train(request):
    extract_embeddings()
    train_model()
    html = "<html><body>Extraction embeddings and training model done.</body></html>"
    return HttpResponse(html)


@login_required(login_url='/login/', redirect_field_name='/emotion_recognize/')
def emotion_recognize(request):
    image = cv2.imread("./CloudAndGridREC/images/emcka.jpg")
    target_emotions = ['calm', 'anger', 'happiness', 'surprise', 'disgust', 'fear', 'sadness']
    #model = FERModel(target_emotions, verbose=True)

    print('Predicting on happy image...')
    #image should be in BGR format
    #emotion = model.predict_from_ndarray(image)
    print('Prediction emtion ended')
    #html = "<html><body>Emotion is " + emotion + " </body></html>"
    html="hello"
    return HttpResponse(html)


@login_required(login_url='/login/', redirect_field_name='/start_accounting/')
def record(request):
    try:
        educator = Educator.objects.get(user=request.user)
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        link = 'https://timetable.spbu.ru/api/v1/educators/search/'+ str(request.user.last_name)
        response = requests.get(link).json()
        print(response)
        subjects = []
        for e in response['Educators']:
            if e['FullName'] == (str(request.user.last_name) + " " + str(request.user.first_name) + " " + str(educator.middle_name)):
                link = 'https://timetable.spbu.ru/api/v1/educators/'+ str( e['Id']) + '/events/2020-03-02/2020-03-03'
                response = requests.get(link).json()
                for EducatorEvents in response['EducatorEventsDays']:
                    for dayEvent in EducatorEvents['DayStudyEvents']:
                        subjects.append(dayEvent['Subject'])
        return render(request, 'app/main_page/subjects_page.html', {'subjects':subjects, 'username': request.user.username})
    except Educator.DoesNotExist:
        raise Http404("You are student and doesnt have such abilities")


def rec(request):
    return render(request, "app/main_page/record_page.html")


