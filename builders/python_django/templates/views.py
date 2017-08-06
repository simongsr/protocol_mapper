from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


{% for endpoint in endpoints %}
@require_http_methods(['{{ endpoint.modifiers.method[0]|core.extract_string_value }}'])
@login_required
def {{ endpoint.name }}(request):
    try:
        p = Poll.objects.get(pk=poll_id)
    except Poll.DoesNotExist:
        raise Http404("Poll does not exist")
    return render(request, 'polls/detail.html', {'poll': p})


{% endfor %}
