function switchClub(clubId) {
    // Hide all sections
    document.querySelectorAll('.club-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));

    // Show selected section
    const targetSection = document.getElementById(`club-section-${clubId}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Set active tab styling
    event.currentTarget.classList.add('active');
}

function navigateVenue(venueName, lat, lng) {
    alert(`Triggering Campus Google Map Navigation to: ${venueName} (Lat: ${lat}, Lng: ${lng})`);
    // Here you can integrate with your existing Google Maps API component
    // e.g., window.parent.postMessage({ type: "FOCUS_MAP", lat: lat, lng: lng }, "*");
}
