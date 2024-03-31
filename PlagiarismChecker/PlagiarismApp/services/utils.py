import datetime
import os
import base64
import tempfile
import PyPDF2
import uuid
import io
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from weasyprint import HTML
from pylovepdf.tools.officepdf import OfficeToPdf
from dotenv import load_dotenv
from ..models import Submission, PlagiarismReport
from django.core.exceptions import ValidationError

load_dotenv()

out_dir = os.path.join(os.getcwd(), "temp_dir")
if not os.path.exists(out_dir):
    os.mkdir(out_dir)


class PdfHelper(OfficeToPdf):
    def __init__(self, file_url: str):
        super().__init__(
            public_key=os.getenv("ILOVEPDF_PUBLIC_KEY", None),
            verify_ssl=True,
            proxies=None,
        )

        super().add_file(file_url)
        super().set_output_folder(out_dir)
        super().execute()
        super().download()
        super().delete_current_task()


class HTMLToPdf(HTML):
    def __new__(cls, *args, **kwargs):
        instance = super().__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.base64_pdf

    def __init__(self, string):
        super().__init__(string=string)
        pdf_bytes = self._generate_pdf()
        self.base64_pdf = base64.b64encode(pdf_bytes)

    def _generate_pdf(self):
        return super().write_pdf(bytes=True)


class PlagiarismCheckerService:
    def __init__(self, course_id: int, submission_id: uuid.UUID, student_id: uuid.UUID) -> None:
        self.course_id = course_id
        self.submission_id = submission_id
        self.student_id = student_id

        self.all_submissions = Submission.objects.filter(
            assignment__course__id=self.course_id
        ).exclude(id=self.submission_id)

        self.current_submission = Submission.objects.get(id=self.submission_id)

        self.report = []

    def extract_text_from_pdf(self, pdf_data):
        pdf_data = base64.b64decode(pdf_data)

        with io.BytesIO(pdf_data) as file_buffer:
            pdf_reader = PyPDF2.PdfReader(file_buffer)
            text = ''
            for page_num in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_num].extract_text()
        return text

    def preprocess_text(self, text):
        tokens = word_tokenize(text)
        stemmer = PorterStemmer()
        stemmed_tokens = [stemmer.stem(token) for token in tokens]
        preprocessed_text = ' '.join(stemmed_tokens)
        return preprocessed_text

    def compare_texts(self, text1, text2):
        preprocessed_texts = self.preprocess_text(text1), self.preprocess_text(text2)
        vectorizer = CountVectorizer().fit_transform(preprocessed_texts)
        similarity_matrix = cosine_similarity(vectorizer)
        return similarity_matrix[0][1]

    def compare_with_all_submissions(self):
        self.report = []
        current_text = self.extract_text_from_pdf(self.current_submission.file)
        
        for submission in self.all_submissions:
            comparison_text = self.extract_text_from_pdf(submission.file)
            similarity_percentage = self.compare_texts(current_text, comparison_text)
            if similarity_percentage > 35:  # Only include non-zero similarities
                similarity_report = {
                    "current_submission_id": str(self.current_submission.id),
                    "other_submission_id": str(submission.id),
                    "similarity_percentage": similarity_percentage * 100,
                }
                self.report.append(similarity_report)

    def store_similarity_results(self):
        try:
            similarity_results = []
            current_submission_id = str(self.current_submission.id)

            for report in self.report:
                similarity_results.append({
                    "current_submission_id": current_submission_id,
                    "other_submission_id": report["other_submission_id"],
                    "similarity_percentage": report["similarity_percentage"],
                })

            existing_report = PlagiarismReport.objects.filter(submission_id=current_submission_id).first()

            if existing_report:
                existing_report.similarity_results = similarity_results
                existing_report.save()
            else:
                plagiarism_report = PlagiarismReport(
                    similarity_results=similarity_results,
                    submission_id=current_submission_id,
                )
                plagiarism_report.save()

            return {"message": "Similarity results stored successfully."}

        except ValidationError as ve:
            error_message = "Validation error occurred: " + ", ".join(ve.messages)
            return {"message": error_message}

        except Exception as e:
            error_message = "An error occurred while storing similarity results: " + str(e)
            return {"message": error_message}


ACADEMIC_YEAR = (
    f"{datetime.datetime.now().year} - {int(datetime.datetime.now().year) + 1}"
)
