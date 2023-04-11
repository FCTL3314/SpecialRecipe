from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import ContextMixin, View


class TitleMixin(ContextMixin):
    title = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context


class LogoutRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('accounts:profile', args={request.user.slug}))
        return super().dispatch(request, *args, **kwargs)
