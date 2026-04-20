from flask import Flask, request, jsonify
from ytmusicapi import YTMusic

# Initialize Flask and YTMusic (with India location)
app = Flask(__name__)
yt = YTMusic(location="IN", language="en")

@app.route('/')
def home():
    return jsonify({"message": "API is running! Use /suggestions?q=songname or /lyrics?id=videoid"})

@app.route('/suggestions')
def suggestions():
    query = request.args.get('q', 'tum hi ho') # Default fallback query
    results = yt.get_search_suggestions(query, detailed_runs=True)
    return jsonify(results)

@app.route('/lyrics')
def lyrics():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({"error": "Please provide a video id. Example: /lyrics?id=abc123xyz"}), 400
    
    watch_playlist = yt.get_watch_playlist(videoId=video_id)
    lyrics_id = watch_playlist.get("lyrics")
    
    if lyrics_id:
        lyrics_data = yt.get_lyrics(lyrics_id)
        return jsonify(lyrics_data)
    
    return jsonify({"error": "No lyrics found for this song."}), 404
