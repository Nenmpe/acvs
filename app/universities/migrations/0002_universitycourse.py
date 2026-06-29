from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("universities", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UniversityCourse",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("degree_name", models.CharField(max_length=255)),
                ("course_name", models.CharField(max_length=255)),
                ("field_of_study", models.CharField(max_length=255)),
                (
                    "university",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="courses",
                        to="universities.university",
                    ),
                ),
            ],
            options={
                "verbose_name": "University Course",
                "verbose_name_plural": "University Courses",
            },
        ),
        migrations.AlterUniqueTogether(
            name="universitycourse",
            unique_together={("university", "degree_name", "course_name", "field_of_study")},
        ),
    ]
