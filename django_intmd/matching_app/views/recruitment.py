import structlog
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.forms.recruitment import RecruitmentForm, SearchRecruitmentForm
from matching_app.models import Recruitment

RECRUITMENT_TIMELINE_PAGE_SIZE = 10

logger = structlog.get_logger(__name__)


@login_required
@require_http_methods(["GET"])
def recruitment_timeline(request: HttpRequest) -> HttpResponse:
    min_age = request.session.get("search_min_age")
    max_age = request.session.get("search_max_age")

    recruitments = Recruitment.objects.select_related("user").all()
    if min_age:
        recruitments = recruitments.filter(user__userprofile__age__gte=min_age)
    if max_age:
        recruitments = recruitments.filter(user__userprofile__age__lte=max_age)

    pagenator = Paginator(recruitments, RECRUITMENT_TIMELINE_PAGE_SIZE)
    page_number = request.GET.get("page", default=1)
    page_obj = pagenator.page(page_number)

    return render(
        request,
        "recruitment_timeline.html",
        {"page_obj": page_obj},
    )


@login_required
@require_http_methods(["GET", "POST"])
def recruitment_search(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = SearchRecruitmentForm(request.POST)
        if form.is_valid():
            request.session["search_min_age"] = form.cleaned_data["min_age"]
            request.session["search_max_age"] = form.cleaned_data["max_age"]
            return redirect("recruitment_timeline")
        else:
            logger.error("invalid search recruitment form", form_errors=form.errors)
    else:
        initial = {
            "min_age": request.session.get("search_min_age"),
            "max_age": request.session.get("search_max_age"),
        }
        form = SearchRecruitmentForm(initial=initial)
    return render(request, "recruitment_search.html", {"form": form})


@login_required
@require_http_methods(["GET"])
def recruitment_detail(request: HttpRequest, pk: int) -> HttpResponse:
    recruitment = get_object_or_404(Recruitment.objects.select_related("user"), pk=pk)
    return render(request, "recruitment_detail.html", {"recruitment": recruitment})


@login_required
@require_http_methods(["GET", "POST"])
def recruitment_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RecruitmentForm(request.POST)
        if form.is_valid():
            recruitment = form.save(commit=False)
            recruitment.user = request.user
            recruitment.save()
            return redirect("recruitment_timeline")
        else:
            logger.error("Invalid create recruitment form", error=form.errors)
    else:
        form = RecruitmentForm()

    return render(
        request,
        "recruitment_create.html",
        {"form": form},
    )


@login_required
@require_http_methods(["GET", "POST"])
def recruitment_update(request: HttpRequest, pk: int) -> HttpResponse:
    recruitment = get_object_or_404(Recruitment.objects.select_related("user"), pk=pk)
    if recruitment.user != request.user:
        logger.warning("User is not the owner of the recruitment", user=request.user, recruitment=recruitment)
        raise PermissionDenied

    if request.method == "POST":
        form = RecruitmentForm(request.POST, instance=recruitment)
        if form.is_valid():
            form.save()
            return redirect("recruitment_timeline")
        else:
            logger.error("Invalid update recruitment form", error=form.errors)
    else:
        form = RecruitmentForm(instance=recruitment)

    return render(
        request,
        "recruitment_update.html",
        {
            "form": form,
            "recruitment": recruitment,
        },
    )


@login_required
@require_http_methods(["DELETE"])
def recruitment_delete(request: HttpRequest, pk: int) -> JsonResponse:
    recruitment = get_object_or_404(Recruitment.objects.select_related("user"), pk=pk)
    if recruitment.user != request.user:
        logger.warning("User is not the owner of the recruitment", user=request.user, recruitment=recruitment)
        raise PermissionDenied

    recruitment.delete()
    return JsonResponse({"message": "Recruitment deleted successfully"}, status=200)
