from gte.models import Frame

IMAGE_URL_FORMAT = "https://wolfdw.pythonanywhere.com/static/frame_{}.jpeg"


def get_image_url(frame: Frame) -> str:
    return IMAGE_URL_FORMAT.format(frame.frame_id)
