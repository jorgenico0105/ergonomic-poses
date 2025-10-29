import cv2
import math
import os
import mediapipe as mp
from mediapipe.python.solutions.drawing_utils import DrawingSpec
import cloudinary.uploader

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

landmark_style_rojo = DrawingSpec(color=(0, 0, 255), thickness=2, circle_radius=3)
connection_style_rojo = DrawingSpec(color=(0, 0, 255), thickness=2)
landmark_style_verde = DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=3)
connection_style_verde = DrawingSpec(color=(0, 255, 0), thickness=2)


def process_video_posture(video_path, output_path):
    try:
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            return {
                'success': False,
                'error': 'No se pudo abrir el video'
            }

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = None

        pose = mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        total_frames = 0
        malas_posturas = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            total_frames += 1

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if out is None:
                h, w = frame.shape[:2]
                out = cv2.VideoWriter(output_path, fourcc, 20.0, (w, h))

            if results.pose_landmarks:
                es_mala_postura = analyze_and_annotate_frame(
                    frame,
                    results.pose_landmarks
                )

                if es_mala_postura:
                    malas_posturas += 1

            out.write(frame)

        cap.release()
        out.release()
        pose.close()

        try:
            upload_result = cloudinary.uploader.upload_large(
                output_path,
                resource_type="video",
                eager=[{"width": 1280, "height": 720, "crop": "pad"}]
            )
            video_url = upload_result['eager'][0]['secure_url']
        except Exception as e:
            return {
                'success': False,
                'error': f'Error al subir a Cloudinary: {str(e)}'
            }

        if os.path.exists(video_path):
            os.remove(video_path)

        return {
            'success': True,
            'total_frames': total_frames,
            'malas_posturas': malas_posturas,
            'cloudinary_url': video_url
        }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error al procesar video: {str(e)}'
        }


def analyze_and_annotate_frame(frame, pose_landmarks):
    left_ear = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_EAR]
    right_ear = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_EAR]
    left_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_shoulder = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    nose = pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE]
    left_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_hip = pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

    mid_hip_y = (left_hip.y + right_hip.y) / 2

    angulo_cuello = calcular_angulo_cuello(
        left_ear, right_ear,
        left_shoulder, right_shoulder
    )

    if angulo_cuello > 115 or angulo_cuello < 75:
        cuello_msg = "Cuello correcto"
        cuello_color = (0, 255, 0)
    elif 95 <= angulo_cuello <= 115:
        cuello_msg = "Cuello inclinado"
        cuello_color = (0, 0, 255)
    else:
        cuello_msg = "Cuello levemente inclinado"
        cuello_color = (0, 255, 255)

    cv2.putText(
        frame,
        f"{cuello_msg} ({angulo_cuello:.1f}°)",
        (50, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        cuello_color,
        2
    )

    es_mala_postura = False

    if abs(nose.y - mid_hip_y) < 0.15:
        es_mala_postura = True
        cv2.putText(
            frame,
            "Columna muy erguida",
            (50, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            2
        )
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=landmark_style_rojo,
            connection_drawing_spec=connection_style_rojo
        )
    else:
        cv2.putText(
            frame,
            "Postura correcta",
            (50, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )
        mp_drawing.draw_landmarks(
            frame,
            pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=landmark_style_verde,
            connection_drawing_spec=connection_style_verde
        )

    return es_mala_postura


def calcular_angulo_cuello(left_ear, right_ear, left_shoulder, right_shoulder):
    mid_ear_x = (left_ear.x + right_ear.x) / 2
    mid_ear_y = (left_ear.y + right_ear.y) / 2
    mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
    mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

    vect_x = mid_ear_x - mid_shoulder_x
    vect_y = mid_ear_y - mid_shoulder_y
    angulo_rad = math.atan2(vect_x, vect_y)
    angulo_deg = abs(math.degrees(angulo_rad))

    return angulo_deg
