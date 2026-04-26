"""Tests for the CivicSync application."""

import pytest
from unittest.mock import patch, MagicMock
from google.genai import errors

# Set environment variable for testing so module loading doesn't fail if testing locally
import os
os.environ["GOOGLE_API_KEY"] = "test_key"

from main import (
    generate_civic_content,
    handle_generation_error,
    MODEL_NAME
)


def test_generate_civic_content_success(mocker):
    """Test that content generation returns the expected text when API call succeeds."""
    mock_client = mocker.patch("main.genai.Client")
    mock_response = MagicMock()
    mock_response.text = "This is a mocked response."
    
    mock_client.return_value.models.generate_content.return_value = mock_response

    # Clear cache for the function to ensure the mock is hit during testing
    generate_civic_content.clear()
    
    result = generate_civic_content("Test prompt", "test_key")
    assert result == "This is a mocked response."
    
    # Verify the client was called with correct model
    mock_client.return_value.models.generate_content.assert_called_once()
    args, kwargs = mock_client.return_value.models.generate_content.call_args
    assert kwargs["model"] == MODEL_NAME
    assert kwargs["contents"] == "Test prompt"


def test_generate_civic_content_empty_response(mocker):
    """Test that ValueError is raised when the API returns an empty response."""
    mock_client = mocker.patch("main.genai.Client")
    mock_response = MagicMock()
    mock_response.text = None
    
    mock_client.return_value.models.generate_content.return_value = mock_response

    generate_civic_content.clear()

    with pytest.raises(ValueError, match="Received empty response from the model."):
        generate_civic_content("Test prompt", "test_key")


@patch("main.st")
def test_handle_generation_error_api_error_429(mock_st):
    """Test that handle_generation_error shows a specific message for 429 quota errors."""
    # errors.APIError requires response_json
    error = errors.APIError("429 RESOURCE_EXHAUSTED", {})
    handle_generation_error(error)
    mock_st.error.assert_called_once()
    assert "traffic" in mock_st.error.call_args[0][0].lower()


@patch("main.st")
def test_handle_generation_error_api_error_generic(mock_st):
    """Test that handle_generation_error shows a generic message for other API errors."""
    error = errors.APIError("500 Internal Server Error", {})
    handle_generation_error(error)
    mock_st.error.assert_called_once()
    assert "API error occurred" in mock_st.error.call_args[0][0]


@patch("main.st")
def test_handle_generation_error_unexpected(mock_st, capsys):
    """Test that handle_generation_error logs the error and shows a fallback message."""
    error = Exception("Unexpected failure")
    handle_generation_error(error)
    mock_st.error.assert_called_once()
    assert "unexpected error" in mock_st.error.call_args[0][0].lower()
    
    # Check that secure logging to print happened
    captured = capsys.readouterr()
    assert "Secure Log" in captured.out
    assert "Unexpected failure" in captured.out
