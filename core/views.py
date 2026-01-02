from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User, Task, Company
from .serializers import TaskSerializer
from .permissions import IsManager
from .throttles import LoginThrottle, TaskCreateThrottle
from django.http import HttpResponse


class ManagerSignup(APIView):
    def post(self, request):
        company = Company.objects.create(name=request.data['company'])
        User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            role='MANAGER',
            company=company
        )
        return Response({"message": "Manager registered"})


class LoginView(APIView):
    throttle_classes = [LoginThrottle]

    def post(self, request):
        user = authenticate(
            username=request.data['username'],
            password=request.data['password']
        )
        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token)
        })


class CreateReportee(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        User.objects.create_user(
            username=request.data['username'],
            password=request.data['password'],
            role='REPORTEE',
            company=request.user.company
        )
        return Response({"message": "Reportee created"})


class CreateTask(APIView):
    permission_classes = [IsAuthenticated, IsManager]
    throttle_classes = [TaskCreateThrottle]

    def post(self, request):
        Task.objects.create(
            title=request.data['title'],
            description=request.data['description'],
            status='DEV',
            categories=request.data['categories'],
            assigned_to_id=request.data['assigned_to'],
            created_by=request.user,
            company=request.user.company
        )
        return Response({"message": "Task created"})


class ListTasks(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(company=request.user.company)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)


class UpdateTask(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        task = Task.objects.get(pk=pk, company=request.user.company)
        if request.user.role == 'REPORTEE' and request.data['status'] != 'COMP':
            return Response({"error": "Only COMPLETE allowed"}, status=403)
        task.status = request.data['status']
        task.save()
        return Response({"message": "Updated"})


class ExportTasks(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.append(["Title", "Status", "Assigned To"])

        for t in Task.objects.filter(company=request.user.company):
            ws.append([t.title, t.status, t.assigned_to.username])

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=tasks.xlsx'
        wb.save(response)
        return response
