import cv2
import numpy as np
import mediapipe as mp


mp_pose = mp.solutions.pose

# Colores
GREEN = (0, 255, 0)
RED = (0, 0, 255)


def get_segment_colors(angles):

    colors = {}


    if 'left_hip' in angles and 'right_hip' in angles:
        avg_hip = (angles['left_hip'] + angles['right_hip']) / 2
        colors['hip'] = GREEN if 80 <= avg_hip <= 120 else RED
        colors['left_hip'] = GREEN if 80 <= angles['left_hip'] <= 120 else RED
        colors['right_hip'] = GREEN if 80 <= angles['right_hip'] <= 120 else RED


    if 'left_knee' in angles:
        colors['left_knee'] = GREEN if 80 <= angles['left_knee'] <= 110 else RED

    if 'right_knee' in angles:
        colors['right_knee'] = GREEN if 80 <= angles['right_knee'] <= 110 else RED

    if 'left_ankle' in angles:
        colors['left_ankle'] = GREEN if 80 <= angles['left_ankle'] <= 120 else RED

    if 'right_ankle' in angles:
        colors['right_ankle'] = GREEN if 80 <= angles['right_ankle'] <= 120 else RED

    if 'left_elbow' in angles:
        colors['left_elbow'] = GREEN if 90 <= angles['left_elbow'] <= 120 else RED

    if 'right_elbow' in angles:
        colors['right_elbow'] = GREEN if 90 <= angles['right_elbow'] <= 120 else RED

    if 'neck' in angles:
        colors['neck'] = GREEN if 130 <= angles['neck'] <= 180 else RED

    if 'left_shoulder' in angles:
        colors['left_shoulder'] = GREEN if 0 <= angles['left_shoulder'] <= 20 else RED

    if 'right_shoulder' in angles:
        colors['right_shoulder'] = GREEN if 0 <= angles['right_shoulder'] <= 20 else RED

    if 'left_wrist' in angles:
        colors['left_wrist'] = GREEN if 160 <= angles['left_wrist'] <= 190 else RED

    if 'right_wrist' in angles:
        colors['right_wrist'] = GREEN if 160 <= angles['right_wrist'] <= 190 else RED

    if 'visual' in angles:
        colors['visual'] = GREEN if 80 <= angles['visual'] <= 110 else RED

    return colors


def get_connection_color(start_idx, end_idx, segment_colors):

    if (start_idx == 11 and end_idx == 13):
        return segment_colors.get('left_shoulder', GREEN)

    if (start_idx == 12 and end_idx == 14):
        return segment_colors.get('right_shoulder', GREEN)

    if (start_idx == 13 and end_idx == 15):
        return segment_colors.get('left_elbow', GREEN)

    if (start_idx == 14 and end_idx == 16):
        return segment_colors.get('right_elbow', GREEN)


    if (start_idx == 15 and end_idx in [19, 17]):
        return segment_colors.get('left_wrist', GREEN)


    if (start_idx == 16 and end_idx in [20, 18]):
        return segment_colors.get('right_wrist', GREEN)


    if (start_idx == 11 and end_idx == 23) or (start_idx == 23 and end_idx == 25):
        return segment_colors.get('left_hip', GREEN)


    if (start_idx == 12 and end_idx == 24) or (start_idx == 24 and end_idx == 26):
        return segment_colors.get('right_hip', GREEN)


    if (start_idx == 25 and end_idx == 27):
        return segment_colors.get('left_knee', GREEN)


    if (start_idx == 26 and end_idx == 28):
        return segment_colors.get('right_knee', GREEN)


    if (start_idx == 27 and end_idx == 31):
        return segment_colors.get('left_ankle', GREEN)


    if (start_idx == 28 and end_idx == 32):
        return segment_colors.get('right_ankle', GREEN)


    if (start_idx in [7, 8] and end_idx == 0) or (start_idx == 0 and end_idx in [7, 8]):
        return segment_colors.get('visual', GREEN)


    if (start_idx == 0 or end_idx == 0) or \
       (start_idx in [11, 12] and end_idx in [11, 12]) or \
       (start_idx in [23, 24] and end_idx in [23, 24]) or \
       (start_idx in [11, 12] and end_idx in [23, 24]):
        return segment_colors.get('neck', GREEN)


    return GREEN


