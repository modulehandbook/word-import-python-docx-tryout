import json
from docx import Document
import re
import sys


class ConfigLoader:
    @staticmethod
    def load_config(path: str):
        with open(path, 'r') as file:
            return json.load(file)

class CourseDocumentParser:
    def __init__(self, document_source, config_path, raw_mode=False):
        """
        document_source: either a file path (default) or a pre-split Document object if raw_mode=True
        """
        if raw_mode:
            self.document = document_source
        else:
            self.document = Document(document_source)

        self.config = ConfigLoader.load_config(config_path)

        self.paragraph_mapping_keywords = self.config["paragraph_keywords"]
        self.non_paragraph_mapping_keywords = self.config["non_paragraph_keywords"]
        self.all_keywords = set(self.paragraph_mapping_keywords.keys()) | set(self.non_paragraph_mapping_keywords)

    def extract_course_info(self):
        paragraph_extractor = ParagraphExtractor(self.document, self.paragraph_mapping_keywords, self.all_keywords)
        table_extractor = TableExtractor(self.document.tables)

        combined_data = {
            **paragraph_extractor.extract_paragraph_data(), #** to unpack dicts, take to dicts and combine them into one
            **table_extractor.extract_table_data()
        }

        return combined_data


class ParagraphExtractor:
    def __init__(self, document, paragraph_mapping_keywords, all_keywords):
        self.document = document
        self.paragraph_mapping_keywords = paragraph_mapping_keywords
        self.all_keywords = all_keywords

    def extract_paragraph_data(self):
        paragraphs = [p.text.strip() for p in self.document.paragraphs if p.text.strip()]
        extracted_data = {}

        extracted_data["name"] = self._extract_name(paragraphs[0])
        extracted_data["code"] = self._extract_code(paragraphs[0])

        print(extracted_data["name"]) #!!!!!!!!!!!!!!!!!!

        current_field_keyword = None
        current_field_value = ""
        for i, paragraph_text in enumerate(paragraphs[1:], 1): #skip first paragraph
            field_name = self._get_matching_field(paragraph_text)

            # if field name in paragraph and not currently collecting
            if field_name:
                if ":" in paragraph_text:
                    extracted_data[field_name] = paragraph_text.split(":", 1)[1].strip()
                else:
                    current_field_keyword = field_name

            # if currently collecting
            elif current_field_keyword:
                current_field_value += f"\n{paragraph_text}"
                if self._is_next_paragraph_keyword(paragraphs, i):
                    extracted_data[current_field_keyword] = current_field_value.strip()
                    current_field_keyword, current_field_value = None, ""

        if current_field_keyword:
            extracted_data[current_field_keyword] = current_field_value.strip()

        return extracted_data

    def _extract_name(self, first_paragraph):
        return re.findall(r'[“"](.*?)[”"]', first_paragraph)[0]

    def _extract_code(self, first_paragraph):
        return re.findall(r'^[^"“]*', first_paragraph)[0].strip()

    def _get_matching_field(self, paragraph_text):
        for keyword, field_name in self.paragraph_mapping_keywords.items():
            if keyword.lower() in paragraph_text.lower():
                return field_name
        return None

    def _is_next_paragraph_keyword(self, paragraphs, index):
        if index + 1 < len(paragraphs):
            next_paragraph = paragraphs[index + 1]
            return any(keyword in next_paragraph for keyword in self.all_keywords)
        return False

