import pandas as pd
import themoviedb
import argparse
import time
import webbrowser
import os

def create_or_update_tmdb_list(csv_filepath, list_name, api_key, dry_run=True):
    themoviedb.API_KEY = api_key

    try:
        # --- TMDb Authentication (Corrected and Simplified with themoviedb) ---
        # themoviedb handles session automatically

        # ... (Rest of the code for list management)
        df = pd.read_csv(csv_filepath)
        movie_titles = df['title'].tolist()

        # Corrected: Instantiate Account object
        account = themoviedb.Account()  # Instantiate Account
        account_details = account.get_account_details() # Correct call
        account_id = account_details['id']

        lists_response = account.get_movie_lists()
        lists = lists_response['results']

        my_list = None
        my_list_id = None
        for lst in lists:
            if lst['name'] == list_name:
                my_list_id = lst['id']
                break

        if my_list_id is None:
            if not dry_run:
                my_list = account.create_movie_list(name=list_name, description="List created by script")
                my_list_id = my_list['id']
                print(f"Created new list: {list_name} (ID: {my_list_id})")
        else:
            print(f"Found existing list: {list_name} (ID: {my_list_id})")

        if not dry_run:
            list_details = account.get_movie_list(my_list_id)
            current_movies_in_list = [item['title'] for item in list_details.get('items', []) if isinstance(item, dict) and 'title' in item]
        else:
            current_movies_in_list = []

        movies_added = 0
        movies_not_found = 0
        movies_already_in_list = 0

        search = themoviedb.Search()

        for title in movie_titles:
            if title in current_movies_in_list:
                movies_already_in_list += 1
                print(f"(Dry Run) Movie already in list: {title}")
                continue

            search_results = search.movie(query=title)['results']

            if search_results:
                movie = search_results[0]
                if dry_run:
                    print(f"(Dry Run) Would add: {title} (TMDb ID: {movie['id']})")
                    movies_added += 1
                else:
                    try:
                        account.add_movie_to_list(list_id=my_list_id, media_id=movie['id'])
                        movies_added += 1
                        print(f"Added: {title} (TMDb ID: {movie['id']})")
                        time.sleep(1)
                    except Exception as e:
                        print(f"Error adding {title}: {e}")
                        movies_not_found += 1

            else:
                print(f"Movie not found: {title}")
                movies_not_found += 1

        print(f"\nSummary:")
        print(f"Movies added: {movies_added}")
        print(f"Movies already in list: {movies_already_in_list}")
        print(f"Movies not found: {movies_not_found}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage TMDb lists from a CSV file.")
    parser.add_argument("csv_file", help="Path to the CSV file.")
    parser.add_argument("list_name", nargs="?", default="My Movie List", help="Name of the TMDb list.")
    parser.add_argument("api_key", help="Your TMDb API key.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Perform a dry run.")

    args = parser.parse_args()

    create_or_update_tmdb_list(args.csv_file, args.list_name, args.api_key, dry_run=args.dry_run)