def get_landmark_color(idx, segment_colors):
    # Landmarks de hombro izquierdo (tronco-brazo)
    if idx == 11:  # left shoulder
        return segment_colors.get('left_shoulder', GREEN)

    # Landmarks de hombro derecho (tronco-brazo)
    if idx == 12:  # right shoulder
        return segment_colors.get('right_shoulder', GREEN)

    # Landmarks de codo izquierdo
    if idx == 13:  # left elbow
        return segment_colors.get('left_elbow', GREEN)

    # Landmarks de codo derecho
    if idx == 14:  # right elbow
        return segment_colors.get('right_elbow', GREEN)

    # Landmarks de muñeca izquierda
    if idx in [15, 17, 19]:  # left wrist, left pinky, left index
        return segment_colors.get('left_wrist', GREEN)

    # Landmarks de muñeca derecha
    if idx in [16, 18, 20]:  # right wrist, right pinky, right index
        return segment_colors.get('right_wrist', GREEN)

    # Landmarks de rodilla izquierda
    if idx == 25:
        return segment_colors.get('left_knee', GREEN)

    # Landmarks de rodilla derecha
    if idx == 26:
        return segment_colors.get('right_knee', GREEN)

    # Landmarks de tobillo izquierdo
    if idx in [27, 31]:
        return segment_colors.get('left_ankle', GREEN)

    # Landmarks de tobillo derecho
    if idx in [28, 32]:
        return segment_colors.get('right_ankle', GREEN)

    # Landmarks de cadera izquierda
    if idx == 23:
        return segment_colors.get('left_hip', GREEN)

    # Landmarks de cadera derecha
    if idx == 24:
        return segment_colors.get('right_hip', GREEN)

    # Landmarks de ángulo visual (cabeza)
    if idx in [0, 7, 8]:  # nose, left ear, right ear
        return segment_colors.get('visual', GREEN)

    # Landmarks de cuello/columna
    if idx in [0, 11, 12]:  # nose, shoulders
        return segment_colors.get('neck', GREEN)

    # Por defecto, verde
    return GREEN

def analyze_posture(image_file):
    try:
        image_bytes = image_file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return {
                'success': False,
                'error': 'No se pudo leer la imagen'
            }

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        with mp_pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        ) as pose:
            results = pose.process(image_rgb)

            if not results.pose_landmarks:
                return {
                    'success': False,
                    'error': 'No se detectó ninguna persona en la imagen'
                }

            landmarks = extract_landmarks(results.pose_landmarks)
            angles = calculate_angles(landmarks)
            is_good_posture = evaluate_posture(angles)

            annotated_image = image.copy()


            h, w, _ = annotated_image.shape


            segment_colors = get_segment_colors(angles)


            for connection in mp_pose.POSE_CONNECTIONS:
                start_idx = connection[0]
                end_idx = connection[1]

                start_landmark = results.pose_landmarks.landmark[start_idx]
                end_landmark = results.pose_landmarks.landmark[end_idx]

                start_x = int(start_landmark.x * w)
                start_y = int(start_landmark.y * h)
                end_x = int(end_landmark.x * w)
                end_y = int(end_landmark.y * h)


                connection_color = get_connection_color(start_idx, end_idx, segment_colors)

                cv2.line(annotated_image, (start_x, start_y), (end_x, end_y), connection_color, 10)

            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                x = int(landmark.x * w)
                y = int(landmark.y * h)

                landmark_color = get_landmark_color(idx, segment_colors)

                cv2.circle(annotated_image, (x, y), 3, landmark_color, 1)

            recommendations = generate_recommendations(angles)

            return {
                'success': True,
                'landmarks': landmarks,
                'angles': angles,
                'recommendations': recommendations,
                'processed_image': annotated_image,
                'is_good_posture': is_good_posture
            }

    except Exception as e:
        return {
            'success': False,
            'error': f'Error al procesar la imagen: {str(e)}'
        }

def extract_landmarks(pose_landmarks):
    landmarks = {}

    landmark_names = {
        0: 'nose',
        7: 'left_ear',
        8: 'right_ear',
        11: 'left_shoulder',
        12: 'right_shoulder',
        13: 'left_elbow',
        14: 'right_elbow',
        15: 'left_wrist',
        16: 'right_wrist',
        17: 'left_pinky',
        18: 'right_pinky',
        19: 'left_index',
        20: 'right_index',
        23: 'left_hip',
        24: 'right_hip',
        25: 'left_knee',
        26: 'right_knee',
        27: 'left_ankle',
        28: 'right_ankle',
        31: 'left_foot_index',
        32: 'right_foot_index'
    }

    for idx, name in landmark_names.items():
        landmark = pose_landmarks.landmark[idx]
        landmarks[name] = {
            'x': landmark.x,
            'y': landmark.y,
            'z': landmark.z
        }

    return landmarks


