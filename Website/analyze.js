const form = document.getElementById('articleLinkForm');
const resultContainer = document.getElementById('resultContainer');
const spinner = document.createElement('div');
spinner.className = 'spinner';
spinner.innerHTML = '<div class="loader"></div>';
form.addEventListener('submit', handleFormSubmit);

async function handleFormSubmit(event) {
    event.preventDefault();
    const input = form.querySelector('.linkInput');
    const url = input.value;

    resultContainer.innerHTML = '';
    resultContainer.appendChild(spinner);

    try {
        const response = await fetch('http://127.0.0.1:8000/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text:url, url:true })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const result = await response.json();
        displayResult(result);
    } catch (error) {
        console.error('Error:', error);
        resultContainer.innerHTML = '<p class="error">There was an error processing your request. Please try again later.</p>';
    } finally {
        spinner.remove();
    }
}

function displayResult(result) {
    const params = new URLSearchParams({ details: JSON.stringify(result) });
    window.location.href = `details.html?${params.toString()}`;
}