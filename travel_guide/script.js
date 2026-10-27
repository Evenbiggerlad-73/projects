// Initialize the map centered on the world
const map = L.map('map').setView([20, 0], 2);

// Add the tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// Color scale mapping from rating (1-5) to colors
function getColor(rating) {
    switch(rating) {
        case 5: return '#22c55e'; // Green (Best)
        case 4: return '#a8e063'; // Light Green (Great)
        case 3: return '#facc15'; // Yellow (Average)
        case 2: return '#fb923c'; // Orange (Not Ideal)
        case 1: return '#ef4444'; // Red (Avoid)
        default: return '#94a3b8';
    }
}

// Layer group to hold our circles so we can clear/update them
let markersLayer = L.layerGroup().addTo(map);

function updateMap(season) {
    // Clear existing markers
    markersLayer.clearLayers();

    destinations.forEach(dest => {
        const rating = dest.ratings[season];
        const color = getColor(rating);

        const circle = L.circleMarker(dest.coords, {
            radius: 12,
            fillColor: color,
            color: '#fff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.8
        });

        // Tooltip/Popup content
        const popupContent = `
            <div class="popup-content">
                <h3>${dest.name}</h3>
                <p><span class="label">Rating:</span> ${rating}/5 in ${season}</p>
                <p><span class="label">Weather:</span> ${dest.details.weather}</p>
                <p><span class="label">Avg Price:</span> ${dest.details.price}</p>
                <div class="tags">
                    ${dest.details.locations.map(loc => `<span class="tag">${loc}</span>`).join('')}
                </div>
            </div>
        `;

        circle.bindPopup(popupContent, {
            className: 'custom-popup'
        });

        // Hover effects
        circle.on('mouseover', function(e) {
            this.setStyle({
                weight: 4,
                fillOpacity: 1,
                radius: 15
            });
            this.openPopup();
        });

        circle.on('mouseout', function(e) {
            this.setStyle({
                weight: 2,
                fillOpacity: 0.8,
                radius: 12
            });
            // We don't automatically close popup on mouseout so user can read, 
            // but we could if we wanted a strictly "hover" feel.
        });

        circle.addTo(markersLayer);
    });
}

// Event listener for season change
document.getElementById('season-select').addEventListener('change', (e) => {
    updateMap(e.target.value);
});

// Initial load
updateMap('Spring');
