from pytubefix import Playlist
from mutagen.mp4 import MP4, MP4Cover
import os
import requests
from io import BytesIO

def add_m4a_metadata(file_path, track_number, title, artist, album, total_tracks, cover_url=None):
    """Adds metadata to .m4a file"""
    try:
        audio = MP4(file_path)
        
        # Basic metadata
        audio["\xa9nam"] = title  # Title
        audio["\xa9ART"] = artist  # Artist
        audio["\xa9alb"] = album    # Album
        audio["\xa9day"] = "2001"   # Year
        audio["\xa9gen"] = "Alternative Rock"  # Genre
        
        # Track number (format: current number/total)
        audio["trkn"] = [(track_number, total_tracks)]
        
        # Add album cover if available
        if cover_url:
            try:
                response = requests.get(cover_url)
                if response.status_code == 200:
                    cover_data = BytesIO(response.content).getvalue()
                    audio["covr"] = [MP4Cover(cover_data, imageformat=MP4Cover.FORMAT_JPEG)]
            except:
                print("  ⚠️ Could not download cover")
        
        # Save metadata
        audio.save()
        print(f"  ✓ Metadata added: Track {track_number} - {title}")
        
    except Exception as e:
        print(f"  ✗ Error adding metadata: {e}")

def download_playlist_with_metadata(playlist_url, artist="Artist", album="Album"):
    """Downloads complete playlist with metadata"""
    
    pl = Playlist(playlist_url)
    total_videos = len(pl.videos)
    
    print(f"Playlist: {pl.title}")
    print(f"Total videos: {total_videos}")
    print("-" * 50)
    
    # Create downloads folder
    downloads_folder = "downloads"
    os.makedirs(downloads_folder, exist_ok=True)
    
    for index, video in enumerate(pl.videos, start=1):
        try:
            print(f"\n[{index}/{total_videos}] Processing: {video.title}")
            
            # Get audio stream
            audio_stream = video.streams.get_audio_only()
            
            # Clean title for valid filename
            clean_title = "".join(c for c in video.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Filename with track number
            filename = f"{index:02d} - {clean_title}.m4a"
            full_path = os.path.join(downloads_folder, filename)
            
            # Download audio
            print(f"  📥 Downloading...")
            audio_stream.download(
                output_path=downloads_folder,
                filename=filename
            )
            
            # Try to get thumbnail for cover
            cover_url = video.thumbnail_url if hasattr(video, 'thumbnail_url') else None
            
            # Add metadata
            add_m4a_metadata(
                full_path,
                track_number=index,
                title=f"{index:02d} - {video.title}",
                artist=artist,
                album=album,
                total_tracks=total_videos,
                cover_url=cover_url
            )
            
            print(f"  ✅ Completed: {filename}")
            
        except Exception as e:
            print(f"  ❌ Error with video {index}: {e}")
    
    print(f"\n🎉 Download complete! {total_videos} files processed.")

# USAGE:
if __name__ == "__main__":
    url = "YOUR_PLAYLIST_URL_HERE"
    
    # Customize with album data
    artist_name = "Band Name"
    album_name = "Album Name"
    
    download_playlist_with_metadata(url, artist_name, album_name)
