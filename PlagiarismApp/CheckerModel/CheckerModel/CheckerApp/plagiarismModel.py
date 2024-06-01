import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Initialize NLTK resources
# nltk.download('punkt')

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Initialize Porter Stemmer
    stemmer = PorterStemmer()
    
    # Stemming tokens
    stemmed_tokens = [stemmer.stem(token) for token in tokens]
    
    # Join the stemmed tokens back into a single string
    preprocessed_text = ' '.join(stemmed_tokens)
    
    return preprocessed_text

def compare_texts(*texts):
    # Preprocess the texts
    preprocessed_texts = [preprocess_text(text) for text in texts]
    
    # Vectorize the preprocessed texts
    vectorizer = CountVectorizer().fit_transform(preprocessed_texts)
    
    # Calculate cosine similarity for all pairs of texts
    similarity_matrix = cosine_similarity(vectorizer)
    
    # Print similarity percentages for all pairs of texts
    for i in range(len(texts)):
        for j in range(i+1, len(texts)):
            similarity_percentage = similarity_matrix[i][j] * 100
            print("Similarity Percentage between Text {} and Text {}: {:.2f}%".format(i+1, j+1, similarity_percentage))

# Example usage:
text1 = ""
text2 = ""
text3 = ""

compare_texts(text1, text2, text3)
