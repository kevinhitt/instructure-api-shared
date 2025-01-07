#############################################################################################
# 
# FILE: notif-by-orders.py
# AUTHOR: Kevin Hitt
# DATE CREATED: 2023-July-05
# PYTHON VERSION: 3.11.4
# 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ DESCRIPTION ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# Bot to ultimately notify ETC partners of new registrations. 
# 
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~[ NOTES ]~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 
# TODO: scheduling logic via Windows Task Scheduler
#       IMAP/POP optimization 
#
############################################

import datetime
import requests
import time
import json
import csv
import sys

############################################ CHECK LAST RUN
# Get date of the last time USF checked for ETC registrations 
# (stored in JSON file that is overwritten with each execution)

def read_last_execution_date():
    try:
        with open('queries/last_execution_datetime.json', 'r') as f:
            data = json.load(f)
            return data['last_execution_datetime']
    except FileNotFoundError:
        return None

def update_last_execution_date(date):
    with open('queries/last_execution_datetime.json', 'w') as f:
        json.dump({'last_execution_datetime': date}, f)

last_execution_date = read_last_execution_date()
last_execution_time = last_execution_date 
print("Last execution time from file: ", last_execution_time, "-----------------------")

# Convert the last execution time to a datetime object
last_execution_datetime = datetime.datetime.fromisoformat(last_execution_time[:-1])

# Get the current UTC time
current_datetime = datetime.datetime.utcnow()
# Compare the current time with the last execution time
if current_datetime >= last_execution_datetime:
    print("Script execution condition is met. Proceed with executing the script.")
else:
    print("Script execution condition is not met. Skip the script.")
    sys.exit()

############################################ CATALOG ORDERS

# Define API details
url = "https://usfcorporatetraining.catalog.instructure.com/api/v1/orders?page={}&from={}&per_page=10000"
headers = {'Authorization': 'Token token=3c5bf7bff61926f1fe9226f9e2eb796e'}

# Parameter dictionary via requests package doesn't seem to work with Catalog
page = 1  
from_date = last_execution_time
data = []
start_time = time.time()

while True:
    # Make API request for the current page
    response = requests.get(url.format(page,from_date), headers=headers)
    response_json = response.json()
    response_data = response_json['orders']

    # Append the orders to the data list
    data.extend(response_data)

    # Check if there are more pages to fetch
    if not response_data or len(response_data) < 100:
        break

    # Increment the page counter
    page += 1

with open('mydata.json', 'w') as f:
    json.dump(data, f)

############################################ FILTER ORDERS
################## only successful orders
################## only target categories

# FILTER - orders within Test Prep
''' (old categories before subcatalog changes)
target_categories = ["SAT Review Online","SAT Review","LSAT Review Online","GRE Review Online","GMAT Review Online",
                     "Summer K-5 Math Camp", "SAT Review", "LSAT Review", "GRE Review", "GMAT Review",
                     "ACT Review","ACT Review Online","Summer K-12 Education Camps",
                     "Grade 1 (K-8 Math)","Grade 2 (K-8 Math)","Grade 3 (K-8 Math)","Grade 4 (K-8 Math)",
                     "Grade 5 (K-8 Math)","Grade 6 (K-8 Math)","Grade 7 (K-8 Math)","Grade 8 (K-8 Math)",]
'''
target_categories = ["YXP SAT Preparation","YXP LSAT Preparation","YXP GRE Preparation",
                     "YXP GMAT Preparation","YXP ACT Preparation","YXP ETC Courses",
                     "YXP K-8 Math Camps",
                     "YXP Grade 1 (K-8 Math)", "YXP Grade 2 (K-8 Math)", "YXP Grade 3 (K-8 Math)", "YXP Grade 4 (K-8 Math)", 
                     "YXP Grade 5 (K-8 Math)", "YXP Grade 6 (K-8 Math)", "YXP Grade 7 (K-8 Math)", "YXP Grade 8 (K-8 Math)"]

# Iterate over the orders and extract values where course[category] matches the target
matching_orders = []
successful_orders = []
unsuccessful_orders = []

for order in data:
    if order["catalog"]["name"] in target_categories:
        matching_orders.append(order)

for order in matching_orders:
    if order["purchased_at"] is None and len(order.get("promotions", [])) == 0:
        unsuccessful_orders.append(order)
    else:
        successful_orders.append(order)

with open('matching_orders.json', 'w') as f:
    json.dump(matching_orders, f)

