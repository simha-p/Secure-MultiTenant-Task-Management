from django.contrib import admin
from .models import User, Company, Task


# -----------------------------
# USER ADMIN
# -----------------------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'company')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.role == 'MANAGER':
            # Manager sees all users in their company
            return qs.filter(company=request.user.company)

        # Reportee sees only themselves
        return qs.filter(id=request.user.id)


# -----------------------------
# COMPANY ADMIN
# -----------------------------
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        # Manager & Reportee see only their company
        return qs.filter(id=request.user.company.id)


# -----------------------------
# TASK ADMIN
# -----------------------------
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'assigned_to', 'created_by', 'company')

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        if request.user.is_superuser:
            return qs

        if request.user.role == 'MANAGER':
            # Manager sees all tasks of company
            return qs.filter(company=request.user.company)

        # Reportee sees only assigned tasks
        return qs.filter(assigned_to=request.user)

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True

        if request.user.role == 'MANAGER':
            return True

        # Reportee can edit ONLY status
        if request.user.role == 'REPORTEE' and obj:
            return True

        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.role == 'REPORTEE':
            return (
                'title',
                'description',
                'categories',
                'assigned_to',
                'created_by',
                'company',
            )
        return ()
