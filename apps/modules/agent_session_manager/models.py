from django.db import models

class ZendeskAgent(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.TextField()
    password = models.TextField()
    employee_id = models.TextField(null=True, blank=True)
    first_name = models.TextField()
    last_name = models.TextField()
    username = models.TextField()
    session_id = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    salt = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "zendesk_agents"
        managed = True  # table already exists in MySQL

    @property
    def names(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
