import subprocess
import os
import shutil


def resume_convert_tex_to_pdf(tex_path):
    if not os.path.isfile(tex_path):
        print(f"The file {tex_path} does not exist.")
        return

    try:
        # Create the results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)

        # Run pdflatex to convert .tex to .pdf
        subprocess.run(['pdflatex', tex_path], check=True)
        print(f"Successfully converted {tex_path} to PDF.")

        # Move the generated PDF to the results directory
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.isfile(pdf_path):
            shutil.move(pdf_path, os.path.join('results', 'resume.pdf'))
            print(f"PDF moved to results/resume.pdf")
        else:
            print("PDF not found. Please check if pdflatex ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting {tex_path} to PDF: {e}")
    except FileNotFoundError:
        print(
            "pdflatex command not found. Please ensure that a LaTeX distribution is installed and added to your PATH.")

    # Define the files to be removed and the PDF file to be moved
    files_to_remove = ['resume.aux', 'resume.log', 'resume.out']
    pdf_file = 'resume.pdf'
    target_directory = 'results'

    # Remove the specified files
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f'Removed {file}')
        else:
            print(f'{file} does not exist')

    # Move the PDF file to the target directory
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f'Created directory {target_directory}')

    if os.path.exists(pdf_file):
        shutil.move(pdf_file, os.path.join(target_directory, pdf_file))
        print(f'Moved {pdf_file} to {target_directory}')
    else:
        print(f'{pdf_file} does not exist')


def cover_convert_tex_to_pdf(tex_path):
    if not os.path.isfile(tex_path):
        print(f"The file {tex_path} does not exist.")
        return

    try:
        # Create the results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)

        # Run pdflatex to convert .tex to .pdf
        subprocess.run(['pdflatex', tex_path], check=True)
        print(f"Successfully converted {tex_path} to PDF.")

        # Move the generated PDF to the results directory
        pdf_path = tex_path.replace('.tex', '.pdf')
        if os.path.isfile(pdf_path):
            shutil.move(pdf_path, os.path.join('results', 'cover.pdf'))
            print(f"PDF moved to results/cover.pdf")
        else:
            print("PDF not found. Please check if pdflatex ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting {tex_path} to PDF: {e}")
    except FileNotFoundError:
        print(
            "pdflatex command not found. Please ensure that a LaTeX distribution is installed and added to your PATH.")

    # Define the files to be removed and the PDF file to be moved
    files_to_remove = ['cover.log']
    pdf_file = 'cover.pdf'
    target_directory = 'results'

    # Remove the specified files
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f'Removed {file}')
        else:
            print(f'{file} does not exist')

    # Move the PDF file to the target directory
    if not os.path.exists(target_directory):
        os.makedirs(target_directory)
        print(f'Created directory {target_directory}')

    if os.path.exists(pdf_file):
        shutil.move(pdf_file, os.path.join(target_directory, pdf_file))
        print(f'Moved {pdf_file} to {target_directory}')
    else:
        print(f'{pdf_file} does not exist')

