import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, request, jsonify, render_template
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from dotenv import load_dotenv
import os
import logging
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Spotify client
def init_spotify():
    try:
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in .env file")
            
        logger.info("Initializing Spotify client...")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        
        # Test the connection
        spotify.search(q='test', limit=1)
        logger.info("✓ Spotify client initialized successfully")
        return spotify
        
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {str(e)}")
        raise

# Initialize Spotify client
try:
    sp = init_spotify()
except Exception as e:
    logger.error("Critical error: Failed to initialize Spotify client")
    logger.error(str(e))
    raise

def get_artist_top_tracks(artist_id, track_id):
    """Tier 1: Get artist's top tracks (90% similarity)"""
    try:
        top_tracks = sp.artist_top_tracks(artist_id)
        recommendations = []
        
        if top_tracks and 'tracks' in top_tracks:
            for track in top_tracks['tracks'][:5]:  # Get top 5 tracks
                if track['id'] != track_id:  # Avoid the input track
                    recommendations.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track.get('preview_url'),
                        'similarity': 90.0,
                        'reason': "Same artist's top track"
                    })
                    
        logger.info(f"Found {len(recommendations)} top tracks from artist")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in get_artist_top_tracks: {str(e)}")
        return []

def get_related_artists_tracks(artist_id, track_id):
    """Tier 2: Get tracks from related artists (85% similarity)"""
    try:
        related = sp.artist_related_artists(artist_id)
        recommendations = []
        
        if related and 'artists' in related:
            for artist in related['artists'][:3]:  # Get top 3 related artists
                top_tracks = sp.artist_top_tracks(artist['id'])
                if top_tracks and 'tracks' in top_tracks:
                    for track in top_tracks['tracks'][:2]:  # Get top 2 tracks per artist
                        if track['id'] != track_id:
                            recommendations.append({
                                'id': track['id'],
                                'name': track['name'],
                                'artist': track['artists'][0]['name'],
                                'preview_url': track.get('preview_url'),
                                'similarity': 85.0,
                                'reason': f'Top track by similar artist {artist["name"]}'
                            })
                            
        logger.info(f"Found {len(recommendations)} tracks from related artists")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in get_related_artists_tracks: {str(e)}")
        return []

def get_spotify_recommendations(track_id, genres=None):
    """Tier 3: Use Spotify's recommendation engine (80% similarity)"""
    try:
        params = {
            'seed_tracks': [track_id],
            'limit': 10,
            'min_popularity': 20
        }
        if genres:
            params['seed_genres'] = genres[:2]
            
        results = sp.recommendations(**params)
        recommendations = []
        
        if results and 'tracks' in results:
            for track in results['tracks']:
                if track['id'] != track_id:
                    recommendations.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track.get('preview_url'),
                        'similarity': 80.0,
                        'reason': 'Recommended by Spotify'
                    })
                    
        logger.info(f"Found {len(recommendations)} Spotify recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in get_spotify_recommendations: {str(e)}")
        return []

def get_artist_fallback(artist_name, track_id):
    """Tier 4: Artist-only fallback search (70% similarity)"""
    try:
        results = sp.search(q=artist_name, type='track', limit=10)
        recommendations = []
        
        if results and 'tracks' in results:
            for track in results['tracks']['items']:
                if track['id'] != track_id:
                    recommendations.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artist': track['artists'][0]['name'],
                        'preview_url': track.get('preview_url'),
                        'similarity': 70.0,
                        'reason': 'Other song by this artist'
                    })
                    
        logger.info(f"Found {len(recommendations)} artist fallback tracks")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error in get_artist_fallback: {str(e)}")
        return []

def find_similar_songs(track_id):
    """Find similar songs using 4-tier strategy"""
    try:
        # Get track info first
        track = sp.track(track_id)
        if not track:
            logger.error("Could not get track info")
            return []
            
        artist_id = track['artists'][0]['id']
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        
        logger.info(f"Finding recommendations for: {track_name} by {artist_name}")
        recommendations = []
        
        # Get artist info for genres
        artist_info = sp.artist(artist_id)
        genres = artist_info.get('genres', [])
        
        # Tier 1: Artist's Top Tracks (90% similarity)
        tier1 = get_artist_top_tracks(artist_id, track_id)
        recommendations.extend(tier1)
        
        # Tier 2: Related Artists (85% similarity)
        if len(recommendations) < 10:
            tier2 = get_related_artists_tracks(artist_id, track_id)
            recommendations.extend(tier2)
        
        # Tier 3: Spotify Smart Engine (80% similarity)
        if len(recommendations) < 10:
            tier3 = get_spotify_recommendations(track_id, genres)
            recommendations.extend(tier3)
        
        # Tier 4: Artist-Only Fallback (70% similarity)
        if len(recommendations) < 5:
            tier4 = get_artist_fallback(artist_name, track_id)
            recommendations.extend(tier4)
        
        if not recommendations:
            logger.warning(f"No recommendations found for: {track_name} by {artist_name}")
            return []
        
        # Remove duplicates while preserving order (higher tiers first)
        seen = set()
        unique_recommendations = []
        for r in recommendations:
            if r['id'] not in seen and r['id'] != track_id:
                seen.add(r['id'])
                unique_recommendations.append(r)
        
        logger.info(f"Returning {len(unique_recommendations[:10])} unique recommendations")
        return unique_recommendations[:10]  # Return top 10
        
    except Exception as e:
        logger.error(f"Error in find_similar_songs: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """Search for a song"""
    try:
        query = request.json.get('query', '')
        if not query:
            return jsonify({'success': False, 'error': 'No search query provided'})
            
        logger.info(f"Searching for: {query}")
        results = sp.search(q=query, limit=10)
        
        tracks = []
        for track in results['tracks']['items']:
            tracks.append({
                'id': track['id'],
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'preview_url': track.get('preview_url')
            })
            
        logger.info(f"Found {len(tracks)} tracks")
        return jsonify({
            'success': True,
            'tracks': tracks
        })
        
    except Exception as e:
        logger.error(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error searching for songs'
        })

@app.route('/recommend', methods=['POST'])
def recommend():
    """Get song recommendations"""
    try:
        data = request.get_json()
        logger.info(f"Raw recommendation request data: {json.dumps(data)}")
        
        track_id = data.get('track_id', '')
        if not track_id:
            logger.error("No track ID provided in request")
            return jsonify({
                'success': False,
                'error': 'No track ID provided'
            })
            
        # First verify the track exists
        try:
            track = sp.track(track_id)
            artist_name = track['artists'][0]['name']
            track_name = track['name']
            logger.info(f"Found track: {track_name} by {artist_name}")
        except Exception as e:
            logger.error(f"Failed to get track info: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid track ID or Spotify API error'
            })
            
        # Get recommendations using 4-tier strategy
        similar_songs = find_similar_songs(track_id)
        
        if not similar_songs:
            logger.warning(f"No recommendations found for: {track_name} by {artist_name}")
            return jsonify({
                'success': False,
                'error': 'Could not find similar songs. Please try another track.'
            })
            
        logger.info(f"Found {len(similar_songs)} recommendations")
        logger.info(f"First recommendation: {json.dumps(similar_songs[0])}")
        
        return jsonify({
            'success': True,
            'recommendations': similar_songs
        })
        
    except Exception as e:
        logger.error(f"Error in recommend route: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Server error while getting recommendations'
        })

if __name__ == '__main__':
    app.run(debug=True)
