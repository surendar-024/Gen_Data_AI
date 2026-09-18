# nlp_manager/schema_registry.py

"""
Central schema registry — the SINGLE SOURCE OF TRUTH for all domain column
definitions.  Every column specifies its canonical name, type, aliases the
user might type, and optional defaults (min/max, choices, unique, nullable,
pattern).

Validation, constraint parsing, and field generation all derive behaviour
from this registry.
"""

SCHEMA_REGISTRY = {

    # ================================================================
    #  STUDENT DOMAIN
    # ================================================================
    "student": {
        "columns": {

            # ---------- Identity ----------
            "id": {
                "type": "uuid",
                "unique": True,
                "aliases": ["id", "studentid", "student_id", "sid"]
            },
            "roll_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "R001",
                "aliases": ["roll", "rollnumber", "roll_number", "rollno", "roll_no", "roll number"]
            },
            "registration_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "REG001",
                "aliases": [
                    "registration", "registrationnumber", "registration_number",
                    "regnumber", "reg_number", "regno", "reg_no",
                    "registernumber", "register_number"
                ]
            },

            # ---------- Personal ----------
            "name": {
                "type": "name",
                "aliases": ["name", "fullname", "full_name", "studentname", "student_name"]
            },
            "first_name": {
                "type": "first_name",
                "aliases": ["firstname", "first_name", "fname"]
            },
            "last_name": {
                "type": "last_name",
                "aliases": ["lastname", "last_name", "lname", "surname"]
            },
            "middle_name": {
                "type": "first_name",
                "nullable": True,
                "aliases": ["middlename", "middle_name", "mname"]
            },
            "age": {
                "type": "integer",
                "min": 5,
                "max": 25,
                "aliases": ["age"]
            },
            "gender": {
                "type": "choice",
                "choices": ["Male", "Female", "Other"],
                "aliases": ["gender", "sex"]
            },
            "date_of_birth": {
                "type": "date",
                "aliases": ["dob", "dateofbirth", "date_of_birth", "birthdate", "birthday"]
            },
            "blood_group": {
                "type": "choice",
                "choices": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
                "aliases": ["bloodgroup", "blood_group", "blood_type", "bloodtype"]
            },
            "nationality": {
                "type": "choice",
                "choices": ["Indian", "American", "British", "Canadian", "Australian", "Other"],
                "aliases": ["nationality", "nation"]
            },
            "religion": {
                "type": "choice",
                "choices": ["Hindu", "Muslim", "Christian", "Sikh", "Buddhist", "Jain", "Other"],
                "aliases": ["religion"]
            },
            "category": {
                "type": "choice",
                "choices": ["General", "OBC", "SC", "ST", "EWS"],
                "aliases": ["category", "caste", "reservation", "quota"]
            },

            # ---------- Contact ----------
            "email": {
                "type": "email",
                "unique": True,
                "aliases": ["email", "mail", "emailid", "email_id", "emailaddress"]
            },
            "phone": {
                "type": "phone",
                "aliases": ["phone", "mobile", "phonenumber", "phone_number", "phone number",
                            "mobilenumber", "mobile_number", "contact", "contactnumber"]
            },
            "address": {
                "type": "address",
                "nullable": True,
                "aliases": ["address", "addr", "fulladdress", "full_address", "residence", "home",
                            "residential_address", "permanentaddress"]
            },
            "city": {
                "type": "city",
                "aliases": ["city", "town"]
            },
            "state": {
                "type": "state",
                "aliases": ["state", "province"]
            },
            "country": {
                "type": "country",
                "aliases": ["country", "nation_name"]
            },
            "pincode": {
                "type": "pincode",
                "aliases": ["pincode", "pin_code", "zipcode", "zip_code", "zip", "postalcode", "postal_code"]
            },

            # ---------- Academic ----------
            "marks": {
                "type": "integer",
                "min": 0,
                "max": 100,
                "aliases": ["marks", "score", "totalmarks", "total_marks", "obtainedmarks", "math_score", "science_score", "math score", "science score"]
            },
            "grade": {
                "type": "choice",
                "choices": ["A+", "A", "B+", "B", "C+", "C", "D", "F"],
                "aliases": ["grade", "lettergrade", "letter_grade"]
            },
            "gpa": {
                "type": "float",
                "min": 0.0,
                "max": 10.0,
                "aliases": ["gpa"]
            },
            "cgpa": {
                "type": "float",
                "min": 0.0,
                "max": 10.0,
                "aliases": ["cgpa", "cumulativegpa", "cumulative_gpa"]
            },
            "sgpa": {
                "type": "float",
                "min": 0.0,
                "max": 10.0,
                "aliases": ["sgpa", "semestergpa", "semester_gpa"]
            },
            "percentage": {
                "type": "float",
                "min": 0.0,
                "max": 100.0,
                "aliases": ["percentage", "percent", "pct"]
            },
            "attendance": {
                "type": "float",
                "min": 0.0,
                "max": 100.0,
                "aliases": [
                    "attendance", "attendancepercent", "attendance_percentage",
                    "attendancepercentage", "attendance_percent"
                ]
            },
            "semester": {
                "type": "integer",
                "min": 1,
                "max": 8,
                "aliases": ["semester", "sem"]
            },
            "academic_year": {
                "type": "integer",
                "min": 1,
                "max": 5,
                "aliases": ["academicyear", "academic_year", "studyyear", "study_year", "year_of_study", "academic year", "study year"]
            },
            "section": {
                "type": "choice",
                "choices": ["A", "B", "C", "D"],
                "aliases": ["section", "sec"]
            },
            "division": {
                "type": "choice",
                "choices": ["A", "B", "C", "D"],
                "aliases": ["division", "div"]
            },
            "subjects": {
                "type": "choice",
                "choices": [
                    "Mathematics", "Physics", "Chemistry", "Biology",
                    "English", "Computer Science", "History", "Geography",
                    "Economics", "Political Science"
                ],
                "aliases": ["subject", "subjects", "sub"]
            },

            # ---------- Institutional ----------
            "department": {
                "type": "choice",
                "choices": [
                    "Computer Science", "Electrical Engineering",
                    "Mechanical Engineering", "Civil Engineering",
                    "Electronics", "Information Technology",
                    "Chemical Engineering", "Biotechnology"
                ],
                "aliases": ["department", "dept", "dep"]
            },
            "major": {
                "type": "choice",
                "choices": [
                    "Computer Science", "Electrical Engineering",
                    "Mechanical Engineering", "Civil Engineering",
                    "Electronics", "Information Technology"
                ],
                "aliases": ["major", "specialization", "specialisation", "stream"]
            },
            "branch": {
                "type": "choice",
                "choices": [
                    "CSE", "ECE", "EEE", "MECH", "CIVIL", "IT", "CHEM", "BIO"
                ],
                "aliases": ["branch"]
            },
            "course": {
                "type": "choice",
                "choices": ["B.Tech", "M.Tech", "BCA", "MCA", "B.Sc", "M.Sc", "MBA", "PhD"],
                "aliases": ["course", "program", "programme", "degree"]
            },
            "enrollment_year": {
                "type": "integer",
                "min": 2015,
                "max": 2026,
                "aliases": [
                    "enrollmentyear", "enrollment_year", "admissionyear",
                    "admission_year", "joiningyear", "joining_year",
                    "yearofadmission", "year_of_admission", "year",
                    "enrollment year", "admission year"
                ]
            },
            "graduation_year": {
                "type": "integer",
                "min": 2019,
                "max": 2030,
                "aliases": [
                    "graduationyear", "graduation_year", "passingyear",
                    "passing_year", "passoutyear", "passout_year",
                    "yearofgraduation", "year_of_graduation"
                ]
            },
            "college_name": {
                "type": "choice",
                "choices": [
                    "IIT Delhi", "IIT Bombay", "IIT Madras",
                    "NIT Trichy", "NIT Warangal", "BITS Pilani",
                    "VIT Vellore", "SRM Chennai", "Anna University"
                ],
                "aliases": [
                    "collegename", "college_name", "college",
                    "institute", "institutename", "institute_name"
                ]
            },
            "university_name": {
                "type": "choice",
                "choices": [
                    "Anna University", "Delhi University", "Mumbai University",
                    "Pune University", "JNTU Hyderabad", "Osmania University",
                    "Bangalore University", "Madras University"
                ],
                "aliases": [
                    "universityname", "university_name", "university",
                    "uni", "univ"
                ]
            },
            "board": {
                "type": "choice",
                "choices": ["CBSE", "ICSE", "State Board", "IB", "Cambridge"],
                "aliases": ["board", "educationboard", "education_board"]
            },

            # ---------- Family ----------
            "father_name": {
                "type": "name",
                "aliases": ["fathername", "father_name", "fatherName", "dadname", "dad_name"]
            },
            "mother_name": {
                "type": "name",
                "aliases": ["mothername", "mother_name", "motherName", "momname", "mom_name"]
            },
            "parent_phone": {
                "type": "phone",
                "aliases": [
                    "parentphone", "parent_phone", "guardianphone",
                    "guardian_phone", "emergencycontact", "emergency_contact"
                ]
            },

            # ---------- Financial ----------
            "scholarship": {
                "type": "integer",
                "min": 0,
                "max": 500000,
                "aliases": ["scholarship", "scholarshipamount", "scholarship_amount"]
            },
            "fees": {
                "type": "integer",
                "min": 5000,
                "max": 500000,
                "aliases": ["fees", "tuition", "tuitionfee", "tuition_fee",
                            "fee", "feesamount", "fees_amount"]
            },

            # ---------- Status ----------
            "status": {
                "type": "choice",
                "choices": ["Active", "Graduated", "Dropped", "Suspended", "On Leave"],
                "aliases": ["status", "studentstatus", "student_status",
                            "enrollmentstatus", "enrollment_status"]
            },
        }
    },

    # ================================================================
    #  GENERIC DOMAIN (fallback)
    # ================================================================
    "generic": {
        "columns": {
            "id": {
                "type": "uuid",
                "unique": True,
                "aliases": ["id"]
            },
            "name": {
                "type": "name",
                "aliases": ["name"]
            },
            "email": {
                "type": "email",
                "unique": True,
                "aliases": ["email"]
            }
        }
    },
    "employee": {
        "domain_name": "employee",
        "columns": {
            # ---------- Identity ----------
            "id": {
                "type": "pattern",
                "unique": True,
                "pattern": "EMP-1001",
                "aliases": ["id", "employeeid", "employee_id", "staffid", "staff_id", "staff_no", "staff_number"]
            },
            "employee_uuid": {
                "type": "uuid",
                "unique": True,
                "aliases": ["uuid", "guid", "external_id"]
            },
            "employee_code": {
                "type": "pattern",
                "unique": True,
                "pattern": "CORP-###",
                "aliases": ["code", "employeecode", "employee_code", "corp_id", "internal_id"]
            },
            "biometric_id": {
                "type": "pattern",
                "unique": True,
                "pattern": "BIO-#####",
                "aliases": ["biometric", "biometric_id", "punch_id", "fingerprint_id"]
            },
            "ssn": {
                "type": "pattern",
                "unique": True,
                "pattern": "###-##-####",
                "aliases": ["ssn", "social_security", "national_id", "aadhaar", "pan_card", "pan"]
            },

            # ---------- Personal ----------
            "name": {
                "type": "name",
                "aliases": ["name", "fullname", "full_name", "employeename", "employee_name"]
            },
            "first_name": {
                "type": "first_name",
                "aliases": ["firstname", "first_name", "fname"]
            },
            "last_name": {
                "type": "last_name",
                "aliases": ["lastname", "last_name", "lname", "surname"]
            },
            "gender": {
                "type": "choice",
                "choices": ["Male", "Female", "Non-binary", "Prefer not to say"],
                "aliases": ["gender", "sex"]
            },
            "date_of_birth": {
                "type": "date",
                "min": 1960,
                "max": 2005,
                "aliases": ["dob", "date_of_birth", "birthdate", "birthday"]
            },
            "marital_status": {
                "type": "choice",
                "choices": ["Single", "Married", "Divorced", "Widowed"],
                "aliases": ["marital_status", "marital", "relationship_status"]
            },
            "blood_group": {
                "type": "choice",
                "choices": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
                "aliases": ["bloodgroup", "blood_group"]
            },
            "nationality": {
                "type": "choice",
                "choices": ["Indian", "American", "British", "Canadian", "Australian", "German", "French"],
                "aliases": ["nationality", "nation"]
            },

            # ---------- Contact ----------
            "email": {
                "type": "email",
                "unique": True,
                "aliases": ["email", "mail", "workemail", "work_email", "office_email"]
            },
            "personal_email": {
                "type": "email",
                "unique": True,
                "aliases": ["personal_email", "personal_mail", "private_email"]
            },
            "phone": {
                "type": "phone",
                "aliases": ["phone", "mobile", "phonenumber", "phone_number", "contact", "mobile_no"]
            },
            "work_phone": {
                "type": "phone",
                "aliases": ["work_phone", "office_phone", "desk_phone", "extension"]
            },
            "address": {
                "type": "address",
                "aliases": ["address", "current_address", "residence", "location"]
            },
            "city": {
                "type": "city",
                "aliases": ["city", "town", "hometown"]
            },
            "state": {
                "type": "state",
                "aliases": ["state", "province", "region"]
            },

            # ---------- Employment ----------
            "department": {
                "type": "choice",
                "choices": ["Engineering", "Sales", "Marketing", "HR", "Finance", "Legal", "Operations", "Product", "QA", "IT Support"],
                "aliases": ["department", "dept", "team", "division"]
            },
            "designation": {
                "type": "choice",
                "choices": ["Intern", "Junior Engineer", "Software Engineer", "Senior Engineer", "Lead Engineer", "Manager", "Senior Manager", "Director", "VP", "CTO", "CEO"],
                "aliases": ["designation", "role", "title", "position"]
            },
            "level": {
                "type": "choice",
                "choices": ["L1", "L2", "L3", "L4", "L5", "L6"],
                "aliases": ["level", "grade", "band", "rank"]
            },
            "employment_type": {
                "type": "choice",
                "choices": ["Full-time", "Part-time", "Contract", "Freelance", "Internship"],
                "aliases": ["employment_type", "job_type", "contract_type"]
            },
            "work_mode": {
                "type": "choice",
                "choices": ["Remote", "On-site", "Hybrid"],
                "aliases": ["work_mode", "work_type", "workplace"]
            },
            "manager_name": {
                "type": "name",
                "aliases": ["manager", "supervisor", "reporting_manager", "lead_name"]
            },
            "manager_id": {
                "type": "pattern",
                "pattern": "EMP-####",
                "aliases": ["manager_id", "supervisor_id", "reporting_id"]
            },
            "hire_date": {
                "type": "date",
                "min": 2010,
                "max": 2024,
                "aliases": ["hiredate", "hire_date", "joining_date", "date_of_joining"]
            },
            "experience": {
                "type": "integer",
                "min": 0,
                "max": 40,
                "aliases": ["experience", "years_of_experience", "total_exp"]
            },
            "notice_period": {
                "type": "integer",
                "min": 15,
                "max": 90,
                "multiple_of": 15,
                "aliases": ["notice_period", "notice_days", "exit_period"]
            },
            "shift": {
                "type": "choice",
                "choices": ["General", "Morning", "Afternoon", "Night", "Rotating"],
                "aliases": ["shift", "shift_timing", "working_hours"]
            },

            # ---------- Financial ----------
            "salary": {
                "type": "integer",
                "min": 30000,
                "max": 500000,
                "aliases": ["salary", "monthly_pay", "base_pay", "income"]
            },
            "annual_ctc": {
                "type": "integer",
                "min": 400000,
                "max": 8000000,
                "aliases": ["ctc", "package", "annual_salary", "annual_income"]
            },
            "bonus": {
                "type": "percentage",
                "min": 5,
                "max": 30,
                "aliases": ["bonus", "incentive", "variable_pay"]
            },
            "bank_name": {
                "type": "choice",
                "choices": ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra", "CitiBank", "HSBC"],
                "aliases": ["bank", "bank_name"]
            },
            "account_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "##########",
                "aliases": ["account_number", "acc_no", "bank_account"]
            },
            "ifsc_code": {
                "type": "pattern",
                "pattern": "BANK000####",
                "aliases": ["ifsc", "ifsc_code", "branch_code"]
            },
            "pf_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "PF/####/#####",
                "aliases": ["pf_number", "provident_fund", "pf_id"]
            },

            # ---------- Performance & Skills ----------
            "performance_rating": {
                "type": "float",
                "min": 1.0,
                "max": 5.0,
                "aliases": ["rating", "performance", "score", "kpi_rating"]
            },
            "skills": {
                "type": "choice",
                "choices": ["Python", "Java", "React", "Node.js", "SQL", "Project Management", "Leadership", "Salesforce", "Cloud Computing"],
                "aliases": ["skills", "expertise", "specialization", "tech_stack"]
            },
            "projects_completed": {
                "type": "integer",
                "min": 0,
                "max": 50,
                "aliases": ["projects", "projects_count", "assignments"]
            },
            "certification_count": {
                "type": "integer",
                "min": 0,
                "max": 10,
                "aliases": ["certifications", "certs", "courses_completed"]
            },
            "travel_requirement": {
                "type": "choice",
                "choices": ["None", "Occasional", "Frequent", "Extensive"],
                "aliases": ["travel", "travel_required", "on_field"]
            },
            "status": {
                "type": "choice",
                "choices": ["Active", "On Notice", "Resigned", "Terminated", "On Leave", "Probation"],
                "aliases": ["status", "employment_status", "work_status"]
            }
        }
    },
    "healthcare": {
        "domain_name": "healthcare",
        "columns": {
            # ---------- Patient Identity ----------
            "id": {
                "type": "pattern",
                "unique": True,
                "pattern": "PAT-#####",
                "aliases": ["id", "patientid", "patient_id", "pid"]
            },
            "mrn": {
                "type": "pattern",
                "unique": True,
                "pattern": "MRN-######",
                "aliases": ["mrn", "medical_record_number", "record_number"]
            },
            "ssn": {
                "type": "pattern",
                "unique": True,
                "pattern": "###-##-####",
                "aliases": ["ssn", "social_security", "national_id", "aadhaar", "pan"]
            },
            # ---------- Patient Personal ----------
            "name": {
                "type": "name",
                "aliases": ["name", "fullname", "patient_name", "full_name"]
            },
            "first_name": {
                "type": "first_name",
                "aliases": ["firstname", "fname"]
            },
            "last_name": {
                "type": "last_name",
                "aliases": ["lastname", "lname"]
            },
            "gender": {
                "type": "choice",
                "choices": ["Male", "Female", "Other", "Unknown"],
                "aliases": ["gender", "sex"]
            },
            "date_of_birth": {
                "type": "date",
                "min": 1930,
                "max": 2024,
                "aliases": ["dob", "birthdate", "birthday"]
            },
            "age": {
                "type": "integer",
                "min": 0,
                "max": 100,
                "aliases": ["age"]
            },
            "blood_group": {
                "type": "choice",
                "choices": ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"],
                "aliases": ["blood_group", "bloodgroup", "blood_type"]
            },
            "marital_status": {
                "type": "choice",
                "choices": ["Single", "Married", "Divorced", "Widowed"],
                "aliases": ["marital_status", "marital"]
            },
            # ---------- Contact ----------
            "phone": {
                "type": "phone",
                "aliases": ["phone", "mobile", "contact"]
            },
            "email": {
                "type": "email",
                "aliases": ["email", "mail"]
            },
            "emergency_contact": {
                "type": "name",
                "aliases": ["emergency_contact", "next_of_kin", "guardian"]
            },
            "emergency_phone": {
                "type": "phone",
                "aliases": ["emergency_phone", "guardian_phone"]
            },
            "address": {
                "type": "address",
                "aliases": ["address", "location"]
            },
            "city": {
                "type": "city",
                "aliases": ["city"]
            },
            # ---------- Clinical Vitals ----------
            "blood_pressure": {
                "type": "blood_pressure",
                "aliases": ["bp", "blood_pressure", "vitals_bp"]
            },
            "heart_rate": {
                "type": "integer",
                "min": 60,
                "max": 100,
                "aliases": ["heart_rate", "pulse", "bpm"]
            },
            "body_temperature": {
                "type": "float",
                "min": 36.1,
                "max": 39.5,
                "aliases": ["temperature", "temp", "body_temp"]
            },
            "respiratory_rate": {
                "type": "integer",
                "min": 12,
                "max": 25,
                "aliases": ["respiratory_rate", "breathing_rate"]
            },
            "weight": {
                "type": "float",
                "min": 3.0,
                "max": 150.0,
                "aliases": ["weight", "wt", "mass"]
            },
            "height": {
                "type": "float",
                "min": 50.0,
                "max": 210.0,
                "aliases": ["height", "ht"]
            },
            "bmi": {
                "type": "bmi",
                "aliases": ["bmi", "body_mass_index"]
            },
            # ---------- Medical Details ----------
            "diagnosis": {
                "type": "choice",
                "choices": ["Hypertension", "Diabetes Type 2", "Common Cold", "Asthma", "COVID-19", "Flu", "Migraine", "Pneumonia", "Heart Disease"],
                "aliases": ["diagnosis", "disease", "condition", "medical_condition"]
            },
            "symptoms": {
                "type": "choice",
                "choices": ["Fever", "Cough", "Headache", "Nausea", "Fatigue", "Chest Pain", "Dizziness", "Shortness of Breath"],
                "aliases": ["symptoms", "primary_symptom", "complaint"]
            },
            "severity": {
                "type": "choice",
                "choices": ["Mild", "Moderate", "Severe", "Critical"],
                "aliases": ["severity", "condition_level", "urgency"]
            },
            "patient_status": {
                "type": "choice",
                "choices": ["Inpatient", "Outpatient", "Emergency", "Observation", "Discharged"],
                "aliases": ["status", "patient_status", "admission_type"]
            },
            "admission_date": {
                "type": "date",
                "aliases": ["admission_date", "admitted_on"]
            },
            "discharge_date": {
                "type": "date",
                "aliases": ["discharge_date", "discharged_on"]
            },
            # ---------- Medication & Lab ----------
            "medication": {
                "type": "choice",
                "choices": ["Paracetamol", "Metformin", "Amoxicillin", "Lisinopril", "Atorvastatin", "Albuterol", "Ibuprofen"],
                "aliases": ["medication", "medicine", "drug", "prescription"]
            },
            "dosage": {
                "type": "choice",
                "choices": ["500mg", "1000mg", "5mg", "10mg", "20mg", "2.5mg"],
                "aliases": ["dosage", "dose", "amount"]
            },
            "frequency": {
                "type": "choice",
                "choices": ["Once daily", "Twice daily", "Thrice daily", "Every 4 hours", "As needed"],
                "aliases": ["frequency", "timing", "schedule"]
            },
            "lab_result": {
                "type": "choice",
                "choices": ["Normal", "Abnormal", "Borderline", "Inconclusive"],
                "aliases": ["lab_result", "test_result", "findings"]
            },
            "cholesterol": {
                "type": "integer",
                "min": 100,
                "max": 300,
                "aliases": ["cholesterol", "ldl", "hdl"]
            },
            "glucose": {
                "type": "integer",
                "min": 70,
                "max": 250,
                "aliases": ["glucose", "sugar_level", "blood_sugar"]
            },
            # ---------- Hospital & Staff ----------
            "hospital_name": {
                "type": "choice",
                "choices": ["Apollo Hospital", "Fortis Healthcare", "Max Hospital", "AIIMS", "City Medical Center", "Unity Health"],
                "aliases": ["hospital", "hospital_name", "clinic", "facility"]
            },
            "doctor_name": {
                "type": "name",
                "prefix": ["Dr."],
                "aliases": ["doctor", "physician", "doctor_name", "md"]
            },
            "department": {
                "type": "choice",
                "choices": ["Cardiology", "Oncology", "Pediatrics", "Neurology", "Orthopedics", "Dermatology", "General Medicine", "Radiology"],
                "aliases": ["department", "dept", "specialty"]
            },
            "room_number": {
                "type": "pattern",
                "pattern": "ROOM-###",
                "aliases": ["room", "room_number", "bed_number", "ward"]
            },
            # ---------- Insurance & Billing ----------
            "insurance_provider": {
                "type": "choice",
                "choices": ["Blue Cross", "UnitedHealth", "Aetna", "Cigna", "Kaiser Permanente", "Humana", "Medicare"],
                "aliases": ["insurance", "provider", "insurance_company"]
            },
            "policy_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "POL-########",
                "aliases": ["policy", "policy_number", "insurance_id"]
            },
            "billing_amount": {
                "type": "integer",
                "min": 100,
                "max": 50000,
                "aliases": ["billing", "amount", "total_charge", "bill"]
            },
            "payment_status": {
                "type": "choice",
                "choices": ["Paid", "Pending", "Overdue", "Insurance Processing", "Partially Paid"],
                "aliases": ["payment_status", "billing_status"]
            }
        }
    },
    "sales": {
        "domain_name": "sales",
        "columns": {
            # ---------- Order Identity ----------
            "id": {
                "type": "pattern",
                "unique": True,
                "pattern": "ORD-#######",
                "aliases": ["id", "orderid", "order_id", "order_no"]
            },
            "invoice_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "INV-2024-#####",
                "aliases": ["invoice", "invoice_no", "bill_number"]
            },
            "tracking_number": {
                "type": "pattern",
                "unique": True,
                "pattern": "TRK-################",
                "aliases": ["tracking", "tracking_id", "consignment_no"]
            },

            # ---------- Customer Details ----------
            "customer_id": {
                "type": "pattern",
                "unique": True,
                "pattern": "CUST-#####",
                "aliases": ["customer_id", "client_id", "user_id"]
            },
            "customer_name": {
                "type": "name",
                "aliases": ["customer", "customer_name", "client_name", "buyer"]
            },
            "customer_email": {
                "type": "email",
                "aliases": ["customer_email", "buyer_email"]
            },
            "customer_segment": {
                "type": "choice",
                "choices": ["Consumer", "Corporate", "Home Office", "Wholesale", "Retail"],
                "aliases": ["segment", "customer_type", "buyer_group"]
            },
            "shipping_address": {
                "type": "address",
                "aliases": ["shipping_address", "delivery_address", "destination"]
            },
            "shipping_city": {
                "type": "city",
                "aliases": ["shipping_city", "city", "town"]
            },

            # ---------- Product Details ----------
            "product_id": {
                "type": "pattern",
                "pattern": "PRD-####",
                "aliases": ["product_id", "item_id", "sku"]
            },
            "product_name": {
                "type": "choice",
                "choices": ["Laptop Pro 15", "Wireless Mouse", "Mechanical Keyboard", "Monitor 4K", "Smartphone X1", "Noise Cancelling Headphones", "Tablet 10", "Smart Watch"],
                "aliases": ["product", "product_name", "item_name", "sku_name"]
            },
            "category": {
                "type": "choice",
                "choices": ["Electronics", "Computers", "Mobile Phones", "Accessories", "Home Appliances", "Office Supplies"],
                "aliases": ["category", "product_category", "department"]
            },
            "brand": {
                "type": "choice",
                "choices": ["TechGiant", "Innovate", "FutureGear", "Apex", "GlobalTech", "CoreConnect"],
                "aliases": ["brand", "manufacturer", "make"]
            },

            # ---------- Transaction Details ----------
            "order_date": {
                "type": "date",
                "min": 2023,
                "max": 2024,
                "aliases": ["order_date", "purchase_date", "transaction_date"]
            },
            "quantity": {
                "type": "integer",
                "min": 1,
                "max": 10,
                "aliases": ["quantity", "qty", "units"]
            },
            "unit_price": {
                "type": "float",
                "min": 10.0,
                "max": 2000.0,
                "aliases": ["price", "unit_price", "rate"]
            },
            "subtotal": {
                "type": "float",
                "min": 10.0,
                "max": 20000.0,
                "aliases": ["subtotal", "base_amount"]
            },
            "tax_amount": {
                "type": "float",
                "min": 0.0,
                "max": 2000.0,
                "aliases": ["tax", "gst", "vat", "sales_tax"]
            },
            "discount_percentage": {
                "type": "percentage",
                "min": 0,
                "max": 50,
                "aliases": ["discount_pct", "off_percentage", "discount"]
            },
            "shipping_fee": {
                "type": "float",
                "min": 0.0,
                "max": 100.0,
                "aliases": ["shipping", "freight", "delivery_charge"]
            },
            "total_amount": {
                "type": "float",
                "min": 10.0,
                "max": 25000.0,
                "aliases": ["total", "total_amount", "grand_total", "final_price"]
            },

            # ---------- Payment & Logistics ----------
            "payment_method": {
                "type": "choice",
                "choices": ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "PayPal"],
                "aliases": ["payment_method", "payment_type", "mode_of_payment"]
            },
            "payment_status": {
                "type": "choice",
                "choices": ["Paid", "Pending", "Authorized", "Captured", "Failed", "Refunded"],
                "aliases": ["payment_status", "status"]
            },
            "shipping_method": {
                "type": "choice",
                "choices": ["Standard", "Express", "Next Day", "Free Shipping", "Priority"],
                "aliases": ["shipping_method", "delivery_type", "ship_mode"]
            },
            "courier_partner": {
                "type": "choice",
                "choices": ["FedEx", "DHL", "UPS", "BlueDart", "Delhivery", "Ecom Express"],
                "aliases": ["courier", "carrier", "shipping_partner"]
            },
            "delivery_status": {
                "type": "choice",
                "choices": ["Pending", "Processing", "Shipped", "In Transit", "Out for Delivery", "Delivered", "Returned", "Cancelled"],
                "aliases": ["delivery_status", "order_status", "shipment_status"]
            },
            "coupon_code": {
                "type": "pattern",
                "pattern": "SAVE##",
                "aliases": ["coupon", "promo_code", "discount_code"]
            },
            "is_returning_customer": {
                "type": "boolean",
                "aliases": ["returning", "is_old_customer"]
            }
        }
    }
}

