// Initialize the map centered on the world
const map = L.map('map').setView([20, 0], 2);

// Add the tile layer (OpenStreetMap)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

let markersLayer = L.layerGroup().addTo(map);
let fetchedDestinations = [];
let currentMonthIndex = 0;
let tripDurationDays = 7; // Default to 1 week
let specificDateRange = null;

// Expanded list of diverse global cities
const cityList = [
    "Tokyo", "Paris", "New York City", "Bali", "Cape Town", 
    "Sydney", "Rome", "London", "Bangkok", "Barcelona",
    "Rio de Janeiro", "Cairo", "Dubai", "Reykjavik", "Vancouver",
    "Marrakech", "Seoul", "Mexico City", "Buenos Aires", "Mumbai",
    "Singapore", "Athens", "Lisbon", "Amsterdam", "Hanoi"
];

// Color scale mapping
function getColor(rating) {
    const colors = { 5: '#22c55e', 4: '#a8e063', 3: '#facc15', 2: '#fb923c', 1: '#ef4444' };
    return colors[rating] || '#94a3b8';
}

// Calculate rating based on temperature
function calculateRating(temp) {
    if (temp >= 18 && temp <= 25) return 5;
    if (temp >= 12 && temp < 18 || temp > 25 && temp <= 30) return 4;
    if (temp > 30 && temp <= 35 || temp > 5 && temp < 12) return 3;
    return 2;
}

// Estimates precise weekly price range based on destination
function estimatePrice(cityName, country) {
    const tier1 = ["Switzerland", "Iceland", "Norway", "Singapore", "New York", "London", "Tokyo", "Paris", "Dubai"];
    const tier2 = ["Italy", "Spain", "Germany", "Netherlands", "Canada", "Australia", "Greece"];
    const tier3 = ["Thailand", "Vietnam", "Indonesia", "India", "Egypt", "Mexico", "South Africa", "Brazil", "Morocco"];
    
    let base = 1200; // Moderate base
    if (tier1.some(c => cityName.includes(c) || (country && country.includes(c)))) {
        base = 2500;
    } else if (tier3.some(c => cityName.includes(c) || (country && country.includes(c)))) {
        base = 600;
    } else if (tier2.some(c => cityName.includes(c) || (country && country.includes(c)))) {
        base = 1500;
    }

    // Adjust for trip duration (scaled roughly)
    const total = Math.round(base * (tripDurationDays / 7));
    const range = Math.round(total * 0.25);
    return `$${(total - range).toLocaleString()} - $${(total + range).toLocaleString()}`;
}

async function fetchClimateData(lat, lon) {
    const url = `https://archive-api.open-meteo.com/v1/archive?latitude=${lat}&longitude=${lon}&start_date=2023-01-01&end_date=2023-12-31&daily=temperature_2m_mean&timezone=auto`;
    const res = await fetch(url).then(r => r.json());
    return res.daily.temperature_2m_mean;
}

function getDayOfYear(date) {
    const start = new Date(date.getFullYear(), 0, 0);
    const diff = date - start;
    const oneDay = 1000 * 60 * 60 * 24;
    return Math.floor(diff / oneDay);
}

