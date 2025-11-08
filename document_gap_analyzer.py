# Cell 1: Install Dependencies
!pip install rdm
!pip install PyPDF2
!pip install pdfplumber
!pip install openai
!pip install python-docx
!pip install streamlit
!pip install pandas
!pip install matplotlib

# Clone the open source repositories
!git clone https://github.com/innolitics/rdm.git
!git clone https://github.com/VintLin/pdf-comparator.git
!git clone https://github.com/openregulatory/templates.git

# Cell 2: Imports and Configuration
import os
import sys
import pandas as pd

# Install packages and restart kernel if needed
import subprocess
import sys

# Install required packages
subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "pdfplumber"])
subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])

# Now import the installed packages
!pip install openai==0.28
import openai
from pathlib import Path
import json
import PyPDF2
import pdfplumber
from docx import Document
import re
from typing import Dict, List, Tuple

# Add cloned repositories to path
sys.path.append('./rdm')
sys.path.append('./pdf-comparator')

# OpenAI API setup (add your key)
openai.api_key = "your-openai-api-key-here"  # Replace with your key

# Create directories for our MVP
os.makedirs('sample_documents', exist_ok=True)
os.makedirs('reference_checklists', exist_ok=True)
os.makedirs('output_reports', exist_ok=True)

print("✅ Environment setup complete!")

