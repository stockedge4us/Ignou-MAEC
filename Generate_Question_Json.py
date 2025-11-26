import json
import os
import re
from tkinter import Tk, filedialog
from docx import Document


def is_question(text):
    """
    Determine if text is likely a question by checking for three formats:
    1. Starts with a number (e.g., "1. What is...")
    2. Starts with a list item (e.g., "(i) ...", "(a) ...", "a. ...")
    3. Is a keyword-based question (e.g., "Compare AI...")
    """
    clean_text = text.strip()

    # Case 1: Starts with a number (e.g., "1. What is...")
    if re.match(r'^\d+\.', clean_text):
        return True

    # Case 2: Starts with a list item (e.g., "(i) ...", "(a) ...")
    if re.match(r'^\s*\([a-z0-9ivx]+\)', clean_text, re.IGNORECASE):
        return True

    # Case 3: It's a keyword-based question (for MCS-224)
    if len(clean_text) < 30:
        return False
    question_words = [
        'what', 'how', 'why', 'explain', 'discuss', 'describe',
        'distinguish', 'compare', 'differentiate', 'define',
        'analyze', 'examine', 'evaluate', 'illustrate', 'state',
        'bring out', 'give', 'write', 'using', 'critically',
        'let ', 'for the following', 'consider the', 'suppose a',
        'apply the', 'obtain ', 'transform the', 'find the',
        'draw ', 'write ', 'differentiate', 'critically'
    ]
    text_lower = clean_text.lower()
    has_question_indicator = (
            clean_text.endswith('?') or
            any(text_lower.startswith(word) for word in question_words)
    )
    if not has_question_indicator:
        has_question_indicator = any(word in text_lower for word in question_words)
    return has_question_indicator


def is_skip_line(text):
    """Lines to completely ignore"""
    text_lower = text.lower()
    if any(keyword in text_lower for keyword in skip_keywords):
        skip_keywords = [
            'summary statistics', 'total unique', 'total questions', 'note:',
            'this consolidated', 'repetitive questions', 'questions with similar',
            'exam pattern', 'time:', 'maximum marks:', 'weightage:', 'structure:',
            'december 20', 'june 20', 'attempt any', 'answer any', 'marks each',
            'words each', 'the following table:', 'write short notes on any',
            'group 1:', 'group 2:', 'group 3:', 'group 4:', 'group 5:', 'group 6:', 'group 7:'
        ]
        return True
    if len(text) < 30 and not re.match(r'^\s*(\d+\.|\([a-z0-9ivx]+\))', text, re.IGNORECASE) and not text.endswith('?'):
        if text.count(' ') < 5 and not any(text.lower().startswith(w) for w in ['what', 'how', 'why']):
            return True
    return False


def parse_question_bank(docx_path):
    doc = Document(docx_path)
    data = {}
    current_subject = None
    current_section = None
    in_skip_zone = False

    question_counter = 1  # This will be reset for each subject

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        clean_text = text.replace('**', '').strip()

        # Check if we're entering a skip zone
        if re.match(r'^Summary Statistics', clean_text, re.IGNORECASE):
            in_skip_zone = True
            current_subject = None
            current_section = None
            print(f"\n--- Entering Skip Zone (Summary Statistics) ---")
            continue

        # Skip everything if in skip zone
        if in_skip_zone:
            if re.match(r'^[A-Z]{2,}-\d+', clean_text):
                in_skip_zone = False
                print(f"--- Exiting Skip Zone ---")
            else:
                continue

        # --- KEY CHANGE IS HERE ---
        # Detect subject titles
        if re.match(r'^[A-Z]{2,}-\d+', clean_text):
            current_subject = clean_text
            data[current_subject] = {}
            current_section = None
            question_counter = 1  # <-- RESET COUNTER FOR NEW SUBJECT
            print(f"\n📚 Found subject: {current_subject}")
            continue
        # --- END OF CHANGE ---

        # Detect section headers
        section_match = re.match(r'^(SECTION|QUESTION)\s+([A-Z0-9]+)', clean_text, re.IGNORECASE)
        if section_match:
            current_section = clean_text
            if current_subject:
                if current_subject not in data:
                    data[current_subject] = {}
                data[current_subject][current_section] = []
                print(f"   📂 Found section: {current_section}")
            continue

        # Skip specific lines
        if is_skip_line(clean_text):
            preview = clean_text[:80] + "..." if len(clean_text) > 80 else clean_text
            print(f"      - Skipping line: {preview}")
            continue

        # Skip if no subject/section context
        if not current_subject or not current_section:
            continue

        # Check if this is an actual question
        if is_question(clean_text):
            # 1. Clean up old numbering
            processed_text = re.sub(r'^\s*(\d+\.|\([a-z0-9ivx]+\))', '', clean_text).strip()

            # 2. Add our new subject-specific number
            numbered_question = f"{question_counter}. {processed_text}"

            if current_subject in data and current_section in data[current_subject]:
                data[current_subject][current_section].append(numbered_question)

                preview = processed_text[:75] + "..." if len(processed_text) > 75 else processed_text
                print(f"      ✓ Q{question_counter}: {preview}")

                question_counter += 1  # Increment for this subject
            else:
                print(
                    f"      ⚠️ ERROR: Tried to add question but context was lost (Subj: {current_subject}, Sec: {current_section})")
        else:
            preview = clean_text[:80] + "..." if len(clean_text) > 80 else clean_text
            print(f"      - Skipping (Not a question/header): {preview}")

    # Calculate total questions at the end
    total_questions = 0
    for subject in data:
        for section in data[subject]:
            total_questions += len(data[subject][section])

    return data, total_questions


if __name__ == "__main__":
    print("=" * 70)
    print("📖 QUESTION BANK PARSER v7.0 (Subject-Specific Numbering)")
    print("=" * 70)
    print("\n📂 Please select your Word file (e.g., Question_Bank.docx)\n")

    Tk().withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Question Bank Word File",
        filetypes=[("Word files", "*.docx")]
    )

    if not file_path:
        print("❌ No file selected. Exiting.")
        exit()

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        exit()

    output_dir = os.path.join(os.path.dirname(file_path), "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "questions.json")

    print(f"\n🔄 Parsing: {os.path.basename(file_path)}")
    print("-" * 70)

    questions_data, total_extracted = parse_question_bank(file_path)

    # Print detailed summary
    print("\n" + "=" * 70)
    print("📊 PARSING SUMMARY")
    print("=" * 70)

    if not questions_data:
        print("NO DATA PARSED. Check your file and script logic.")

    for subject, sections in questions_data.items():
        subject_count = 0
        if not sections:
            print(f"\n📚 {subject} (0 questions)")
            continue

        for section, questions in sections.items():
            subject_count += len(questions)

        print(f"\n📚 {subject}")
        print(f"   Total: {subject_count} questions")

        for section, questions in sections.items():
            section_name = section[:60] + "..." if len(section) > 60 else section
            print(f"   • {section_name}: {len(questions)} questions")

    print("\n" + "=" * 70)
    print(f"✅ TOTAL QUESTIONS EXTRACTED: {total_extracted}")
    print("=" * 70)

    # Save to JSON
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(questions_data, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Output saved to: {output_file}")
    print("\n✨ Parsing complete! Your new JSON file has subject-specific numbering.\n")