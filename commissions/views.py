from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, IntegerField, Value, When
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from .forms import CommissionForm, JobForm
from .models import Commission, Job, JobApplication
from .services import CommissionService


JobFormSet = inlineformset_factory(
    Commission,
    Job,
    form=JobForm,
    extra=1,
    can_delete=True,
)


def user_is_commission_maker(user):
    return (
        user.is_authenticated
        and hasattr(user, 'profile')
        and user.profile.has_role('Commission Maker')
    )


def sorted_commissions(queryset):
    return queryset.annotate(
        status_order=Case(
            When(status=Commission.STATUS_OPEN, then=Value(1)),
            When(status=Commission.STATUS_FULL, then=Value(2)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by("status_order", "-created_on")


def sorted_jobs(queryset):
    return queryset.annotate(
        status_order=Case(
            When(status=Job.STATUS_OPEN, then=Value(1)),
            When(status=Job.STATUS_FULL, then=Value(2)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by("status_order", "-manpower_required", "role")


def sorted_applications(queryset):
    return queryset.annotate(
        status_order=Case(
            When(status=JobApplication.STATUS_PENDING, then=Value(1)),
            When(status=JobApplication.STATUS_ACCEPTED, then=Value(2)),
            When(status=JobApplication.STATUS_REJECTED, then=Value(3)),
            default=Value(99),
            output_field=IntegerField(),
        )
    ).order_by("status_order", "-applied_on")


class CommissionListView(ListView):
    model = Commission
    template_name = "commissions/request_list.html"
    context_object_name = "all_commissions"

    def get_queryset(self):
        return sorted_commissions(Commission.objects.all())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated and hasattr(self.request.user, "profile"):
            profile = self.request.user.profile

            created_commissions = Commission.objects.filter(maker=profile)
            applied_commissions = Commission.objects.filter(
                jobs__applications__applicant=profile
            ).distinct()

            excluded_ids = list(created_commissions.values_list("id", flat=True)) + list(
                applied_commissions.values_list("id", flat=True)
            )

            context["created_commissions"] = sorted_commissions(created_commissions)
            context["applied_commissions"] = sorted_commissions(applied_commissions)
            context["all_commissions"] = sorted_commissions(
                Commission.objects.exclude(id__in=excluded_ids)
            )

        return context


class CommissionDetailView(DetailView):
    model = Commission
    template_name = "commissions/request_detail.html"
    context_object_name = "commission"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commission = self.object

        current_profile = None
        user_applications = []

        if self.request.user.is_authenticated and hasattr(self.request.user, "profile"):
            current_profile = self.request.user.profile
            user_applications = list(
                JobApplication.objects.filter(
                    applicant=current_profile,
                    job__commission=commission,
                ).values_list("job_id", flat=True)
    )

        context["current_profile"] = current_profile

        job_rows = []

        for job in sorted_jobs(commission.jobs.all()):
            accepted_count = job.applications.filter(
                status=JobApplication.STATUS_ACCEPTED
            ).count()

            is_full = job.status == Job.STATUS_FULL or accepted_count >= job.manpower_required
            display_status = Job.STATUS_FULL if is_full else job.status

            job_rows.append(
                {
                    "job": job,
                    "accepted_count": accepted_count,
                    "is_full": is_full,
                    "display_status": display_status,
                    "already_applied": job.id in user_applications,
                    "applications": sorted_applications(job.applications.all()),
                }
            )

        context["job_rows"] = job_rows
        context["summary"] = CommissionService.get_commission_summary(commission)

        return context


class CommissionCreateView(LoginRequiredMixin, CreateView):
    model = Commission
    form_class = CommissionForm
    template_name = "commissions/request_form.html"

    def dispatch(self, request, *args, **kwargs):
        if not user_is_commission_maker(request.user):
            return redirect("permission_denied")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job_formset"] = JobFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        job_formset = JobFormSet(self.request.POST)

        if job_formset.is_valid():
            jobs_data = [
                job_form.cleaned_data
                for job_form in job_formset
                if job_form.cleaned_data and not job_form.cleaned_data.get("DELETE")
            ]

            commission = CommissionService.create_commission(
                author=self.request.user.profile,
                data=form.cleaned_data,
                jobs_data=jobs_data,
            )

            return redirect("commissions:request_detail", pk=commission.pk)

        return self.render_to_response(
            self.get_context_data(form=form, job_formset=job_formset)
        )


class CommissionUpdateView(LoginRequiredMixin, UpdateView):
    model = Commission
    form_class = CommissionForm
    template_name = "commissions/request_form.html"
    context_object_name = "commission"

    def dispatch(self, request, *args, **kwargs):
        commission = self.get_object()

        if not user_is_commission_maker(request.user):
            return redirect("permission_denied")

        if commission.maker != request.user.profile:
            return redirect("permission_denied")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if "job_formset" not in context:
            context["job_formset"] = JobFormSet(
                self.request.POST or None,
                instance=self.object,
            )

        return context

    def form_valid(self, form):
        job_formset = JobFormSet(self.request.POST, instance=self.object)

        if job_formset.is_valid():
            commission = form.save(commit=False)
            commission.maker = self.object.maker
            commission.save()

            job_formset.instance = commission
            job_formset.save()

            CommissionService.sync_commission_status(commission)

            return redirect("commissions:request_detail", pk=commission.pk)

        return self.render_to_response(
            self.get_context_data(form=form, job_formset=job_formset)
        )


class ApplyToJobView(LoginRequiredMixin, View):
    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        if not hasattr(request.user, "profile"):
            return redirect("permission_denied")

        CommissionService.apply_to_job(
            applicant=request.user.profile,
            job=job,
        )

        return redirect("commissions:request_detail", pk=job.commission.pk)