class TableExtractor:
    def __init__(self, tables):
        self.tables = tables

    def extract_table_data(self):
        extracted_data = {}

        # Course info table
        if len(self.tables) > 0:
            extracted_data.update(self._extract_info_course_info_table(self.tables[0]))
        else:
            raise ValueError("Course info table is missing!")

        # Contents table
        if len(self.tables) > 1:
            extracted_data["contents"] = self._extract_info_content_table(self.tables[1])
        else:
            extracted_data["contents"] = []

        # Assessment table
        if len(self.tables) > 2:
            extracted_data["examination"] = self._extract_info_assessment_table(self.tables[2])
        else:
            extracted_data["examination"] = []

        return extracted_data

    def _extract_info_course_info_table(self, table):
        # noch in config tun ???? --> braucht überhaupt??
        semester_map = {
            "first semester" : 1,
            "second semester" : 2,
            "third semester" : 3,
            "fourth semester" : 4,
            "fifth semester" : 5,
            "sixth semester" : 6,
            "seventh semester" : 7,
            "eighth semester" : 8
        }

        rows = table.rows
        if len(rows) < 9 or any(len(r.cells) < 2 for r in rows[:9]):
            print("[WARNING] Course info table does not have enough rows or cells.")
            return extracted_data

        extracted_data = {
            "semester": semester_map[table.rows[0].cells[1].text.lower()],
            "semester_type": table.rows[1].cells[1].text,
            "department": table.rows[3].cells[1].text,
            "specialization": table.rows[4].cells[1].text,
            "required": table.rows[5].cells[1].text,
            "ects": table.rows[8].cells[1].text
        }

        session_details = table.rows[6].cells[1].text
        session_hours = self._calculate_session_hours(session_details)
        extracted_data.update(session_hours)

        return extracted_data

    def _extract_info_content_table(self, table):
        table_data = []
        sub_headers = [cell.text.strip() for cell in table.rows[1].cells]

        # Initialize totals
        total_hours = [0] * (len(sub_headers) - 1)  # exclude first column 'Topic'

        for row in table.rows[2:-1]:  # skip header and last row
            row_data = {"Topic": row.cells[0].text.strip()}

            teaching_hours = []
            for index in range(1, len(row.cells)):
                cell_text = row.cells[index].text.strip()
                if not cell_text:
                    cell_text = "0"
                teaching_hours.append(cell_text)

                # accumulate totals
                if '/' in cell_text:  # e.g., "2/2"
                    parts = cell_text.split('/')
                    for i, part in enumerate(parts):
                        try:
                            total_hours[i] += int(part)
                        except ValueError:
                            pass
                else:
                    try:
                        total_hours[index - 1] += int(cell_text)
                    except ValueError:
                        pass

            subheader_path = "/".join([sub for i, sub in enumerate(sub_headers[1:], start=1) if sub])
            row_data[f"No. of Teaching Hours: {subheader_path}"] = "/".join(teaching_hours)

            table_data.append(row_data)

        # Append total row
        if any(total_hours):
            total_row = {"Topic": "Total Hours"}
            total_row[f"No. of Teaching Hours: {subheader_path}"] = "/".join(str(h) for h in total_hours)
            table_data.append(total_row)

        return table_data

    def _extract_info_assessment_table(self, table):
        table_data = []
        headers = [cell.text.strip() for cell in table.rows[0].cells]

        for row in table.rows[1:]:
            row_data = {}
            for i, cell in enumerate(row.cells):
                row_data[headers[i]] = cell.text.strip()

            table_data.append(row_data)
        return table_data

    def _calculate_session_hours(self, session_details):
        session_hours = {"lectureHrs": 0, "tutorialHrs": 0, "labHrs": 0} #initialize to 0 to add weekly and bi-weekly if both is given for one type

        for session in self._split_sessions_into_categories(session_details):
            sws = self._calculate_sws(session)
            session_lower = session.lower()

            if "lecture" in session_lower:
                session_hours["lectureHrs"] += sws
            elif "tutorial" in session_lower:
                session_hours["tutorialHrs"] += sws
            elif "lab" in session_lower:
                session_hours["labHrs"] += sws

        return session_hours

    def _split_sessions_into_categories(self, session_string: str) -> list:
        return re.split(r'\s*(?:\+|,|and)\s*', session_string, flags=re.IGNORECASE)

    def _calculate_sws(self, session_string: str) -> int:
        session_string = session_string.strip()

        match = re.match(r'(\d+)', session_string)
        if not match:
            return 0

        number = int(match.group(1))

        if re.search(r'bi\s*-?\s*weekly', session_string.lower()):
            return number
        else:
            return number * 2


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:  python3 course_document_parser.py <document_path>")
        sys.exit(1)

    document_path = sys.argv[1]
    output_path = 'output/output.json'

    parser = CourseDocumentParser(document_path, "config.json")
    course_info = parser.extract_course_info()

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(course_info, json_file, indent=4)

    print(json.dumps(course_info, indent=4))
    print(f"Course information extracted successfully! Saved to {output_path}")