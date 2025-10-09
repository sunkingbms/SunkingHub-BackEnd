from django.db import models
from django.contrib.auth.models import Group, Permission

# Create your models here.
class Role(Group):
    """
        Role model inheriting from Django's Group
        Each Role can have permissions and be assigned to users
    """
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'Role'
        verbose_name_plural = "Roles"
        
    def __str__(self):
        return self.name