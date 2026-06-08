import pytest
from unittest.mock import Mock, patch

from tracker import NtfyProvider


def test_ntfy_provider_init():
    """Test NtfyProvider initialization with base_url, topic_name, and auth_token."""
    base_url = "https://ntfy.sh"
    topic_name = "test-topic"
    auth_token = "test-token"
    
    provider = NtfyProvider(base_url, topic_name, auth_token)
    
    assert provider.base_url == base_url
    assert provider.topic_name == topic_name
    assert provider.auth_token == auth_token
    assert provider.url == f"{base_url}/{topic_name}"


def test_ntfy_provider_init_without_trailing_slash():
    """Test NtfyProvider initialization with base_url that has trailing slash."""
    base_url = "https://ntfy.sh/"
    topic_name = "test-topic"
    auth_token = "test-token"
    
    provider = NtfyProvider(base_url, topic_name, auth_token)
    
    assert provider.base_url == "https://ntfy.sh"
    assert provider.url == f"{base_url.rstrip('/')}/{topic_name}"


@patch("tracker.requests.post")
def test_ntfy_provider_send(mock_post):
    """Test NtfyProvider send method with mocked HTTP request."""
    base_url = "https://ntfy.sh"
    topic_name = "test-topic"
    auth_token = "test-token"
    
    provider = NtfyProvider(base_url, topic_name, auth_token)
    
    # Mock the response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Test sending notification
    title = "Test Title"
    message = "Test Message"
    
    provider.send(title, message)
    
    # Verify the request was made with correct parameters
    mock_post.assert_called_once_with(
        provider.url,
        data=message,
        headers={
            "Title": title,
            "Message": message,
            "Authorization": f"Bearer {auth_token}"
        }
    )


@patch("tracker.requests.post")
def test_ntfy_provider_send_with_none_auth_token(mock_post):
    """Test NtfyProvider send method with None auth_token."""
    base_url = "https://ntfy.sh"
    topic_name = "test-topic"
    auth_token = None
    
    provider = NtfyProvider(base_url, topic_name, auth_token)
    
    # Mock the response
    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Test sending notification
    title = "Test Title"
    message = "Test Message"
    
    provider.send(title, message)
    
    # Verify the request was made with correct parameters
    mock_post.assert_called_once_with(
        provider.url,
        data=message,
        headers={
            "Title": title,
            "Message": message,
            "Authorization": "Bearer None"
        }
    )

def test_ntfy_provider_with_actual_send():
    """This test is meant to be run manually with valid credentials."""
    base_url = "https://ntfy.sh"
    topic_name = "test-topic"
    auth_token = "your_actual_auth_token_here"

    provider = NtfyProvider(base_url, topic_name, auth_token)
    try:
        provider.send("Test Notification", "This is a test message from NtfyProvider.")
        print("Notification sent successfully. Check your ntfy client.")
    except Exception as e:
        print(f"Failed to send notification: {e}")
        