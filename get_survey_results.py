#~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# File: get_survey_results.py
# Author: Kevin Hitt
# Date: 17 September 2024

# With list of courses, get Quiz IDs.
# Use Quiz IDs to generate "Student Analysis" reports.
# Get URLs from that POST response.
# Save URLs to later download the report w student responses. 
#
#~~~~~~~~~~~~~~~~~~~~~~~~~~

import requests
import csv
import re

# Relevant courses
"""
    2817	Technical Training
    2735	Awareness New
    2683	Awareness Old
    3334	Executive Nov. 2024
    3333	Executive Dec. 2024
    3332	Executive Sep. 2024
    3317	Executive Oct. 2024
    3316	Executive Aug. 2024
"""
course_ids = [2817,2735,2683,3334,3333,3332,3317,3316]

# Headers for authentication
headers = {'Authorization': 'Bearer INSERT_YOUR_API_KEY'}
base_url = 'https://usfcorporatetraining.instructure.com'
params = {
    'quiz_report[report_type]': 'student_analysis'
}

# Initialize list
data_list = []

# Loop through courses
for course_id in course_ids:
    print(f'Processing course #: {course_id}')
    # Step 1: Get all quizzes for the course
    quizzes_url = f'{base_url}/api/v1/courses/{course_id}/quizzes'
    try:
        quizzes_response = requests.get(quizzes_url, headers=headers)
        if quizzes_response.status_code == 200:
            quizzes = quizzes_response.json()
            # Step 2: Filter quizzes where title contains "pre" (case-insensitive)
            filtered_quizzes = [
                quiz for quiz in quizzes if re.search(r'pre', quiz.get('title', ''), re.IGNORECASE)
            ]
            if not filtered_quizzes:
                print(f'No quizzes containing "pre" found for course {course_id}')
                continue
            # Step 3: For each filtered quiz, extract URL
            for quiz in filtered_quizzes:
                quiz_id = quiz['id']
                quiz_title = quiz['title']
                # Generate report
                report_url = f'{base_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/reports'
                params = {
                    'quiz_report[report_type]': 'student_analysis',
                }
                report_response = requests.post(report_url, headers=headers, params=params)
                if report_response.status_code in (200,201):
                    report_json = report_response.json()
                    file_info = report_json.get('file', {})
                    file_url = file_info.get('url', '')
                    data_list.append({
                        'course_id': course_id,
                        'quiz_id': quiz_id,
                        'quiz_title': quiz_title,
                        'url': file_url
                    })
                    print(f'Successfully retrieved URL for quiz "{quiz_title}" (ID: {quiz_id}) in course {course_id}')
                else:
                    print(f'Failed to generate report for quiz "{quiz_title}" (ID: {quiz_id}) in course {course_id}, status code {report_response.status_code}')
                    data_list.append({
                        'course_id': course_id,
                        'quiz_id': quiz_id,
                        'quiz_title': quiz_title,
                        'url': 'Failed to retrieve'
                    })
        else:
            print(f'Failed to retrieve quizzes for course {course_id}, status code {quizzes_response.status_code}')
    except Exception as e:
        print(f'Error processing course {course_id}: {e}')

# Write to CSV
csv_file = 'output.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    fieldnames = ['course_id', 'quiz_id', 'quiz_title', 'url']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for data in data_list:
        writer.writerow(data)

print(f'Data has been written to {csv_file}')
