document.getElementById('recommendation-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const age = document.getElementById('age').value;
    const size = document.getElementById('size').value;
    const weather = document.getElementById('weather').value;
    const place = document.getElementById('place').value;
    const gender = document.getElementById('gender').value;
    const occasion = document.getElementById('occasion').value || 'casual';
    const style = document.getElementById('style').value || 'modern';

    const response = await fetch('/api/outfit_recommendations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ age, size, weather, place, gender, occasion, style })
    });

    const data = await response.json();
    const recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.innerHTML = `<pre>${JSON.stringify(data.recommendations, null, 2)}</pre>`;
});
