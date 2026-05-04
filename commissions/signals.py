from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import JobApplication
from .services import CommissionService


@receiver(post_save, sender=JobApplication)
def sync_statuses_after_application_save(sender, instance, **kwargs):
    job = instance.job
    CommissionService.sync_job_status(job)
    CommissionService.sync_commission_status(job.commission)


@receiver(post_delete, sender=JobApplication)
def sync_statuses_after_application_delete(sender, instance, **kwargs):
    job = instance.job
    CommissionService.sync_job_status(job)
    CommissionService.sync_commission_status(job.commission)