def calculate_angle(point1, point2, point3):

    a = np.array([point1['x'], point1['y']])
    b = np.array([point2['x'], point2['y']])
    c = np.array([point3['x'], point3['y']])

    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)

    if angle > 180.0:
        angle = 360 - angle

    return angle


def calculate_angles(landmarks):
    angles = {}

    try:
        angles['left_hip'] = calculate_angle(
            landmarks['left_shoulder'],
            landmarks['left_hip'],
            landmarks['left_knee']
        )

        angles['right_hip'] = calculate_angle(
            landmarks['right_shoulder'],
            landmarks['right_hip'],
            landmarks['right_knee']
        )

        angles['left_knee'] = calculate_angle(
            landmarks['left_hip'],
            landmarks['left_knee'],
            landmarks['left_ankle']
        )

        angles['right_knee'] = calculate_angle(
            landmarks['right_hip'],
            landmarks['right_knee'],
            landmarks['right_ankle']
        )

        angles['left_ankle'] = calculate_angle(
            landmarks['left_knee'],
            landmarks['left_ankle'],
            landmarks['left_foot_index']
        )

        angles['right_ankle'] = calculate_angle(
            landmarks['right_knee'],
            landmarks['right_ankle'],
            landmarks['right_foot_index']
        )

        angles['left_elbow'] = calculate_angle(
            landmarks['left_shoulder'],
            landmarks['left_elbow'],
            landmarks['left_wrist']
        )

        angles['right_elbow'] = calculate_angle(
            landmarks['right_shoulder'],
            landmarks['right_elbow'],
            landmarks['right_wrist']
        )

        mid_shoulder_x = (landmarks['left_shoulder']['x'] + landmarks['right_shoulder']['x']) / 2
        mid_shoulder_y = (landmarks['left_shoulder']['y'] + landmarks['right_shoulder']['y']) / 2
        mid_shoulder = {'x': mid_shoulder_x, 'y': mid_shoulder_y}

        mid_hip_x = (landmarks['left_hip']['x'] + landmarks['right_hip']['x']) / 2
        mid_hip_y = (landmarks['left_hip']['y'] + landmarks['right_hip']['y']) / 2
        mid_hip = {'x': mid_hip_x, 'y': mid_hip_y}

        angles['neck'] = calculate_angle(
            mid_hip,
            mid_shoulder,
            landmarks['nose']
        )

        angles['left_shoulder'] = calculate_angle(
            landmarks['left_hip'],
            landmarks['left_shoulder'],
            landmarks['left_elbow']
        )


        angles['right_shoulder'] = calculate_angle(
            landmarks['right_hip'],
            landmarks['right_shoulder'],
            landmarks['right_elbow']
        )

        left_hand_mid_x = (landmarks['left_index']['x'] + landmarks['left_pinky']['x']) / 2
        left_hand_mid_y = (landmarks['left_index']['y'] + landmarks['left_pinky']['y']) / 2
        left_hand_mid = {'x': left_hand_mid_x, 'y': left_hand_mid_y}

        angles['left_wrist'] = calculate_angle(
            landmarks['left_elbow'],
            landmarks['left_wrist'],
            left_hand_mid
        )


        right_hand_mid_x = (landmarks['right_index']['x'] + landmarks['right_pinky']['x']) / 2
        right_hand_mid_y = (landmarks['right_index']['y'] + landmarks['right_pinky']['y']) / 2
        right_hand_mid = {'x': right_hand_mid_x, 'y': right_hand_mid_y}

        angles['right_wrist'] = calculate_angle(
            landmarks['right_elbow'],
            landmarks['right_wrist'],
            right_hand_mid
        )


        mid_ear_x = (landmarks['left_ear']['x'] + landmarks['right_ear']['x']) / 2
        mid_ear_y = (landmarks['left_ear']['y'] + landmarks['right_ear']['y']) / 2
        mid_ear = {'x': mid_ear_x, 'y': mid_ear_y}

        angles['visual'] = calculate_angle(
            mid_shoulder,
            mid_ear,
            landmarks['nose']
        )

    except Exception as e:
        print(f"Error calculando ángulos: {e}")

    return angles


