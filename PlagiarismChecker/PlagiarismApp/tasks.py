from celery import shared_task
from .services.utils import PlagiarismCheckerService
import uuid


@shared_task
def check_for_plagiarism(course_id: int, submission_id: uuid, student_id: uuid):

    checker = PlagiarismCheckerService(
        course_id=course_id, submission_id=submission_id, student_id=student_id
    )
    checker.compare_with_all_submissions()        

    return checker.store_similarity_results()