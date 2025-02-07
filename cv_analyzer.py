# pip install streamlit pypdf python-docx google-generativeai pandas

import streamlit as st
import io  # For handling file uploads as bytes
import pypdf  # To read PDF files
from docx import Document  # To read Word Docx Files
import google.generativeai as genai #Google AI Studio API
import pandas as pd
import json



# Replace with your actual Google AI Studio API key
GOOGLE_API_KEY = "AIzaSyARBYGybxXDO_11GyYR0yH8WbrNKP0se90"
genai.configure(api_key=GOOGLE_API_KEY)

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = pypdf.PdfReader(pdf_file)
    text = ""
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

# Function to extract text from Word Doc
def extract_text_from_docx(docx_file):
    document = Document(docx_file)
    text = '\n'.join([paragraph.text for paragraph in document.paragraphs])
    return text

# Function to call Google AI Studio API
def analyze_cv(cv_text, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro') # Or specify another model
        response = model.generate_content(prompt + "\n\n" + cv_text)
        return response.text  # Extract the text content from the response
    except Exception as e:
        return f"Error calling AI Studio API: {e}"



# Function to convert DJ document into markdown
def convert_dj_to_markdown(file_path):
    """
    Converts a DJ file (PDF or Word doc) to markdown text using the Google AI Studio API.
    """
    try:
        # Determine the file type and extract text accordingly
        if file_path.name.lower().endswith(".pdf"):
            dj_text = extract_text_from_pdf(file_path)
        elif file_path.name.lower().endswith(".docx"):
            dj_text = extract_text_from_docx(file_path)
        else:
            st.error("Unsupported file type for DJ file. Please upload a PDF or Word doc.")
            return None

        # Prepare the prompt for converting the DJ file to markdown
        prompt = "Convert the following text to markdown format:\n"

        # Use the Gemini Pro model to convert the text to markdown
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt + dj_text)

        # Return the markdown text
        return response.text

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Change Dictonary key values in Indicator-1, Indicator-2, ... serial. Because AI model gives us slightly different key names every time, which is a issue.
def dict_keys(dic):
  keys_list = list(dic.keys())
  key = []
  for i in range(len(keys_list)):
    key.append("Indicator-" + str(i))
  new_dict = dict(zip(key, dic.values()))
  return new_dict


