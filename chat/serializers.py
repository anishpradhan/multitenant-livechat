import os.path

from rest_framework import serializers
from .models import *


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['name', 'support_group', 'details']


def serialize_file_model(m: UploadedFile):
    return {
        'id': str(m.id),
        'url': m.file.url,
        'size': m.file.size,
        'name': os.path.basename(m.get_file_name()),
        'uploaded_by': m.uploaded_by
    }