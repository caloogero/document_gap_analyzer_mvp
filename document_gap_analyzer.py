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

# Cell 5: School AI Prompt Generation (Replaces GPT Integration)
import json
from typing import Dict

def create_school_ai_prompt(document_text: str, checklist: Dict) -> str:
    """Create optimized prompt for school ChatGPT/Claude"""
    
    # Truncate document for manual copying (most AI tools handle 8000-12000 chars well)
    max_length = 8000
    truncated_text = document_text[:max_length]
    if len(document_text) > max_length:
        truncated_text += f"\n\n[Document truncated from {len(document_text)} to {max_length} characters for analysis...]"
    
    # Format checklist clearly
    checklist_text = ""
    requirement_count = 0
    for category, items in checklist.items():
        checklist_text += f"\n**{category}:**\n"
        for item in items:
            requirement_count += 1
            checklist_text += f"  {requirement_count}. {item}\n"
    
    # Create comprehensive prompt
    prompt = f"""I need you to perform a regulatory compliance gap analysis for a medical device supplier document against ISO 14971 Risk Management requirements.

**SUPPLIER DOCUMENT TO ANALYZE:**

    
**ISO 14971 REQUIREMENTS CHECKLIST ({requirement_count} total requirements):**
{checklist_text}

**ANALYSIS INSTRUCTIONS:**
Please analyze the document systematically and provide:

1. **COMPLIANCE ASSESSMENT** for each numbered requirement:
   - ✅ **Met**: Requirement clearly addressed with sufficient detail and evidence
   - ⚠️ **Partially Met**: Requirement mentioned but lacks completeness or detail
   - ❌ **Not Met**: Requirement not addressed, missing, or inadequate
   - ➖ **Not Applicable**: Requirement doesn't apply to this document type

2. **EVIDENCE QUOTES**: For each requirement, quote specific text from the document that supports your assessment (use "No evidence found" if none)

3. **GAP IDENTIFICATION**: For Partially Met and Not Met items, specify exactly what is missing or insufficient

4. **RISK PRIORITIZATION**: Assign risk levels for gaps:
   - 🔴 **Critical**: Major regulatory compliance issue, could block approval
   - 🟡 **Major**: Significant gap requiring attention before submission
   - 🟢 **Minor**: Small improvement recommended but not blocking

**OUTPUT FORMAT:**
Please structure your response with clear sections for each requirement category. Use the exact requirement numbers (1, 2, 3, etc.) and include specific quotes from the document as evidence.

Focus on practical regulatory compliance for medical device risk management. Be specific about what evidence supports each assessment.
"""
    
    return prompt

