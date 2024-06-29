import sys
import csv
from jinja2 import Template

# Read the command line arguments
input_list = sys.argv

# Initialize variables
student_course = []
course_marks = []
total = 0

# Read data from CSV (data.csv)
with open("data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        if input_list[1] == '-s':
            if input_list[2] in row[8]:
                total = int(row[2].strip())
                student_course.append(row)
        elif input_list[1] == '-c':
            if input_list[2] in row[2]:
                course_marks.append(int(row[2].strip()))

# Handle invalid input
if not student_course or not course_marks:
    data = """<h1>Wrong Inputs</h1><p>Something went wrong</p>"""
    with open('output.html', 'w') as f:
        f.write(data)
else:
    if input_list[1] == '-s':
        template_text = """
        <h1>Student Details</h1>
        <table border="2">
            <tr>
                <th>Student ID</th>
                <th>Course ID</th>
                <th>Marks</th>
            </tr>
            {% for student in student_course %}
            <tr>
                <td>{{ student[8].strip() }}</td>
                <td>{{ student[1].strip() }}</td>
                <td>{{ student[2].strip() }}</td>
            </tr>
            {% endfor %}
            <tr>
                <td colspan="2">Total Marks</td>
                <td>{{ total }}</td>
            </tr>
        </table>
        """
    elif input_list[1] == '-c':
        average_marks = sum(course_marks) / len(course_marks)
        max_marks = max(course_marks)
        template_text = """
        <h1>Course Details</h1>
        <table>
            <tr>
                <th>Average Marks</th>
                <th>Maximum Marks</th>
            </tr>
            <tr>
                    <td>{{ average_marks }}</td>
                <td>{{ max_marks }}</td>
            </tr>
        </table>
        """

# Create Jinja2 template and render
       # Create Jinja2 template and render
        template = Template(template_text)
        output = template.render(average_marks=average_marks, max_marks=max_marks)

# Write rendered HTML to output file
        with open('output.html', 'w') as f:
           f.write(output)

    