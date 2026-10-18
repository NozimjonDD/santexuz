from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from .development import local_preview_enabled


@method_decorator(xframe_options_exempt, name="dispatch")
class MiniAppView(TemplateView):
    template_name = "8mobile/home.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), "local_preview_enabled": local_preview_enabled(self.request)}

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response["Content-Security-Policy"] = "frame-ancestors 'self' https://web.telegram.org https://*.telegram.org https://telegram.org"
        response["Cache-Control"] = "no-store"
        return response
