# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based REST API for postural/ergonomic analysis using MediaPipe and OpenCV. The application processes images of people to detect body landmarks, calculate joint angles, and provide ergonomic recommendations based on posture analysis.

## Development Commands

### Environment Setup
```bash
# Create virtual environment (if not exists)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration
Create a `.env` file with the following variables:
- `CLOUDINARY_CLOUD_NAME` - Cloudinary cloud name
- `CLOUDINARY_API_KEY` - Cloudinary API key
- `CLOUDINARY_API_SECRET` - Cloudinary API secret
- `OPENAI_API_KEY` - OpenAI API key for Vision and GPT models
- `FLASK_ENV` - Environment mode (development/production)
- `PORT` - Server port (defaults to 5000)
- `SECRET_KEY` - Flask secret key (defaults to 'dev-secret-key' in development)

### Running the Application
```bash
# Development mode
python app.py

# Or using Flask CLI
flask run
```

The server runs on `http://0.0.0.0:{PORT}` (default port 5000).

## Architecture

### Application Factory Pattern
The app uses Flask's application factory pattern:
- `app.py` - Entry point that calls `create_app()` and runs the server
- `app/__init__.py` - Contains `create_app(config_name)` factory function
- Configurations loaded from `app/config/config.py` based on environment

### Configuration System
Three configuration classes in `app/config/config.py`:
- `Config` - Base configuration with common settings
- `DevelopmentConfig` - Development-specific settings (DEBUG=True)
- `ProductionConfig` - Production-specific settings (DEBUG=False)

Configuration includes file upload limits (16MB max) and allowed image extensions.

### Blueprint-Based Module System
The application is organized using Flask Blueprints for modularity. Each feature is a separate module in `app/modules/`:

**Current Modules:**
- `analisis_ergonomico` - Image-based ergonomic analysis registered at `/api/analisis-ergonomico`
- `analisis_postural` - Video-based posture analysis registered at `/api/analisis-postural`

**Module Structure:**
```
app/modules/[module_name]/
  __init__.py       # Module initialization
  routes.py         # Blueprint with API endpoints
```

**Adding New Modules:**
1. Create new directory under `app/modules/[module_name]/`
2. Create `__init__.py` and `routes.py` with Blueprint
3. Register blueprint in `app/__init__.py` using `app.register_blueprint()`

### Helper Utilities (`app/utils/`)

**mediapipe_helper.py** - Core posture analysis logic:
- `analyze_posture(image_file)` - Main function that processes images and returns analysis results
- `extract_landmarks(pose_landmarks)` - Extracts 21 key body landmarks (nose, ears, shoulders, elbows, wrists, hand indices/pinkies, hips, knees, ankles, foot indices)
- `calculate_angles(landmarks)` - Computes 11 joint angles: left/right hip, knee, ankle, elbow, shoulder, wrist, plus neck alignment and visual angle
- `evaluate_posture(angles)` - Determines if posture is good (all angles within optimal ranges)
- `generate_recommendations(angles)` - Returns ergonomic recommendations based on angle thresholds
- Uses MediaPipe Pose with `static_image_mode=True`, `model_complexity=1`, `min_detection_confidence=0.5`
- Annotates images with green landmarks (good posture) or red landmarks (bad posture)

**Ergonomic Angle Thresholds:**
- Hip (tronco-muslo): 90-110°
- Knee (muslo-pierna): 90-100°
- Ankle (pierna-pie): 90-100°
- Elbow (brazo-antebrazo): 90-100°
- Neck (cabeza-tronco alignment): 160-180°
- Shoulder (brazo-tronco): 0-20°
- Wrist (antebrazo-mano): 0-15°
- Visual angle (cabeza-tronco): 10-20°

**cloudinary_helper.py** - Image storage integration:
- `upload_image(image_data, folder, public_id)` - Uploads to Cloudinary, handles numpy arrays from cv2
- `delete_image(public_id)` - Removes images from Cloudinary
- `get_image_url(public_id, transformations)` - Generates URLs with optional transformations

**openai_helper.py** - AI-powered ergonomic analysis:
- `generate_ergonomic_report(client, image_url, angles, angle_details, recommendations, is_good_posture)` - Generates comprehensive workplace ergonomic report using OpenAI Vision API (gpt-4o)
- `generate_ergonomic_report_with_local_image(client, image_array, ...)` - Alternative version that works with local numpy arrays instead of URLs
- Uses vision capabilities to analyze workspace setup (furniture, equipment, lighting)
- Provides detailed recommendations for immediate and long-term improvements
- Identifies ergonomic risks and suggests preventive exercises
- Returns JSON-structured report with executive summary, critical points, recommendations, and ergonomic scoring (0-100)

