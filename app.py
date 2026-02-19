import gradio as gr
import openai
from PyPDF2 import PdfReader
from docx import Document
import re
import urllib.parse

openai.api_key = "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"

# === TEXT EXTRACTION ===
def extract_text(file):
    try:
        if file.name.endswith('.pdf'):
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        elif file.name.endswith('.docx'):
            doc = Document(file)
            text = "\n".join([para.text for para in doc.paragraphs if para.text])
            return text.strip()
    except:
        return None
    return None

# === SKILLS DATABASE ===
SKILLS_DB = {
    'python', 'java', 'javascript', 'typescript', 'sql', 'aws', 'azure', 'gcp', 'docker', 
    'kubernetes', 'tensorflow', 'pytorch', 'machine learning', 'deep learning', 'data engineering',
    'etl', 'spark', 'hadoop', 'kafka', 'airflow', 'mongodb', 'postgresql', 'mysql', 'redis',
    'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi', 'ci/cd', 'jenkins',
    'git', 'linux', 'bash', 'agile', 'scrum', 'tableau', 'power bi', 'pandas', 'numpy',
    'nlp', 'computer vision', 'microservices', 'rest api', 'graphql', 'terraform', 'ansible'
}

def extract_skills(text):
    if not text:
        return []
    text_lower = text.lower()
    found = []
    for skill in SKILLS_DB:
        if skill in text_lower:
            found.append(skill)
    return list(set(found))

# === JOB SEARCH GENERATOR ===
def generate_job_links(skills, location="United States"):
    if not skills:
        return "No skills detected. Upload a resume first."
    
    top_skills = skills[:5]
    skills_query = " ".join(top_skills)
    
    # LinkedIn search
    linkedin_params = {
        'keywords': skills_query,
        'location': location,
        'f_TPR': 'r86400'  # Past 24 hours
    }
    linkedin_url = f"https://www.linkedin.com/jobs/search/?{urllib.parse.urlencode(linkedin_params)}"
    
    # Indeed search
    indeed_params = {
        'q': skills_query,
        'l': location,
        'fromage': '1'  # Past 24 hours
    }
    indeed_url = f"https://www.indeed.com/jobs?{urllib.parse.urlencode(indeed_params)}"
    
    # Glassdoor search
    glassdoor_url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={urllib.parse.quote(skills_query)}"
    
    # Simulate job matches based on skills
    job_templates = [
        {"title": f"{top_skills[0].title()} Engineer", "company": "TechCorp", "match": "95%"},
        {"title": f"Senior {top_skills[1].title()} Developer", "company": "DataSystems Inc", "match": "88%"},
        {"title": f"{top_skills[2].title()} Specialist", "company": "CloudFirst", "match": "82%"},
        {"title": "Full Stack Developer", "company": "StartupXYZ", "match": "78%"},
        {"title": f"Lead {top_skills[0].title()} Architect", "company": "Enterprise Solutions", "match": "91%"}
    ]
    
    html = f"""
    <div style="background: #f5f5f5; padding: 20px; border-radius: 10px; border: 2px solid #333;">
        <h3 style="color: #000; margin-bottom: 15px;">🎯 Jobs Matching Your Skills</h3>
        <p style="color: #555; font-size: 0.9em; margin-bottom: 15px;">
            Based on: {', '.join(top_skills)}
        </p>
        
        <div style="margin-bottom: 20px;">
    """
    
    for job in job_templates:
        html += f"""
            <div style="background: white; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #000;">
                <div style="font-weight: bold; color: #000;">{job['title']}</div>
                <div style="color: #555; font-size: 0.9em;">{job['company']}</div>
                <div style="color: #2e7d32; font-size: 0.85em; font-weight: 600;">Match: {job['match']}</div>
            </div>
        """
    
    html += f"""
        </div>
        
        <div style="background: #000; color: #fff; padding: 15px; border-radius: 8px; text-align: center;">
            <p style="margin: 0 0 10px 0; font-weight: 600;">Search Real Jobs Now</p>
            <a href="{linkedin_url}" target="_blank" style="display: inline-block; background: #0077b5; color: white; padding: 10px 20px; margin: 5px; border-radius: 20px; text-decoration: none; font-size: 0.9em;">LinkedIn Jobs</a>
            <a href="{indeed_url}" target="_blank" style="display: inline-block; background: #2557a7; color: white; padding: 10px 20px; margin: 5px; border-radius: 20px; text-decoration: none; font-size: 0.9em;">Indeed</a>
            <a href="{glassdoor_url}" target="_blank" style="display: inline-block; background: #0caa41; color: white; padding: 10px 20px; margin: 5px; border-radius: 20px; text-decoration: none; font-size: 0.9em;">Glassdoor</a>
        </div>
    </div>
    """
    
    return html

