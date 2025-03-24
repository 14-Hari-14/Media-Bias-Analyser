document.addEventListener('DOMContentLoaded', (event) => {
    const urlParams = new URLSearchParams(window.location.search);
    const details = JSON.parse(urlParams.get('details'));

    const mainElement = document.querySelector('main.details');

    if (details) {
        for (const [key, value] of Object.entries(details)) {
            if (!value) continue;

            const detailElement = document.createElement('div');
            detailElement.classList.add('detail-item');

            const keyElement = document.createElement('h2');
            keyElement.textContent = key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
            detailElement.appendChild(keyElement);

            if (key === 'top_image') {
                const imgElement = document.createElement('img');
                imgElement.src = value;
                imgElement.classList.add('details-img');
                detailElement.appendChild(imgElement);
            } else if (['left', 'right', 'center'].includes(key)) {
                const listElement = document.createElement('ul');
                value.forEach(sentence => {
                    if (sentence.length >= 20) {
                        const listItem = document.createElement('li');
                        listItem.textContent = sentence;
                        listElement.appendChild(listItem);
                    }
                });
                detailElement.appendChild(listElement);
            } else {
                const valueElement = document.createElement('p');
                valueElement.textContent = value;
                detailElement.appendChild(valueElement);
            }

            mainElement.appendChild(detailElement);
        }
    } else {
        mainElement.textContent = 'No details available.';
    }
});