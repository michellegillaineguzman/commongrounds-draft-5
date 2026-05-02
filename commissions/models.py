from django.db import models
from accounts.models import Profile


class CommissionType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Commission(models.Model):
    STATUS_OPEN = "Open"
    STATUS_FULL = "Full"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_FULL, "Full"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.ForeignKey(
        CommissionType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="commissions",
    )
    maker = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="commissions_created",
    )
    people_required = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_on"]

    def __str__(self):
        return self.title


class Job(models.Model):
    STATUS_OPEN = "Open"
    STATUS_FULL = "Full"

    STATUS_CHOICES = [
        (STATUS_OPEN, "Open"),
        (STATUS_FULL, "Full"),
    ]

    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        related_name="jobs",
    )
    role = models.CharField(max_length=255)
    manpower_required = models.PositiveIntegerField(default=1)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )

    def __str__(self):
        return f"{self.role} for {self.commission.title}"


class JobApplication(models.Model):
    STATUS_PENDING = "Pending"
    STATUS_ACCEPTED = "Accepted"
    STATUS_REJECTED = "Rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    applicant = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="job_applications",
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    applied_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["job", "applicant"],
                name="unique_job_application_per_applicant",
            )
        ]

    def __str__(self):
        return f"{self.applicant} applied for {self.job}"