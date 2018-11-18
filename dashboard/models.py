from django.db import models
from django.utils import timezone


# Create your models here.
class ApiCall(models.Model):
    api_call_date=models.DateTimeField(default=timezone.now,verbose_name="Date/heure debut du call")
    api_res_date = models.DateTimeField(null=True,verbose_name="Date/heure reponse du call")
    api_verbe = models.CharField(max_length=20,verbose_name="Verbe")
    api_env = models.CharField(max_length=20,verbose_name="Environnement")
    api_user = models.CharField(null=True,max_length=50, verbose_name="UserName")
    api_url = models.CharField(max_length=300,verbose_name="URL")
    api_prefix_url=models.CharField(max_length=300,verbose_name="Prefixe URL")
    api_suffix_url = models.CharField(max_length=300,verbose_name="Suffixe URL")
    api_header = models.TextField(null=True,verbose_name="Request Header")
    api_payload = models.TextField(null=True,verbose_name="Payload")
    api_res_retcode = models.CharField(max_length=10,null=True,verbose_name="Code retour")
    api_res_header = models.TextField(null=True,verbose_name="Response Header")
    api_res_body=models.TextField(null=True,verbose_name="Response Body")

    class Meta:
        ordering = ['-api_call_date']

    def __str__(self):
        return self.api_suffix_url