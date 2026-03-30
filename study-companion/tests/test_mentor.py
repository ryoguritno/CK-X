import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from bot.mentor import Mentor

@pytest.fixture
def mentor():
    return Mentor(host="http://localhost:11434", model="llama3.1:8b", timeout=10)

@pytest.mark.asyncio
async def test_explain_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "NetworkPolicy controls traffic between pods."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.explain("NetworkPolicy", "Task 10: Networking", phase=2)

    assert len(result) > 0

@pytest.mark.asyncio
async def test_hint_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "Think about how packets flow through iptables chains."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.hint("Step 2: Understand iptables", "Task 10: Networking")

    assert len(result) > 0

@pytest.mark.asyncio
async def test_quiz_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "Q: What does iptables ACCEPT do? A) ... B) ... C) ... D) ..."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.quiz("Task 10: Networking", phase=2)

    assert len(result) > 0

@pytest.mark.asyncio
async def test_is_reachable_true_on_200(mentor):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.is_reachable()

    assert result is True

@pytest.mark.asyncio
async def test_is_reachable_false_on_exception(mentor):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.is_reachable()

    assert result is False
