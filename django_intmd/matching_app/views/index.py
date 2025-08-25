from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from matching_app.forms.login import LoginForm
from matching_app.views.login import login_view


def index(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        return login_view(request)
    else:
        form = LoginForm()

    return render(request, "index.html", {"form": form})
