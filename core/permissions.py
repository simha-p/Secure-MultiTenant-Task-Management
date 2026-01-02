from rest_framework.permissions import BasePermission

class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'MANAGER'


class ReporteeCanCompleteOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'REPORTEE':
            return request.data.get('status') == 'COMP'
        return True
