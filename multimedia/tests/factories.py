import factory

from multimedia.models import EncodeProfile


class EncodeProfileFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = EncodeProfile

    command = 'ffmpeg -y -i \"%(input)s\" -vn \"%(output)s\"'
    container = 'mp3'
    name = 'MP3 Audio'
