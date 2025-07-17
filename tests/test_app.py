import pytest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
from app import app, load_saved_data, save_data, get_user_id, extract_song_features


class TestSongHubApp:
    """Test suite for SongHub Flask application"""
    
    @pytest.fixture
    def client(self):
        """Create a test client"""
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key'
        with app.test_client() as client:
            with app.app_context():
                yield client
    
    @pytest.fixture
    def mock_ytmusic(self):
        """Mock YTMusic API"""
        with patch('app.ytmusic') as mock:
            mock.search.return_value = [
                {
                    'videoId': 'test123',
                    'title': 'Test Song',
                    'artists': [{'name': 'Test Artist'}],
                    'thumbnails': [{'url': 'http://test.com/thumb.jpg'}],
                    'duration': '3:30'
                }
            ]
            mock.get_charts.return_value = {
                'tracks': [
                    {
                        'videoId': 'chart123',
                        'title': 'Chart Song',
                        'artists': [{'name': 'Chart Artist'}],
                        'thumbnails': [{'url': 'http://test.com/chart.jpg'}]
                    }
                ]
            }
            yield mock
    
    def test_home_page(self, client):
        """Test home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'SongHub' in response.data
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
    
    def test_search_endpoint(self, client, mock_ytmusic):
        """Test search functionality"""
        response = client.get('/search?q=test')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['results']) > 0
        assert data['results'][0]['title'] == 'Test Song'
    
    def test_search_empty_query(self, client):
        """Test search with empty query"""
        response = client.get('/search?q=')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['status'] == 'error'
        assert 'Query parameter is required' in data['message']
    
    def test_recommendations_endpoint(self, client, mock_ytmusic):
        """Test recommendations endpoint"""
        response = client.get('/recommendations')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'recommendations' in data
    
    def test_trending_endpoint(self, client, mock_ytmusic):
        """Test trending songs endpoint"""
        response = client.get('/trending')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'trending' in data
    
    def test_get_stream_url(self, client):
        """Test stream URL endpoint"""
        with patch('app.yt_dlp.YoutubeDL') as mock_ydl:
            mock_instance = MagicMock()
            mock_instance.extract_info.return_value = {
                'formats': [{
                    'url': 'http://test.com/stream.mp4',
                    'format_id': 'test',
                    'ext': 'mp4'
                }]
            }
            mock_ydl.return_value.__enter__.return_value = mock_instance
            
            response = client.get('/get_stream_url/test123')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['status'] == 'success'
            assert 'stream_url' in data
    
    def test_create_playlist(self, client):
        """Test playlist creation"""
        playlist_data = {
            'name': 'Test Playlist',
            'description': 'A test playlist'
        }
        response = client.post('/create_playlist', 
                             data=json.dumps(playlist_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'playlist_id' in data
    
    def test_add_to_playlist(self, client):
        """Test adding song to playlist"""
        # First create a playlist
        playlist_data = {'name': 'Test Playlist'}
        create_response = client.post('/create_playlist',
                                    data=json.dumps(playlist_data),
                                    content_type='application/json')
        playlist_id = json.loads(create_response.data)['playlist_id']
        
        # Add song to playlist
        song_data = {
            'playlist_id': playlist_id,
            'video_id': 'test123',
            'title': 'Test Song',
            'artist': 'Test Artist'
        }
        response = client.post('/add_to_playlist',
                             data=json.dumps(song_data),
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_get_playlists(self, client):
        """Test getting user playlists"""
        response = client.get('/playlists')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'playlists' in data
    
    def test_recently_played(self, client):
        """Test recently played endpoint"""
        response = client.get('/recently_played')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'recently_played' in data


class TestUtilityFunctions:
    """Test utility functions"""
    
    def test_extract_song_features(self):
        """Test song feature extraction"""
        song = {
            'title': 'Test Song',
            'artists': [{'name': 'Test Artist'}],
            'duration_seconds': 210,
            'year': 2023
        }
        features = extract_song_features(song)
        assert features['title'] == 'Test Song'
        assert features['artist'] == 'Test Artist'
        assert features['duration'] == 210
        assert features['year'] == 2023
    
    def test_extract_song_features_missing_data(self):
        """Test feature extraction with missing data"""
        song = {'title': 'Test Song'}
        features = extract_song_features(song)
        assert features['title'] == 'Test Song'
        assert features['artist'] == ''
        assert features['duration'] == 0
        assert features['year'] == 0
    
    def test_get_user_id(self):
        """Test user ID generation"""
        with app.test_request_context():
            user_id = get_user_id()
            assert isinstance(user_id, str)
            assert len(user_id) == 8
    
    def test_save_and_load_data(self):
        """Test data persistence"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                # Test saving data
                save_data()
                
                # Test loading data
                load_saved_data()
                
                # Check if files were created
                assert os.path.exists('playlists.pkl')
                assert os.path.exists('recently_played.pkl')
                assert os.path.exists('user_profiles.pkl')
                
            finally:
                os.chdir(original_cwd)


class TestErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.fixture
    def client(self):
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_invalid_video_id_stream(self, client):
        """Test stream URL with invalid video ID"""
        response = client.get('/get_stream_url/invalid_id')
        assert response.status_code == 200
        data = json.loads(response.data)
        # Should fallback to YouTube URL
        assert 'youtube.com' in data.get('stream_url', '')
    
    def test_malformed_json_playlist(self, client):
        """Test playlist creation with malformed JSON"""
        response = client.post('/create_playlist',
                             data='invalid json',
                             content_type='application/json')
        assert response.status_code == 400
    
    @patch('app.ytmusic.search')
    def test_ytmusic_api_failure(self, mock_search, client):
        """Test handling of YTMusic API failures"""
        mock_search.side_effect = Exception("API Error")
        
        response = client.get('/search?q=test')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['status'] == 'error'


if __name__ == '__main__':
    pytest.main([__file__])