# Streamlit App
def main():
    st.title("CV Analyzer")
    # Description
    st.text("Streamline your candidate screening process with our AI-powered platform.  Simply upload a job description and a batch of CVs, and our intelligent system will analyze each resume against your specified criteria.  Leveraging cutting-edge AI, the platform identifies key skills, experience, and qualifications, providing a comprehensive competency score for every applicant.  Results are conveniently delivered in an Excel file, enabling you to quickly identify top talent and accelerate your hiring workflow.  Define your evaluation parameters with natural language prompts, making the process intuitive and efficient.  Our platform empowers you to make data-driven hiring decisions, saving you time and resources while ensuring you find the perfect fit for your organization.")
    st.html("<hr>")

    # 1. DJ File Upload
    st.header("Upload DJ File")
    dj_file = st.file_uploader("Upload DJ PDF or DOCX", type=["pdf", "docx"])

    if dj_file is not None:
        # Convert DJ file to markdown
        markdown_text = convert_dj_to_markdown(dj_file)
        

        if markdown_text:
            st.markdown("**Update: DJ file Prepared for Analysis.**")
            # DJ_show = st.radio("**Do you want to see DJ file here?**", ["No need","Yes, Show"])
            # if {DJ_show}=="Yes, Show":
            # st.subheader("Converted Markdown Text")
            # st.markdown(markdown_text)
        else:
            st.warning("Failed to convert DJ file to markdown.")


    # 2. CV File Upload
    st.header("Upload CV Files")
    cv_files = st.file_uploader("Upload CV PDFs or DOCX files", type=["pdf", "docx"], accept_multiple_files=True)

    # 3. Prompt Input
    st.header("Enter Prompt")
    default_prompt = "Find a job description and a CV attached. Go through both files and give me your thought about the job candidate following the below indicators: (a) Educational Background: \"subject name\"  (b) How many Year of Experience? (c) Is work experience align to the DJ: integer marking between 0 to 10. if as expected in DJ then give mark around 6. more than expectation then give more marks. (d) Candidate name: (e) Mobile no.: (f) Email address:"
    # default_prompt = "Extract the following information from applicant's CV a)name, b)email address, c)mobile number, d)Does the candidate have work experience with government? e) Does have skilled in MS office software? f) What is education background?, g)What percentage of DJ key roles match with previous work experience? Example: { \"Applicant_Name\": \"John Doe\", \"Email_Address\": \"johndoe@example.com\", \"Mobile_Numbe\": \"+1234567890\", \"Government experience\": \"Yes or No\"}"
    prompt_body = st.text_area("**How you want to analysis the CVs. Give indicators, like** Extract the applicant's a)name, b)email address, c)mobile number, and d)Does the candidate have work experience in nutrition and health from the given CVs. **Example:** {\"Applicant_Name\": \"John Doe\", \"Email_Address\": \"johndoe@example.com\",  \"Mobile_Number\": \"+1234567890\", \"Have experience in health\": \"Yes\"}", default_prompt)
    post_prompt = "Maintain the given indicator order when return the response. Response will be a valid JSON object, without any extra formatting, code blocks, or explanations."
    prompt = prompt_body + post_prompt

    # Process button
    process_clicked = st.button("Process")
    # keys_list = []
    # Check if the button is clicked before executing the code block
    if process_clicked:
        
        if cv_files:
            # Initialize progress bar
            progress_bar = st.progress(0)  
            total_files = len(cv_files)  # Total number of CVs
            # Initialize an empty list to store the extracted data
            data = []


            # for cv_file in cv_files:
            for index, cv_file in enumerate(cv_files):
                st.write(f"Analyzing: {cv_file.name}")

                try:
                    # Determine file type and extract text
                    if cv_file.name.lower().endswith(".pdf"):
                        cv_text = extract_text_from_pdf(cv_file)
                    elif cv_file.name.lower().endswith(".docx"):
                        cv_text = extract_text_from_docx(cv_file)
                    else:
                        st.error(f"Unsupported file type for {cv_file.name}.  Skipping.")
                        # continue  # Skip to the next file

                    # Call Google AI Studio API
                    api_response = analyze_cv(cv_text, prompt)
                    api_response = api_response.replace("'''","")
                    api_response = api_response.replace("#","")
                    api_response = api_response.replace("python", "")
                    api_response = api_response.replace("json", "")
                    api_response = api_response.split("{")
                    api_response = api_response[1]
                    api_response = api_response.split("}")
                    api_response = api_response[0]
                    api_response = "{"+api_response+"}"
                    # print(str(type(api_response))) this is text


                    # Parse the response
                    try:
                        # Important: Attempt to parse the API response as a Python dictionary
                        parsed_data = json.loads(api_response)  # Expecting a dictionary
                        # if (f"{index}")=="0": # Try for column head rename
                        #     keys_list = parsed_data.keys()
                        # print(parsed_data)
                        # print(str(type(parsed_data))) This is a dictionary
                        parsed_data = dict_keys(parsed_data) # give common name of the dictionary keys
                        data.append(parsed_data) # Append result dictionary to the data list
                        

                    except json.JSONDecodeError as e:
                        st.error(f"Error decoding JSON from AI Studio response for {cv_file.name}: {e}.  Raw response: {api_response}")
                        # You might want to add a fallback or error handling here.
                        data.append({"error": f"JSON Decode Error: {e}"})  # Append a fallback
                        # continue  # Skip to the next file

                except Exception as e:
                    st.error(f"Error processing {cv_file.name}: {e}")
                    data.append({"error": str(e)})  # Add error info to the data
            
            # **Update progress bar**
            # progress_bar.progress((i + 1) / total_files)


            # st.write(data)
            # 4. Create DataFrame and Display
            if data: # Check if there is any data
                df = pd.DataFrame(data)
                # print(df.columns)
                # print(keys_list)
                # df.columns = keys_list.append("SL")
                st.header("Results")
                st.dataframe(df)
            else:
                st.info("No data to display.  Make sure CV files are uploaded and processed correctly.")

if __name__ == "__main__":
    main()
