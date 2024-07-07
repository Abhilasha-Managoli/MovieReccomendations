import requests
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout


def home(request):
    return render(request, "home.html")


@login_required
def movie_recommendation(request):
    user_name = request.user.first_name.capitalize() if request.user.first_name else ''
    return render(request, 'moviehome.html', {'user_name': user_name})


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
    query = request.GET.get('query', '')
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': "6d9d64446aa322b6e954111c63b34344",
        'query': query,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Check if the request was successful
        data = response.json()
        movies = data.get('results', [])
        return render(request, 'moviehome.html', {'movies': movies, 'query': query})
    except requests.exceptions.RequestException as e:
        return HttpResponse(f"An error occurred: {e}", status=500)
