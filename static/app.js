document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('searchInput');
    const searchButton = document.getElementById('searchButton');
    const searchResults = document.getElementById('searchResults');
    const recommendationsSection = document.getElementById('recommendationsSection');
    const recommendationsList = document.getElementById('recommendationsList');
    const loadingSpinner = document.getElementById('loadingSpinner');

    // Search logic
    async function searchSongs() {
        const query = searchInput.value.trim();
        if (!query) {
            showError('Please enter a song name');
            return;
        }

        try {
            console.log('Searching for:', query);
            showLoading(true);
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query }),
            });

            const data = await response.json();
            console.log('Search response:', data);
            if (data.success && data.tracks && data.tracks.length > 0) {
                displaySearchResults(data.tracks);
            } else {
                showError(data.error || 'No songs found. Try a different search.');
            }
        } catch (error) {
            console.error('Search error:', error);
            showError('Failed to connect to server');
        } finally {
            showLoading(false);
        }
    }

    // Display search results
    function displaySearchResults(tracks) {
        console.log('Displaying search results:', tracks);
        searchResults.innerHTML = tracks.map(track => `
            <div class="song-card" data-track-id="${track.id}">
                <h4>${track.name}</h4>
                <p class="text-muted">${track.artist}</p>
                <small class="text-info">Click to get recommendations</small>
            </div>
        `).join('');

        // Click listeners for song cards
        document.querySelectorAll('.song-card').forEach(card => {
            card.addEventListener('click', () => {
                const trackId = card.dataset.trackId;
                console.log('Song card clicked - Track ID:', trackId);
                if (!trackId) {
                    console.error('No track ID found on clicked card');
                    return;
                }
                // Remove active class from all cards
                document.querySelectorAll('.song-card').forEach(c => c.classList.remove('active'));
                // Add active class to clicked card
                card.classList.add('active');
                getRecommendations(trackId);
            });
        });
    }

    // Get recommendations for selected song
    async function getRecommendations(trackId) {
        console.log('Getting recommendations for track:', trackId);
        try {
            showLoading(true);
            recommendationsSection.style.display = 'none';
            recommendationsList.innerHTML = ''; // Clear previous recommendations
            
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ track_id: trackId }),
            });

            const data = await response.json();
            console.log('Recommendations response:', data);
            
            if (data.success && data.recommendations && data.recommendations.length > 0) {
                displayRecommendations(data.recommendations);
            } else {
                showError(data.error || 'Could not find similar songs. Please try another track.');
                recommendationsSection.style.display = 'none';
            }
        } catch (error) {
            console.error('Recommendations error:', error);
            showError('Failed to get recommendations');
            recommendationsSection.style.display = 'none';
        } finally {
            showLoading(false);
        }
    }

    // Display recommendations
    function displayRecommendations(recommendations) {
        console.log('Displaying recommendations:', recommendations);
        
        // Create recommendation cards with enhanced info
        const recommendationsHTML = recommendations.map(song => `
            <div class="col-md-6 mb-3">
                <div class="recommendation-card">
                    <h5>${song.name}</h5>
                    <p class="mb-1">${song.artist}</p>
                    <div class="recommendation-details">
                        <div class="similarity-score">
                            Match: ${song.similarity}%
                        </div>
                        <div class="recommendation-reason">
                            ${song.reason}
                        </div>
                        ${song.preview_url ? `
                            <div class="preview-player mt-2">
                                <audio controls src="${song.preview_url}">
                                    Your browser does not support the audio element.
                                </audio>
                            </div>
                        ` : '<div class="text-muted small">No preview available</div>'}
                    </div>
                </div>
            </div>
        `).join('');
        
        // Update content and show the section
        recommendationsList.innerHTML = recommendationsHTML;
        recommendationsSection.style.display = 'block';
        
        // Scroll to recommendations
        recommendationsSection.scrollIntoView({ behavior: 'smooth' });
    }

    // Utility functions
    function showLoading(show) {
        loadingSpinner.style.display = show ? 'block' : 'none';
        searchButton.disabled = show;
    }

    function showError(message) {
        console.error('Error:', message);
        searchResults.innerHTML = `
            <div class="alert alert-warning">
                <strong>Oops!</strong> ${message}
            </div>
        `;
        recommendationsSection.style.display = 'none';
    }

    // Event listeners
    searchButton.addEventListener('click', searchSongs);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') searchSongs();
    });
});
