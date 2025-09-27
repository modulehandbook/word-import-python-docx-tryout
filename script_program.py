import json
import sys
from program_document_parser import ProgramDocumentParser


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage:  python3 script_program.py <document_path>")
        sys.exit(1)

    document_path = sys.argv[1]
    output_path = 'output/program_output.json'

    parser = ProgramDocumentParser(document_path, "config.json")
    program_info = parser.extract_program_info()

    with open(output_path, 'w', encoding='utf-8') as json_file:
        json.dump(program_info, json_file, indent=4, ensure_ascii=False)

    print(json.dumps(program_info, indent=4, ensure_ascii=False))
    print(f"Program information extracted successfully! Saved to {output_path}")