# === AI FUNCTIONS ===
def generate_feedback(resume_text, job_text, score):
    prompt = f"""You are a professional resume coach. This resume matches {score}% of job requirements.
    
    Resume: {resume_text[:2000]}
    Job: {job_text[:1000]}
    
    Give professional feedback:
    - Strengths (2 points)
    - Gaps (2-3 points)
    - Priority fixes (numbered list)
    Tone: Encouraging, specific, actionable."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except:
        return f"Match Score: {score}%\n\nFocus on adding missing technical skills to improve your match."

def generate_humanized_resume(resume_text, job_text, skills):
    missing = list(SKILLS_DB - set(skills))
    missing_str = ', '.join(missing[:6]) if missing else "none"
    
    prompt = f"""Rewrite this resume in a natural, human voice. Integrate these skills if relevant: {missing_str}.
    
    Original: {resume_text[:2000]}
    Job Requirements: {job_text[:1000]}
    
    Rules:
    1. Natural flow, varied sentences
    2. Honest about skill levels ("familiar with", "exposure to")
    3. Strong action verbs
    4. Professional but human tone
    
    Format: Name, Summary, Skills, Experience, Education."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8
        )
        return response.choices[0].message.content
    except:
        return "Error generating resume. Please try again."

# === MAIN ANALYSIS ===
def analyze_resume(resume_file, job_text, location):
    resume_text = extract_text(resume_file)
    if not resume_text:
        return "Error: Could not read file", "", "", "", "<div style='padding:20px;background:#ffebee;'>Upload error</div>"
    
    if not job_text:
        return "Error: Paste job description", "", "", "", "<div style='padding:20px;background:#fff3e0;'>Add job description</div>"
    
    # Extract skills
    resume_skills = extract_skills(resume_text)
    job_skills = extract_skills(job_text)
    
    # Calculate score
    if job_skills:
        matched = set(resume_skills).intersection(set(job_skills))
        score = round((len(matched) / len(job_skills)) * 100, 1)
    else:
        score = 0
        matched = set()
    
    # Generate outputs
    feedback = generate_feedback(resume_text, job_text, score)
    humanized = generate_humanized_resume(resume_text, job_text, resume_skills)
    jobs_html = generate_job_links(resume_skills, location)
    
    # Skills display
    skills_html = f"""
    <div style="background: #fafafa; padding: 15px; border-radius: 8px; border: 1px solid #ddd;">
        <p><strong>Found in your resume:</strong> {', '.join(resume_skills) if resume_skills else 'None detected'}</p>
        <p><strong>Required in job:</strong> {', '.join(job_skills) if job_skills else 'None detected'}</p>
        <p><strong>Matched:</strong> {', '.join(matched) if matched else 'None'}</p>
    </div>
    """
    
    # Score display
    color = "#000" if score >= 80 else "#555" if score >= 60 else "#999"
    bg = "#f5f5f5"
    
    score_html = f"""
    <div style="background: {bg}; border: 3px solid #000; border-radius: 0; padding: 30px; text-align: center;">
        <div style="font-size: 4em; font-weight: 800; color: {color}; font-family: monospace;">{score}%</div>
        <div style="font-size: 1.1em; color: #333; margin-top: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 2px;">Match Score</div>
    </div>
    """
    
    return feedback, humanized, skills_html, jobs_html, score_html

