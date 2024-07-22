import os
import ast
import fitz  # PyMuPDF

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv
from utils import scrape_linkedin_job, extract_skills, create_dir, generate_objective, generate_cover_content
from latex import generate_resume_latex, generate_cover_latex
from pdf import resume_convert_tex_to_pdf, cover_convert_tex_to_pdf

load_dotenv()
downloads_folder = create_dir()


def download_file(results_file_path, file_name):
    with open(results_file_path, "rb") as file:
        st.download_button(
            label=f"Download {file_name}",
            data=file,
            file_name=file_name,
            mime="application/octet-stream"
        )


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
if "url_verified" not in st.session_state:
    st.session_state.url_verified = False

st.session_state.resume_files = []
st.session_state.cover_files = []

# Set the app title in the app itself
st.title("Job Application Automation")

# Sidebar for uploading PDF files
# maybe add support for Latex and Doc files later
uploaded_resumes = st.sidebar.file_uploader("Upload Resumes (PDF files)", type="pdf", accept_multiple_files=True)
uploaded_covers = st.sidebar.file_uploader("Upload Cover (PDF files)", type="pdf", accept_multiple_files=True)

# Save uploaded files to the "downloads" folder
if uploaded_resumes:
    for uploaded_file in uploaded_resumes:
        file_path = os.path.join(downloads_folder + '/resume', uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.resume_files.append(uploaded_file.name)
        # st.sidebar.write(f"Saved: {uploaded_file.name}")

if uploaded_covers:
    for uploaded_file in uploaded_covers:
        file_path = os.path.join(downloads_folder + '/cover', uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.session_state.cover_files.append(uploaded_file.name)
        # st.sidebar.write(f"Saved: {uploaded_file.name}")

# Check if there are any PDF files in the folder if no new files were uploaded
if not uploaded_resumes and not st.session_state.resume_files:
    existing_files = os.listdir(downloads_folder + '/resume')
    st.session_state.resume_files = [f for f in existing_files if f.lower().endswith('.pdf')]

# Check if there are any PDF files in the folder if no new files were uploaded
if not uploaded_covers and not st.session_state.cover_files:
    existing_files = os.listdir(downloads_folder + '/cover')
    st.session_state.cover_files = [f for f in existing_files if f.lower().endswith('.pdf')]

# Check if there are any PDF files in the folder
if not st.session_state.resume_files:
    st.error("No resume uploaded. Upload your resume by clicking on the sidebar.")

# Check if there are any PDF files in the folder
if not st.session_state.cover_files:
    st.error("No cover uploaded. Upload your cover by clicking on the sidebar.")

url = st.text_input("Enter LinkedIn URL here")
model = ChatOpenAI(model="gpt-3.5-turbo")

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
                                                            skill_type="analytical", defaults=f"Regulatory "
                                                                                              f"Compliance, "
                                                                                              f"Lifecycle Assessment,"
                                                                                              f"Policy Analysis, "
                                                                                              f"Data Analysis, "
                                                                                              f"Sustainable Finance "
                                                                                              f"Reporting, "
                                                                                              f"Public Relations,"
                                                                                              f"Project Management, "
                                                                                              f"Stakeholder "
                                                                                              f"Management, "
                                                                                              f"Dutch A0 + "
                                                                                              f"Self-Learning")

        st.session_state.technical_skills = extract_skills(model=model,
                                                           text=st.session_state.job_details['job_description'],
                                                           skill_type="technical",
                                                           defaults=f"PowerBI, MS Excel, QGIS, Greenly, SimaPro, "
                                                                    f"Salesforce, ERP")

        # Sometimes the LLM responds with a text not a list - especially when you choose gpt-3.5-turbo
        if len(st.session_state.analytical_skills) == 1:
            items = st.session_state.analytical_skills[0].split('\n')
            st.session_state.analytical_skills = [item.split('. ', 1)[1] for item in items]

        if len(st.session_state.technical_skills) == 1:
            items = st.session_state.technical_skills[0].split('\n')
            st.session_state.technical_skills = [item.split('. ', 1)[1] for item in items]

        print(st.session_state.analytical_skills)
        print(st.session_state.technical_skills)

        # Reset checked skills
        st.session_state.checked_analytical_skills = [False] * len(st.session_state.analytical_skills)
        st.session_state.checked_technical_skills = [False] * len(st.session_state.technical_skills)

        # Reset confirmation state
        st.session_state.confirmed = False
        st.session_state.url_verified = True
    else:
        st.error("Please enter a valid Linkedin URL")

if st.session_state.url_verified:
    # Create two columns
    col1, col2 = st.columns(2)

    # Display the first list with checkboxes in the first column
    with col1:
        st.header("Analytical Skills")

        # Buttons to check/uncheck all
        if st.button("Check All Analytical Skills"):
            st.session_state.checked_analytical_skills = [True] * len(st.session_state.analytical_skills)
        if st.button("Uncheck All Analytical Skills"):
            st.session_state.checked_analytical_skills = [False] * len(st.session_state.analytical_skills)

        # Display checkboxes
        for i, item in enumerate(st.session_state.analytical_skills):
            st.session_state.checked_analytical_skills[i] = st.checkbox(item, key=f"analytical_{i}",
                                                                        value=
                                                                        st.session_state.checked_analytical_skills[i])

    # Display the second list with checkboxes in the second column
    with col2:
        st.header("Technical Skills")

        # Buttons to check/uncheck all
        if st.button("Check All Technical Skills"):
            st.session_state.checked_technical_skills = [True] * len(st.session_state.technical_skills)
        if st.button("Uncheck All Technical Skills"):
            st.session_state.checked_technical_skills = [False] * len(st.session_state.technical_skills)

        # Display checkboxes
        for i, item in enumerate(st.session_state.technical_skills):
            st.session_state.checked_technical_skills[i] = st.checkbox(item, key=f"technical_{i}",
                                                                       value=st.session_state.checked_technical_skills[
                                                                           i])
    # Confirm button
    if st.button("Confirm"):
        st.session_state.confirmed = True

if st.session_state.confirmed:
    # st.header("Selected Analytical Skills")
    selected_analytical = [skill for skill, checked in
                           zip(st.session_state.analytical_skills, st.session_state.checked_analytical_skills) if
                           checked]
    # for skill in selected_analytical:
    #     st.write(skill)

    # st.header("Selected Technical Skills")
    selected_technical = [skill for skill, checked in
                          zip(st.session_state.technical_skills, st.session_state.checked_technical_skills) if checked]
    # for skill in selected_technical:
    #     st.write(skill)

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
            file_path = os.path.join(downloads_folder + '/resume', uploaded_file)
            with fitz.open(file_path) as pdf:
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    pdf_content += page.get_text()

            st.session_state.resume_contents[uploaded_file] = pdf_content
            pdf_content = ""

        pdf_content = ""
        st.session_state.cover_contents = {}
        for uploaded_file in st.session_state.cover_files:
            file_path = os.path.join(downloads_folder + '/cover', uploaded_file)
            with fitz.open(file_path) as pdf:
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    pdf_content += page.get_text()

            st.session_state.cover_contents[uploaded_file] = pdf_content
            pdf_content = ""

        # print(st.session_state.resume_contents)
        # print("--------------------------------------------------------------")
        # print(st.session_state.cover_contents)

        # st.header("Selected Skills")
        # st.write(selected_analytical + selected_technical)

        st.success("If you want to make re-generate the content, you can do so by clicking on the buttons below")
        st.success("Once you finalize If you want to make minor changes the text, you can do so by editing the "
                   "downloaded .tex")

        st.header("Finalize Modifications")
        if 'gen_obj' not in st.session_state:
            st.session_state.gen_obj = generate_objective(
                model=model,
                job_skills=selected_analytical + selected_technical,
                job_desc=st.session_state.job_details['job_description'],
                sample_objective=f"I'm a motivated sustainability professional with over three years of experience in "
                                 f"policy-making, compliance, communications, and project management. I excel at "
                                 f"designing and implementing policies, conducting thorough analyses, and maintaining "
                                 f"strong stakeholder relationships. With proven expertise in data analysis and "
                                 f"sustainability initiatives, I'm committed to fostering equity and positive impact "
                                 f"in the corporate sector. I'm seeking an opportunity to leverage my skills in a "
                                 f"dynamic organization, contributing to its mission of creating sustainable and "
                                 f"impactful solutions.")
            st.session_state.gen_obj.replace("Objective:", "")

        if st.button('Rewrite Objective in Resume'):
            st.session_state.gen_obj = generate_objective(
                model=model,
                job_skills=selected_analytical + selected_technical,
                job_desc=st.session_state.job_details['job_description'],
                sample_objective=f"I'm a motivated sustainability professional with over three years of experience in "
                                 f"policy-making, compliance, communications, and project management. I excel at "
                                 f"designing and implementing policies, conducting thorough analyses, and maintaining "
                                 f"strong stakeholder relationships. With proven expertise in data analysis and "
                                 f"sustainability initiatives, I'm committed to fostering equity and positive impact "
                                 f"in the corporate sector. I'm seeking an opportunity to leverage my skills in a "
                                 f"dynamic organization, contributing to its mission of creating sustainable and "
                                 f"impactful solutions.")

            st.session_state.gen_obj.replace("Objective:", "")

        st.write(st.session_state.gen_obj)

        if 'gen_cover_content' not in st.session_state:
            st.session_state.gen_cover_content = generate_cover_content(
                model=model,
                sample=st.session_state.cover_contents.get('sample_cover.pdf'),
                ls_skills=selected_technical + selected_analytical,
                job_description=st.session_state.job_details.get('job_description'),
                resume=st.session_state.resume_contents.get('sample_resume.pdf')
            )

        if st.button('Rewrite Content in Cover Letter'):
            st.session_state.gen_cover_content = generate_cover_content(
                model=model,
                sample=st.session_state.cover_contents.get('sample_cover.pdf'),
                ls_skills=selected_technical + selected_analytical,
                job_description=st.session_state.job_details.get('job_description'),
                resume=st.session_state.resume_contents.get('sample_resume.pdf')
            )

        st.session_state.gen_obj.replace('"', '')
        st.write(st.session_state.gen_cover_content)

        generate_cover_latex(content=st.session_state.gen_cover_content,
                             job_title=st.session_state.job_details['job_title'])

        generate_resume_latex(objective=st.session_state.gen_obj,
                              analytical_skills=selected_analytical,
                              technical_skills=selected_technical)

        resume_tex_file_path = 'results/resume.tex'
        cover_tex_file_path = 'results/cover.tex'

        if os.path.exists(resume_tex_file_path):
            download_file(resume_tex_file_path, 'resume.tex')

        if os.path.exists(cover_tex_file_path):
            download_file(cover_tex_file_path, 'cover.tex')
