from datetime import datetime

def get_image_extension(value, default_value=None):
    index = value.rfind('.')
    before_get_queries = value.rfind('?')
    if index == -1:
        return default_value
    if before_get_queries == -1:
        return value[index + 1:]
    return value[index + 1:before_get_queries]


def generate_image_name(url):
    dt = datetime.now().strftime('%Y%m%d-%H%M%S')
    extension = get_image_extension(url, "")
    image_name = "".join(['IMG_', dt, '.', extension])
    return image_name