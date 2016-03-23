from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator


class SuperuserRequiredMixin(object):
    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super(SuperuserRequiredMixin, self).dispatch(
            request, *args, **kwargs)
