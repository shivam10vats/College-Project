# Hospital Management System - PowerPoint Presentation Generator

This repository contains a Python script that generates a comprehensive PowerPoint presentation for the Hospital Management System project.

## Features

The presentation includes all the requested sections:

1. **Project Title** - Hospital Management System overview
2. **Introduction & Objectives** - Project goals and features
3. **SRS (System Requirements Specification)** - Functional and non-functional requirements
4. **Process Logic** - System workflow and data flow
5. **Gantt Chart** - 3-month project timeline
6. **Data Dictionary** - Database schema and field descriptions
7. **DFD (Data Flow Diagram)** - System data flow visualization
8. **ER Diagram** - Entity Relationship diagram
9. **Interface Design** - User interface components
10. **Expected Reports** - Report generation capabilities
11. **References** - Technical bibliography
12. **Future Scope** - Enhancement possibilities

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the presentation generator:
```bash
python create_presentation.py
```

2. The script will create a file named `Hospital_Management_System_Presentation.pptx` in the current directory.

## Presentation Content

### Project Overview
- Web-based Hospital Management System
- Built with Django (Python Framework)
- SQLite Database backend
- Secure admin interface

### Key Features
- Doctor Management (Add, View, Delete)
- Patient Management (Add, View)
- Appointment Scheduling
- Admin Dashboard with Statistics
- User Authentication

### Technical Stack
- **Backend**: Django 5.2.3
- **Database**: SQLite3
- **Frontend**: HTML, CSS, Bootstrap
- **Authentication**: Django Auth System

### Database Schema
- **Doctor**: id, name, specialization, contact_number
- **Patient**: id, name, gender, mobile_number, address
- **Appointment**: id, patient_id, doctor_id, appointment_date, appointment_time

## Customization

You can modify the `create_presentation.py` file to:
- Add your team member names
- Update project dates
- Modify content for specific requirements
- Add custom styling
- Include additional slides

## Notes

- The presentation is generated programmatically using python-pptx
- All content is based on the actual Hospital Management System implementation
- The ER diagram is represented in text format within the presentation
- You can enhance the presentation by adding actual screenshots of your application

## Output

The generated PowerPoint file will contain 12 slides covering all aspects of the Hospital Management System project, suitable for academic presentations and project demonstrations. 