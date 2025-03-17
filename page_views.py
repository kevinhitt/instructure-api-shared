# Purpose:  Provided a list of User ID #s, retrieve all Canvas LMS page view activity and export in CSV format.
# Author:   Kevin Hitt
# Date:     March 2025

import csv
import requests
import time

# Base URL not specific to course #2703 as predefined user ID list assumes this filter
base_url = 'https://usfcorporatetraining.instructure.com/api/v1'   

auth_token = 'INSERT HERE'

def get_all_page_views(user_id, delay=0.2):
    """
    Fetches all page views for a given user, handling pagination.
    Returns a list of JSON objects (page view records).
    
    :param user_id: The user's ID
    :param delay: Seconds to wait between requests (to limit rate)
    """
    url = f"{base_url}/users/{user_id}/page_views"
    headers = {'Authorization': f'Bearer {auth_token}'}
    params = {'per_page': 100}
    
    all_views = []
    page_count = 0

    while url:
        # Show progress for each page request
        print(f"  Requesting page {page_count + 1} for user {user_id} -> {url}")
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        data = response.json()
        all_views.extend(data)
        
        # Handle pagination
        if 'next' in response.links:
            url = response.links['next']['url']
            params = {}
        else:
            url = None
        
        page_count += 1
        
        # Delay to avoid spamming the API
        time.sleep(delay)
    
    print(f"  Finished fetching. Total pages: {page_count}, total views: {len(all_views)}")
    return all_views

def main():
    input_csv = 'user_ids.csv'          # CSV file with a single column named 'user_id'
    output_csv = 'user_page_views.csv'  # Consolidated output of all page views
    
    fieldnames = [
        'user_id',
        'id',
        'app_name',
        'url',
        'context_type',
        'asset_type',
        'controller',
        'action',
        'contributed',
        'interaction_seconds',
        'created_at',
        'user_request',
        'render_time',
        'user_agent',
        'participated',
        'http_method',
        'remote_ip',
        'links_user',
        'links_account'
    ]

    with open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(fieldnames)

        with open(input_csv, mode='r', newline='', encoding='utf-8') as in_file:
            reader = csv.DictReader(in_file)
            for i, row in enumerate(reader, start=1):
                user_id = row['user_id']
                print(f"\nProcessing user #{i}: {user_id}...")

                # Fetch the page views for this user (with a small delay between pages)
                page_views = get_all_page_views(user_id, delay=0.2)

                for pv in page_views:
                    writer.writerow([
                        user_id,
                        pv.get('id'),
                        pv.get('app_name'),
                        pv.get('url'),
                        pv.get('context_type'),
                        pv.get('asset_type'),
                        pv.get('controller'),
                        pv.get('action'),
                        pv.get('contributed'),
                        pv.get('interaction_seconds'),
                        pv.get('created_at'),
                        pv.get('user_request'),
                        pv.get('render_time'),
                        pv.get('user_agent'),
                        pv.get('participated'),
                        pv.get('http_method'),
                        pv.get('remote_ip'),
                        pv.get('links', {}).get('user'),
                        pv.get('links', {}).get('account')
                    ])
                
                print(f"Done processing user {user_id}. PageViews written: {len(page_views)}")
                # Brief delay between *users* (in addition to delays between each page)
                time.sleep(0.2)

if __name__ == '__main__':
    main()
