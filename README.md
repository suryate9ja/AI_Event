# AI Event Intelligence & Reel Generator

An AI-powered application that automatically generates highlight reels from event footage with intelligent guest mapping and face detection.

## Features

- 🎥 AI-powered video highlight detection
- 👤 Face detection and tracking
- 🎵 Audio analysis for key moments
- 🗺️ Interactive seating map visualization
- 🌓 Dark/Light mode support
- 🎨 Apple-inspired UI design

## Tech Stack

- Python (Streamlit, OpenCV, YOLOv8)
- React.js with TypeScript
- TailwindCSS
- Machine Learning (PyTorch)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/suryate9ja/AI_Event.git
cd AI_Event
```

2. Install Python dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

- `app.py`: Main Streamlit application
- `video_processing/`: Video analysis and reel generation
- `nlp_guest_mapping/`: Guest clustering and mapping
- `src/`: React frontend components
- `models/`: ML model files
- `utils/`: Helper functions

## License

MIT License
