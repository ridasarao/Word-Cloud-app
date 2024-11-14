import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
from docx import Document
import base64
from io import BytesIO
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

# Functions for file reading
def read_txt(file):
    return file.getvalue().decode("utf-8")

def read_docx(file):
    doc = Document(file)
    return " ".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return " ".join([page.extract_text() for page in pdf.pages if page.extract_text()])

# Function to filter out stopwords
def filter_stopwords(text, additional_stopwords=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_stopwords))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# Function to create download link for plot
def get_image_download_link(buffered, format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Plot as {format_}</a>'

# Function to generate a download link for a DataFrame
def get_table_download_link(df, filename, file_label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{file_label}</a>'

# Streamlit app interface
st.subheader("📁 Upload a PDF, DOCX, or TXT file to generate a Word Cloud")

uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf", "docx"])

if uploaded_file:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
    st.write(file_details)

    # Read the file based on its type
    try:
        if uploaded_file.type == "text/plain":
            text = read_txt(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        else:
            st.error("File type not supported. Please upload a txt, pdf, or docx file.")
            st.stop()
    except Exception as e:
        st.error(f"An error occurred while reading the file: {e}")
        st.stop()

    # Generate and filter word count table
    words = text.split()
    word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)

    # Sidebar for options and filters
    with st.sidebar.expander("Word Cloud Options"):
        use_standard_stopwords = st.checkbox("Use standard stopwords?", True)
        top_words = word_count['Word'].head(50).tolist()
        additional_stopwords = st.multiselect("Additional stopwords:", sorted(top_words))
        
        if use_standard_stopwords:
            all_stopwords = STOPWORDS.union(set(additional_stopwords))
        else:
            all_stopwords = set(additional_stopwords)
        
        filtered_text = filter_stopwords(text, all_stopwords)

        # Word Cloud dimensions
        width = st.slider("Select Word Cloud Width", 400, 2000, 1200, 50)
        height = st.slider("Select Word Cloud Height", 200, 2000, 800, 50)

    # Generate Word Cloud
    st.subheader("Generated Word Cloud")
    fig, ax = plt.subplots(figsize=(width/100, height/100))  # Convert pixels to inches for figsize
    wordcloud_img = WordCloud(width=width, height=height, background_color='white', max_words=200, contour_width=3, contour_color='steelblue').generate(filtered_text)
    ax.imshow(wordcloud_img, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig)

    # Save plot function
    with st.expander("Save Options"):
        format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
        resolution = st.slider("Select Resolution", 100, 500, 300, 50)
        
        if st.button(f"Save as {format_}"):
            buffered = BytesIO()
            plt.savefig(buffered, format=format_, dpi=resolution)
            st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

    # Display Word Count Table at the end
    st.subheader("Word Count Table")
    st.write(word_count)
    
# Provide download link for table
    if st.button('Download Word Count Table as CSV'):
        st.markdown(get_table_download_link(word_count, "word_count.csv", "Click Here to Download"), unsafe_allow_html=True)

    # Sidebar: Author and social links
    with st.sidebar.expander("About the Creator"):
        st.markdown("Created by: [Rida Razzaq](https://github.com/ridasarao)")
        st.markdown("Contact: [Email](mailto:ridarazzaq89@gmail.com)")
        st.markdown("### Social Media Links")
        st.markdown("[GitHub](https://github.com/ridasarao) | [LinkedIn](https://www.linkedin.com/in/rida-razzaq-2a30ba257/) | [Kaggle](https://www.kaggle.com/ridarazzaq)")
