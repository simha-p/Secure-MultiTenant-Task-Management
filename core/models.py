from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

class Company(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, username, password=None, role='REPORTEE', company=None):
        if not username:
            raise ValueError("Username is required")

        user = self.model(
            username=username,
            role=role,
            company=company
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password):
        company, _ = Company.objects.get_or_create(name="ADMIN_COMPANY")

        user = self.model(
            username=username,
            role='MANAGER',
            company=company,
            is_staff=True,
            is_superuser=True
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('MANAGER', 'Manager'),
        ('REPORTEE', 'Reportee'),
    )

    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=True)  # 👈 allows admin login

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    objects = UserManager()

    def __str__(self):
        return self.username


class Task(models.Model):
    STATUS_CHOICES = (
        ('DEV', 'Development'),
        ('TEST', 'Testing'),
        ('STUCK', 'Stuck'),
        ('COMP', 'Completed'),
    )

    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    categories = models.CharField(max_length=200)

    assigned_to = models.ForeignKey(
        User,
        related_name='tasks',
        on_delete=models.CASCADE
    )
    created_by = models.ForeignKey(
        User,
        related_name='created_tasks',
        on_delete=models.CASCADE
    )
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
