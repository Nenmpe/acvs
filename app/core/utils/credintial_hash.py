import json
import hashlib


def generate_credential_data_string(credential):
    data = {
        "student": credential.student.username,
        "degree": credential.degree_name,
        "field": credential.field_of_study,
        "issue_date": str(credential.issue_date),
        "grade": credential.grade,
    }

    return json.dumps(data, sort_keys=True)


def generate_credential_hash(credential):
    data_string = generate_credential_data_string(credential)

    return hashlib.sha256(data_string.encode()).hexdigest()