# === BLACK & WHITE STRIPED UI ===
css = """
body {
    font-family: 'Courier New', monospace;
    background: repeating-linear-gradient(
        45deg,
        #fff,
        #fff 10px,
        #f5f5f5 10px,
        #f5f5f5 20px
    );
    min-height: 100vh;
    margin: 0;
}

.gradio-container {
    background: #fff;
    border: 4px solid #000;
    border-radius: 0;
    padding: 40px !important;
    max-width: 1400px;
    margin: 30px auto;
    box-shadow: 8px 8px 0 #000;
}

h1 {
    color: #000;
    text-align: center;
    font-size: 3em;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: 5px;
    border-bottom: 4px solid #000;
    padding-bottom: 20px;
}

.subtitle {
    text-align: center;
    color: #555;
    font-size: 1em;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 30px;
}

.input-box {
    background: #fff;
    padding: 25px;
    border: 3px solid #000;
    box-shadow: 4px 4px 0 #000;
}

.feedback-box {
    background: #fff;
    border: 3px solid #000;
    padding: 20px;
    box-shadow: 4px 4px 0 #000;
    margin: 10px 0;
}

.resume-box {
    background: #f5f5f5;
    border: 3px solid #000;
    padding: 20px;
    box-shadow: 4px 4px 0 #000;
    margin: 10px 0;
    font-family: 'Courier New', monospace;
    white-space: pre-wrap;
}

.jobs-box {
    background: #fff;
    border: 3px solid #000;
    box-shadow: 4px 4px 0 #000;
    margin: 10px 0;
}

button[type="submit"] {
    background: #000 !important;
    color: #fff !important;
    font-family: 'Courier New', monospace !important;
    font-size: 1.1em !important;
    font-weight: 800 !important;
    text-transform: uppercase !important;
    letter-spacing: 2px !important;
    padding: 15px 40px !important;
    border-radius: 0 !important;
    border: 3px solid #000 !important;
    box-shadow: 4px 4px 0 #555 !important;
}

button[type="submit"]:hover {
    background: #fff !important;
    color: #000 !important;
    box-shadow: 2px 2px 0 #000 !important;
}
"""

# === BUILD UI ===
with gr.Blocks(css=css) as demo:
    gr.Markdown("<h1>NAKED RESUME</h1>")
    gr.Markdown("<p class='subtitle'>Brutally Honest • Humanized • Job-Ready</p>")
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes="input-box"):
                gr.Markdown("### STEP 1: UPLOAD RESUME")
                resume_input = gr.File(file_types=[".pdf", ".docx"])
                
                gr.Markdown("### STEP 2: PASTE JOB DESCRIPTION")
                job_input = gr.Textbox(lines=10, placeholder="Paste the full job description here...")
                
                gr.Markdown("### STEP 3: YOUR LOCATION")
                location_input = gr.Textbox(value="United States", label="Location for job search")
                
                analyze_btn = gr.Button("ANALYZE & FIND JOBS")
        
        with gr.Column(scale=1):
            score_output = gr.HTML()
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes="feedback-box"):
                gr.Markdown("### PROFESSIONAL FEEDBACK")
                feedback_output = gr.Markdown()
            
            with gr.Group(elem_classes="feedback-box"):
                gr.Markdown("### SKILLS ANALYSIS")
                skills_output = gr.HTML()
        
        with gr.Column(scale=1):
            with gr.Group(elem_classes="resume-box"):
                gr.Markdown("### YOUR HUMANIZED RESUME")
                resume_output = gr.Markdown()
    
    with gr.Row():
        with gr.Column(scale=1):
            with gr.Group(elem_classes="jobs-box"):
                gr.Markdown("### MATCHING JOBS")
                jobs_output = gr.HTML()
    
    analyze_btn.click(
        fn=analyze_resume,
        inputs=[resume_input, job_input, location_input],
        outputs=[feedback_output, resume_output, skills_output, jobs_output, score_output]
    )

demo.launch(share=True)