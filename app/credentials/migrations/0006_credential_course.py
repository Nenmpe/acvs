from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("credentials", "0005_rename_hash_value_credential_credential_hash_value_and_more"),
        ("universities", "0002_universitycourse"),
    ]

    operations = [
        migrations.AddField(
            model_name="credential",
            name="course",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="credentials",
                to="universities.universitycourse",
            ),
        ),
    ]
