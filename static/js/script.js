async function sendMessage()
{
    const message = document.getElementById('message').value;
    const response = await fetch(
        '/chat',
        {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        }
    );

    const data = await response.json();
    document.getElementById('chat').innerHTML += `<p><strong>You:</strong> ${message}</p>`;
    document.getElementById('chat').innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
    document.getElementById('message').value = '';
        }