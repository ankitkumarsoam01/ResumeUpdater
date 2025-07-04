# 🤖 AI Resume Experience Updater

A web application that uses OpenAI's GPT-4 to automatically update your work experience descriptions based on job descriptions. Upload your PDF resume and let AI tailor your experience to match any job opportunity!

## ✨ Features

- **PDF Resume Upload**: Upload your existing resume in PDF format
- **AI-Powered Experience Updates**: Uses OpenAI GPT-4 to update work experience descriptions
- **Smart Text Extraction**: Automatically extracts and parses resume content from PDF
- **Targeted Updates**: Only updates work experience descriptions, keeping other sections intact
- **Real-time Preview**: See your resume updates instantly
- **Manual Editing**: Edit your resume manually when needed
- **Persistent Storage**: Your resume is automatically saved
- **Download Functionality**: Export your resume as JSON
- **Beautiful UI**: Modern, responsive interface built with Streamlit

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd PDFUpdate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `env_example.txt` to `.env`
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - Navigate to `http://localhost:8501`

## 🌐 Deploy to Streamlit Community Cloud

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Ensure your repository structure looks like this:**
   ```
   PDFUpdate/
   ├── app.py
   ├── requirements.txt
   ├── README.md
   ├── env_example.txt
   └── .streamlit/
       └── config.toml
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to [Streamlit Community Cloud](https://share.streamlit.io/)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Configure your app:**
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your default branch)
   - **Main file path**: `app.py`
   - **App URL**: Choose a custom URL (optional)

5. **Set up secrets:**
   - Click on your app → Settings → Secrets
   - Add your OpenAI API key:
     ```toml
     OPENAI_API_KEY = "your_actual_api_key_here"
     ```

6. **Deploy!**
   - Click "Deploy" and wait for the build to complete
   - Your app will be available at `https://your-app-name.streamlit.app`

## 📖 How to Use

1. **Upload Resume**: Upload your PDF resume using the file uploader
2. **Parse Resume**: Click "Parse Resume" to extract and structure your resume content
3. **Paste Job Description**: Copy the job description from the company website and paste it in the sidebar
4. **Update Experience**: Click "Update Work Experience" button
5. **Review Changes**: The AI will update your work experience descriptions to match the job requirements
6. **Download**: Save your updated resume as JSON

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Supported File Formats

- **PDF**: Upload your resume in PDF format
- The app will automatically extract text and parse the structure

## 💡 Tips for Best Results

- **Complete Job Descriptions**: Include the full job description for better AI analysis
- **Clear PDF Format**: Ensure your PDF resume has clear, readable text
- **Review AI Changes**: Always review the AI-generated experience updates before using them
- **Manual Edits**: Use the manual editor for fine-tuning specific details
- **Keep Original Structure**: The AI only updates experience descriptions, preserving your job titles and companies

## 🛠️ Technical Details

- **Framework**: Streamlit
- **AI Model**: OpenAI GPT-4
- **PDF Processing**: PyPDF2 and pdfplumber for text extraction
- **Storage**: Local JSON file (for Streamlit Cloud, consider using a database)
- **Styling**: Custom CSS for modern UI

## 🔒 Security Notes

- Never commit your `.env` file or API keys to version control
- Use Streamlit's secrets management for production deployments
- Consider rate limiting for API calls in production
- PDF files are processed locally and not stored permanently

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

If you encounter any issues:
1. Check the Streamlit logs in the Community Cloud dashboard
2. Verify your OpenAI API key is correct
3. Ensure all dependencies are properly installed
4. Make sure your PDF resume has extractable text

---

**Happy job hunting! 🎯** 