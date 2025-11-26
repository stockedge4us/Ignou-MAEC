import json
import os


def validate_questions_json(json_path):
    """Validate and display questions from JSON file"""

    if not os.path.exists(json_path):
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("=" * 80)
    print("📋 QUESTION BANK VALIDATION REPORT")
    print("=" * 80)

    total_questions = 0
    issues_found = []

    for subject_name, sections in data.items():
        print(f"\n{'=' * 80}")
        print(f"📚 SUBJECT: {subject_name}")
        print(f"{'=' * 80}")

        subject_total = 0

        for section_name, questions in sections.items():
            section_count = len(questions)
            subject_total += section_count

            print(f"\n📂 {section_name}")
            print(f"   Questions: {section_count}")
            print(f"   {'-' * 76}")

            for i, question in enumerate(questions, 1):
                # Display first 100 chars
                preview = question[:100].replace('\n', ' ')
                if len(question) > 100:
                    preview += "..."
                print(f"   {i}. {preview}")

                # Validation checks
                if len(question) < 20:
                    issues_found.append(f"⚠️ Short question in {section_name}: {question}")

                if not any(c.isalpha() for c in question):
                    issues_found.append(f"⚠️ No letters in {section_name}: {question}")

                # Check for likely non-questions
                non_question_indicators = [
                    'summary statistics',
                    'total unique',
                    'exam pattern',
                    'note:',
                    'consolidated document'
                ]
                if any(ind in question.lower() for ind in non_question_indicators):
                    issues_found.append(f"⚠️ Possible non-question in {section_name}: {question[:50]}...")

        print(f"\n   {'=' * 76}")
        print(f"   📊 Subject Total: {subject_total} questions")
        total_questions += subject_total

    # Overall summary
    print(f"\n{'=' * 80}")
    print(f"📊 OVERALL STATISTICS")
    print(f"{'=' * 80}")
    print(f"Total Subjects: {len(data)}")
    print(f"Total Questions: {total_questions}")

    # Issues report
    if issues_found:
        print(f"\n{'=' * 80}")
        print(f"⚠️ POTENTIAL ISSUES FOUND ({len(issues_found)})")
        print(f"{'=' * 80}")
        for issue in issues_found[:10]:  # Show first 10 issues
            print(issue)
        if len(issues_found) > 10:
            print(f"\n... and {len(issues_found) - 10} more issues")
    else:
        print(f"\n✅ No obvious issues found!")

    print(f"\n{'=' * 80}")

    # Interactive question viewer
    print("\n🔍 Would you like to view specific questions? (y/n): ", end='')
    choice = input().lower()

    if choice == 'y':
        subjects = list(data.keys())
        print("\nAvailable subjects:")
        for i, subj in enumerate(subjects, 1):
            print(f"{i}. {subj}")

        try:
            print("\nEnter subject number: ", end='')
            subj_idx = int(input()) - 1
            selected_subject = subjects[subj_idx]

            sections = list(data[selected_subject].keys())
            print(f"\nSections in {selected_subject}:")
            for i, sect in enumerate(sections, 1):
                print(f"{i}. {sect} ({len(data[selected_subject][sect])} questions)")

            print("\nEnter section number: ", end='')
            sect_idx = int(input()) - 1
            selected_section = sections[sect_idx]

            print(f"\n{'=' * 80}")
            print(f"Questions in {selected_section}")
            print(f"{'=' * 80}\n")

            for i, q in enumerate(data[selected_subject][selected_section], 1):
                print(f"{i}. {q}\n")

        except (ValueError, IndexError):
            print("Invalid selection.")


if __name__ == "__main__":
    json_file = "data/questions.json"

    if not os.path.exists(json_file):
        print(f"❌ File not found: {json_file}")
        print("Please run Generate_Question_Json.py first to create the JSON file.")
    else:
        validate_questions_json(json_file)