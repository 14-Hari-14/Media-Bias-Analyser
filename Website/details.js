document.addEventListener('DOMContentLoaded', (event) => {
    let details = JSON.parse(localStorage.getItem('myData')).result;
    const mainElement = document.querySelector('main.details');

    if (!details) {
        chrome.storage.local.get("myData", (result) => {
            if (result.myData) {
                console.log("Stored value:", result.myData);
                details = JSON.parse(result.myData).result;
                // Do something with parsedData if needed
            } else {
                console.error("No data found in chrome.storage.local");
            }
        });
    }

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
                    if (sentence.length >= 80) {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = sentence;
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