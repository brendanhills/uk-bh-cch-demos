#!/usr/bin/env python3
import argparse
from itertools import count
import mimetypes
import os
import sys
from PyPDF2 import PdfReader
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models

def process_files(directories=None, input_files=None, output=None, max_size=None, skip_types=None):
    """
    Process each file in the specified directories or input files, extracting text from PDFs and reading text from text files.
    Skip files that exceed the specified maximum size or match the skip file types.
    
    Args:
    - directories: A list of directories containing the files to be processed.
    - input_files: A list of single files to process.
    - output: Optional. A file path where the combined contents of the files will be written.
    - max_size: Optional. Maximum file size in KB to process.
    - skip_types: Optional. List of file extensions to skip.
    """
    prompt = ""  # Initialize the variable to store the combined contents of the files.
    
    if directories:
        for directory in directories:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if should_process_file(file_path, max_size, skip_types):
                        prompt += process_single_file(file_path)
    if input_files:
        for input_file in input_files:
            if should_process_file(input_file, max_size, skip_types):
                prompt += process_single_file(input_file)

    # Write the combined contents to a file if the output option is provided
    if output:
        with open(output, 'w') as f:
            f.write(prompt)

    return prompt

def should_process_file(file_path, max_size=None, skip_types=None):
    """
    Determine whether a file should be processed based on its size and type.
    
    Args:
    - file_path: Path to the file.
    - max_size: Maximum size in KB.
    - skip_types: List of file extensions to skip.
    
    Returns:
    True if the file should be processed, False otherwise.
    """
    if max_size is not None:
        file_size = os.path.getsize(file_path) / 1024  # Convert size to KB
        if file_size > max_size:
            return False

    if skip_types is not None:
        extension = os.path.splitext(file_path)[1][1:]  # Get file extension without the dot
        if extension.lower() in skip_types:
            return False

    return True

def process_single_file(file_path):
    """
    Process a single file, extracting its contents based on its MIME type.
    
    Args:
    - file_path: The path to the file being processed.
    
    Returns:
    A string containing the processed file contents.
    """
    prompt_section = ""
    try:
        mime_type, _ = mimetypes.guess_type(file_path)
        print(f"Processing File: {os.path.basename(file_path)}")
        # Process PDF files
        if mime_type == 'application/pdf':
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
        # Process text files
        else: # None for unknown types, treated as text
            with open(file_path, 'r') as f:
                text = f.read()
        # Append the content to the prompt variable
        prompt_section = f"************\n{file_path}\n\n{text}\n"
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
    
    return prompt_section
def generate(prompt, count_tokens=False):
    """
    Generate content based on a prompt using Vertex AI's generative model.

    Args:
    - prompt: The prompt to generate content for.
    """
    vertexai.init(project="uk-bh-experiments-argolis", location="us-central1")
    model = GenerativeModel("gemini-1.0-pro")
    if count_tokens:
        print("Get Token Counts")
        print(model.count_tokens(prompt))
        return
    print("Generate Content")
    print("Sending to model")
    responses = model.generate_content(
        prompt,
        generation_config={
            "max_output_tokens": 8000,
            "temperature": 0.5,
            "top_p": 0.4
        },
        safety_settings={
        generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
        },
        stream=True,
    )
    
    for response in responses:
        print(response.text, end="")

def main():
    # Setup command line argument parsing
    parser = argparse.ArgumentParser(description="Process files and generate content based on them.")
    parser.add_argument("-d", "--directory", action='append', help="Directory containing files to process. Can be used multiple times.")
    parser.add_argument("-i", "--input_file", action='append', help="A single file to process. Can be used multiple times.")
    parser.add_argument("-p", "--prompt",  help="Prompt to generate content for.")
    parser.add_argument("-o", "--output", help="Optional output file to write the combined contents.")
    parser.add_argument("-s", "--max_size", type=int, help="Maximum file size in KB to include.")
    parser.add_argument("-t", "--skip_type", action='append', help="File extensions to skip. Can be used multiple times.")
    parser.add_argument("-c", "--count_tokens" , action='store_true', help="Count the number of tokens in the documents only")
    
    args = parser.parse_args()

    # Validate at least one directory or file is provided
    if not args.directory and not args.input_file:
        print("Error: At least one directory or input file must be provided.")
        sys.exit(1)

    # Process the files in the directories or the input files
    combined_text = process_files(directories=args.directory, input_files=args.input_file, output=args.output,
                                  max_size=args.max_size, skip_types=args.skip_type)
    
    # Append the user-provided prompt to the combined text
    final_prompt = f"{combined_text}\n{args.prompt}"

    # Generate content based on the final prompt
    generate(final_prompt, count_tokens=args.count_tokens)

if __name__ == "__main__":
    main()