with open('good_orders.json', 'w') as f:
    json.dump(successful_orders, f)

with open('bad_orders.json', 'w') as f:
    json.dump(unsuccessful_orders, f)

for order in successful_orders:
    print("Order ID:", order["id"])
    print("Purchased at:", order["purchased_at"])

    if "payments" in order and len(order["payments"]) > 0:
        print("Payment Reference:", order["payments"][0]["reference_id"])
        print("Payment Amount:", order["payments"][0]["amount"])

    print("User ID:", order["user"]["id"])
    print("User Name:", order["user"]["name"])
    print("User Email:", order["user"]["email"])
    print("Course ID:", order["listings"][0]["canvas_course_id"])
    print("Course Category:", order["catalog"]["name"])
    print("-----")

############################################ COURSE SECTION START DATE

# Extract list of user IDs from ETC orders
course_list = []

for order in successful_orders:
    course_list.append(order["listings"][0]["canvas_course_id"])

print(course_list)

# GET START DATE
data_course = []
url_course = "https://canvas.instructure.com/api/v1/accounts/134780000000000001/courses/13478000000000{}"
params_course = {
    'per_page': '1000',
    'page': '1',
    'include[]':'sections'
}
headers_course = {'Authorization': 'Bearer TOKEN'}

for course in course_list:
    response = requests.get(url_course.format(course), params=params_course, headers=headers_course)
    response_json = response.json()
    try:
        response_data = {}  # Initialize response_data as an empty dictionary
        
        response_data['course_id'] = response_json['id']
        response_data['name'] = response_json['name']

        # Parse the date string and convert it to a different format
        start_date_str = response_json['sections'][0]['start_at']
        start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M:%SZ")
        response_data['start_date'] = start_date.strftime("%m/%d/%Y")
        response_data['code'] = response_json['course_code']
        
        # Append the data to the data_course list
        data_course.append(response_data)
    except KeyError:
        # Handle the case when 'user_registration' key is missing or has unexpected structure
        print("Error: Invalid response JSON structure for course #")
        print(course)


with open('etc-courses.json', 'w') as f:
    json.dump(data_course, f)

############################################ USER REGISTRATION INFORMATION

# Extract list of user IDs from ETC orders
user_list = []

for order in successful_orders:
    user_list.append(order["user"]["id"])

print(user_list)

# Make API calls for User_Registrations 
# While UDF fields should match, they may not all historically
# or from parents with different source subcatalogs, so 
# formatting may be challenging. 

# Deprecated in June 2024 with adoption enrollment level UDFs
# url_user = "https://usfcorporatetraining.catalog.instructure.com/api/v1/user_registrations/{}"
url_user = "https://usfcorporatetraining.catalog.instructure.com/api/v1/users?canvas_user_id={}"

data_user = []

for user in user_list:
    response = requests.get(url_user.format(user), headers=headers)
    response_json = response.json()
    #print(response_json)
    try:
        response_data = {}
        response_data['user_id'] = user
        # response_data['custom_fields'] = response_json['user_registration']['custom_fields'] #modified from 'user_registrations' used in batch import
        response_data['custom_fields'] = response_json['users'][0]['custom_fields'] # modified from above line after June 2024 enrollment level UDF update
        # Append the orders to the data list
        data_user.append(response_data)
    except KeyError:
        # Handle the case when 'user_registration' key is missing or has unexpected structure
        print("Error: Invalid response JSON structure for user #")
        print(user)
        

with open('etc-users.json', 'w') as f:
    json.dump(data_user, f)

# Print all
for custom_fields in data_user:
    # Access individual fields within each custom_fields array
    for field, value in custom_fields.items():
        print(f"{field}: {value}")
    print("-----")

############################################ FORMATTING

for order in successful_orders:
    # Update USER array based on canvas_user_id
    canvas_user_id = order["user"]["id"]
    for user_info in data_user:
        if user_info["user_id"] == canvas_user_id:
            order["user"].update(user_info)
            break  # Break the loop after finding a matching canvas_user_id

    # Update LISTING array based on canvas_course_id
    canvas_course_id = str(order["listings"][0]["canvas_course_id"])  # Convert to string
    for course_info in data_course:
        if str(course_info["course_id"])[-4:] == canvas_course_id[-4:]:
            order["listings"].append(course_info)
            break  # Break the loop after finding a matching canvas_course_id


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Request completed in {elapsed_time:.2f} seconds.")

