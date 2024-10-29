#############################################################################################
#                                                                                             
#                             ____  __  __  ____  ____ 
#                            (  _ \(  )(  )(  _ \(  _ \
#                             )___/ )(__)(  )   / )   /
#                            (__)  (______)(_)\_)(_)\_)
#                      Providing Universities Reliable Reports                           
#                                                                                            
# ~~~~~~~~~~~~~~~~~~~~~~~~~[ get_CANVAS_enrollments.py ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# FILE: get_CANVAS_enrollments.py
# AUTHOR: Kevin Hitt
# DATE CREATED: 2023-July-03
# PYTHON VERSION: 3.11.4
# 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ DESCRIPTION ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Enrollments are captured below through 1 of 2 available means, by course instead of by
# user endpoint. Course #1403 is notably excluded.
# An API call is made for a list of courses, while on that 1 page of courses another API
# call is made to capture the enrollments of those courses.
# Only the enrollment data is appended throughout the loop, discarding the course data. 
# Courses in the initial API call do not include deleted courses. 
# 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ NOTES ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# TODO: To reduce bloat of future imports, expand list of "skip courses" to include those
#       where enrollment is definitively closed or deemed irreleveant. Also consider list
#       of courses to include, as to avoid initial API call.
#
# TODO: Add optimization described above to Sections import as well? 
#  
# First execution: 1842.81 seconds for ~54 MB [30 minutes]
#
############################################

import requests
import json
import time
from connection_canvas import CANVAS_API_TOKEN


def get_CANVAS_enrollments():
    print(" ~*~*~*~ ~*~*~*~ EXECUTING get_CANVAS_enrollments ~*~*~*~ ~*~*~*~")
    start_time = time.time() # Start timing

    headers = CANVAS_API_TOKEN

    # API endpoint URL
    api_url = "https://canvas.instructure.com/api/v1/accounts/134780000000000001/courses/"

    # Define the API endpoint parameters
    # Starting with courses - do not load enrollments for 
    params = {
        'per_page': '1000',
        'page': '1',
        'include[]': ['total_students'],
        'state[]': ['completed','unpublished','available']
    }

    params_enr = {
        'per_page': '1000',
        'page': '1',
        'include[]': ['avatar_url', 'cuurent_points'],
        'state[]': ['active','invited','creation_pending','deleted','rejected','completed','inactive','current_and_invited','current_and_future','current_and_concluded']
    }

    # Start timing
    start_time = time.time()

    # Make API request to retrieve courses
    all_data = []  # To store all the retrieved data
    page = 1
    has_more_pages = True

    # IDs of courses to skip when retrieving enrollments
    skip_course_ids = [1403]

    while has_more_pages:
        params['page'] = str(page)
        response = requests.get(api_url, params=params, headers=headers)
        if response.status_code == 200:
            courses = response.json()
            for course in courses:
                course_id = course['id']
                if course_id not in skip_course_ids:
                    print("Getting data for Course ID#: ", course_id)
                    enrollments_response = requests.get(f"https://canvas.instructure.com/api/v1/courses/{course_id}/enrollments", params=params_enr, headers=headers)
                    if enrollments_response.status_code == 200:
                        enrollments = enrollments_response.json()
                        for enrollment in enrollments:
                            enrollment['course_id'] = course_id
                            all_data.append(enrollment)
            page += 1
            if not courses:
                has_more_pages = False
        else:
            print("No 200 status code")
            break

    # End timing
    end_time = time.time()

    # Save the combined data to a JSON file
    with open('x-canvas-enrollments.json', 'w') as f:
        json.dump(all_data, f)

    print(f" ~*~*~*~ ~*~*~*~ CREATED x-canvas-enrollments.json ~*~*~*~ ~*~*~*~")
    print(f'Done in {time.time()-start_time:.2f} seconds!')
    return "...checking with conductor..."

# Call the function if script1.py is executed directly
if __name__ == "__main__":
    result = get_CANVAS_enrollments()
    print(result)
