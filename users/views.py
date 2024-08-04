import json
import logging

import requests
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.views.decorators.http import require_POST

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
    user_name = request.user.first_name.capitalize() if request.user.first_name else ''
    return render(request, 'popcornpicks.html', {'user_name': user_name})

@login_required
def userinfo_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)
    favorites = Favorites.objects.filter(user=request.user)

    movie_details = []
    favorite_details = []

    def fetch_movie_details(movie_title):
        search_url = f'https://api.themoviedb.org/3/search/movie'
        params = {'api_key': API_KEY, 'query': movie_title}
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            search_results = response.json().get('results', [])
            if search_results:
                movie_id = search_results[0]['id']
                url_movie_details = f'https://api.themoviedb.org/3/movie/{movie_id}'
                details_response = requests.get(url_movie_details, params={'api_key': API_KEY})
                details_response.raise_for_status()
                details = details_response.json()
                logging.debug(f"Movie details for '{movie_title}': {details}")
                return {
                    'title': details.get('title'),
                    'poster_path': details.get('poster_path'),
                    'genre_ids': [genre['id'] for genre in details.get('genres', [])],
                    'overview': details.get('overview')
                }
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching movie details for '{movie_title}': {e}")
            return None

    for movie in wishlist:
        details = fetch_movie_details(movie.movie_title)
        if details:
            movie_details.append(details)

    for movie in favorites:
        details = fetch_movie_details(movie.movie_title)
        if details:
            favorite_details.append(details)

    genres = fetch_genres()
    logging.debug(f"Genres fetched: {genres}")

    for movie in movie_details:
        genre_names = [genres.get(genre_id, 'Unknown') for genre_id in movie.get('genre_ids', [])]
        movie['genre_names'] = genre_names
        logging.debug(f"Wishlist movie '{movie['title']}' genres: {genre_names}")

    for movie in favorite_details:
        genre_names = [genres.get(genre_id, 'Unknown') for genre_id in movie.get('genre_ids', [])]
        movie['genre_names'] = genre_names
        logging.debug(f"Favorite movie '{movie['title']}' genres: {genre_names}")

    return render(request, 'userinfo.html', {
        'user': request.user,
        'wishlist': movie_details,
        'favorites': favorite_details,
    })

@csrf_exempt
def remove_from_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_title = data.get('movie_title')
        user = request.user
        print(f"Removing from wishlist: {movie_title} for user {user.username}")

        try:
            movie = Wishlist.objects.get(user=user, movie_title=movie_title)
            movie.delete()
            return JsonResponse({'success': True})
        except Wishlist.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Movie not found in wishlist.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

@csrf_exempt
def remove_from_favorites(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_title = data.get('movie_title')
        user = request.user
        print(f"Removing from favorites: {movie_title} for user {user.username}")

        try:
            movie = Favorites.objects.get(user=user, movie_title=movie_title)
            movie.delete()
            return JsonResponse({'success': True})
        except Favorites.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Movie not found in favorites.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})

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

            # Ensure genre_ids is a list of IDs, not a list of dicts
            genre_ids = [genre['id'] for genre in movie_details.get('genres', [])] if isinstance(
                movie_details.get('genres', []), list) and isinstance(movie_details.get('genres', [])[0],
                                                                      dict) else movie_details.get('genre_ids', [])
            movie_details['genre_names'] = [genres.get(genre_id, 'Unknown') for genre_id in genre_ids]

            return render(request, 'moviehome.html', {
                'movies': [movie_details],  # Pass movie details to the template
                'query': '',
                'user_name': user_name
            })
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"An error occurred: {e}", status=500)

    # Default response if neither movie_id nor query is provided
    return render(request, 'moviehome.html', {
        'movies': [],
        'query': '',
        'user_name': user_name
    })

@login_required
@csrf_protect
def add_to_wishlist(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_title = data.get('movie_title')
        if Wishlist.objects.filter(user=request.user, movie_title=movie_title).exists():
            return JsonResponse({'success': False, 'message': 'Movie already added to watchlist!'})

        Wishlist.objects.create(user=request.user, movie_title=movie_title)
        return JsonResponse({'success': True, 'message': 'Movie added to watchlist successfully.'})
    return HttpResponse(status=405)


@login_required
@csrf_protect
def add_to_favorites(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        movie_title = data.get('movie_title')
        if Favorites.objects.filter(user=request.user, movie_title=movie_title).exists():
            return JsonResponse({'success': False, 'message': 'Movie already added to favorites!'})

        Favorites.objects.create(user=request.user, movie_title=movie_title)
        return JsonResponse({'success': True, 'message': 'Movie added to Favorites successfully.'})
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
            movies = [{
                'id': item['id'],
                'title': item.get('title') or item.get('name'),
                'poster_url': f"https://image.tmdb.org/t/p/w200{item.get('poster_path')}" if item.get('poster_path') else None
            } for item in results if item.get('media_type') == 'movie']
            return JsonResponse(movies, safe=False)
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


def get_streaming_url(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            movie_title = data.get('movie_title')

            search_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={movie_title}"
            response = requests.get(search_url)

            if response.status_code == 200:
                results = response.json()
                items = results.get('results', [])

                urls = {
                    'netflix': None,
                    'amazon_prime': None
                }

                for item in items:
                    if item['title'].lower() == movie_title.lower():
                        # Construct URLs
                        urls['netflix'] = f"https://www.netflix.com/search?q={movie_title.replace(' ', '%20')}"
                        urls['amazon_prime'] = f"https://www.amazon.com/s?k={movie_title.replace(' ', '+')}"
                        break

                return JsonResponse({'success': True, 'urls': urls})

            return JsonResponse({'success': False, 'message': 'No streaming link found.'})

        except Exception as e:
            print(f"Exception: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Invalid request method.'})