from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
#from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import AlbumForm, ImagesForm, UserForm
from .models import Album, Images

IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def create_album(request):
    if not request.user.is_authenticated():
        return render(request, 'images/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'images/create_album.html', context)
            album.save()
            return render(request, 'images/detail.html', {'album': album})
        context = {
            "form": form,
        }
        return render(request, 'images/create_album.html', context)


def create_image(request, album_id):
    form = ImagesForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        albums_images = album.image_set.all()
        for s in albums_images:
            if s.image_title == form.cleaned_data.get("image_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that image',
                }
                return render(request, 'images/create_image.html', context)
        image = form.save(commit=False)
        image.album = album
        image.image_file = request.FILES['image_file']
        file_type = image.image_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in IMAGE_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Image file must be PNG, JPG, or JPEG',
            }
            return render(request, 'images/create_image.html', context)

        image.save()
        return render(request, 'images/detail.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'images/create_image.html', context)


def delete_album(request, album_id):
    album = Album.objects.get(pk=album_id)
    album.delete()
    albums = Album.objects.filter(user=request.user)
    return render(request, 'images/index.html', {'albums': albums})


def delete_image(request, album_id, image_id):
    album = get_object_or_404(Album, pk=album_id)
    image = Images.objects.get(pk=image_id)
    image.delete()
    return render(request, 'images/detail.html', {'album': album})


def detail(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'images/login.html')
    else:
        user = request.user
        album = get_object_or_404(Album, pk=album_id)
        return render(request, 'images/detail.html', {'album': album, 'user': user})


def favorite(request, image_id):
    image = get_object_or_404(Images, pk=image_id)
    try:
        if image.is_favorite:
            image.is_favorite = False
        else:
            image.is_favorite = True
        image.save()
    except (KeyError, Images.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except (KeyError, Album.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'images/login.html')
    else:
        albums = Album.objects.filter(user=request.user)
        image_results = Images.objects.all()
        query = request.GET.get("q")
        if query:
            albums = albums.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            image_results = image_results.filter(
                Q(image_title__icontains=query)
            ).distinct()
            return render(request, 'images/index.html', {
                'albums': albums,
                'images': image_results,
            })
        else:
            return render(request, 'images/index.html', {'albums': albums})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'images/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'images/index.html', {'albums': albums})
            else:
                return render(request, 'images/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'images/login.html', {'error_message': 'Invalid login'})
    return render(request, 'images/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'images/index.html', {'albums': albums})
    context = {
        "form": form,
    }
    return render(request, 'images/register.html', context)


def images(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'images/login.html')
    else:
        try:
            image_ids = []
            for album in Album.objects.filter(user=request.user):
                for image in album.image_set.all():
                    image_ids.append(image.pk)
            users_images = Images.objects.filter(pk__in=image_ids)
            if filter_by == 'favorites':
                users_images = users_images.filter(is_favorite=True)
        except Album.DoesNotExist:
            users_images = []
        return render(request, 'images/image.html', {
            'image_list': users_images,
            'filter_by': filter_by,
        })