**video_posture_helper.py** - Video posture analysis logic:
- `process_video_posture(video_path, output_path)` - Main function that processes videos frame by frame at 20 fps
- `analyze_and_annotate_frame(frame, pose_landmarks)` - Analyzes a single frame and adds visual annotations
- `calcular_angulo_cuello(left_ear, right_ear, left_shoulder, right_shoulder)` - Calculates neck angle based on ear/shoulder positions
- Uses MediaPipe Pose with `static_image_mode=False`, `model_complexity=1`, `min_detection_confidence=0.5`, `min_tracking_confidence=0.5`
- Detects bad posture when spine is too upright (abs(nose.y - mid_hip_y) < 0.15)
- Neck angle evaluation: correct if >115° or <75°, incorrect if 95-115°, slight issue if between
- Annotates frames with red (bad posture) or green (good posture) landmarks
- Uploads processed videos to Cloudinary using `upload_large()` with eager transformations (1280x720, padded)
- Cleans up uploaded video but preserves output video for local downloads

### API Endpoints

**Root Endpoints:**
- `GET /` - API information and available modules
- `GET /health` - Health check endpoint

**Análisis Ergonómico Module (`/api/analisis-ergonomico`):**
- `POST /analyze` - Main endpoint: accepts `image` file upload, returns analysis with landmarks, angles, recommendations, and processed image URL
- `GET /test` - Module health check
- `GET /info` - Module documentation

**Análisis Postural Module (`/api/analisis-postural`):**
- `POST /analizar-postura` - Main endpoint: accepts `video` file upload, processes frame by frame, returns statistics and processed video URL
- `GET /download/<filename>` - Download processed video file locally
- `GET /test` - Module health check
- `GET /info` - Module documentation

## Key Dependencies

- **Flask 3.0.0** - Web framework
- **flask-cors 4.0.0** - CORS support (enabled for all origins)
- **mediapipe 0.10.9** - Pose detection and landmark extraction
- **opencv-python 4.9.0.80** - Image processing
- **cloudinary 1.37.0** - Image storage and delivery
- **openai 2.6.1** - OpenAI API client for Vision and GPT models
- **python-dotenv 1.0.0** - Environment variable management

## Important Patterns

### Error Handling
Helper functions return structured dictionaries with `success` boolean and `error` field:
```python
{
    'success': False,
    'error': 'Error message'
}
```

### Image Processing Flow (with AI Enhancement)
1. Receive image via Flask request.files
2. Process with MediaPipe to detect pose landmarks
3. Calculate ergonomic angles from landmarks (11 angles total)
4. Generate basic recommendations based on angle thresholds
5. Annotate image with color-coded landmarks (green=correct, red=incorrect)
6. Upload annotated image to Cloudinary
7. Send image URL + biomechanical data to OpenAI Vision API (gpt-4o)
8. Generate comprehensive ergonomic report with workplace analysis
9. Return JSON with:
   - Biomechanical analysis (landmarks, angles, basic recommendations)
   - Processed image URL
   - AI-generated detailed report (workspace analysis, risks, exercises, scoring)

### Cloudinary Integration
Cloudinary is initialized in `create_app()` using config values. Processed media is stored in specific folders:
- Images: `analisis-ergonomico` folder with IDs like `analysis_{uuid}`
- Videos: Uploaded using `upload_large()` with eager transformations (1280x720, padded)

### Video Processing Flow
1. Receive video via Flask request.files
2. Save video to `uploaded_videos/` directory with unique ID
3. Process video frame by frame with MediaPipe Pose
4. Analyze each frame for neck angle and spine alignment
5. Annotate frames with colored landmarks (red=bad posture, green=good)
6. Write processed frames to output video in `output_videos/`
7. Upload processed video to Cloudinary
8. Clean up input video, keep output video for local download
9. Return JSON with statistics (total frames, bad postures) and video URLs

### Local Video Storage
- `uploaded_videos/` - Temporary storage for uploaded videos (deleted after processing)
- `output_videos/` - Processed videos available for download via `/api/analisis-postural/download/<filename>`
- Both directories are gitignored and created automatically on first use
