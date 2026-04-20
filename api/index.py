# pip install ytmusicapi syncedlyrics
from ytmusicapi import YTMusic
import syncedlyrics

yt = YTMusic(location="IN", language="en")

def get_best_lyrics(video_id, song_title, artist_name):
    # 1. Try YouTube Music API first
    watch_playlist = yt.get_watch_playlist(videoId=video_id)
    lyrics_id = watch_playlist.get("lyrics")
    
    if lyrics_id:
        yt_lyrics = yt.get_lyrics(lyrics_id)
        
        # If YouTube Music HAS synced lyrics, return them!
        if yt_lyrics.get("hasTimestamps"):
            return {"source": "YouTube", "synced": True, "data": yt_lyrics['lyrics']}
            
    # 2. FALLBACK: YouTube only gave us plain text (or nothing).
    # Let's bypass YouTube and ask Musixmatch/NetEase directly using syncedlyrics!
    
    search_query = f"{song_title} {artist_name}"
    print(f"YouTube failed to give synced lyrics. Falling back to external providers for: {search_query}")
    
    # This searches Musixmatch, Lrclib, and NetEase for the LRC (synced) format
    lrc_lyrics = syncedlyrics.search(search_query)
    
    if lrc_lyrics:
        return {"source": "External (Musixmatch/Lrclib)", "synced": True, "data": lrc_lyrics}
    
    # 3. Final Fallback: Return YouTube's plain text if nothing else exists
    if lyrics_id and yt_lyrics:
        return {"source": "YouTube", "synced": False, "data": yt_lyrics['lyrics']}
        
    return {"error": "No lyrics found anywhere"}
