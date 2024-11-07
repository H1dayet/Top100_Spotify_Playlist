import requests
from bs4 import BeautifulSoup
import pprint as pp
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify credentials from .env
client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
redirect_uri = os.getenv('REDIRECT_URI')

if not client_id or not client_secret or not redirect_uri:
    raise ValueError("Spotify credentials are missing. Check your .env file.")

# Authenticate with Spotify
scope = 'user-library-read playlist-modify-public'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))

# Function to search for a track by name and return its ID
def search_track(track_name):
    results = sp.search(q=track_name, type='track', limit=1)
    if results['tracks']['items']:
        track = results['tracks']['items'][0]
        track_id = track['id']
        print(f"Found: {track['name']} by {track['artists'][0]['name']} (ID: {track_id})")
        return track_id
    else:
        print(f"No track found for: {track_name}")
        return None

# Scrape Billboard Hot 100 chart
user_choice = input("What year would you like to travel to? \n")
URL = f"https://www.billboard.com/charts/hot-100/{user_choice}/"
headers = {"User-Agent": "Mozilla/5.0"}

response = requests.get(URL, headers=headers)
if response.status_code != 200:
    print(f"Failed to retrieve data. Status code: {response.status_code}")
    exit()

soup = BeautifulSoup(response.text, 'html.parser')
titles = soup.find_all('h3', class_='a-no-trucate')
title_text = [title.get_text().strip() for title in titles]

# Search for track IDs on Spotify
track_ids = [search_track(title) for title in title_text if search_track(title)]

# Create a new playlist
def create_playlist(name, description="Generated with Python"):
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(
        user=user_id, 
        name=name, 
        public=True, 
        description=description
    )
    print(f"Created playlist: {playlist['name']} (ID: {playlist['id']})")
    return playlist['id']

# Add tracks to the playlist
def add_tracks_to_playlist(playlist_id, track_ids):
    sp.playlist_add_items(playlist_id, track_ids)
    print(f"Added {len(track_ids)} tracks to the playlist.")

# Create a playlist and add tracks
playlist_name = f"Billboard Hot 100 - {user_choice}"
playlist_id = create_playlist(playlist_name)
if track_ids:
    add_tracks_to_playlist(playlist_id, track_ids)
else:
    print("No valid tracks found to add to the playlist.")
