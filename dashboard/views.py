from django.shortcuts import render, HttpResponse, HttpResponseRedirect
from dashboard.models import Hike, ImageSave, Favorite
from dashboard.forms import HikeForm
import json
# Create your views here.
def dashboard(request):
    return render(request, 'dashboard.html')

def feed(request):
    context = {}
    #Calculates hike stats and populates hike list
    hikes = Hike.objects.all()
    total_miles = 0
    total_elevation_gain=0
    total_elevation_loss=0
    name_filter = request.GET.get('search','')
    favoriteButton = request.GET.get('Favorites')
    count = Favorite.objects.all().count()
    if count == 0:
        favModel = Favorite.objects.create(fav = False) 
    else:
        favModel = Favorite.objects.get(id=1)
    favoriteBool = favModel.fav
    coords = []
    filtered_hikes = []
    for hike in hikes:
        hike.list_of_tags = hike.tag.split(", ")
        total_miles += abs(hike.miles)
        total_elevation_gain+= abs(hike.elevationGain)
        total_elevation_loss+= abs(hike.elevationLoss)
        if hike.name.lower().startswith(name_filter.lower(), 0, len(name_filter)) or name_filter in hike.list_of_tags:
            coords.append({'lat': hike.latitude, 'lng': hike.longitude, 'name': hike.name})
            filtered_hikes.append(hike)
        
        
    if favoriteButton == "Favorites":
        if not favoriteBool:
            for hike in hikes:
                if hike.starred == False:
                    filtered_hikes.remove(hike)
        if favoriteBool:
            filtered_hikes.clear()
            for hike in hikes:
                filtered_hikes.append(hike)
        favModel.fav = not favoriteBool
        favModel.save()
    context['favoriteButton'] = favoriteButton
    context['hikes'] = filtered_hikes
    context['num_hikes'] = len(hikes)
    context['average_miles'] = int(total_miles/context['num_hikes']) if context['num_hikes']>0 else 0
    context['average_elevation_gain'] = int(total_elevation_gain/context['num_hikes']) if context['num_hikes']>0 else 0
    context['average_elevation_loss'] = int(total_elevation_loss/context['num_hikes']) if context['num_hikes']>0 else 0
    context['total_miles'] = int(total_miles)
    context['total_elevation_gain'] = int(total_elevation_gain)
    context['total_elevation_loss'] = int(total_elevation_loss)
    context['coords'] = json.dumps(coords)
    context['name_filter'] = name_filter
    return render(request, 'feed.html' , context)

def addEntry(request):
    if(request.method == "POST"):
        form = HikeForm(request.POST, request.FILES)
        starredBool = False
        if request.POST.get("starred") == 'on':
            starredBool = True
        if(form.is_valid()):
            Hike.objects.createHike(request.POST.get("name"),
            request.POST.get("latitude"),
            request.POST.get("longitude"),
            request.POST.get("startDate"),
            request.POST.get("endDate"),
            request.POST.get("miles"),
            request.POST.get("elevationGain"),
            request.POST.get("elevationLoss"),
            request.POST.get("description"),
            starredBool,
            request.FILES['image1'],
            request.FILES['image2'],
            request.FILES['image3'],
            request.POST.get("tag")
            )
            return HttpResponseRedirect('/')
    else:
        form = HikeForm()
    return render(request, 'addEntry.html', {"form" : form})

def editEntry(request, id):
    selected_hike = Hike.objects.get(pk=id)
    if(request.method == "POST"):
        form = HikeForm(request.POST, request.FILES)
        starredBool = False
        if request.POST.get("starred") == 'on':
            starredBool = True
        if(form.is_valid()):
            Hike.objects.filter(pk=id).update(
                name= request.POST.get("name"),
                description= request.POST.get("description"),
                latitude= request.POST.get("latitude"),
                longitude= request.POST.get("longitude"),
                startDate= request.POST.get("startDate"),
                endDate= request.POST.get("endDate"),
                elevationGain= request.POST.get("elevationGain"),
                elevationLoss= request.POST.get("elevationLoss"),
                starred= starredBool,
                image1= request.FILES['image1'],
                image2= request.FILES['image2'],
                image3= request.FILES['image3'],
                tag=request.POST.get("tag")
            )

            addImage = ImageSave(image=request.FILES['image1'])
            addImage.save()
            addImage = ImageSave(image=request.FILES['image2'])
            addImage.save()
            addImage = ImageSave(image=request.FILES['image3'])
            addImage.save()
            return HttpResponseRedirect('/')
    else:
        form = HikeForm(
            initial={
                'name':selected_hike.name,
                'description':selected_hike.description,
                'miles': selected_hike.miles,
                'latitude': selected_hike.latitude, 
                'longitude':selected_hike.longitude, 
                'startDate': selected_hike.startDate,
                'endDate':selected_hike.endDate,
                'elevationGain':selected_hike.elevationGain,
                'elevationLoss':selected_hike.elevationLoss,
                'starred':selected_hike.starred,
                'image1':selected_hike.image1,
                'image2':selected_hike.image2,
                'image3':selected_hike.image3,
                'tag':selected_hike.tag})
    return render(request,'editEntry.html',{'hike':selected_hike, "form" : form})

def viewEntry(request,id):
    return render(request,'viewEntry.html',{'hike':Hike.objects.get(pk=id)})

def gallery(request):
    hikes = Hike.objects.all()
    return render(request,'gallery.html',{'hikes':hikes})

def deleteEntry(request,id):
    hike=Hike.objects.get(pk=id)
    hike.delete()
    return HttpResponseRedirect('/')

