from django.db import models
from django.contrib.postgres.fields import JSONField
from django.conf import settings
import re

# TODO: add id, indexes
# TODO: template group and template spaces
# TODO: user auth, maker-checker, changelog track


class Template(models.Model):

    name = models.CharField(max_length=1000)
    default_version_id = models.IntegerField(null=True)
    attributes = JSONField(default=dict)  # TODO: default callable add from settings
    created_on = models.DateTimeField(auto_now_add=True) # TODO: Timezone support check
    modified_on = models.DateTimeField(auto_now=True)
    deleted_on = models.DateTimeField(null=True)

    class Meta:
        db_table = "editor_template"

    def clean(self):
        # all validations here
        if self.default_version_id and (TemplateVersion.objects.get(id=self.default_version_id).id != self.default_version_id):
            raise ValidationError({'default_version_id': _("specified id doesn't correspond to same template version")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Template, self).save(*args, **kwargs)


class TemplateVersion(models.Model):
    STATUS_CHOICES = [
        ("D", "DRAFT"),
        ("R", "READY"),
        ("L", "LIVE"),
    ]

    template_id = models.ForeignKey(Template, on_delete=models.PROTECT)
    data = models.TextField(blank=True)
    version = models.CharField(max_length=50)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    sample_context_data = JSONField(default=dict)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    deleted_on = models.DateTimeField(null=True)

    class Meta:
        db_table = "editor_template_version"
        unique_together = ("template_id", "version")

    def clean(self):
        # all validations here
        if self.version and not re.fullmatch("\d+\.\d+", self.version):
            raise ValidationError({'version': _("version must be specified like 1.3")})

    def save(self, *args, **kwargs):
        self.full_clean()
        super(TemplateVersion, self).save(*args, **kwargs)

