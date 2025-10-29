import cloudinary.uploader
from io import BytesIO
import base64

def upload_image(image_data, folder='uploads', public_id=None):

    try:
        upload_options = {
            'folder': folder,
            'resource_type': 'image',
            'overwrite': True
        }

        if public_id:
            upload_options['public_id'] = public_id


        if hasattr(image_data, 'shape'):
            import cv2

            _, buffer = cv2.imencode('.jpg', image_data)
            image_bytes = BytesIO(buffer.tobytes())
            result = cloudinary.uploader.upload(image_bytes, **upload_options)

        else:
            result = cloudinary.uploader.upload(image_data, **upload_options)

        return {
            'success': True,
            'url': result['secure_url'],
            'public_id': result['public_id'],
            'format': result['format'],
            'width': result['width'],
            'height': result['height']
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def delete_image(public_id):
    """
    Eliminar imagen de Cloudinary

    Args:
        public_id: ID público de la imagen a eliminar

    Returns:
        dict: Resultado de la operación
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            'success': True,
            'result': result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def get_image_url(public_id, transformations=None):

    try:
        from cloudinary import CloudinaryImage

        if transformations:
            return CloudinaryImage(public_id).build_url(**transformations)
        return CloudinaryImage(public_id).build_url()

    except Exception as e:
        return None
