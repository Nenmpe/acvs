from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_student_universityadmin_verifier"),
        ("universities", "0002_universitycourse"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="students",
                to="universities.universitycourse",
            ),
        ),
    ]
