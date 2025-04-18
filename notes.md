# Mappings

  p_keywords = {
        "Course Aim": "mission",
        "Knowledge and Understanding": "skills_knowledge_understanding",
        "Intellectual Skills": "skills_intellectual",
        "Professional and Practical Skills": "skills_practical",
        "General and Transferable Skills": "skills_general",
        "General and Transferrable Skills": "skills_general", #typo in some files
        "Learning and Teaching Methods": "methods",
        "Facilities Required For Teaching and Learning": "equipment",
        "References": "literature",
        "Head of the Department:": "department_head",
        "Course Coordinator:": "responsible_person",
        "E-mail:": "mail"
    }


    non_p_keywords = [
        "Course Content", #tabelle
        "Assessment", #tabelle
        "Learning Outcomes", #liste
        "C- Administrative Information"  # fehlt noch?
    ]

table_general = document.tables[0]
  
extracted_info = {"semester": table_general.rows[0].cells[1].text,
                      "required": table_general.rows[5].cells[1].text,
                      "ects": table_general.rows[8].cells[1].text,
                      "lectureHrs": 0,
                      "tutorialHrs": 0,
                      "labHrs": 0,
                      "contents": contents_table_to_json(document.tables[1]),
                      "examination": assessment_table_to_json(document.tables[2])
                      }

Sum teaching hours total?
