import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from django.utils.translation import ugettext_lazy as _


class SupportGroup(models.Model):
    name = models.CharField(_("name"), max_length=225)
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='agent_support_groups')
    supervisors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='supervisor_support_groups')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Support group')
        verbose_name_plural = _('Support groups')


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return f"Uploaded_Files/user_{instance.uploaded_by}/{filename}"


class UploadedFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    uploaded_by = models.CharField(_("name"), max_length=255, null=True, blank=True)
    file = models.FileField(verbose_name=_("File"), blank=False, null=False, upload_to=user_directory_path)
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name=_("Upload date"))

    def __str__(self):
        return str(self.file.name)

    def get_file_name(self):
        return self.file.name.split("/")[-1]



class RoomManager(models.Manager):
    def get_query_set(self):
        return super(RoomManager, self).get_query_set().filter(ended=None)


class Room(models.Model):
    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    name = models.CharField(_("name"), max_length=255)
    details = models.TextField(blank=True)
    started = models.DateTimeField(auto_now=True)
    ended = models.DateTimeField(null=True, blank=True)
    agents = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='chats')
    objects = models.Manager()
    active = RoomManager()
    support_group = models.ForeignKey(SupportGroup, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.started}:{self.name}'

    def end(self):
        self.ended = datetime.now()
        self.save()

    # def is_active(self):
    #     return cac
    class Meta:
        # permissions = (
        #     ("chat_admin", "Chat Admin")
        # )
        verbose_name = _('Chat')
        verbose_name_plural = _('Chats')


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    name = models.CharField(max_length=255, blank=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    message = models.TextField()
    file = models.ForeignKey(UploadedFile, related_name='message', on_delete=models.DO_NOTHING, verbose_name=_("File"),
                             blank=True, null=True)
    sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sent}: "{self.message}" in Room "{self.room}"'

    def get_name(self):
        if self.agent:
            return self.agent.firstname or self.agent.Username
        else:
            return self.name

    class Meta:
        # ordering = ['-id']
        verbose_name = _('Chat message')
        verbose_name_plural = _('Chat messages')
