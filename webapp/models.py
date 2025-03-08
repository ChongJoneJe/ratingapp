from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Module(models.Model):
    code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.code} {self.name}"


class Professor(models.Model):
    professor_id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.professor_id}, {self.name}"


class ModuleInstance(models.Model):
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    year = models.IntegerField()  # e.g. 2018 representing 2018-19 academic year
    semester = models.IntegerField()  # e.g. 1 or 2
    professors = models.ManyToManyField(Professor)

    def __str__(self):
        profs = ", ".join([p.professor_id for p in self.professors.all()])
        return f"{self.module.code} {self.module.name} {self.year} S{self.semester} taught by {profs}"


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    module_instance = models.ForeignKey(ModuleInstance, on_delete=models.CASCADE)
    professor = models.ForeignKey(Professor, on_delete=models.CASCADE)
    rating = models.IntegerField()  # between 1 and 5

    def __str__(self):
        return f"{self.professor.professor_id} rated {self.rating} by {self.user.username}"
    
    class Meta:
        unique_together = ('user', 'module_instance', 'professor')