def evaluate_posture(angles):
    bad_angles = 0
    total_checks = 0

    if 'left_hip' in angles and 'right_hip' in angles:
        total_checks += 1
        avg_hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        if avg_hip_angle < 80 or avg_hip_angle > 120:
            bad_angles += 1

    if 'left_knee' in angles:
        total_checks += 1
        if angles['left_knee'] < 80 or angles['left_knee'] > 110:
            bad_angles += 1

    if 'right_knee' in angles:
        total_checks += 1
        if angles['right_knee'] < 80 or angles['right_knee'] > 110:
            bad_angles += 1

    if 'left_ankle' in angles:
        total_checks += 1
        if angles['left_ankle'] < 80 or angles['left_ankle'] > 120:
            bad_angles += 1

    if 'right_ankle' in angles:
        total_checks += 1
        if angles['right_ankle'] < 80 or angles['right_ankle'] > 120:
            bad_angles += 1

    if 'left_elbow' in angles:
        total_checks += 1
        if angles['left_elbow'] < 90 or angles['left_elbow'] > 120:
            bad_angles += 1

    if 'right_elbow' in angles:
        total_checks += 1
        if angles['right_elbow'] < 90 or angles['right_elbow'] > 120:
            bad_angles += 1

    if 'neck' in angles:
        total_checks += 1
        if angles['neck'] < 130 or angles['neck'] > 180:
            bad_angles += 1

    if 'left_shoulder' in angles:
        total_checks += 1
        if angles['left_shoulder'] < 0 or angles['left_shoulder'] > 20:
            bad_angles += 1

    if 'right_shoulder' in angles:
        total_checks += 1
        if angles['right_shoulder'] < 0 or angles['right_shoulder'] > 20:
            bad_angles += 1

    if 'left_wrist' in angles:
        total_checks += 1
        if angles['left_wrist'] < 160 or angles['left_wrist'] > 190:
            bad_angles += 1

    if 'right_wrist' in angles:
        total_checks += 1
        if angles['right_wrist'] < 160 or angles['right_wrist'] > 190:
            bad_angles += 1

    if 'visual' in angles:
        total_checks += 1
        if angles['visual'] < 80 or angles['visual'] > 110:
            bad_angles += 1

    if total_checks == 0:
        return True

    return bad_angles == 0


