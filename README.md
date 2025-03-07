# VibeJam 🎵

VibeJam is an AI-powered music recommendation system that helps you discover new music using Spotify's extensive library. It uses a sophisticated 4-tier recommendation strategy to find songs that match your musical taste.

## Features

- **Smart Song Search**: Easily search for any song in Spotify's library
- **4-Tier Recommendation System**: Get highly accurate song recommendations
- **Preview Support**: Listen to 30-second previews of recommended songs
- **Beautiful UI**: Modern, responsive interface with a purple theme
- **Detailed Insights**: See similarity scores and recommendation reasons

## How It Works

VibeJam uses a 4-tier recommendation strategy to find the perfect songs for you:

1. **Artist's Top Tracks (90% similarity)**
   - Recommends other popular songs by the same artist
   - Perfect for discovering an artist's best work

2. **Related Artists (85% similarity)**
   - Finds songs from artists with similar musical styles
   - Great for branching out while staying within your comfort zone

3. **Spotify Smart Engine (80% similarity)**
   - Uses Spotify's recommendation engine with song features and genres
   - Helps discover hidden gems that match the song's style

4. **Artist-Only Fallback (70% similarity)**
   - Last resort recommendations from the same artist
   - Ensures you always get relevant suggestions

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd music
   ```

2. **Set Up Virtual Environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Spotify API**
   - Create a `.env` file in the project root
   - Add your Spotify API credentials:
     ```
     SPOTIFY_CLIENT_ID=your_client_id_here
     SPOTIFY_CLIENT_SECRET=your_client_secret_here
     ```

5. **Run the Application**
   ```bash
   python -m flask run --debug
   ```
   The app will be available at `http://localhost:5000`

## Usage

1. Enter a song name in the search bar
2. Click on a song from the search results
3. Get personalized recommendations with:
   - Similarity scores
   - Recommendation reasons
   - 30-second previews (when available)

## Dependencies

- Flask: Web framework
- Spotipy: Spotify API wrapper
- Python-dotenv: Environment variable management
- Other dependencies listed in `requirements.txt`

## Contributing

Feel free to open issues and submit pull requests to help improve VibeJam!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
