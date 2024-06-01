import re
import os

pattern = r'({%[\s]*static[\s]*[\W])([a-zA-Z0-9//.]+)([\W][\s]*%})'
replacement = r'/static/\2'  # Corrected replacement string

def replace_in_files(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.html'):  # You can adjust the file extension as needed
                file_path = os.path.join(root, file_name)
                with open(file_path, 'r') as file:
                    content = file.read()
                updated_content = re.sub(pattern, replacement, content)
                with open(file_path, 'w') as file:
                    file.write(updated_content)

# Replace content in the current directory and subdirectories
replace_in_files('.')
