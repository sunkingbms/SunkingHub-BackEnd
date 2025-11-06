from django import forms
from .models import ZendeskAgent

class AgentForm(forms.ModelForm):
    mode = forms.CharField(required=False)  # '' or 'edit'
    user_id = forms.IntegerField(required=False)

    class Meta:
        model = ZendeskAgent
        fields = ["email", "employee_id", "first_name", "last_name", "username", "country"]

    def clean(self):
        cleaned = super().clean()
        email = (cleaned.get("email") or "").strip()
        employee_id = (cleaned.get("employee_id") or "").strip()
        first_name = (cleaned.get("first_name") or "").strip()
        last_name = (cleaned.get("last_name") or "").strip()
        username = (cleaned.get("username") or "").strip()
        status = (cleaned.get("status") or "ACTIVE").strip()
        country = (cleaned.get("country") or "").strip()

        if not first_name: raise forms.ValidationError("First Name missing")
        if not last_name:  raise forms.ValidationError("Last Name missing")
        if not username:   raise forms.ValidationError("Username missing")
        if not email:      raise forms.ValidationError("Email missing")
        if not employee_id:raise forms.ValidationError("Employee ID missing")
        if not status:     raise forms.ValidationError("Status missing")
        if not country:    raise forms.ValidationError("Country missing")

        user_id = self.data.get("user_id")
        qs = ZendeskAgent.objects.all()

        if user_id:
            qs_username = qs.exclude(id=user_id).filter(username=username)
            qs_empid   = qs.exclude(id=user_id).filter(employee_id=employee_id)
            qs_email   = qs.exclude(id=user_id).filter(email=email)
        else:
            qs_username = qs.filter(username=username)
            qs_empid   = qs.filter(employee_id=employee_id)
            qs_email   = qs.filter(email=email)

        if qs_username.exists(): raise forms.ValidationError("Username is already taken.")
        if qs_empid.exists():    raise forms.ValidationError("Employee ID is already taken.")
        if qs_email.exists():    raise forms.ValidationError("Email address is registered with us.")

        # Trimmed fields back
        cleaned["email"] = email
        cleaned["employee_id"] = employee_id
        cleaned["first_name"] = first_name
        cleaned["last_name"] = last_name
        cleaned["username"] = username
        cleaned["status"] = status
        cleaned["country"] = country
        return cleaned
