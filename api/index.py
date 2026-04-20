from flask import Flask, request, jsonify
from ytmusicapi import YTMusic

app = Flask(__name__)

# --- ENABLE CORS (Cross-Origin Resource Sharing) ---
# This ensures any website or app can fetch data from this API without being blocked.
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

# --- INITIALIZE YTMUSIC ---
# Forcing India location so autocomplete and lyrics default to Indian regional content
yt = YTMusic(location="IN", language="en")

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Welcome to the YT Music Suggestions & Lyrics API",
        "endpoints": {
            "suggestions": "/api/suggestions?q=YOUR_QUERY",
            "lyrics": "/api/lyrics?id=YOUR_VIDEO_ID"
        }
    })

# --- ENDPOINT 1: SEARCH SUGGESTIONS ---
@app.route('/api/suggestions')
def suggestions():
    # Get the query from the URL (e.g., ?q=arijit)
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"error": "Please provide a search query. Example: /api/suggestions?q=tum hi ho"}), 400
        
    try:
        # detailed_runs=True gives rich text formatting metadata
        results = yt.get_search_suggestions(query, detailed_runs=True)
        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# --- ENDPOINT 2: LYRICS (Synced / Plain Text) ---
@app.route('/api/lyrics')
def lyrics():
    # Get the video ID from the URL (e.g., ?id=xyz123)
    video_id = request.args.get('id')
    
    if not video_id:
        return jsonify({"error": "Please provide a video id. Example: /api/lyrics?id=xyz123"}), 400
    
    try:
        # Step 1: Get the watch playlist to extract the unique lyrics ID
        watch_playlist = yt.get_watch_playlist(videoId=video_id)
        lyrics_id = watch_playlist.get("lyrics")
        
        if lyrics_id:
            # Step 2: Fetch the actual lyrics data using the lyrics ID
            lyrics_data = yt.get_lyrics(lyrics_id)
            
            # YouTube Music will return 'hasTimestamps': True if synced lyrics exist
            return jsonify({
                "success": True, 
                "is_synced": lyrics_data.get('hasTimestamps', False),
                "data": lyrics_data
            })
        
        # If lyrics_id is None, it means the song is an instrumental or has no lyrics on YTM
        return jsonify({"success": False, "error": "No lyrics found for this song on YouTube Music."}), 404
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
