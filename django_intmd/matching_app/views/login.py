import structlog
from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from matching_app.forms.login import LoginForm

logger = structlog.get_logger(__name__)


@require_http_methods(["GET", "POST"])
def login_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = authenticate(email=email, password=password)
            if user is None:
                logger.warning("login failed", email=email, password=password)
                return render(request, "login_error.html")
            login(request, user)
            return redirect("user_home")

        return render(request, "login.html", {"form": form})
    else:
        form = LoginForm()

    return render(request, "login.html", {"form": form})


@require_http_methods(["POST"])
def logout_view(request: HttpRequest) -> HttpResponse:
    logout(request)
    return redirect("index")
