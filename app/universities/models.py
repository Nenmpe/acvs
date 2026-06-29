from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.TextField()
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UniversityCourse(models.Model):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    degree_name = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)

    class Meta:
        verbose_name = "University Course"
        verbose_name_plural = "University Courses"
        unique_together = ("university", "degree_name", "course_name", "field_of_study")

    def __str__(self):
        return f"{self.course_name} - {self.degree_name} ({self.field_of_study})"
