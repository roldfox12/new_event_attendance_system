from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class College(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='students')
    id_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100, blank=True)
    school_year = models.CharField(max_length=20, blank=True)
    picture = models.ImageField(upload_to='student_pics/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.id_number}) - {self.college.name}"

class Event(models.Model):
    name = models.CharField(max_length=200)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='events')
    date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Attendance(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendances')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances')
    am_sign_in_time = models.DateTimeField(null=True, blank=True)
    am_sign_out_time = models.DateTimeField(null=True, blank=True)
    pm_sign_in_time = models.DateTimeField(null=True, blank=True)
    pm_sign_out_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.student.name} - {self.event.name}"

    class Meta:
        unique_together = ['event', 'student']

class SBOOfficerManager(BaseUserManager):
    def create_user(self, username, college, password=None):
        if not username:
            raise ValueError("SBO Officers must have a username")
        if not college:
            raise ValueError("SBO Officers must have a college")

        # If college is not a College instance, assume it's an ID and fetch the instance
        if not isinstance(college, College):
            try:
                college = College.objects.get(id=college)
            except College.DoesNotExist:
                raise ValueError(f"College with ID {college} does not exist.")

        user = self.model(
            username=username,
            college=college,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, college, password=None):
        user = self.create_user(
            username=username,
            college=college,
            password=password,
        )
        user.is_admin = True
        user.is_superuser = True  # Add is_superuser for PermissionsMixin
        user.save(using=self._db)
        return user

class SBOOfficer(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='sbo_officers')
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = SBOOfficerManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['college']

    def __str__(self):
        return f"{self.username} ({self.college.name})"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin

    @property
    def is_staff(self):
        return self.is_admin