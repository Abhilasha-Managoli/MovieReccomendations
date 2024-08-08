import json
import logging

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
logger = logging.getLogger(__name__)


from users.models import Wishlist, Favorites

API_KEY = "6d9d64446aa322b6e954111c63b34344"


def fetch_genres():
    url_movie_genres = 'https://api.themoviedb.org/3/genre/movie/list'
    url_tv_genres = 'https://api.themoviedb.org/3/genre/tv/list'
    params = {'api_key': API_KEY}

    genres = {}
    try:
        response_movie = requests.get(url_movie_genres, params=params)
        response_movie.raise_for_status()
        movie_genres = response_movie.json().get('genres', [])

        response_tv = requests.get(url_tv_genres, params=params)
        response_tv.raise_for_status()
        tv_genres = response_tv.json().get('genres', [])

        for genre in movie_genres + tv_genres:
            genres[genre['id']] = genre['name']
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching genres: {e}")

    return genres


def get_similar_movie(movie_id):
    url_similar = f'https://api.themoviedb.org/3/movie/{movie_id}/similar'
    params = {'api_key': API_KEY}
    try:
        response = requests.get(url_similar, params=params)
        response.raise_for_status()
        similar_movies = response.json().get('results', [])
        return similar_movies
    except requests.exceptions.RequestException:
        return []


def home(request):
    url_trending_movies = 'https://api.themoviedb.org/3/trending/movie/week'
    url_trending_shows = 'https://api.themoviedb.org/3/trending/tv/week'
    params = {'api_key': API_KEY}

    try:
        response_trending_movies = requests.get(url_trending_movies, params=params)
        response_trending_movies.raise_for_status()
        trending_movies = response_trending_movies.json().get('results', [])[:6]

        response_trending_shows = requests.get(url_trending_shows, params=params)
        response_trending_shows.raise_for_status()
        trending_shows = response_trending_shows.json().get('results', [])[:6]

        return render(request, 'home.html', {
            'trending_movies': trending_movies,
            'trending_shows': trending_shows
        })
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}", status=500)


@login_required
def popcornpicks_view(request):
    if request.user.is_authenticated:
        favorites = Favorites.objects.filter(user=request.user)
        favorite_ids = [fav.movie_id for fav in favorites if fav.movie_id]

        # Initialize recommendations list
        recommendations = []

        if favorite_ids:
            # Call the TMDB API to get similar movies
            api_key: API_KEY
            for movie_id in favorite_ids:
                url = f'https://api.themoviedb.org/3/movie/{movie_id}/recommendations'
                params = {
                    'api_key': API_KEY,
                    'language': 'en-US',
                    'page': 1
                }
                response = requests.get(url, params=params).json()
                recommendations.extend(response.get('results', []))

            # Limit the number of recommendations to 6
            recommendations = recommendations[:6]

        context = {
            'recommendations': recommendations
        }

        return render(request, 'popcornpicks.html', context)
    else:
        return redirect('account_login')


