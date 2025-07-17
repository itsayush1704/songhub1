from locust import HttpUser, task, between
import random


class SongHubUser(HttpUser):
    """Locust user class for performance testing SongHub"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when a user starts"""
        # Test health endpoint first
        self.client.get("/health")
    
    @task(3)
    def view_homepage(self):
        """Test loading the homepage"""
        self.client.get("/")
    
    @task(2)
    def search_songs(self):
        """Test search functionality"""
        search_terms = [
            "taylor swift", "ed sheeran", "billie eilish", 
            "the weeknd", "ariana grande", "drake",
            "pop music", "rock songs", "hip hop"
        ]
        query = random.choice(search_terms)
        self.client.get(f"/search?q={query}")
    
    @task(2)
    def get_recommendations(self):
        """Test recommendations endpoint"""
        self.client.get("/recommendations")
    
    @task(1)
    def get_trending(self):
        """Test trending songs endpoint"""
        self.client.get("/trending")
    
    @task(1)
    def get_top_charts(self):
        """Test top charts endpoint"""
        self.client.get("/top_charts")
    
    @task(1)
    def get_recently_played(self):
        """Test recently played endpoint"""
        self.client.get("/recently_played")
    
    @task(1)
    def get_playlists(self):
        """Test playlists endpoint"""
        self.client.get("/playlists")
    
    @task(1)
    def create_playlist(self):
        """Test playlist creation"""
        playlist_name = f"Test Playlist {random.randint(1, 1000)}"
        self.client.post("/playlists", json={
            "name": playlist_name,
            "description": "Performance test playlist"
        })
    
    @task(1)
    def test_stream_url(self):
        """Test getting stream URL (with fallback)"""
        # Use a known video ID for testing
        test_video_ids = [
            "dQw4w9WgXcQ",  # Rick Astley - Never Gonna Give You Up
            "9bZkp7q19f0",  # PSY - Gangnam Style
            "kJQP7kiw5Fk"   # Luis Fonsi - Despacito
        ]
        video_id = random.choice(test_video_ids)
        self.client.get(f"/get_stream_url/{video_id}")
    
    def on_stop(self):
        """Called when a user stops"""
        pass


class AdminUser(HttpUser):
    """Admin user for testing admin-specific functionality"""
    
    wait_time = between(2, 5)
    weight = 1  # Lower weight means fewer admin users
    
    @task
    def health_check(self):
        """Admin health monitoring"""
        self.client.get("/health")
    
    @task
    def bulk_operations(self):
        """Test bulk operations that admins might perform"""
        # Create multiple playlists
        for i in range(3):
            self.client.post("/playlists", json={
                "name": f"Admin Bulk Playlist {i}",
                "description": "Bulk operation test"
            })


class MobileUser(HttpUser):
    """Mobile user simulation with different usage patterns"""
    
    wait_time = between(2, 8)  # Mobile users might have longer pauses
    weight = 2  # More mobile users
    
    @task(4)
    def mobile_search(self):
        """Mobile users search more frequently"""
        mobile_queries = [
            "trending", "new songs", "popular", "hits",
            "workout music", "chill songs", "party music"
        ]
        query = random.choice(mobile_queries)
        self.client.get(f"/search?q={query}")
    
    @task(3)
    def mobile_browse(self):
        """Mobile browsing behavior"""
        endpoints = ["/recommendations", "/trending", "/top_charts"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)
    
    @task(1)
    def mobile_playlist_management(self):
        """Mobile playlist operations"""
        self.client.get("/playlists")