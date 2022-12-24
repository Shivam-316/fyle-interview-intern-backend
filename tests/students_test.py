def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        }
    )

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_update_assignment_bad_assignment(client, h_student_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """

    content = 'TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

    new_content = 'UPDATED TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': 10000000,
            'content': new_content
        }
    )

    assert response.status_code == 404
    error_response = response.json

    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'No assignment with this id was found'


def test_update_assignment_not_draft(client, h_student_1):
    """
    failure case: If an assignment is not draft
    """

    content = 'TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': data['id'],
            'teacher_id': 2
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


    new_content = 'UPDATED TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': data['id'],
            'content': new_content
        }
    )

    assert response.status_code == 400
    error_response = response.json

    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only assignment in draft state can be edited'


def test_update_assignment_student_2(client, h_student_1):
    content = 'TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

    new_content = 'UPDATED TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': data['id'],
            'content': new_content
        }
    )

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == new_content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_update_assignment_student_2_cross(client, h_student_1, h_student_2):
    """
    failure case: assignment 1 was created by to student 1 and not student 2
    """
    content = 'TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

    new_content = 'WRONG UPDATED TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_2,
        json={
            'id': data['id'],
            'content': new_content
        })

    assert response.status_code == 400

    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'This assignment belongs to some other student'


def test_submit_assignment_bad_assignment(client, h_student_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": 100000,
            'teacher_id': 2
        }
    )

    assert response.status_code == 404
    error_response = response.json

    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'No assignment with this id was found'


def test_submit_assignment_no_teacher(client, h_student_1):
    """
    failure case: If an teacher does not exists
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": 2
        }
    )
    assert response.status_code == 400
    
    error_response = response.json

    assert error_response['error'] == 'ValidationError'


def test_submit_assignment_no_assignment(client, h_student_1):
    """
    failure case: If an teacher does not exists
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "teacher_id": 2
        }
    )
    assert response.status_code == 400
    
    error_response = response.json

    assert error_response['error'] == 'ValidationError'


def test_submit_assignment_bad_teacher(client, h_student_1):
    """
    failure case: If an teacher does not exists
    """
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": 2,
            'teacher_id': 100000
        }
    )
    assert response.status_code == 400
    
    error_response = response.json

    assert error_response['error'] == 'IntegrityError'


def test_submit_assignment_no_content(client, h_student_1):
    """
    failure case: Submitting assignment with no content
    """

    content = None

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        }
    )

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": data['id'],
            'teacher_id': 1
        }
    )
    assert response.status_code == 400
    error_response = response.json

    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'assignment with empty content cannot be submitted'
    

def test_submit_assignment_cross(client, h_student_1, h_student_2):
    """
    failure case: assignment 1 was created by to student 1 and not student 2
    """
    content = 'WRONG TESTSUBMIT'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None

    response = client.post(
        '/student/assignments/submit',
        headers=h_student_2,
        json={
            'id': data['id'],
            'teacher_id': 1
        })

    assert response.status_code == 400

    error_response = response.json
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'This assignment belongs to some other student'


def test_submit_assignment_student_1(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        }
    )

    assert response.status_code == 200

    data = response.json['data']
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2


def test_assingment_resubmitt_error(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'


def test_grade_assignment_student_forbidden(client, h_student_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_student_1
        , json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 403
    data = response.json

    assert data['error'] == 'FyleError'
