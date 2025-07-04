import streamlit as st
import openai
import json
import os
from dotenv import load_dotenv
import PyPDF2
import pdfplumber
import io

# Load environment variables for local development
load_dotenv()

# Configure OpenAI - use Streamlit secrets for production, env vars for local development
def get_openai_client():
    """Get OpenAI client with proper API key handling"""
    try:
        # Try to get API key from Streamlit secrets first (production)
        api_key = st.secrets.get("OPENAI_API_KEY")
        if not api_key:
            # Fallback to environment variable (local development)
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            st.error("❌ OpenAI API key not found. Please add it to Streamlit secrets or environment variables.")
            return None
            
        return openai.OpenAI(api_key=api_key)
    except Exception as e:
        st.error(f"❌ Error initializing OpenAI client: {e}")
        return None

# Initialize OpenAI client
client = get_openai_client()

# Page configuration
st.set_page_config(
    page_title="AI Resume Updater",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .resume-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .job-description-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2196f3;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .upload-section {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    try:
        # Try with pdfplumber first (better for complex layouts)
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        
        if text.strip():
            return text
        
        # Fallback to PyPDF2 if pdfplumber doesn't work
        pdf_file.seek(0)  # Reset file pointer
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def parse_resume_from_text(text):
    """Parse resume text and extract structured information"""
    try:
        if not client:
            st.error("❌ OpenAI client not initialized. Please check your API key configuration.")
            return None
            
        prompt = f"""
        Please parse the following resume text and extract the information in JSON format.
        Focus on extracting:
        1. Personal information (name, email, phone, location, linkedin)
        2. Professional summary
        3. Work experience (title, company, duration, description)
        4. Education (degree, school, year)
        5. Skills
        
        Resume text:
        {text}
        
        Return only valid JSON with this structure:
        {{
            "personalInfo": {{
                "name": "Full Name",
                "email": "email@example.com",
                "phone": "phone number",
                "location": "city, state",
                "linkedin": "linkedin url"
            }},
            "summary": "professional summary",
            "experience": [
                {{
                    "title": "job title",
                    "company": "company name",
                    "duration": "duration",
                    "description": "job description"
                }}
            ],
            "education": [
                {{
                    "degree": "degree name",
                    "school": "school name",
                    "year": "graduation year"
                }}
            ],
            "skills": ["skill1", "skill2", "skill3"]
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a resume parser. Extract structured information from resume text and return it in JSON format. Be accurate and maintain the original information."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=2000
        )

        parsed_text = response.choices[0].message.content
        return json.loads(parsed_text)
        
    except Exception as e:
        st.error(f"Error parsing resume: {e}")
        return None

def update_experience_with_ai(job_description, current_experience):
    """Update only the work experience section based on job description"""
    try:
        if not client:
            st.error("❌ OpenAI client not initialized. Please check your API key configuration.")
            return None, "OpenAI client not available"
            
        prompt = f"""
        Based on the following job description, please update and optimize the work experience descriptions to better match the job requirements.
        Focus on making the experience descriptions more relevant to the target job while maintaining truthfulness.
        
        Target Job Description:
        {job_description}
        
        Current Work Experience:
        {json.dumps(current_experience, indent=2)}
        
        Please return the updated work experience in JSON format with the same structure.
        Only update the "description" field for each experience to be more relevant to the job description.
        Keep the job titles, companies, and durations the same.
        Make the descriptions more targeted and relevant to the job requirements.
        """

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional resume writer. Your task is to update work experience descriptions to better match specific job descriptions while maintaining truthfulness and relevance."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )

        updated_experience_text = response.choices[0].message.content
        
        try:
            updated_experience = json.loads(updated_experience_text)
            return updated_experience, None
        except json.JSONDecodeError as e:
            return None, f"Failed to parse AI response: {e}"
            
    except Exception as e:
        return None, f"Error updating experience: {e}"

def load_resume_from_file():
    """Load resume from JSON file if it exists"""
    try:
        if os.path.exists('resume-data.json'):
            with open('resume-data.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading resume: {e}")
    return None

def save_resume_to_file(resume):
    """Save resume to JSON file"""
    try:
        with open('resume-data.json', 'w') as f:
            json.dump(resume, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving resume: {e}")
        return False

def display_resume(resume):
    """Display the resume in a formatted way"""
    st.markdown('<div class="section-header">📄 Current Resume</div>', unsafe_allow_html=True)
    
    # Personal Information
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("**Personal Information**")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {resume['personalInfo']['name']}")
        st.write(f"**Email:** {resume['personalInfo']['email']}")
        st.write(f"**Phone:** {resume['personalInfo']['phone']}")
    with col2:
        st.write(f"**Location:** {resume['personalInfo']['location']}")
        st.write(f"**LinkedIn:** {resume['personalInfo']['linkedin']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("**Professional Summary**")
    st.write(resume['summary'])
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Experience
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("**Work Experience**")
    for i, exp in enumerate(resume['experience']):
        st.markdown(f"**{exp['title']}** at {exp['company']} ({exp['duration']})")
        st.write(exp['description'])
        if i < len(resume['experience']) - 1:
            st.markdown("---")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Education
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("**Education**")
    for edu in resume['education']:
        st.markdown(f"**{edu['degree']}**")
        st.write(f"{edu['school']} - {edu['year']}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Skills
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("**Skills**")
    skills_text = ", ".join(resume['skills'])
    st.write(skills_text)
    st.markdown('</div>', unsafe_allow_html=True)

def main():
    # Check if OpenAI client is available
    if not client:
        st.error("""
        ## ❌ OpenAI API Key Not Configured
        
        Please add your OpenAI API key to Streamlit secrets:
        
        1. Go to your app's **Settings** → **Secrets**
        2. Add the following configuration:
        ```toml
        OPENAI_API_KEY = "your_actual_openai_api_key_here"
        ```
        3. Save and redeploy your app
        
        Get your API key from: https://platform.openai.com/api-keys
        """)
        return

    # Initialize session state
    if 'resume' not in st.session_state:
        st.session_state.resume = None
    if 'resume_uploaded' not in st.session_state:
        st.session_state.resume_uploaded = False

    # Load existing resume if available
    if not st.session_state.resume:
        saved_resume = load_resume_from_file()
        if saved_resume:
            st.session_state.resume = saved_resume
            st.session_state.resume_uploaded = True

    # Main header
    st.markdown('<h1 class="main-header">🤖 AI Resume Experience Updater</h1>', unsafe_allow_html=True)
    st.markdown("### Update your work experience to match any job description using AI")
    
    # Resume Upload Section
    if not st.session_state.resume_uploaded:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("## 📤 Upload Your Resume")
        st.markdown("Please upload your resume in PDF format to get started.")
        
        uploaded_file = st.file_uploader(
            "Choose your resume PDF file",
            type=['pdf'],
            help="Upload your resume in PDF format"
        )
        
        if uploaded_file is not None:
            with st.spinner("Extracting text from PDF..."):
                text = extract_text_from_pdf(uploaded_file)
                
                if text:
                    st.success("✅ PDF text extracted successfully!")
                    st.markdown("**Extracted Text Preview:**")
                    st.text_area("", text[:500] + "..." if len(text) > 500 else text, height=200, disabled=True)
                    
                    if st.button("🔄 Parse Resume", type="primary"):
                        with st.spinner("Parsing resume structure..."):
                            parsed_resume = parse_resume_from_text(text)
                            
                            if parsed_resume:
                                st.session_state.resume = parsed_resume
                                st.session_state.resume_uploaded = True
                                save_resume_to_file(parsed_resume)
                                st.success("✅ Resume parsed and loaded successfully!")
                                st.rerun()
                            else:
                                st.error("❌ Failed to parse resume. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main application (only show if resume is uploaded)
    if st.session_state.resume_uploaded and st.session_state.resume:
        # Sidebar for controls
        with st.sidebar:
            st.markdown("## ⚙️ Controls")
            
            # Job Description Input
            st.markdown("### 📝 Target Job Description")
            job_description = st.text_area(
                "Paste the job description here:",
                height=200,
                placeholder="Paste the complete job description from the company website..."
            )
            
            # Update button
            if st.button("🚀 Update Work Experience", type="primary", use_container_width=True):
                if job_description.strip():
                    with st.spinner("AI is updating your work experience..."):
                        updated_experience, error = update_experience_with_ai(job_description, st.session_state.resume['experience'])
                        
                        if updated_experience:
                            st.session_state.resume['experience'] = updated_experience
                            save_resume_to_file(st.session_state.resume)
                            st.success("✅ Work experience updated successfully!")
                        else:
                            st.error(f"❌ {error}")
                else:
                    st.error("Please enter a job description first.")
            
            st.markdown("---")
            
            # Manual resume editing
            st.markdown("### ✏️ Edit Resume Manually")
            if st.button("Edit Resume", use_container_width=True):
                st.session_state.editing = True
            
            # Download resume
            st.markdown("### 💾 Download Resume")
            if st.button("Download as JSON", use_container_width=True):
                resume_json = json.dumps(st.session_state.resume, indent=2)
                st.download_button(
                    label="📥 Download Resume",
                    data=resume_json,
                    file_name="resume.json",
                    mime="application/json"
                )
            
            # Reset resume
            st.markdown("### 🔄 Reset")
            if st.button("Upload New Resume", use_container_width=True):
                st.session_state.resume = None
                st.session_state.resume_uploaded = False
                st.rerun()
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Display current resume
            display_resume(st.session_state.resume)
        
        with col2:
            # Job description preview
            if job_description:
                st.markdown('<div class="job-description-box">', unsafe_allow_html=True)
                st.markdown("### 📋 Target Job Description")
                st.text_area("", job_description, height=300, disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Instructions
            st.markdown("### 📖 How to Use")
            st.markdown("""
            1. **Upload Resume**: Upload your PDF resume (already done!)
            2. **Paste Job Description**: Copy the job description from the company website
            3. **Click Update**: Press "Update Work Experience" button
            4. **Review Changes**: The AI will update your work experience descriptions
            5. **Download**: Save your updated resume as JSON
            """)
            
            # Tips
            st.markdown("### 💡 Tips")
            st.markdown("""
            - Include the complete job description for better results
            - The AI focuses on updating work experience descriptions
            - Your job titles, companies, and durations remain unchanged
            - You can manually edit the resume anytime
            """)

        # Manual editing mode
        if st.session_state.get('editing', False):
            st.markdown("---")
            st.markdown("## ✏️ Manual Resume Editor")
            
            # Personal Info
            st.markdown("### Personal Information")
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.resume['personalInfo']['name'] = st.text_input("Name", st.session_state.resume['personalInfo']['name'])
                st.session_state.resume['personalInfo']['email'] = st.text_input("Email", st.session_state.resume['personalInfo']['email'])
                st.session_state.resume['personalInfo']['phone'] = st.text_input("Phone", st.session_state.resume['personalInfo']['phone'])
            with col2:
                st.session_state.resume['personalInfo']['location'] = st.text_input("Location", st.session_state.resume['personalInfo']['location'])
                st.session_state.resume['personalInfo']['linkedin'] = st.text_input("LinkedIn", st.session_state.resume['personalInfo']['linkedin'])
            
            # Summary
            st.session_state.resume['summary'] = st.text_area("Professional Summary", st.session_state.resume['summary'])
            
            # Experience
            st.markdown("### Work Experience")
            for i, exp in enumerate(st.session_state.resume['experience']):
                st.markdown(f"**Experience {i+1}**")
                exp['title'] = st.text_input(f"Job Title {i+1}", exp['title'], key=f"title_{i}")
                exp['company'] = st.text_input(f"Company {i+1}", exp['company'], key=f"company_{i}")
                exp['duration'] = st.text_input(f"Duration {i+1}", exp['duration'], key=f"duration_{i}")
                exp['description'] = st.text_area(f"Description {i+1}", exp['description'], key=f"desc_{i}")
                st.markdown("---")
            
            # Skills
            skills_text = ", ".join(st.session_state.resume['skills'])
            skills_input = st.text_input("Skills (comma-separated)", skills_text)
            st.session_state.resume['skills'] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            
            # Save manual changes
            if st.button("💾 Save Manual Changes"):
                save_resume_to_file(st.session_state.resume)
                st.success("Manual changes saved!")
                st.session_state.editing = False
                st.rerun()

if __name__ == "__main__":
    main() 