from django.views.generic import TemplateView

class AuthView(TemplateView):
    """
    Vista para renderizar un template donde se pueda interactuar con la API de usuarios.
    """
    template_name = "security/auth.html"