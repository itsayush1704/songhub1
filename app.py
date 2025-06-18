from flask import Flask, render_template, request, jsonify, session, send_file
from flask import Flask, render_template, request, jsonify
from ytmusicapi import YTMusic
import os
from dotenv import load_dotenv
import yt_dlp
import json
from datetime import datetime
import pickle

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize YouTube Music API
ytmusic = YTMusic()

# In-memory storage for playlists (in a real app, use a database)
playlists = {}
# In-memory storage for recently played songs with timestamps
recently_played = []

# Load saved data if exists
def load_saved_data():
    global playlists, recently_played
    try:
        if os.path.exists('playlists.pkl'):
            with open('playlists.pkl', 'rb') as f:
                playlists = pickle.load(f)
        if os.path.exists('recently_played.pkl'):
            with open('recently_played.pkl', 'rb') as f:
                recently_played = pickle.load(f)
    except Exception as e:
        print(f"Error loading saved data: {e}")

# Save data to files
def save_data():
    try:
        with open('playlists.pkl', 'wb') as f:
            pickle.dump(playlists, f)
        with open('recently_played.pkl', 'wb') as f:
            pickle.dump(recently_played, f)
    except Exception as e:
        print(f"Error saving data: {e}")

# Load saved data on startup
load_saved_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.json.get('query', '')
    try:
        search_results = ytmusic.search(query, filter='songs')
        return jsonify({
            'status': 'success',
            'results': search_results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/get_stream_url/<video_id>')
def get_stream_url(video_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'youtube_include_dash_manifest': True,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch',
            'extract_flat': True,
            'force_generic_extractor': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://music.youtube.com/watch?v={video_id}", download=False)
            if 'entries' in info:
                audio_url = info['entries'][0]['url']
            else:
                audio_url = info['url']

        return jsonify({
            'status': 'success',
            'stream_url': audio_url
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/play_event', methods=['POST'])
def play_event():
    song = request.json
    # Add timestamp to the song data
    song['timestamp'] = datetime.now().isoformat()
    
    # Avoid duplicates, keep only last 20
    global recently_played
    recently_played = [s for s in recently_played if s.get('videoId') != song.get('videoId')]
    recently_played.insert(0, song)
    recently_played = recently_played[:20]
    
    # Save data after updating
    save_data()
    return jsonify({'status': 'success'})

@app.route('/recently_played')
def get_recently_played():
    # Sort by timestamp if available
    sorted_recent = sorted(recently_played, 
                         key=lambda x: x.get('timestamp', ''), 
                         reverse=True)
    return jsonify({'status': 'success', 'recently_played': sorted_recent})

@app.route('/recommendations')
def get_recommendations():
    try:
        # Get recommendations based on YouTube Music home
        home = ytmusic.get_home()
        
        # Get recommendations based on recently played songs
        recent_recommendations = []
        if recently_played and len(recently_played) > 0:
            # Get recommendations based on the most recent song
            recent_song = recently_played[0]
            if isinstance(recent_song, dict) and 'videoId' in recent_song:
                try:
                    watch_playlist = ytmusic.get_watch_playlist(recent_song['videoId'])
                    if isinstance(watch_playlist, dict) and 'tracks' in watch_playlist:
                        recent_recommendations = watch_playlist['tracks'][:5]  # Get 5 recommendations
                except Exception as e:
                    print(f"Error getting watch playlist: {e}")

        # Get recommendations from home page
        home_recommendations = []
        if isinstance(home, list):
            for shelf in home:
                if isinstance(shelf, dict) and shelf.get('title') in ['Quick picks', 'Your favorites', 'Recommended for you', 'New releases']:
                    contents = shelf.get('contents', [])
                    if isinstance(contents, list):
                        for item in contents:
                            if isinstance(item, dict) and item.get('resultType') == 'song':
                                home_recommendations.append(item)

        # Get location-based chart recommendations
        chart_recommendations = []
        try:
            # Get top songs chart
            charts = ytmusic.get_charts()
            if isinstance(charts, dict) and 'tracks' in charts:
                chart_recommendations = charts['tracks'][:5]  # Get top 5 chart songs
        except Exception as e:
            print(f"Error getting charts: {e}")

        # Combine and deduplicate recommendations
        all_recommendations = []
        seen_video_ids = set()

        # Add recent recommendations first
        for rec in recent_recommendations:
            if isinstance(rec, dict) and 'videoId' in rec and rec['videoId'] not in seen_video_ids:
                all_recommendations.append(rec)
                seen_video_ids.add(rec['videoId'])

        # Add home recommendations
        for rec in home_recommendations:
            if isinstance(rec, dict) and 'videoId' in rec and rec['videoId'] not in seen_video_ids:
                all_recommendations.append(rec)
                seen_video_ids.add(rec['videoId'])

        # Add chart recommendations if we don't have enough recommendations
        if len(all_recommendations) < 10:
            for rec in chart_recommendations:
                if isinstance(rec, dict) and 'videoId' in rec and rec['videoId'] not in seen_video_ids:
                    all_recommendations.append(rec)
                    seen_video_ids.add(rec['videoId'])

        return jsonify({
            'status': 'success',
            'recommendations': all_recommendations[:15],  # Return top 15 recommendations
            'has_charts': len(chart_recommendations) > 0
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/playlists', methods=['GET', 'POST'])
def handle_playlists():
    if request.method == 'POST':
        data = request.json
        playlist_name = data.get('name')
        playlist_id = str(len(playlists) + 1)
        playlists[playlist_id] = {
            'name': playlist_name,
            'songs': [],
            'created_at': datetime.now().isoformat()
        }
        # Save data after creating new playlist
        save_data()
        return jsonify({
            'status': 'success',
            'playlist_id': playlist_id
        })
    else:
        # Sort playlists by creation date
        sorted_playlists = dict(sorted(
            playlists.items(),
            key=lambda x: x[1].get('created_at', ''),
            reverse=True
        ))
        return jsonify({
            'status': 'success',
            'playlists': sorted_playlists
        })

@app.route('/playlists/<playlist_id>/songs', methods=['GET', 'POST', 'DELETE'])
def handle_playlist_songs(playlist_id):
    if playlist_id not in playlists:
        return jsonify({
            'status': 'error',
            'message': 'Playlist not found'
        }), 404

    if request.method == 'POST':
        song = request.json
        # Add timestamp when song is added to playlist
        song['added_at'] = datetime.now().isoformat()
        playlists[playlist_id]['songs'].append(song)
        # Save data after adding song
        save_data()
        return jsonify({
            'status': 'success',
            'message': 'Song added to playlist'
        })
    elif request.method == 'DELETE':
        song_id = request.json.get('videoId')
        playlists[playlist_id]['songs'] = [
            song for song in playlists[playlist_id]['songs']
            if song['videoId'] != song_id
        ]
        # Save data after removing song
        save_data()
        return jsonify({
            'status': 'success',
            'message': 'Song removed from playlist'
        })
    else:
        # Sort songs by when they were added
        sorted_songs = sorted(
            playlists[playlist_id]['songs'],
            key=lambda x: x.get('added_at', ''),
            reverse=True
        )
        return jsonify({
            'status': 'success',
            'songs': sorted_songs
        })

@app.route('/default_playlists')
def get_default_playlists():
    try:
        # Get YouTube Music default playlists
        library = ytmusic.get_library_playlists()
        return jsonify({
            'status': 'success',
            'playlists': library
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/playlist/<playlist_id>')
def get_playlist_details(playlist_id):
    try:
        playlist = ytmusic.get_playlist(playlist_id)
        return jsonify({
            'status': 'success',
            'playlist': playlist
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=8002)