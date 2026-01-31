from django.shortcuts import render


def access_denied(request):
    """
    Custom view for access denied page.
    """
    return render(request, "403.html", status=403)