def generate_school_ai_analysis_package(file_path: str, supplier_name: str = "Unknown Supplier"):
    """Generate complete package for school AI analysis"""
    
    print(f"📝 Generating school AI package for: {supplier_name}")
    print(f"📄 Document: {file_path}")
    
    try:
        # Step 1: Extract document text
        print("📖 Extracting document text...")
        document_text = process_document(file_path)
        
        if not document_text.strip():
            return {"error": "Could not extract text from document", "status": "failed"}
        
        print(f"✅ Extracted {len(document_text)} characters")
        
        # Step 2: Load checklist
        print("📋 Loading ISO 14971 checklist...")
        checklist_path = 'reference_checklists/iso_14971_checklist.json'
        if os.path.exists(checklist_path):
            with open(checklist_path, 'r') as f:
                checklist = json.load(f)
        else:
            checklist = iso_14971_checklist
        
        # Step 3: Generate prompt
        print("🎓 Creating school AI prompt...")
        prompt = create_school_ai_prompt(document_text, checklist)
        
        # Step 4: Save prompt file
        timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M')
        prompt_filename = f"SCHOOL_AI_PROMPT_{supplier_name.replace(' ', '_')}_{timestamp}.txt"
        prompt_path = f'output_reports/{prompt_filename}'
        
        with open(prompt_path, 'w', encoding='utf-8') as f:
            f.write(f"# SCHOOL AI ANALYSIS PROMPT\n")
            f.write(f"# Supplier: {supplier_name}\n")
            f.write(f"# Document: {file_path}\n")
            f.write(f"# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"# Document Length: {len(document_text)} characters\n")
            f.write(f"# Prompt Length: {len(prompt)} characters\n\n")
            f.write("="*80 + "\n")
            f.write("COPY EVERYTHING BELOW INTO CHATGPT/CLAUDE:\n")
            f.write("="*80 + "\n\n")
            f.write(prompt)
            f.write("\n\n" + "="*80 + "\n")
            f.write("END OF PROMPT - COPY EVERYTHING ABOVE THIS LINE\n")
            f.write("="*80)
        
        print(f"✅ School AI prompt saved to: {prompt_path}")
        
        return {
            "status": "success",
            "prompt_file": prompt_filename,
            "prompt_path": prompt_path,
            "prompt_length": len(prompt),
            "document_length": len(document_text),
            "supplier_name": supplier_name
        }
        
    except Exception as e:
        return {"error": f"Prompt generation failed: {str(e)}", "status": "failed"}

print("✅ School AI prompt generation functions ready!")

# Cell 6: Process School AI Response
def process_school_ai_response_interactive():
    """Interactive function to process AI response from school tools"""
    
    print("🎓 SCHOOL AI RESPONSE PROCESSOR")
    print("="*50)
    print("📋 Instructions:")
    print("1. Copy your AI response from ChatGPT/Claude")
    print("2. Paste it below (can be multiple lines)")
    print("3. Type 'DONE' on a new line when finished")
    print("4. Press Enter to process")
    print("\n📥 Paste your AI response below:")
    print("-" * 30)
    
    ai_response_lines = []
    while True:
        try:
            line = input()
            if line.strip().upper() == "DONE":
                break
            ai_response_lines.append(line)
        except KeyboardInterrupt:
            print("\n👋 Analysis cancelled")
            return None
    
    ai_response = "\n".join(ai_response_lines)
    
    if not ai_response.strip():
        print("❌ No response provided")
        return None
    
    print(f"✅ Received {len(ai_response)} characters of AI response")
    
    # Get additional info
    supplier_name = input("\n🏢 Enter supplier name: ").strip() or "Unknown Supplier"
    ai_tool_used = input("🤖 Which AI tool did you use? (ChatGPT/Claude/Other): ").strip() or "School AI"
    
    return {
        "ai_response": ai_response,
        "supplier_name": supplier_name,
        "ai_tool": ai_tool_used,
        "response_length": len(ai_response)
    }

def format_school_ai_response_to_memo(response_data: dict) -> str:
    """Format school AI response into professional gap memo"""
    
    if not response_data:
        return "Error: No response data provided"
    
    ai_response = response_data["ai_response"]
    supplier_name = response_data["supplier_name"]
    ai_tool = response_data["ai_tool"]
    
    # Create professional memo header
    memo_content = f"""# GAP ANALYSIS MEMO
**Supplier:** {supplier_name}
**Standard:** ISO 14971 Risk Management for Medical Devices
**Analysis Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}
**Analysis Method:** {ai_tool} (School AI Access)
**Analyst:** Automated Gap Analysis Tool

## EXECUTIVE SUMMARY
Comprehensive document analysis completed using institutional AI resources against ISO 14971 requirements. This memo provides a systematic assessment of compliance gaps and recommendations for regulatory submission readiness.

## DETAILED ANALYSIS RESULTS

{ai_response}

## NEXT STEPS AND RECOMMENDATIONS

Based on the analysis above, the following actions are recommended:

### Immediate Actions (Critical/Major Gaps)
1. **Address all Critical gaps** - These must be resolved before regulatory submission
2. **Provide additional documentation** for Major gaps identified
3. **Request clarification** from supplier on Partially Met requirements

### Follow-up Actions (Minor Gaps)
1. **Document improvements** for Minor gaps to strengthen submission
2. **Verify evidence** for all Met requirements is properly documented
3. **Schedule follow-up review** after supplier provides additional documentation

### Quality Assurance
1. **Cross-reference** findings with other regulatory requirements
2. **Validate** all quoted evidence against original documents
3. **Prepare** gap closure tracking spreadsheet

## REGULATORY IMPACT ASSESSMENT
- **Submission Readiness:** Based on Critical and Major gaps identified
- **Risk Level:** Determined by number and severity of compliance gaps
- **Timeline Impact:** Estimated based on gap complexity and supplier responsiveness

---
**Document Information:**
- Analysis completed: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
- AI Tool used: {ai_tool}
- Response length: {response_data.get('response_length', 'Unknown')} characters
- Generated by: Document Gap Analyzer MVP (School AI Version)

*This analysis was performed using institutional AI resources at no cost to the project.*
"""
    
    return memo_content

print("✅ School AI response processing functions ready!")

# Cell 7: Complete School AI Analysis Workflow
def complete_school_ai_workflow(file_path: str, supplier_name: str = "Unknown Supplier"):
    """Complete workflow using school AI tools"""
    
    print("🎓 COMPLETE SCHOOL AI WORKFLOW")
    print("="*60)
    
    # Step 1: Generate prompt for school AI
    print("📝 Step 1: Generating AI prompt...")
    prompt_result = generate_school_ai_analysis_package(file_path, supplier_name)
    
    if prompt_result["status"] == "failed":
        print(f"❌ Prompt generation failed: {prompt_result['error']}")
        return prompt_result
    
    print(f"✅ Prompt generated: {prompt_result['prompt_file']}")
    
    # Step 2: Display instructions for user
    print(f"\n📋 Step 2: Use Your School AI")
    print("-" * 40)
    print(f"1. Open the prompt file: output_reports/{prompt_result['prompt_file']}")
    print("2. Copy the entire prompt (between the === lines)")
    print("3. Go to your school's AI tool:")
    print("   • ChatGPT: chat.openai.com")
    print("   • Claude: claude.ai") 
    print("   • Microsoft Copilot: copilot.microsoft.com")
    print("   • Google Gemini: gemini.google.com")
    print("4. Paste the prompt and submit")
    print("5. Copy the AI's complete response")
    print("6. Come back here and run the next step")
    
    # Step 3: Wait for user to get AI response
    print(f"\n⏳ Step 3: Waiting for your AI response...")
    print("Run the next function when you have the AI response:")
    print(">>> process_and_save_school_ai_analysis()")
    
    return {
        "status": "prompt_ready",
        "prompt_file": prompt_result['prompt_file'],
        "next_step": "Get AI response and run process_and_save_school_ai_analysis()"
    }

def process_and_save_school_ai_analysis():
    """Process AI response and save final gap memo"""
    
    print("📥 PROCESSING SCHOOL AI RESPONSE")
    print("="*50)
    
    # Get AI response from user
    response_data = process_school_ai_response_interactive()
    
    if not response_data:
        return {"error": "No response data received", "status": "failed"}
    
    # Format into professional memo
    print("📝 Formatting professional gap memo...")
    gap_memo = format_school_ai_response_to_memo(response_data)
    
    # Save the final memo
    timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M')
    supplier_clean = response_data["supplier_name"].replace(' ', '_')
    filename = f"GAP_MEMO_{supplier_clean}_{timestamp}.md"
    
    save_gap_memo(gap_memo, filename)
    
    print(f"✅ Analysis complete!")
    print(f"📊 Final report saved: output_reports/{filename}")
    print(f"🤖 AI tool used: {response_data['ai_tool']}")
    print(f"📄 Response length: {response_data['response_length']} characters")
    
    return {
        "status": "success",
        "memo_content": gap_memo,
        "filename": filename,
        "supplier_name": response_data["supplier_name"],
        "ai_tool": response_data["ai_tool"]
    }

print("✅ Complete school AI workflow ready!")

# Cell 8: Test School AI Workflow
def test_school_ai_workflow():
    """Test the school AI workflow with sample document"""
    
    print("🧪 TESTING SCHOOL AI WORKFLOW")
    print("="*50)
    
    # Check if sample PDF exists
    sample_pdf = 'sample_documents/sample_risk_mgmt_doc.pdf'
    if not os.path.exists(sample_pdf):
        print("📄 Creating sample PDF for testing...")
        # Use the PDF creation function from earlier
        try:
            pdf_path, _ = test_pdf_processing()  # From previous step
            sample_pdf = pdf_path
        except:
            print("❌ Could not create sample PDF")
            return None
    
    # Test prompt generation
    print(f"📝 Testing with: {sample_pdf}")
    result = complete_school_ai_workflow(sample_pdf, "Test Supplier (School AI)")
    
    if result["status"] == "prompt_ready":
        print("✅ PROMPT GENERATION TEST PASSED!")
        print(f"📁 Check file: output_reports/{result['prompt_file']}")
        
        # Show preview of prompt
        try:
            with open(f"output_reports/{result['prompt_file']}", 'r', encoding='utf-8') as f:
                content = f.read()
                # Find the actual prompt (between === lines)
                lines = content.split('\n')
                start_idx = None
                end_idx = None
                
                for i, line in enumerate(lines):
                    if "COPY EVERYTHING BELOW" in line:
                        start_idx = i + 2
                    elif "END OF PROMPT" in line:
                        end_idx = i
                        break
                
                if start_idx and end_idx:
                    prompt_preview = '\n'.join(lines[start_idx:start_idx+10])
                    print(f"\n📋 PROMPT PREVIEW (first 10 lines):")
                    print("-" * 40)
                    print(prompt_preview + "...")
                    print("-" * 40)
        except Exception as e:
            print(f"⚠️ Could not preview prompt: {e}")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"1. Open: output_reports/{result['prompt_file']}")
        print(f"2. Copy the prompt to your school's AI tool")
        print(f"3. Run: process_and_save_school_ai_analysis()")
        
        return result
    else:
        print("❌ PROMPT GENERATION FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return None

# Run the test
test_result = test_school_ai_workflow()

if test_result:
    print("\n🎉 SCHOOL AI WORKFLOW IS READY!")
    print("💡 Your MVP now works with free school AI access!")
else:
    print("\n❌ Workflow needs debugging")

# Cell 9: School AI Interactive Interface
def create_school_ai_interface():
    """Create simple interface for school AI workflow"""
    
    print("🎓 SCHOOL AI DOCUMENT ANALYZER")
    print("="*50)
    
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
    
    # Generate prompt
    print(f"\n🔄 Generating school AI prompt...")
    print(f"📄 Document: {Path(selected_file).name}")
    print(f"🏢 Supplier: {supplier_name}")
    
    try:
        result = complete_school_ai_workflow(selected_file, supplier_name)
        
        if result["status"] == "prompt_ready":
            print(f"\n✅ PROMPT READY!")
            print(f"📁 File: output_reports/{result['prompt_file']}")
            
            # Ask if user wants to continue with AI response
            continue_analysis = input("\nDo you have the AI response ready? (y/n): ").strip().lower()
            if continue_analysis in ['y', 'yes']:
                print("\n📥 Processing AI response...")
                final_result = process_and_save_school_ai_analysis()
                
                if final_result and final_result["status"] == "success":
                    print(f"\n🎉 ANALYSIS COMPLETE!")
                    print(f"📊 Final report: output_reports/{final_result['filename']}")
                    
                    # Ask if user wants to see preview
                    show_preview = input("\nShow memo preview? (y/n): ").strip().lower()
                    if show_preview in ['y', 'yes']:
                        print("\n" + "="*60 + " MEMO PREVIEW " + "="*60)
                        preview = final_result.get('memo_content', '')[:1000]
                        print(preview + "..." if len(final_result.get('memo_content', '')) > 1000 else preview)
                        print("="*133)
                else:
                    print("❌ AI response processing failed")
            else:
                print(f"\n💡 Next steps:")
                print(f"1. Open: output_reports/{result['prompt_file']}")
                print(f"2. Copy prompt to your school AI")
                print(f"3. Run: process_and_save_school_ai_analysis()")
        else:
            print(f"\n❌ PROMPT GENERATION FAILED!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
    
    # Ask if user wants to analyze another document
    another = input("\nAnalyze another document? (y/n): ").strip().lower()
    if another in ['y', 'yes']:
        print("\n" + "="*60)
        create_school_ai_interface()  # Recursive call
    else:
        print("👋 Thanks for using the School AI Document Gap Analyzer!")

print("✅ School AI interactive interface ready!")
print("💡 Run: create_school_ai_interface() to start")

# Cell 10: School AI Quick Start Guide
def display_school_ai_quick_start():
    """Display comprehensive quick start guide"""
    
    guide = """
🎓 SCHOOL AI DOCUMENT GAP ANALYZER - QUICK START GUIDE
================================================================

🚀 OPTION 1: INTERACTIVE MODE (Easiest)
----------------------------------------
Run this command:
>>> create_school_ai_interface()

Follow the prompts to:
1. Select your document
2. Enter supplier name  
3. Generate AI prompt
4. Use your school AI
5. Process the response

🔧 OPTION 2: MANUAL MODE (More Control)
---------------------------------------
Step 1: Generate prompt
>>> result = complete_school_ai_workflow('your_document.pdf', 'Supplier Name')

Step 2: Use school AI
- Open the generated prompt file
- Copy to ChatGPT/Claude/Copilot
- Get AI response

Step 3: Process response
>>> final_result = process_and_save_school_ai_analysis()

📚 SCHOOL AI PLATFORMS TO TRY:
-------------------------------
✅ ChatGPT (chat.openai.com) - Often available through school
✅ Claude (claude.ai) - High quality analysis
✅ Microsoft Copilot - Usually free with school accounts
✅ Google Gemini - Available with school Google accounts
✅ Perplexity AI - Often free for students

💡 PRO TIPS:
------------
• Try multiple AI tools and compare results
• Copy the ENTIRE prompt for best results
• Save AI responses for your records
• Check school IT for additional AI resources

📁 FILE LOCATIONS:
------------------
• Input documents: sample_documents/
• Generated prompts: output_reports/SCHOOL_AI_PROMPT_*.txt
• Final reports: output_reports/GAP_MEMO_*.md
• Checklists: reference_checklists/

🆘 TROUBLESHOOTING:
-------------------
• Document not found → Check file path and format (PDF/DOCX)
• Prompt too long → Document will be auto-truncated
• AI gives short response → Ask for more detailed analysis
• Missing checklist → Default ISO 14971 checklist will be used

🎯 SUCCESS INDICATORS:
----------------------
✅ Prompt file generated successfully
✅ AI provides structured compliance assessment  
✅ Professional gap memo created
✅ All requirements analyzed with evidence

================================================================
Ready to start? Run: create_school_ai_interface()
"""
    
    print(guide)

# Display the guide
display_school_ai_quick_start()

# Quick test function
def quick_test_school_ai():
    """Quick test of school AI workflow"""
    print("🧪 Quick test - generating sample prompt...")
    
    # Check if sample document exists
    sample_files = [
        'sample_documents/sample_risk_management_report.pdf',
        'sample_documents/PFMEA-Template-2.pdf'
    ]
    
    test_file = None
    for file in sample_files:
        if os.path.exists(file):
            test_file = file
            break
    
    if test_file:
        result = complete_school_ai_workflow(test_file, "Quick Test Supplier")
        if result["status"] == "prompt_ready":
            print(f"✅ Test successful! Prompt ready at: output_reports/{result['prompt_file']}")
        else:
            print("❌ Test failed")
    else:
        print("⚠️ No sample documents found for testing")
        print("💡 Add a PDF or DOCX file to sample_documents/ folder")

print("\n💡 READY TO USE SCHOOL AI!")
print("Run one of these commands:")
print("• create_school_ai_interface()  # Interactive mode")
print("• quick_test_school_ai()        # Quick test")