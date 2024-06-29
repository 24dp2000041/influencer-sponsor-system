import sys
from jinja2 import Template
import matplotlib.pyplot as plt
import csv

with open("data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile)
    student_course = []
    course_marks = []
    input_list = sys.argv

total = 0
if input_list[1] == '-s':
    for row in reader:
        if input_list[2] in row[8]:
            total = int(row[2].strip())
            student_course.append(row)

    if student_course == []:
        data = """<h1>Wrong Inputs</h1>
                  <p>Something went wrong</p>"""
        with open('output.html', 'w') as File:
            File.write(data)
    else:
        text = """<h1> Student Details </h1>
                  <table border="2">
                  <tr>
                  <th>Student ID</th>
                  <th>Course ID</th>
                  <th>Marks ID</th>
                  </tr>
                  {% for student in student_course %}
                  <tr>
                  <td>{{ student[8].strip() }}</td>
                  <td>{{ student[1].strip() }}</td>
                  <td>{{ student[2].strip() }}</td>
                  </tr>
                  {% endfor %}
                  <tr>
                  <td colspan="2"> Total Marks </td>
                  <td> {{ total }} </td>
                  </tr>
                  </table>"""
        temp = Template(text)
        output1 = temp.render(total=total, student_course=student_course)
        with open('output.html', 'w') as File:
            File.write(output1)


elif input_list[1] == 'c':
    for row in reader:
        if input_list[2] in row[1]:
            course_marks.append(int(row[2].strip()))

    if course_marks == []:
        data = """<h1>Wrong Inputs</h1>
                  <p>Something went wrong</p>"""
        with open('output.html', 'w') as File:
            File.write(data)
    else:
        average_marks = sum(course_marks) / len(course_marks)
        max_marks = max(course_marks)
        course_data = """<h1> Course Details </h1>
                         <table>
                         <tr>
                         <th>Average Marks</th>
                         <th>Maximum Marks</th>
                         </tr>
                         <tr>
                         <td>{{ average_marks }}</td>
                         <td>{{ max_marks }}</td>
                         </tr>
                         </table>"""
        # Create Jinja2 template and render
template = Template(template_text)
output = template.render(average_marks=average_marks, max_marks=max_marks)

# Write rendered HTML to output file
with open('output.html', 'w') as f:
    f.write(output)

                        