with open('good_orders_final.json', 'w') as f:
    json.dump(successful_orders, f)

extracted_data = []

for order in successful_orders:
    
    user_id = order["user"]["id"]
    user_name = order["user"]["name"]
    user_email = order["user"]["email"]
    listing_course_id = order["listings"][0]["canvas_course_id"]
    listing_title = order["listings"][0]["title"]
    listing_start_date = order["listings"][1]["start_date"]
    order_total = order["total"]
    custom_fields = order["user"].get("custom_fields") 
    order_date = order["purchased_at"]

    # Check for missing or empty order_date
    if not order_date:
        print(f"Excluding record: Missing order_date for user {user_name} (ID: {user_id}).")
        continue  # Skip this record and move to the next

    # Add a check for the specific order amount
    if order_total == 195:
        print(f"Alert: Order with total amount 195 detected for user {user_name} (ID: {user_id}). Notify send re: Center for Career Development promotion Fall 2024")


    extracted_data.append({
        "user_id" : user_id,
        "name" : user_name,
        "email" : user_email,
        "course_id" : listing_course_id,
        'title' : listing_title,
        "starts_at" : listing_start_date,
        "total" : order_total,
        "order_date" : order_date,
        "custom_fields": custom_fields
    })

with open('20230704-etc.json', 'w') as f:
    json.dump(extracted_data, f)

# LOAD IT BACK UP (change to just accessing local variable)
with open('20230704-etc.json', 'r') as jsonfile:
    data = json.load(jsonfile)


# Extract field names from the JSON data, including nested fields
field_names = set()
for item in data:
    field_names.update(item.keys())
    if 'user' in item:
        user_fields = item['user'].keys()
        field_names.update([f'user.{field}' for field in user_fields])

# Get all unique custom_fields keys
custom_fields_keys = set()
for record in data:
    if "custom_fields" in record and record["custom_fields"] is not None:
        custom_fields_keys.update(record["custom_fields"].keys())

# Prepare CSV file and write data
csv_filename = "queries/etc-output.csv"
with open(csv_filename, "w", newline="") as csvfile:

    fieldnames = [
        "course_id",
        "title",
        "starts_at",
        "user_id",
        "name",
        "email",
        "total",
        "order_date",
        "street_address",
        "apt_number",
        "city",
        "state",
        "zip_code",
        "country",
        "phone_number",
        "parent_name",
        "parent_email",
        "custom_fields"
    ]
    #writer = csv.DictWriter(csvfile, fieldnames= list(field_names) + list(custom_fields_keys))
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)    
    writer.writeheader()

    for record in data:
        custom_fields = record.get("custom_fields", None) # Added , None) for error handling

        row_data = {
            "course_id": record.get("course_id"),
            "title": record.get("title"),
            "starts_at": record.get("starts_at"),
            "user_id": record.get("user_id"),
            "name": record.get("name"),
            "email": record.get("email"),
            "total": record.get("total"),
            "order_date": record.get("order_date"),
            "street_address": custom_fields.get("street_address") if custom_fields else None,
            "apt_number": custom_fields.get("apt_number") if custom_fields else None,
            "city": custom_fields.get("city") if custom_fields else None,
            "state": custom_fields.get("state") if custom_fields else None,
            "zip_code": custom_fields.get("zip_code") if custom_fields else None,
            "country": custom_fields.get("country") if custom_fields else None,
            "phone_number": custom_fields.get("phone_number") if custom_fields else None,
            "parent_name": custom_fields.get("parent_name") if custom_fields else None,
            "parent_email": custom_fields.get("parent_email") if custom_fields else None,
            #"custom_fields": custom_fields  # still keep the original custom_fields
        }

        writer.writerow(row_data)
"""
    for record in data:
        row_data = {
            "user_id": record["user_id"],
            "name": record["name"],
            "email": record["email"],
            "course_id": record["course_id"],
            "title": record["title"],
            "starts_at": record["starts_at"],
            "total": record["total"],
            "order_date":record["order_date"]
        }
        if "custom_fields" in record and record["custom_fields"] is not None:
            row_data.update(record["custom_fields"])

        writer.writerow(row_data)
"""

print("CSV file exported successfully.")

# Using strftime to control the number of digits in the fractional second
# Must be UTC format for exact time comparisons / to not repeat sending ETC orders
current_date = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


update_last_execution_date(current_date)

print("Updated execution timestamp successfully.")
