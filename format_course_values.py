import json

def format_literature_md(text):
    """
    Converts literature text into Markdown with subheaders and proper lists.
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    md_lines = []
    current_list_started = False

    for line in lines:
        # Detect header lines
        if line.lower().startswith(("recommended", "relevant")):
            if current_list_started:
                md_lines.append("")  
            md_lines.append(f"**{line}**\n")
            current_list_started = True
        else:
            # Normal list item
            md_lines.append(f"- {line}")

    return "\n".join(md_lines)


def markdownify_course(course):
    md_course = dict(course)  # copy (avoid mutating original)

    # Convert skills, mission, equipment, literature fields into Markdown lists / paragraphs
    for field in ['skills_knowledge_understanding', 'skills_intellectual',
                  'skills_practical', 'skills_general', 'equipment', 'literature', 'methods']:
        if field in course and course[field].strip():
            if field == "literature":
                md_course[field] = format_literature_md(course[field])
            else:
                # Split by lines and prefix with "- " for lists
                md_course[field] = "\n".join(f"- {line.strip()}" 
                                             for line in course[field].splitlines() 
                                             if line.strip())

    # Convert contents table to Markdown table string
    if 'contents' in course and course['contents']:
        headers = course['contents'][0].keys()
        md_table = ["\n| " + " | ".join(headers) + " |"]
        md_table.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in course['contents']:
            md_table.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        md_course['contents'] = "\n".join(md_table) + "\n" 

    # Convert examination table to Markdown table string
    if 'examination' in course and course['examination']:
        headers = course['examination'][0].keys()
        md_table = ["\n| " + " | ".join(headers) + " |"]
        md_table.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in course['examination']:
            md_table.append("| " + " | ".join(str(row.get(h, "")) for h in headers) + " |")
        md_course['examination'] = "\n".join(md_table) + "\n"

    return md_course


if __name__ == "__main__":
    # Load original JSON
    with open("output/program_output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    md_data = dict(data)
    md_data["courses"] = [markdownify_course(c) for c in data.get("courses", [])]

    # Save transformed JSON with Markdown-ready values
    with open("output/program_output_md.json", "w", encoding="utf-8") as f:
        json.dump(md_data, f, indent=4, ensure_ascii=False)

    print("Markdown-ready JSON saved to output/program_output_md.json")