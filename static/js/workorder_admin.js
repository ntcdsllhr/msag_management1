document.addEventListener('DOMContentLoaded', function () {
    const cardField = document.querySelector('#id_card_number'); // Replace with the actual ID of the card field
    const portField = document.querySelector('#id_dsl_port'); // Replace with the actual ID of the port field

    if (cardField && portField) {
        cardField.addEventListener('change', function () {
            const cardId = cardField.value;
            const apiUrl = portField.getAttribute('data-api-url').replace('{card_id}', cardId);

            if (cardId) {
                fetch(apiUrl)
                    .then(response => response.json())
                    .then(data => {
                        portField.innerHTML = ''; // Clear current options
                        const defaultOption = document.createElement('option');
                        defaultOption.value = '';
                        defaultOption.textContent = 'Select a Port';
                        portField.appendChild(defaultOption);

                        data.forEach(port => {
                            const option = document.createElement('option');
                            option.value = port.id;
                            option.textContent = `Port ${port.port_number}`;
                            portField.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error fetching ports:', error);
                    });
            } else {
                portField.innerHTML = '<option value="">Select a Card First</option>';
            }
        });
    }
});
