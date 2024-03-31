# detector/utils.py

import os
import tempfile
import PyPDF2
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def save_uploaded_file(uploaded_file):
    _, file_extension = os.path.splitext(uploaded_file.name)
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        for chunk in uploaded_file.chunks():
            temp_file.write(chunk)
        return temp_file.name

def extract_text_from_pdf(pdf_file_path):
    with open(pdf_file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()
    return text

def preprocess_text(text):
    tokens = word_tokenize(text)
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    preprocessed_text = ' '.join(stemmed_tokens)
    return preprocessed_text

def compare_texts(*texts):
    preprocessed_texts = [preprocess_text(text) for text in texts]
    vectorizer = CountVectorizer().fit_transform(preprocessed_texts)
    similarity_matrix = cosine_similarity(vectorizer)
    return similarity_matrix