async function getInfoForLocation(lat, lon, name = null) {
    try {
        let country = "";
        if (!name) {
            const geoUrl = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}`;
            const geoRes = await fetch(geoUrl).then(r => r.json());
            name = geoRes.address.city || geoRes.address.town || geoRes.address.country || "Unknown";
            country = geoRes.address.country || "";
        }

        const wikiUrl = `https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro&explaintext&titles=${encodeURIComponent(name)}&format=json&origin=*`;
        const wikiRes = await fetch(wikiUrl).then(r => r.json());
        const page = Object.values(wikiRes.query.pages)[0];
        const summary = (page && page.extract) ? page.extract.substring(0, 150) + "..." : "A wonderful destination to explore.";

        const dailyTemps = await fetchClimateData(lat, lon);

        return {
            name: name,
            country: country,
            coords: [lat, lon],
            dailyTemps: dailyTemps,
            summary: summary
        };
    } catch (e) {
        return null;
    }
}

function updateMap() {
    markersLayer.clearLayers();

    // Determine target indices
    let targetIndices = [];
    if (specificDateRange) {
        const startIdx = getDayOfYear(new Date(specificDateRange.start));
        const endIdx = getDayOfYear(new Date(specificDateRange.end));
        for (let i = startIdx; i <= endIdx && i < 365; i++) targetIndices.push(i);
    } else {
        const start = currentMonthIndex * 30;
        for (let i = start; i < start + 30 && i < 365; i++) targetIndices.push(i);
    }

    const destinationsWithScore = fetchedDestinations.map(dest => {
        const temps = targetIndices.map(idx => dest.dailyTemps[idx]);
        const avgTemp = temps.reduce((a, b) => a + b, 0) / temps.length;
        return {
            ...dest,
            currentAvgTemp: avgTemp,
            currentRating: calculateRating(avgTemp)
        };
    });

    const topDestinations = destinationsWithScore
        .sort((a, b) => b.currentRating - a.currentRating)
        .slice(0, 10);

    topDestinations.forEach(dest => {
        const color = getColor(dest.currentRating);
        const price = estimatePrice(dest.name, dest.country);

        const circle = L.circleMarker(dest.coords, {
            radius: 14, fillColor: color, color: '#fff', weight: 3, fillOpacity: 0.9
        }).addTo(markersLayer);

        circle.bindPopup(`
            <div class="popup-content">
                <h3 style="margin-bottom:5px">${dest.name}</h3>
                <p><strong>Rating:</strong> ${dest.currentRating}/5 ⭐</p>
                <p><strong>Avg Temp:</strong> ${Math.round(dest.currentAvgTemp)}°C</p>
                <p><strong>Cost (${tripDurationDays} days):</strong> <span style="color:#10b981; font-weight:bold">${price}</span></p>
                <hr style="border:0; border-top:1px solid #eee; margin:10px 0">
                <p style="font-size:0.85rem">${dest.summary}</p>
            </div>
        `);
    });

    if (topDestinations.length > 0) {
        const group = new L.featureGroup(markersLayer.getLayers());
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

function handleDateChange() {
    const start = document.getElementById('start-date').value;
    const end = document.getElementById('end-date').value;
    
    if (start && end) {
        const d1 = new Date(start);
        const d2 = new Date(end);
        tripDurationDays = Math.max(1, Math.ceil((d2 - d1) / (1000 * 60 * 60 * 24)));
        specificDateRange = { start, end };
        updateMap();
    }
}

document.getElementById('month-select').addEventListener('change', (e) => {
    currentMonthIndex = parseInt(e.target.value);
    specificDateRange = null; // Clear specific dates when month is picked
    tripDurationDays = 7;     // Reset to 1 week
    updateMap();
});

document.getElementById('start-date').addEventListener('change', handleDateChange);
document.getElementById('end-date').addEventListener('change', handleDateChange);

map.on('click', async (e) => {
    const { lat, lng } = e.latlng;
    const tempMarker = L.marker([lat, lng]).addTo(map).bindPopup("Analyzing location...").openPopup();
    const newDest = await getInfoForLocation(lat, lng);
    map.removeLayer(tempMarker);
    if (newDest) {
        fetchedDestinations.push(newDest);
        updateMap();
    }
});

async function init() {
    const loading = document.getElementById('loading');
    for (const cityName of cityList) {
        const wikiUrl = `https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&titles=${encodeURIComponent(cityName)}&format=json&origin=*`;
        const wikiRes = await fetch(wikiUrl).then(r => r.json());
        const page = Object.values(wikiRes.query.pages)[0];
        if (page.coordinates) {
            const dest = await getInfoForLocation(page.coordinates[0].lat, page.coordinates[0].lon, cityName);
            if (dest) fetchedDestinations.push(dest);
        }
    }
    if (loading) loading.style.display = 'none';
    updateMap();
}

init();

map.on('click', async (e) => {
    const { lat, lng } = e.latlng;
    const tempMarker = L.marker([lat, lng]).addTo(map).bindPopup("Analyzing location...").openPopup();
    const newDest = await getInfoForLocation(lat, lng);
    map.removeLayer(tempMarker);

    if (newDest) {
        fetchedDestinations.push(newDest);
        updateMap();
    }
});

document.getElementById('month-select').addEventListener('change', (e) => {
    currentMonthIndex = parseInt(e.target.value);
    updateMap();
});

async function init() {
    const loading = document.getElementById('loading');
    
    // We scrape coordinates for our base list first
    for (const cityName of cityList) {
        const wikiUrl = `https://en.wikipedia.org/w/api.php?action=query&prop=coordinates&titles=${encodeURIComponent(cityName)}&format=json&origin=*`;
        const wikiRes = await fetch(wikiUrl).then(r => r.json());
        const page = Object.values(wikiRes.query.pages)[0];
        
        if (page.coordinates) {
            const dest = await getInfoForLocation(page.coordinates[0].lat, page.coordinates[0].lon, cityName);
            if (dest) fetchedDestinations.push(dest);
        }
    }
    
    if (loading) loading.style.display = 'none';
    updateMap();
}

init();
