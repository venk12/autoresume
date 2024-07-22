import requests
from bs4 import BeautifulSoup
import os
import base64

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser
from langchain_core.output_parsers import StrOutputParser

downloads_folder = "downloads"


def scrape_linkedin_job(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    title_tag = soup.find('h1', class_='top-card-layout__title')
    job_title = title_tag.text.strip() if title_tag else 'N/A'

    company_tag = soup.find('a', class_='topcard__org-name-link')
    company_name = company_tag.text.strip() if company_tag else 'N/A'

    description_tag = soup.find('div', class_='description__text')
    job_description = description_tag.text.strip() if description_tag else 'N/A'

    cleaned_jd = (job_description.replace("\n", "")
                  .replace("Show more", "")
                  .replace("Show less", ""))

    return {
        'job_title': job_title,
        'company_name': company_name,
        'job_description': cleaned_jd
    }


def extract_skills(model, text, skill_type, defaults):
    output_parser = CommaSeparatedListOutputParser()
    format_instructions = output_parser.get_format_instructions()

    # print(format_instructions)

    prompt = PromptTemplate(
        template=f"You are a helpful HR Assistant. I want you to help me build my resume"
                 f"Analyze the following job description and find the"
                 f"most relevant analytical skills required for the job. Here is the description: {text}, "
                 f"Do not give me descriptions. only name of the skills."
                 f"Give me {skill_type} skills that would be highly relevant for this job. It should strictly be {skill_type} skills only."
                 f"Do not confuse between analytical skills (soft skills) with technical skills (technology/software)"
                 f"Do not give any other description, elements should not contain commas because the values are comma "
                 f"separated. It confuses the parser. Ensure you dont repeat the skills."
                 f"Add these at the start as they are default skills: {defaults}",
        partial_variables={"format_instructions": format_instructions}
    )

    # print(prompt)

    chain = prompt | model | output_parser
    result = chain.invoke({})
    return result


# Generate base64-encoded URL for PDF files
def get_pdf_url(file_name):
    file_path = os.path.join(downloads_folder, file_name)
    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:application/pdf;base64,{encoded}"


def create_dir():
    resume_folder = os.path.join(downloads_folder, "resume")
    cover_folder = os.path.join(downloads_folder, "cover")

    if not os.path.exists(downloads_folder):
        os.makedirs(downloads_folder)

    # Ensure the "resume" and "cover" directories exist
    if not os.path.exists(resume_folder):
        os.makedirs(resume_folder)
    if not os.path.exists(cover_folder):
        os.makedirs(cover_folder)

    return downloads_folder


def generate_objective(model, job_skills, job_desc, sample_objective):
    output_parser = StrOutputParser()

    prompt = PromptTemplate(
        template=f"You are a helpful HR Assistant. I want you to help me build my resume"
                 f"I will provide you three things:"
                 f"1. list of skills required for the job"
                 f"2. job description"
                 f"3. sample_objective"
                 f"I want you to combine these and give me a objective statement that closely matches the job "
                 f"description. Make it professional. Do not use specific company name. make it a bit generic and "
                 f"sound human not like a robot. Use the sample_objective as a guideline."
                 f"Don't mention trivial and common things like multi-tasking, deadline management etc. "
                 f"be a bit more specific."
                 f"Give an output in string format. Give me the output in less than 75 words."
                 f"1. {job_skills}"
                 f"2. {job_desc}"
                 f"3. {sample_objective}"
    )

    chain = prompt | model | output_parser
    result = chain.invoke({})

    return result


def generate_cover_content(model, sample, ls_skills, job_description, resume):
    output_parser = StrOutputParser()

    prompt = PromptTemplate(
        template=f"You are a helpful HR Assistant. I want you to help me build my cover letter"
                 f"I will provide you three things:"
                 f"1. list of skills required for the job"
                 f"2. job description"
                 f"3. sample cover letter"
                 f"4. resume for reference regarding my experience"
                 f"I want you to combine these and give me a objective statement that closely matches the job"
                 f"Give output in string format. The word could should be around 200 to 300 words. highlight my key "
                 f"competencies and how you would be a great value addition to the team. Just give me the content. "
                 f"Don't mention trivial and common things like multi-tasking, deadline management etc. "
                 f"I will use this to prepare my cover letter with proper formatting"
                 f"1. {', '.join(ls_skills)}"
                 f"2. {job_description}"
                 f"3. {sample}"
                 f"4. {resume}"
                 f"Do not add anything else in the output other than the content itself. No summary or commentaries"
    )

    chain = prompt | model | output_parser
    result = chain.invoke({})

    return result