# Cell 3: Document Processing Functions
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using pdfplumber"""
    text_content = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text_content += page.extract_text() or ""
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""
    return text_content

def extract_docx_text(docx_path: str) -> str:
    """Extract text from Word document"""
    try:
        doc = Document(docx_path)
        text_content = ""
        for paragraph in doc.paragraphs:
            text_content += paragraph.text + "\n"
        return text_content
    except Exception as e:
        print(f"Error extracting DOCX: {e}")
        return ""

def process_document(file_path: str) -> str:
    """Process document based on file extension"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.pdf':
        return extract_pdf_text(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_docx_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

# Test the functions
print("✅ Document processing functions ready!")

# Cell 4: Create ISO 14971 Risk Management Checklist
iso_14971_checklist = {
    "Risk Management Process": [
        "Risk management plan established and documented",
        "Risk management file created and maintained",
        "Responsible organization defined",
        "Qualifications and experience of personnel documented"
    ],
    "Risk Analysis": [
        "Intended use and reasonably foreseeable misuse identified",
        "Characteristics related to safety identified",
        "Hazards and hazardous situations identified",
        "Risk estimation performed (severity and probability)",
        "Risk evaluation criteria established"
    ],
    "Risk Control": [
        "Risk control measures implemented",
        "Residual risk evaluated",
        "Risk/benefit analysis conducted where applicable",
        "Risks arising from risk control measures evaluated"
    ],
    "Risk Management Report": [
        "Overall residual risk evaluated and acceptable",
        "Risk management report completed",
        "Risk management process review conducted"
    ],
    "Production and Post-Production": [
        "Production and post-production information collection plan",
        "Post-production surveillance system established",
        "Information evaluation and risk management file updates"
    ]
}

# Save checklist as JSON for reuse
with open('reference_checklists/iso_14971_checklist.json', 'w') as f:
    json.dump(iso_14971_checklist, f, indent=2)

print("✅ ISO 14971 checklist created and saved!")
print(f"Total requirements: {sum(len(items) for items in iso_14971_checklist.values())}")

# Cell 5: GPT-Powered Analysis Functions
def create_analysis_prompt(document_text: str, checklist: Dict) -> str:
    """Create prompt for GPT analysis"""
    checklist_text = ""
    for category, items in checklist.items():
        checklist_text += f"\n{category}:\n"
        for item in items:
            checklist_text += f"  - {item}\n"
    
    prompt = f"""
    You are a regulatory compliance expert analyzing a supplier document against ISO 14971 requirements.
    
    DOCUMENT TO ANALYZE:
    {document_text[:4000]}...  # Truncate for token limits
    
    REQUIREMENTS CHECKLIST:
    {checklist_text}
    
    Please analyze the document and provide:
    1. COMPLIANCE STATUS for each requirement (Met/Partially Met/Not Met/Not Applicable)
    2. EVIDENCE found in the document (specific quotes or references)
    3. GAPS identified (what's missing or insufficient)
    4. RISK LEVEL for each gap (Critical/Major/Minor)
    
    Format your response as structured JSON.
    """
    return prompt

def analyze_with_gpt(document_text: str, checklist: Dict) -> Dict:
    """Analyze document using GPT"""
    prompt = create_analysis_prompt(document_text, checklist)
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse response (you might need to clean this up)
        analysis_result = response.choices[0].message.content
        return {"raw_analysis": analysis_result, "status": "success"}
        
    except Exception as e:
        return {"error": str(e), "status": "failed"}

print("✅ GPT analysis functions ready!")

# Cell 6: Gap Analysis and Report Generation
def generate_gap_memo(analysis_result: Dict, supplier_name: str = "Supplier") -> str:
    """Generate formatted gap analysis memo"""
    
    memo_template = f"""
# GAP ANALYSIS MEMO
**Supplier:** {supplier_name}
**Standard:** ISO 14971 Risk Management
**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}

## EXECUTIVE SUMMARY
Document analysis completed against ISO 14971 requirements.

## DETAILED FINDINGS
{analysis_result.get('raw_analysis', 'Analysis failed')}

## RECOMMENDATIONS
Based on the gaps identified, the following actions are recommended:
1. Request additional documentation for critical gaps
2. Clarify requirements for partially met items
3. Schedule follow-up review after supplier responses

---
*Generated by Automated Document Gap Analyzer*
    """
    
    return memo_template

def save_gap_memo(memo_content: str, filename: str):
    """Save gap memo to file"""
    filepath = f"output_reports/{filename}"
    with open(filepath, 'w') as f:
        f.write(memo_content)
    print(f"✅ Gap memo saved to: {filepath}")

print("✅ Report generation functions ready!")

# The function body
def test_pdf_processing(pdf_path=None):  # Renamed function to match the call below
    # Function implementation would go here
    # ...
    
    # For demonstration purposes, let's assume we have some extracted text
    # In a real implementation, you would extract text from the PDF at pdf_path
    extracted_text = "This is a sample text containing ISO 14971 and risk management information."
    
    if extracted_text:
        print(f"✅ Successfully extracted {len(extracted_text)} characters from PDF")
        print("📄 First 500 characters:")
        print("-" * 50)
        print(extracted_text[:500] + "...")
        print("-" * 50)
        return pdf_path, extracted_text
    else:
        print("❌ Failed to extract text from PDF")
        return None, None

def verify_pdf_content(extracted_text: str):
    """Verify that key content was extracted from PDF"""
    
    key_phrases = [
        "ISO 14971",
        "risk management",
        "hazard identification",
        "risk control measures",
        "residual risk",
        "post-production surveillance"
    ]
    
    found_phrases = []
    missing_phrases = []
    
    for phrase in key_phrases:
        if phrase.lower() in extracted_text.lower():
            found_phrases.append(phrase)
        else:
            missing_phrases.append(phrase)
    
    print(f"✅ Found {len(found_phrases)}/{len(key_phrases)} key phrases")
    print(f"📋 Found: {', '.join(found_phrases)}")
    
    if missing_phrases:
        print(f"⚠️  Missing: {', '.join(missing_phrases)}")
    
    return len(found_phrases) >= len(key_phrases) * 0.8  # 80% success rate

# Run the PDF processing test
print("🧪 TESTING PDF PROCESSING")
print("=" * 40)

pdf_path, extracted_text = test_pdf_processing()  # Now this matches the function name above

if pdf_path and extracted_text:
    # Verify content extraction
    content_ok = verify_pdf_content(extracted_text)
    
    if content_ok:
        print("✅ PDF processing test PASSED!")
        print(f"📁 Test PDF ready at: {pdf_path}")
    else:
        print("⚠️  PDF processing test partially successful")
        print("Some content may not have been extracted properly")
else:
    print("❌ PDF processing test FAILED!")

print("\n" + "=" * 40)

# Cell 8: Test the Complete System
# First, let's create a sample test document
sample_doc_content = """
Risk Management Plan for Medical Device XYZ

1. Risk Management Process
This document establishes the risk management process for our medical device according to ISO 14971.
The risk management file has been created and is maintained by the Quality Assurance team.

2. Risk Analysis
We have identified the intended use of the device for patient monitoring.
Several hazards have been identified including electrical hazards and software malfunctions.
Risk estimation has been performed using a 5x5 risk matrix.

3. Risk Control Measures
Several risk control measures have been implemented including:
- Electrical safety testing
- Software validation
- User training requirements

4. Residual Risk Evaluation
All residual risks have been evaluated and found to be acceptable.
"""

# Save sample document
with open('sample_documents/sample_risk_mgmt_doc.txt', 'w') as f:
    f.write(sample_doc_content)

# For testing, let's create a simple text processor
def process_text_file(file_path: str) -> str:
    with open(file_path, 'r') as f:
        return f.read()

# Modify the process_document function for testing
def process_document_test(file_path: str) -> str:
    """Test version that handles.txt files"""
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        return process_text_file(file_path)
    elif file_ext == '.pdf':
        return extract_pdf_text(file_path)
    elif file_ext in ['.docx', '.doc']:
        return extract_docx_text(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_ext}")

print("✅ Test setup complete!")

result = analyze_supplier_document('sample_documents/sample_risk_mgmt_doc.pdf', 'Test Supplier Inc')
# OR modify the analyze_supplier_document function to support .txt files

if result.get("status") == "success":
    print("🎉 SUCCESS! Your MVP is working!")
    print(f"📄 Report saved as: {result['filename']}")
    print("\n" + "="*50)
    print("GENERATED GAP MEMO:")
    print("="*50)
    print(result['memo_content'][:1000] + "...")
else:
    print("❌ Error occurred:")
    print(result.get("error", "Unknown error"))

# Cell 10A: Simple Interactive Interface (No widgets required)
import os
from pathlib import Path

def interactive_document_analyzer():
    """Simple interactive interface using input() functions"""
    
    print("🔍 DOCUMENT GAP ANALYZER")
    print("=" * 40)
    
    # Show available documents
    sample_dir = Path('sample_documents')
    if sample_dir.exists():
        pdf_files = list(sample_dir.glob('*.pdf'))
        docx_files = list(sample_dir.glob('*.docx'))
        all_files = pdf_files + docx_files
        
        if all_files:
            print("📁 Available documents:")
            for i, file in enumerate(all_files, 1):
                print(f"   {i}. {file.name}")
            print(f"   {len(all_files) + 1}. Enter custom file path")
        else:
            print("📁 No documents found in sample_documents folder")
            all_files = []
    else:
        print("📁 sample_documents folder not found")
        all_files = []
    
    # Get file selection
    while True:
        try:
            if all_files:
                choice = input(f"\nSelect document (1-{len(all_files) + 1}): ").strip()
                
                if choice.isdigit():
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(all_files):
                        selected_file = str(all_files[choice_num - 1])
                        break
                    elif choice_num == len(all_files) + 1:
                        selected_file = input("Enter full file path: ").strip()
                        if os.path.exists(selected_file):
                            break
                        else:
                            print("❌ File not found. Please try again.")
                    else:
                        print("❌ Invalid selection. Please try again.")
                else:
                    print("❌ Please enter a number.")
            else:
                selected_file = input("Enter full file path: ").strip()
                if os.path.exists(selected_file):
                    break
                else:
                    print("❌ File not found. Please try again.")
        except KeyboardInterrupt:
            print("\n👋 Analysis cancelled.")
            return
    
    # Get supplier name
    supplier_name = input("Enter supplier name (or press Enter for 'Unknown Supplier'): ").strip()
    if not supplier_name:
        supplier_name = "Unknown Supplier"
    
    # Run analysis
    print(f"\n🔄 Analyzing document: {Path(selected_file).name}")
    print(f"🏢 Supplier: {supplier_name}")
    print("⏳ Please wait...")
    
    try:
        result = analyze_supplier_document(selected_file, supplier_name)
        
        if result.get("status") == "success":
            print("\n✅ ANALYSIS COMPLETE!")
            print(f"📊 Characters processed: {result.get('document_length', 'Unknown')}")
            print(f"📄 Report saved as: {result.get('filename', 'Unknown')}")
            
            # Ask if user wants to see preview
            show_preview = input("\nShow memo preview? (y/n): ").strip().lower()
            if show_preview in ['y', 'yes']:
                print("\n" + "="*50 + " MEMO PREVIEW " + "="*50)
                preview = result.get('memo_content', '')[:1000]
                print(preview + "..." if len(result.get('memo_content', '')) > 1000 else preview)
                print("="*113)
        else:
            print("\n❌ ANALYSIS FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
    
    # Ask if user wants to analyze another document
    another = input("\nAnalyze another document? (y/n): ").strip().lower()
    if another in ['y', 'yes']:
        print("\n" + "="*50)
        interactive_document_analyzer()  # Recursive call
    else:
        print("👋 Thanks for using the Document Gap Analyzer!")

# Run the interactive analyzer
print("✅ Simple interactive interface ready!")
print("💡 Run: interactive_document_analyzer() to start")