@login_required
def userinfo_view(request):
    # Fetch user's watchlist and favorites
    wishlist = Wishlist.objects.filter(user=request.user)
    favorites = Favorites.objects.filter(user=request.user)

    # Lists to store movie and TV show details
    movie_details = []
    favorite_details = []
    tv_show_details = []
    favorite_show_details = []

    # Function to fetch movie details
    def fetch_movie_details(item_id):
        search_url = f'https://api.themoviedb.org/3/movie/{item_id}'
        params = {'api_key': API_KEY}
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            details = response.json()
            logging.debug(f"Fetched movie details for ID '{item_id}': {details}")
            return {
                'id': item_id,
                'title': details.get('title'),
                'poster_path': details.get('poster_path'),
                'genre_ids': [genre['id'] for genre in details.get('genres', [])],
                'overview': details.get('overview'),
                'content_type': 'movie'
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching movie details for ID '{item_id}': {e}")
            return None

    # Function to fetch TV show details
    def fetch_tv_details(item_id):
        search_url = f'https://api.themoviedb.org/3/tv/{item_id}'
        params = {'api_key': API_KEY}
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            details = response.json()
            logging.debug(f"Fetched TV show details for ID '{item_id}': {details}")
            return {
                'id': item_id,
                'title': details.get('name'),
                'poster_path': details.get('poster_path'),
                'genre_ids': [genre['id'] for genre in details.get('genres', [])],
                'overview': details.get('overview'),
                'content_type': 'tv'
            }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching TV show details for ID '{item_id}': {e}")
            return None

    # Fetch details for items in the watchlist
    for item in wishlist:
        if item.movie_id:
            details = fetch_movie_details(item.movie_id)
            if details:
                movie_details.append(details)
        elif item.tv_id:
            details = fetch_tv_details(item.tv_id)
            if details:
                tv_show_details.append(details)

    # Fetch details for items in the favorites
    for item in favorites:
        if item.movie_id:
            details = fetch_movie_details(item.movie_id)
            if details:
                favorite_details.append(details)
        elif item.tv_id:
            details = fetch_tv_details(item.tv_id)
            if details:
                favorite_show_details.append(details)

    # Fetch genres and attach genre names to items
    genres = fetch_genres()
    logging.debug(f"Fetched genres: {genres}")

    def attach_genre_names(items):
        for item in items:
            genre_names = [genres.get(genre_id, 'Unknown') for genre_id in item.get('genre_ids', [])]
            item['genre_names'] = genre_names
            logging.debug(f"{item.get('title')} genres: {genre_names}")

    attach_genre_names(movie_details)
    attach_genre_names(favorite_details)
    attach_genre_names(tv_show_details)
    attach_genre_names(favorite_show_details)

    # Render the userinfo template with the fetched data
    return render(request, 'userinfo.html', {
        'user': request.user,
        'wishlist_movies': movie_details,
        'favorites_movies': favorite_details,
        'wishlist_shows': tv_show_details,
        'favorites_shows': favorite_show_details,
    })

@login_required
def delete_from_watchlist(request, movie_id):
    item = get_object_or_404(Wishlist, user=request.user, movie_id=movie_id)
    item.delete()
    return redirect('users:userinfo')  # Redirect to the user info page or any relevant page

@login_required
def delete_show_from_watchlist(request, tv_id):
    wishlist_item = get_object_or_404(Wishlist, tv_id=tv_id, user=request.user)
    wishlist_item.delete()
    return redirect('users:userinfo')


@login_required
def delete_from_favorites(request, movie_id):
    item = get_object_or_404(Favorites, user=request.user, movie_id=movie_id)
    item.delete()
    return redirect('users:userinfo')  # Redirect to the user info page or any relevant page

@login_required
def delete_show_from_favorites(request, tv_id):
    favorite_item = get_object_or_404(Favorites, tv_id=tv_id, user=request.user)
    favorite_item.delete()
    return redirect('users:userinfo')

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
    movie_id = request.GET.get('movie_id')
    tv_id = request.GET.get('tv_id')
    query = request.GET.get('query', '')
    url_movie = 'https://api.themoviedb.org/3/search/movie'
    url_tv = 'https://api.themoviedb.org/3/search/tv'
    params = {'api_key': API_KEY, 'query': query}
    genres = fetch_genres()

    # Handle search by query
    if query:
        try:
            response_movie = requests.get(url_movie, params=params)
            response_movie.raise_for_status()
            movies = response_movie.json().get('results', [])
            response_tv = requests.get(url_tv, params=params)
            response_tv.raise_for_status()
            tv_shows = response_tv.json().get('results', [])
            combined_results = movies + tv_shows

            # Map genre IDs to genre names
            for item in combined_results:
                genre_ids = item.get('genre_ids', [])
                item['genre_names'] = [genres.get(genre_id, 'Unknown') for genre_id in genre_ids]
                item['title'] = item.get('title') or item.get('name')

            return render(request, 'moviehome.html', {
                'movies': combined_results,
                'query': query,
                'user_name': user_name
            })
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    # Handle search by movie_id
    if movie_id:
        url_movie_details = f'https://api.themoviedb.org/3/movie/{movie_id}'
        try:
            response = requests.get(url_movie_details, params={'api_key': API_KEY})
            response.raise_for_status()
            movie_details = response.json()

            genre_ids = [genre['id'] for genre in movie_details.get('genres', [])]
            movie_details['genre_names'] = [genres.get(genre_id, 'Unknown') for genre_id in genre_ids]

            return render(request, 'moviehome.html', {
                'movies': [movie_details],  # Pass movie details to the template
                'query': '',
                'user_name': user_name
            })
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    # Handle search by tv_id
    if tv_id:
        url_tv_details = f'https://api.themoviedb.org/3/tv/{tv_id}'
        try:
            response = requests.get(url_tv_details, params={'api_key': API_KEY})
            response.raise_for_status()
            tv_details = response.json()

            genre_ids = [genre['id'] for genre in tv_details.get('genres', [])]
            tv_details['genre_names'] = [genres.get(genre_id, 'Unknown') for genre_id in genre_ids]

            return render(request, 'moviehome.html', {
                'movies': [tv_details],  # Pass TV show details to the template
                'query': '',
                'user_name': user_name
            })
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    # Default response if neither movie_id, tv_id, nor query is provided
    return render(request, 'moviehome.html', {
        'movies': [],
        'query': '',
        'user_name': user_name
    })


@login_required
@csrf_protect
def add_to_favorites(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        tv_id = data.get('tv_id')
        movie_title = data.get('movie_title')
        show_title = data.get('show_title')

        if movie_id:
            if Favorites.objects.filter(user=request.user, movie_id=movie_id).exists():
                return JsonResponse({'success': False, 'message': 'Movie already added to favorites!'})
            Favorites.objects.create(user=request.user, movie_id=movie_id, movie_title=movie_title)
        elif tv_id:
            if Favorites.objects.filter(user=request.user, tv_id=tv_id).exists():
                return JsonResponse({'success': False, 'message': 'Show already added to favorites!'})
            Favorites.objects.create(user=request.user, tv_id=tv_id, show_title=show_title)

        return JsonResponse({'success': True, 'message': 'Movie/TV Show added to favorites successfully.'})

    return HttpResponse(status=405)

@login_required
@csrf_protect
def add_to_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        tv_id = data.get('tv_id')
        movie_title = data.get('movie_title')
        show_title = data.get('show_title')

        if movie_id:
            if Wishlist.objects.filter(user=request.user, movie_id=movie_id).exists():
                return JsonResponse({'success': False, 'message': 'Movie already added to watchlist!'})
            Wishlist.objects.create(user=request.user, movie_id=movie_id, movie_title=movie_title)
        elif tv_id:
            if Wishlist.objects.filter(user=request.user, tv_id=tv_id).exists():
                return JsonResponse({'success': False, 'message': 'Show already added to watchlist!'})
            Wishlist.objects.create(user=request.user, tv_id=tv_id, show_title=show_title)

        return JsonResponse({'success': True, 'message': 'Movie/TV Show added to watchlist successfully.'})

    return HttpResponse(status=405)


def autocomplete(request):
    if 'term' in request.GET:
        query = request.GET['term']
        url_search = 'https://api.themoviedb.org/3/search/multi'
        params = {'api_key': API_KEY, 'query': query, 'language': 'en-US'}

        try:
            response = requests.get(url_search, params=params)
            response.raise_for_status()
            results = response.json().get('results', [])
            suggestions = [{
                'id': item['id'],
                'title': item.get('title') or item.get('name'),
                'poster_url': f"https://image.tmdb.org/t/p/w200{item.get('poster_path')}" if item.get(
                    'poster_path') else None,
                'media_type': item.get('media_type')
            } for item in results if item.get('media_type') in ['movie', 'tv']]

            return JsonResponse(suggestions, safe=False)
        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse([], safe=False)


def search_results(request):
    query = request.GET.get('query', '')
    url_search = 'https://api.themoviedb.org/3/search/multi'
    params = {'api_key': API_KEY, 'query': query, 'language': 'en-US'}

    try:
        response = requests.get(url_search, params=params)
        response.raise_for_status()
        results = response.json().get('results', [])
        movies = [item for item in results if item.get('media_type') == 'movie']
        return render(request, 'search_results.html', {'movies': movies, 'query': query})
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}", status=500)
