from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt  # for quick start with AJAX; add CSRF properly later
from django.utils import timezone

from .models import ZendeskAgent
from .forms import AgentForm

def index(request: HttpRequest) -> HttpResponse:
    # mimics setting session current_page
    request.session["current_page"] = "system_users"
    return render(request, "modules/agent_session_manager/system_users.html")

def get_users(request: HttpRequest) -> JsonResponse:
    # order by id desc
    rows = ZendeskAgent.objects.all().order_by("-id")
    data = []
    for r in rows:
        data.append({
            "id": r.id,
            "date_created": r.date_created.isoformat() if r.date_created else None,
            "email": r.email,
            "employee_id": r.employee_id,
            "username": r.username,
            "country": r.country,
            "status": r.status,
            "first_name": r.first_name,
            "last_name": r.last_name,
            "Actions": None,
        })

    meta = {
        "page": 1,
        "pages": 1,
        "perpage": -1,
        "total": rows.count(),
        "sort": "desc",
        "field": "id",
    }
    return JsonResponse({"meta": meta, "data": data})

@csrf_exempt
@require_POST
def add_user(request: HttpRequest) -> HttpResponse:
    """
    Create or update an agent.
    POST fields: email, employee_id, status, country, first_name, last_name, username, mode, user_id
    """
    form = AgentForm(request.POST)
    if not form.is_valid():
        # Return the first error message (like your echo + exit)
        return HttpResponse("; ".join([str(e) for e in form.errors.get("__all__", [])]) or "Invalid", status=400)

    cleaned = form.cleaned_data
    mode = (request.POST.get("mode") or "").strip()
    user_id = request.POST.get("user_id")
    if not mode:
        # CREATE
        obj = ZendeskAgent(
            email=cleaned["email"],
            employee_id=cleaned["employee_id"],
            first_name=cleaned["first_name"],
            last_name=cleaned["last_name"],
            username=cleaned["username"],
            status=cleaned["status"],
            country=cleaned["country"],
            date_created=timezone.now(),
        )
        # Note: other columns like password/salt/session_id left as-is (null)
        obj.save(using=None)  # default DB
    else:
        # UPDATE
        if not user_id:
            return HttpResponse("Missing user_id", status=400)
        obj = get_object_or_404(ZendeskAgent, id=int(user_id))
        obj.email       = cleaned["email"]
        obj.employee_id = cleaned["employee_id"]
        obj.first_name  = cleaned["first_name"]
        obj.last_name   = cleaned["last_name"]
        obj.username    = cleaned["username"]
        obj.status      = cleaned["status"]
        obj.country     = cleaned["country"]
        obj.save(using=None)

    return HttpResponse("success")

@csrf_exempt
@require_POST
def get_user_details_for_edit(request: HttpRequest) -> HttpResponse:
    try:
        user_id = int(request.POST.get("id", "0"))
    except ValueError:
        return HttpResponse("error", status=400)

    try:
        r = ZendeskAgent.objects.get(id=user_id)
    except ZendeskAgent.DoesNotExist:
        return HttpResponse("error", status=404)

    payload = [{
        "id": r.id,
        "email": r.email,
        "employee_id": r.employee_id,
        "first_name": r.first_name,
        "last_name": r.last_name,
        "username": r.username,
        "status": r.status,
        "country": r.country,
        "date_created": r.date_created.isoformat() if r.date_created else None,
        "session_id": r.session_id,
        "salt": r.salt,
    }]
    return JsonResponse(payload, safe=False)
