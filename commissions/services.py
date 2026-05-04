from django.db import transaction
from django.db.models import Sum

from .models import Commission, Job, JobApplication


class CommissionService:
    @staticmethod
    @transaction.atomic
    def create_commission(author, data, jobs_data):
        commission = Commission.objects.create(
            title=data["title"],
            description=data["description"],
            type=data["type"],
            maker=author,
            people_required=data["people_required"],
            status=data["status"],
        )

        for job_data in jobs_data:
            if job_data:
                Job.objects.create(
                    commission=commission,
                    role=job_data["role"],
                    manpower_required=job_data["manpower_required"],
                    status=job_data.get("status", Job.STATUS_OPEN),
                )

        return commission

    @staticmethod
    def sync_job_status(job):
        accepted_count = job.applications.filter(
            status=JobApplication.STATUS_ACCEPTED
        ).count()

        if accepted_count >= job.manpower_required:
            new_status = Job.STATUS_FULL
        else:
            new_status = Job.STATUS_OPEN

        if job.status != new_status:
            job.status = new_status
            job.save(update_fields=["status"])

        return job

    @staticmethod
    def apply_to_job(applicant, job):
        job = CommissionService.sync_job_status(job)

        already_applied = JobApplication.objects.filter(
            applicant=applicant,
            job=job,
        ).exists()

        if already_applied:
            return None

        if job.status == Job.STATUS_FULL:
            return None

        application = JobApplication.objects.create(
            applicant=applicant,
            job=job,
        )

        CommissionService.sync_job_status(job)
        CommissionService.sync_commission_status(job.commission)

        return application

    @staticmethod
    def sync_commission_status(commission):
        jobs = list(commission.jobs.all())

        for job in jobs:
            CommissionService.sync_job_status(job)

        if jobs and all(job.status == Job.STATUS_FULL for job in jobs):
            commission.status = Commission.STATUS_FULL
        else:
            commission.status = Commission.STATUS_OPEN

        commission.save(update_fields=["status"])
        return commission

    @staticmethod
    def get_commission_summary(commission):
        total_manpower = commission.jobs.aggregate(
            total=Sum("manpower_required")
        )["total"] or 0

        accepted_count = JobApplication.objects.filter(
            job__commission=commission,
            status=JobApplication.STATUS_ACCEPTED,
        ).count()

        return {
            "total_manpower": total_manpower,
            "open_manpower": total_manpower - accepted_count,
        }