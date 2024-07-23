import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt

from users.models import Wishlist


def home(request):
    url_trending = 'https://api.themoviedb.org/3/trending/movie/week'
    params = {
        'api_key': "6d9d64446aa322b6e954111c63b34344",
    }
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
    return render(request, 'userinfo.html')


@login_required
def process_movie(request):
    if request.method == 'POST':
        favorite_movie = request.POST.get('favorite_movie')
        return render(request, 'moviehome.html', {'user_name': request.user.first_name.capitalize(),
                                                  'favorite_movie': favorite_movie})
    # If the method is not POST, redirect to the movie_recommendation page
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

    params = {
        'api_key': "6d9d64446aa322b6e954111c63b34344",
        'query': query,
    }
    try:
        # Fetch movies
        response_movie = requests.get(url_movie, params=params)
        response_movie.raise_for_status()
        movies = response_movie.json().get('results', [])

        # Fetch TV shows
        response_tv = requests.get(url_tv, params=params)
        response_tv.raise_for_status()
        tv_shows = response_tv.json().get('results', [])

        # Combine movies and TV shows
        combined_results = movies + tv_shows

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
        return render(request, 'moviehome.html', {
            'user_name': request.user.first_name.capitalize(),
            'success_message': 'Movie added to wishlist!'
        })
    return HttpResponse(status=405)
