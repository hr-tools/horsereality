import re

page_regex = re.compile(r'^https?:\/\/(?:(?:www|v2)\.)?horsereality\.com')
horse_page_regex = re.compile(r'^https?:\/\/(?:(?:www|v2)\.)?horsereality\.com\/horses\/(\d{1,10})')
layer_path_regex = re.compile(r'^(?:https:\/\/(?:(?:www|v2)\.)?horsereality\.com)?(\/upload\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z]+\/[a-z0-9]+)\.png$')


def get_lifenumber_from_url(url: str) -> int:
    if not isinstance(url, str):
        return None

    match = horse_page_regex.match(url)
    if not match:
        return None

    lifenumber = match.group(1)
    if not lifenumber:
        return None

    return int(lifenumber)