def generate_recommendations(angles):
    recommendations = []
    angle_info = []

    if 'left_hip' in angles and 'right_hip' in angles:
        avg_hip_angle = (angles['left_hip'] + angles['right_hip']) / 2
        angle_info.append({
            'segment': 'Cadera (tronco-muslo)',
            'current_angle': round(avg_hip_angle, 2),
            'optimal_range': '90-110°',
            'reference': 'Vertical vs horizontal',
            'status': 'correcto' if 80 <= avg_hip_angle <= 120 else 'incorrecto'
        })
        if avg_hip_angle < 80 or avg_hip_angle > 120:
            recommendations.append({
                'type': 'warning',
                'area': 'Cadera',
                'message': 'Ángulo de cadera fuera del rango óptimo (90-110°). Ajusta la posición del tronco.',
                'angle': round(avg_hip_angle, 2)
            })

    if 'left_knee' in angles and 'right_knee' in angles:
        avg_knee_angle = (angles['left_knee'] + angles['right_knee']) / 2
        angle_info.append({
            'segment': 'Rodilla (muslo-pierna)',
            'current_angle': round(avg_knee_angle, 2),
            'optimal_range': '90-100°',
            'reference': 'Horizontal vs vertical',
            'status': 'correcto' if 80 <= avg_knee_angle <= 110 else 'incorrecto'
        })
        if angles['left_knee'] < 80 or angles['left_knee'] > 110 or angles['right_knee'] < 80 or angles['right_knee'] > 110:
            recommendations.append({
                'type': 'warning',
                'area': 'Rodillas',
                'message': 'Ángulo de rodillas fuera del rango óptimo (90-100°). Ajusta la altura del asiento.',
                'angle': round(avg_knee_angle, 2)
            })

    if 'left_ankle' in angles and 'right_ankle' in angles:
        avg_ankle_angle = (angles['left_ankle'] + angles['right_ankle']) / 2
        angle_info.append({
            'segment': 'Tobillo (pierna-pie)',
            'current_angle': round(avg_ankle_angle, 2),
            'optimal_range': '90-100°',
            'reference': 'Pierna vs pie',
            'status': 'correcto' if 80 <= avg_ankle_angle <= 120 else 'incorrecto'
        })
        if angles['left_ankle'] < 80 or angles['left_ankle'] > 120 or angles['right_ankle'] < 90 or angles['right_ankle'] > 120:
            recommendations.append({
                'type': 'warning',
                'area': 'Tobillos',
                'message': 'Ángulo de tobillos fuera del rango óptimo (90-100°). Asegúrate de tener los pies planos en el suelo.',
                'angle': round(avg_ankle_angle, 2)
            })

    if 'left_elbow' in angles and 'right_elbow' in angles:
        avg_elbow_angle = (angles['left_elbow'] + angles['right_elbow']) / 2
        angle_info.append({
            'segment': 'Codo (brazo-antebrazo)',
            'current_angle': round(avg_elbow_angle, 2),
            'optimal_range': '90-100°',
            'reference': 'Brazo vs antebrazo',
            'status': 'correcto' if 90 <= avg_elbow_angle <= 120 else 'incorrecto'
        })
        if angles['left_elbow'] < 90 or angles['left_elbow'] > 120 or angles['right_elbow'] < 90 or angles['right_elbow'] > 120:
            recommendations.append({
                'type': 'warning',
                'area': 'Codos',
                'message': 'Ángulo de codos fuera del rango óptimo (90-100°). Antebrazo debe estar paralelo al escritorio.',
                'angle': round(avg_elbow_angle, 2)
            })

    if 'neck' in angles:
        angle_info.append({
            'segment': 'Cuello (alineación cabeza-tronco)',
            'current_angle': round(angles['neck'], 2),
            'optimal_range': '160-180°',
            'reference': 'Columna vertebral recta',
            'status': 'correcto' if 130 <= angles['neck'] <= 180 else 'incorrecto'
        })
        if angles['neck'] < 130 or angles['neck'] > 180:
            recommendations.append({
                'type': 'warning',
                'area': 'Cuello',
                'message': 'Cabeza no está alineada correctamente con el tronco (160-180°). Mantén el cuello recto.',
                'angle': round(angles['neck'], 2)
            })

    if 'left_shoulder' in angles and 'right_shoulder' in angles:
        avg_shoulder_angle = (angles['left_shoulder'] + angles['right_shoulder']) / 2
        angle_info.append({
            'segment': 'Hombro (brazo-tronco)',
            'current_angle': round(avg_shoulder_angle, 2),
            'optimal_range': '0-20°',
            'reference': 'Brazo respecto al eje del tronco',
            'status': 'correcto' if 0 <= avg_shoulder_angle <= 20 else 'incorrecto'
        })
        if angles['left_shoulder'] < 0 or angles['left_shoulder'] > 20 or angles['right_shoulder'] < 0 or angles['right_shoulder'] > 20:
            recommendations.append({
                'type': 'warning',
                'area': 'Hombros',
                'message': 'Ángulo de hombros fuera del rango óptimo (0-20°). Mantén los hombros relajados, sin elevación o tensión.',
                'angle': round(avg_shoulder_angle, 2)
            })

    if 'left_wrist' in angles and 'right_wrist' in angles:
        avg_wrist_angle = (angles['left_wrist'] + angles['right_wrist']) / 2
        angle_info.append({
            'segment': 'Muñeca (antebrazo-mano)',
            'current_angle': round(avg_wrist_angle, 2),
            'optimal_range': '0-15°',
            'reference': 'Eje del antebrazo respecto al dorso de la mano',
            'status': 'correcto' if 160 <= avg_wrist_angle <= 190 else 'incorrecto'
        })
        if angles['left_wrist'] < 160 or angles['left_wrist'] > 190 or angles['right_wrist'] < 160 or angles['right_wrist'] > 190:
            recommendations.append({
                'type': 'warning',
                'area': 'Muñecas',
                'message': 'Ángulo de muñecas fuera del rango óptimo (0-15°). Evita presión en el túnel carpiano manteniendo las muñecas rectas.',
                'angle': round(avg_wrist_angle, 2)
            })

    if 'visual' in angles:
        angle_info.append({
            'segment': 'Ángulo visual (cabeza-tronco)',
            'current_angle': round(angles['visual'], 2),
            'optimal_range': '10-20°',
            'reference': 'Línea del cuello respecto al eje del tronco',
            'status': 'correcto' if 80 <= angles['visual'] <= 110 else 'incorrecto'
        })
        if angles['visual'] < 80 or angles['visual'] > 110:
            recommendations.append({
                'type': 'warning',
                'area': 'Ángulo visual',
                'message': 'Ángulo visual fuera del rango óptimo (10-20°). Ajusta la inclinación de la cabeza para mirar la pantalla sin excesiva flexión del cuello.',
                'angle': round(angles['visual'], 2)
            })

    if not recommendations:
        recommendations.append({
            'type': 'success',
            'area': 'General',
            'message': 'Tu postura ergonómica es excelente. Todos los ángulos están dentro del rango óptimo.',
            'angle': None
        })

    return {
        'recommendations': recommendations,
        'angle_details': angle_info
    }
