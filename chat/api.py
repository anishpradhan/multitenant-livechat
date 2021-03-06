from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.http import JsonResponse, HttpResponse
from django.forms.models import model_to_dict
from wsgiref.util import FileWrapper
import json


@api_view(['POST'])
def create_room(request):
    if request.method == "POST":
        '''
        department -> member_id
        guest user id
        '''
        name = request.POST['name']
        support = request.POST['support_group']
        details = request.POST['question']
        support_group = SupportGroup.objects.get(name=support)
        support_id = support_group.id
        data = {
            'name': name,
            'support_group': support_id,
            'details': details
        }
        serializer = RoomSerializer(data=data)

        if serializer.is_valid():
            response = serializer.save()
            response = {
                'chat_id': str(response.id),
                'chat_name': response.name,
                'support_group': response.support_group.name,
            }
            response = json.dumps(response)

            return Response(data=json.loads(response), status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def fileUpload(request):
    if request.method == 'POST':

        file = request.FILES['file']

        if file:
            file_created = UploadedFile.objects.create(uploaded_by=request.POST['uploaded_by'], file=file)
            return JsonResponse(serialize_file_model(file_created))


@api_view(['GET'])
def fileDownload(request):
    if request.method == 'GET':
        file_id = request.GET['file_id']

        queryset = UploadedFile.objects.get(id=file_id)
        file_handle = queryset.file.path
        document = open(file_handle, 'rb')
        response = HttpResponse(FileWrapper(document), content_type='application/text')
        response['Content-Disposition'] = 'attachment; filename="%s"' % queryset.file.name
        return response