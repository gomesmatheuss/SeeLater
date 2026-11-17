
import os
import pathlib


TWEET_CACHE_DIR = "./storage/data/tweets"
TWEET_THUMBNAIL_DIR = os.path.join(
    TWEET_CACHE_DIR,
    "thumbnails"
)
TWEET_MEDIA_DIR = os.path.join(
    TWEET_CACHE_DIR,
    "media"
)


# Cria os diretórios caso ainda não existam.
for directory in [
    TWEET_THUMBNAIL_DIR,
    TWEET_MEDIA_DIR
]:
    pathlib.Path(directory).mkdir(
        parents=True,
        exist_ok=True
    )


def get_tweet_thumbnail_path(tweet_id):
    """
    Retorna o caminho da thumbnail de um tweet.
    """

    if not tweet_id:
        return None

    return os.path.join(
        TWEET_THUMBNAIL_DIR,
        f"{tweet_id}.jpg"
    )


def get_tweet_media_path(tweet_id, image_index):
    """
    Retorna o caminho de uma imagem relacionada ao tweet.
    """

    if not tweet_id:
        return None

    tweet_media_dir = os.path.join(
        TWEET_MEDIA_DIR,
        str(tweet_id)
    )

    pathlib.Path(tweet_media_dir).mkdir(
        parents=True,
        exist_ok=True
    )

    return os.path.join(
        tweet_media_dir,
        f"{image_index}.jpg"
    )
