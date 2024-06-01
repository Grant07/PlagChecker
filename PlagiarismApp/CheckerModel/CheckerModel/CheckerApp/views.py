# detector/views.py

from django.shortcuts import render
from .utils import save_uploaded_file, extract_text_from_pdf, compare_texts

def upload_files(request):
    if request.method == 'POST' and request.FILES['pdf_file1'] and request.FILES['pdf_file2'] and request.FILES['pdf_file3']:
        pdf_files = [request.FILES['pdf_file1'], request.FILES['pdf_file2'], request.FILES['pdf_file3']]
        file_paths = [save_uploaded_file(pdf_file) for pdf_file in pdf_files]
        texts = [extract_text_from_pdf(file_path) for file_path in file_paths]

        for text in texts:
            print(text)
        
        similarity_matrix = compare_texts(*texts)
        
        # Process the similarity matrix to generate similarity report
        similarity_report = []
        for i in range(len(texts)):
            for j in range(i+1, len(texts)):
                similarity_percentage = similarity_matrix[i][j] * 100
                similarity_report.append({
                    'text1_index': i + 1,
                    'text2_index': j + 1,
                    'similarity_percentage': similarity_percentage
                })
        
        return render(request, 'report.html', {'similarity_report': similarity_report})
    return render(request, 'upload.html')
