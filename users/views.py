import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from users.models import Wishlist, Favorites

API_KEY = "6d9d64446aa322b6e954111c63b34344"


def get_genres():
    url_movie_genres = 'https://api.themoviedb.org/3/genre/movie/list'
    url_tv_genres = 'https://api.themoviedb.org/3/genre/tv/list'
    params = {'api_key': API_KEY}
    genres = {}

    try:
        response_movie_genres = requests.get(url_movie_genres, params=params)
        response_movie_genres.raise_for_status()
        movie_genres = response_movie_genres.json().get('genres', [])
        genres.update({genre['id']: genre['name'] for genre in movie_genres})

        response_tv_genres = requests.get(url_tv_genres, params=params)
        response_tv_genres.raise_for_status()
        tv_genres = response_tv_genres.json().get('genres', [])
        genres.update({genre['id']: genre['name'] for genre in tv_genres})

        return genres
    except requests.exceptions.RequestException as e:
        return {}


def home(request):
    url_trending = 'https://api.themoviedb.org/3/trending/movie/week'
    params = {'api_key': API_KEY}
    try:
        response_trending = requests.get(url_trending, params=params)
        response_trending.raise_for_status()
        trending_data = response_trending.json().get('results', [])[:6]
        return render(request, 'home.html', {'trending_movies': trending_data})
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


@login_required
def movie_recommendation(request):
    user_name = request.user.first_name.capitalize() if request.user.first_name else ''
    return render(request, 'moviehome.html', {'user_name': user_name})


@login_required
def userinfo_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    favorites = Favorites.objects.filter(user=request.user)  # Query the favorites
    return render(request, 'userinfo.html', {
        'user': request.user,
        'wishlist': wishlist,
        'favorites': favorites,
    })


@login_required
def process_movie(request):
    if request.method == 'POST':
        favorite_movie = request.POST.get('favorite_movie')
        return render(request, 'moviehome.html', {'user_name': request.user.first_name.capitalize(),
                                                  'favorite_movie': favorite_movie})
    return redirect('users:movie_recommendation')


def logout_view(request):
    logout(request)
    return redirect("/")


@login_required
def recommendations(request):
    user_name = request.user.first_name.capitalize() if request.user.first_name else ''
    query = request.GET.get('query', '')
    url_movie = 'https://api.themoviedb.org/3/search/movie'
    url_tv = 'https://api.themoviedb.org/3/search/tv'
    params = {'api_key': API_KEY, 'query': query}
    genres = get_genres()

    try:
        response_movie = requests.get(url_movie, params=params)
        response_movie.raise_for_status()
        movies = response_movie.json().get('results', [])
        response_tv = requests.get(url_tv, params=params)
        response_tv.raise_for_status()
        tv_shows = response_tv.json().get('results', [])
        combined_results = movies + tv_shows

        for item in combined_results:
            item['genre_names'] = [genres.get(genre_id, 'Unknown') for genre_id in item.get('genre_ids', [])]
            item['title'] = item.get('title') or item.get('name')

        return render(request, 'moviehome.html', {
            'movies': combined_results,
            'query': query,
            'user_name': user_name
        })
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


@login_required
@csrf_exempt
def add_to_wishlist(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title')
        Wishlist.objects.create(user=request.user, movie_title=movie_title)
        return JsonResponse({'success': True, 'message': 'Movie added to watchlist!'})
    return HttpResponse(status=405)


@login_required
@csrf_exempt
def add_to_favorites(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title')
        Favorites.objects.create(user=request.user, movie_title=movie_title)
        return JsonResponse({'success': True, 'message': 'Movie added to favorites!'})
    return HttpResponse(status=405)
