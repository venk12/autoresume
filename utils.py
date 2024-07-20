import requests
from bs4 import BeautifulSoup
import os
import base64

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.output_parsers import CommaSeparatedListOutputParser

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


def extract_skills(model, text, skill_type):
    output_parser = CommaSeparatedListOutputParser()
    format_instructions = output_parser.get_format_instructions()

    # print(format_instructions)

    prompt = PromptTemplate(
        template=f"You are a helpful HR Assistant. I want you to help me build my resume"
                 f"Analyze the following job description and find the"
                 f"most relevant analytical skills required for the job. Here is the description: {text}, "
                 f"Do not give me descriptions. only name of the skills."
                 f"Give me 10 {skill_type} skills that would be highly relevant for this job."
                 f"Do not give any other description or comma values as it confuses the parser.",
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
