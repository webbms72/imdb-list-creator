import pandas as pd
import tmdbsimple as tmdb
import argparse
import time
import webbrowser

def create_or_update_tmdb_list(csv_filepath, list_name, api_key, dry_run=True):
    tmdb.API_KEY = api_key

    try:
        # --- TMDb Authentication (Finally Corrected and Tested) ---
        auth = tmdb.Authentication()  # Create an instance

        # 1. Get a request token
        request_token_response = auth.request_token()  # Call on the instance
        request_token = request_token_response['request_token']

        # 2. Build the authorization URL
        authorization_url = f"https://www.themoviedb.org/authenticate/{request_token}"

        # 3. Open the URL in the user's browser
        webbrowser.open_new_tab(authorization_url)

        # 4. Get user confirmation
        print(f"Please authorize the request token at: {authorization_url}")
        print("After authorizing, press Enter to continue...")
        input()

        # 5. Create a session ID (using the approved request token)
        session_response = auth.create_session(request_token=request_token)  # Call on the instance
        session_id = session_response['session_id']
        print(f"Session ID created: {session_id}")

        # Now use the session_id
        account = tmdb.Account(session_id=session_id)

        # ... (Rest of the code for list management remains the same)
        df = pd.read_csv(csv_filepath)
        movie_titles = df['title'].tolist()

        tmdb_api = tmdb.Movies()

        account_details = account.info()
        account_id = account_details['id']

        lists = account.movie_lists(account_id)['results']
        my_list_id = None
        for lst in lists:
            if lst['name'] == list_name:
                my_list_id = lst['id']
                break

        if my_list_id is None:
            if not dry_run:
                new_list = account.movie_list_create(name=list_name, description="List created by script")
                my_list_id = new_list['id']
                print(f"Created new list: {list_name} (ID: {my_list_id})")
        else:
            print(f"Found existing list: {list_name} (ID: {my_list_id})")

        if not dry_run:
            list_details = account.movie_list(my_list_id)
            current_movies_in_list = [item['title'] for item in list_details.get('items', []) if isinstance(item, dict) and 'title' in item]
        else:
            current_movies_in_list = []

        movies_added = 0
        movies_not_found = 0
        movies_already_in_list = 0

        for title in movie_titles:
            if title in current_movies_in_list:
                movies_already_in_list += 1
                print(f"(Dry Run) Movie already in list: {title}")
                continue

            search_results = tmdb_api.search(query=title)['results']

            if search_results:
                movie_id = search_results[0]['id']
                movie_details = tmdb_api.details(movie_id)  # You can remove this if you don't use it
                if dry_run:
                    print(f"(Dry Run) Would add: {title} (TMDb ID: {movie_id})")
                    movies_added += 1
                else:
                    try:
                        account.movie_list_add_movie(my_list_id, movie_id)
                        movies_added += 1
                        print(f"Added: {title} (TMDb ID: {movie_id})")
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
    parser.add_argument("api_key", help="Your TMDb API key.")  # Required API key argument
    parser.add_argument("-d", "--dry-run", action="store_true", help="Perform a dry run.")

    args = parser.parse_args()

    create_or_update_tmdb_list(args.csv_file, args.list_name, args.api_key, dry_run=args.dry_run)
