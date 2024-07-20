import os
import ast
import fitz  # PyMuPDF

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
from utils import scrape_linkedin_job, extract_skills, create_dir

load_dotenv()
downloads_folder = create_dir()

# Initialize session state variables if not already done
if "url" not in st.session_state:
    st.session_state.url = ""
if "url_type" not in st.session_state:
    st.session_state.url_type = "linkedin"
if "job_details" not in st.session_state:
    st.session_state.job_details = {
        'job_title': "",
        'company_name': "",
        'job_description': ""
    }
if "analytical_skills" not in st.session_state:
    st.session_state.analytical_skills = []
if "technical_skills" not in st.session_state:
    st.session_state.technical_skills = []
if "checked_analytical_skills" not in st.session_state:
    st.session_state.checked_analytical_skills = []
if "checked_technical_skills" not in st.session_state:
    st.session_state.checked_technical_skills = []
if "confirmed" not in st.session_state:
    st.session_state.confirmed = False

st.session_state.resume_files = []
st.session_state.cover_files = []

# Sidebar for uploading PDF files
# maybe add support for Latex and Doc files later
uploaded_resumes = st.sidebar.file_uploader("Upload Resumes (PDF files)", type="pdf", accept_multiple_files=True)
uploaded_covers = st.sidebar.file_uploader("Upload Cover (PDF files)", type="pdf", accept_multiple_files=True)

# Save uploaded files to the "downloads" folder
if uploaded_resumes:
    for uploaded_file in uploaded_resumes:
        file_path = os.path.join(downloads_folder+'/resume', uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.resume_files.append(uploaded_file.name)
        # st.sidebar.write(f"Saved: {uploaded_file.name}")

if uploaded_covers:
    for uploaded_file in uploaded_covers:
        file_path = os.path.join(downloads_folder+'/cover', uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.cover_files.append(uploaded_file.name)
        # st.sidebar.write(f"Saved: {uploaded_file.name}")

# Check if there are any PDF files in the folder if no new files were uploaded
if not uploaded_resumes and not st.session_state.resume_files:
    existing_files = os.listdir(downloads_folder+'/resume')
    st.session_state.resume_files = [f for f in existing_files if f.lower().endswith('.pdf')]

# Check if there are any PDF files in the folder if no new files were uploaded
if not uploaded_covers and not st.session_state.cover_files:
    existing_files = os.listdir(downloads_folder+'/cover')
    st.session_state.cover_files = [f for f in existing_files if f.lower().endswith('.pdf')]

# Check if there are any PDF files in the folder
if not st.session_state.resume_files:
    st.error("No resume uploaded. Upload your resume by clicking on the sidebar.")

# Check if there are any PDF files in the folder
if not st.session_state.cover_files:
    st.error("No cover uploaded. Upload your cover by clicking on the sidebar.")


url = st.text_input("Enter LinkedIn URL here")
model = ChatOpenAI(model="gpt-4")

if st.button("Submit"):
    if url:
        st.session_state.job_details = scrape_linkedin_job(url)
        st.success("Job details fetched successfully!")

        st.subheader("Fetched Details")
        st.write(st.session_state.job_details['job_title'])
        st.write(st.session_state.job_details['company_name'])
        st.write(st.session_state.job_details['job_description'])

        st.session_state.analytical_skills = extract_skills(model=model,
                                                            text=st.session_state.job_details['job_description'],
                                                            skill_type="analytical")

        st.session_state.technical_skills = extract_skills(model=model,
                                                           text=st.session_state.job_details['job_description'],
                                                           skill_type="technical")

        # Reset checked skills
        st.session_state.checked_analytical_skills = [False] * len(st.session_state.analytical_skills)
        st.session_state.checked_technical_skills = [False] * len(st.session_state.technical_skills)

        # Reset confirmation state
        st.session_state.confirmed = False
    else:
        st.error("Please enter a valid Linkedin URL")

# Create two columns
col1, col2 = st.columns(2)

# Display the first list with checkboxes in the first column
with col1:
    st.header("Analytical Skills")
    for i, item in enumerate(st.session_state.analytical_skills):
        st.session_state.checked_analytical_skills[i] = st.checkbox(item, key=f"analytical_{i}", value=st.session_state.checked_analytical_skills[i])

# Display the second list with checkboxes in the second column
with col2:
    st.header("Technical Skills")
    for i, item in enumerate(st.session_state.technical_skills):
        st.session_state.checked_technical_skills[i] = st.checkbox(item, key=f"technical_{i}", value=st.session_state.checked_technical_skills[i])

# Confirm button
if st.button("Confirm"):
    st.session_state.confirmed = True

if st.session_state.confirmed:
    st.header("Selected Analytical Skills")
    selected_analytical = [skill for skill, checked in zip(st.session_state.analytical_skills, st.session_state.checked_analytical_skills) if checked]
    for skill in selected_analytical:
        st.write(skill)

    st.header("Selected Technical Skills")
    selected_technical = [skill for skill, checked in zip(st.session_state.technical_skills, st.session_state.checked_technical_skills) if checked]
    for skill in selected_technical:
        st.write(skill)

    # st.write("Now using the resume you uploaded...")
    # Check if there are any PDF files in the folder
    if not st.session_state.resume_files:
        st.error("No resume uploaded. Upload your resume by clicking on the sidebar.")

    if not st.session_state.cover_files:
        st.error("No cover letter uploaded. Upload your cover letter by clicking on the sidebar.")

    else:
        pdf_content = ""
        st.session_state.resume_contents = {}
        for uploaded_file in st.session_state.resume_files:
            file_path = os.path.join(downloads_folder+'/resume', uploaded_file)
            with fitz.open(file_path) as pdf:
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    pdf_content += page.get_text()

            st.session_state.resume_contents[uploaded_file] = pdf_content
            pdf_content = ""

        pdf_content = ""
        st.session_state.cover_contents = {}
        for uploaded_file in st.session_state.cover_files:
            file_path = os.path.join(downloads_folder+'/cover', uploaded_file)
            with fitz.open(file_path) as pdf:
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    pdf_content += page.get_text()

            st.session_state.cover_contents[uploaded_file] = pdf_content
            pdf_content = ""

    print(st.session_state.resume_contents)
    print("--------------------------------------------------------------")
    print(st.session_state.cover_contents)
