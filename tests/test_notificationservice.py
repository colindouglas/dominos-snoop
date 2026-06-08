import pytest
from unittest.mock import Mock, patch

from tracker import NotificationService, PushoverProvider, NtfyProvider


def test_notification_service_init_no_providers():
    """Test NotificationService initialization with no providers configured."""
    config = {}
    
    service = NotificationService(config)
    
    assert len(service.providers) == 0


def test_notification_service_init_pushover_only():
    """Test NotificationService initialization with only Pushover provider."""
    config = {
        "pushover": {
            "user_key": "test_user_key",
            "app_token": "test_app_token"
        }
    }
    
    service = NotificationService(config)
    
    assert len(service.providers) == 1
    assert isinstance(service.providers[0], PushoverProvider)
    assert service.providers[0].user_key == "test_user_key"
    assert service.providers[0].app_token == "test_app_token"


def test_notification_service_init_ntfy_only():
    """Test NotificationService initialization with only Ntfy provider."""
    config = {
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic",
            "auth_token": "test-token"
        }
    }
    
    service = NotificationService(config)
    
    assert len(service.providers) == 1
    assert isinstance(service.providers[0], NtfyProvider)
    assert service.providers[0].base_url == "https://ntfy.sh"
    assert service.providers[0].topic_name == "test-topic"
    assert service.providers[0].auth_token == "test-token"


def test_notification_service_init_ntfy_without_auth_token():
    """Test NotificationService initialization with Ntfy provider but no auth_token."""
    config = {
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic"
        }
    }
    
    service = NotificationService(config)
    
    assert len(service.providers) == 1
    assert isinstance(service.providers[0], NtfyProvider)
    assert service.providers[0].auth_token is None


def test_notification_service_init_both_providers():
    """Test NotificationService initialization with both Pushover and Ntfy providers."""
    config = {
        "pushover": {
            "user_key": "test_user_key",
            "app_token": "test_app_token"
        },
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic",
            "auth_token": "test-token"
        }
    }
    
    service = NotificationService(config)
    
    assert len(service.providers) == 2
    
    # Check Pushover provider
    assert isinstance(service.providers[0], PushoverProvider)
    assert service.providers[0].user_key == "test_user_key"
    assert service.providers[0].app_token == "test_app_token"
    
    # Check Ntfy provider
    assert isinstance(service.providers[1], NtfyProvider)
    assert service.providers[1].base_url == "https://ntfy.sh"
    assert service.providers[1].topic_name == "test-topic"
    assert service.providers[1].auth_token == "test-token"


@patch("tracker.PushoverProvider.send")
@patch("tracker.NtfyProvider.send")
def test_notification_service_notify_no_providers(mock_ntfy_send, mock_pushover_send):
    """Test NotificationService notify method with no providers."""
    config = {}
    service = NotificationService(config)
    
    service.notify("Test Title", "Test Message")
    
    # No providers should be called
    mock_pushover_send.assert_not_called()
    mock_ntfy_send.assert_not_called()


@patch("tracker.PushoverProvider.send")
@patch("tracker.NtfyProvider.send")
def test_notification_service_notify_pushover_only(mock_ntfy_send, mock_pushover_send):
    """Test NotificationService notify method with only Pushover provider."""
    config = {
        "pushover": {
            "user_key": "test_user_key",
            "app_token": "test_app_token"
        }
    }
    service = NotificationService(config)
    
    service.notify("Test Title", "Test Message")
    
    # Only Pushover provider should be called
    mock_pushover_send.assert_called_once_with("Test Title", "Test Message")
    mock_ntfy_send.assert_not_called()


@patch("tracker.PushoverProvider.send")
@patch("tracker.NtfyProvider.send")
def test_notification_service_notify_ntfy_only(mock_ntfy_send, mock_pushover_send):
    """Test NotificationService notify method with only Ntfy provider."""
    config = {
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic",
            "auth_token": "test-token"
        }
    }
    service = NotificationService(config)
    
    service.notify("Test Title", "Test Message")
    
    # Only Ntfy provider should be called
    mock_ntfy_send.assert_called_once_with("Test Title", "Test Message")
    mock_pushover_send.assert_not_called()


@patch("tracker.PushoverProvider.send")
@patch("tracker.NtfyProvider.send")
def test_notification_service_notify_both_providers(mock_ntfy_send, mock_pushover_send):
    """Test NotificationService notify method with both providers."""
    config = {
        "pushover": {
            "user_key": "test_user_key",
            "app_token": "test_app_token"
        },
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic",
            "auth_token": "test-token"
        }
    }
    service = NotificationService(config)
    
    service.notify("Test Title", "Test Message")
    
    # Both providers should be called
    mock_pushover_send.assert_called_once_with("Test Title", "Test Message")
    mock_ntfy_send.assert_called_once_with("Test Title", "Test Message")


@patch("tracker.PushoverProvider.send")
@patch("tracker.NtfyProvider.send")
def test_notification_service_notify_provider_exception_handling(mock_ntfy_send, mock_pushover_send):
    """Test NotificationService notify method handles exceptions from providers."""
    # Make Pushover throw an exception
    mock_pushover_send.side_effect = Exception("Pushover error")
    
    config = {
        "pushover": {
            "user_key": "test_user_key",
            "app_token": "test_app_token"
        },
        "ntfy": {
            "base_url": "https://ntfy.sh",
            "topic_name": "test-topic",
            "auth_token": "test-token"
        }
    }
    service = NotificationService(config)
    
    # This should not raise an exception even though Pushover fails
    service.notify("Test Title", "Test Message")
    
    # Both providers should be called (the exception is caught)
    mock_pushover_send.assert_called_once_with("Test Title", "Test Message")
    mock_ntfy_send.assert_called_once_with("Test Title", "Test Message")