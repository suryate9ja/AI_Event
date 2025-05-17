# AI Event Intelligence & Instant Reel Generator

An AI-powered application that generates highlight reels from event videos, with features like face detection, emotion analysis, and interactive seating maps.

## Features

- 🎥 Automatic highlight reel generation
- 😊 Face detection and emotion analysis
- 🗺️ Interactive seating map visualization
- 🌓 Dark/Light mode support
- 📱 Responsive design with Apple-inspired UI

## Prerequisites

- Python 3.8+
- FFmpeg
- CUDA-capable GPU (optional, for faster processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-event-reel-generator.git
cd ai-event-reel-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download required models:
```bash
python download_models.py
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Upload your event videos (MP4 format)

4. Click "Generate" to create your highlight reel

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── download_models.py     # Script to download AI models
├── video_processing/      # Video processing modules
│   ├── face_analyzer.py   # Face detection and analysis
│   ├── reel_generator.py  # Video reel generation
│   └── audio_analyzer.py  # Audio analysis
└── models/               # AI model files
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- YOLOv8 for face detection
- Streamlit for the web interface
- Plotly for interactive visualizations 