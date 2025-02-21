import pandas as pd
import tmdbsimple as tmdb
import argparse
import time
import sys, os

def create_or_update_tmdb_list(csv_filepath, list_id, username, password, api_key, dry_run=True):
    tmdb.API_KEY=api_key  # Initialize TMDb class

    try:
        # --- TMDb Authentication (Corrected and Simplified with tdbsimple) ---
        auth = tmdb.Authentication()
        token = auth.token_new()['request_token']
        success = auth.token_validate_with_login(request_token=token, username=username, password=password)
        if not success:
            raise Exception("Authentication failed.") # Handle authentication failure

        session = auth.session_new(request_token=token)['session_id']
        tmdb.session_id = session # Set the session id

        account = tmdb.Account(session_id=session)
        info = account.info()

        # ... (Rest of the code for list management)
        df = pd.read_csv(csv_filepath)
        movie_tuples = list(zip(df['title'], df['year']))
        # movie_titles = df['title'].tolist()

        lists_response = account.lists()
        lists = lists_response['results']
        
        my_list = None
        my_list_id = None
        for lst in lists:
            if lst['name'] == list_id:
                my_list_id = lst['id']
                break

        if my_list_id is None:
            print(f"Failed to locate list (ID: {my_list_id})")
            return
        else:
            print(f"Found existing list (ID: {my_list_id})")

        movie_list = None
        if not dry_run:
            movie_list = tmdb.Lists(id=my_list_id, session_id=session)
            list_details = movie_list.info()
            current_movies_in_list = [item['title'] for item in list_details.get('items', []) if isinstance(item, dict) and 'title' in item]
        else:
            current_movies_in_list = []

        movies_added = 0
        movies_not_found = 0
        movies_already_in_list = 0

        search = tmdb.Search()

        for title, year in movie_tuples:
            if title in current_movies_in_list:
                movies_already_in_list += 1
                if dry_run:
                    print(f"(Dry Run) Movie already in list: {title}")
                continue

            search_results = search.movie(query=title, year=year)['results']

            if search_results:
                movie = search_results[0]
                if dry_run:
                    print(f"(Dry Run) Would add: {title} (TMDb ID: {movie['id']})")
                    movies_added += 1
                else:
                    try:
                        movie_list.add_item(media_id=movie['id'])
                        movies_added += 1
                        print(f"Added: {title} y={year} (TMDb ID: {movie['id']})")
                        time.sleep(1)
                    except Exception as e:
                        # print(f"Error adding {title} y={year}: {e}")
                        movies_already_in_list += 1

            else:
                print(f"Movie not found: {title}")
                movies_not_found += 1

        print(f"\nSummary:")
        print(f"Movies added: {movies_added}")
        print(f"Movies already in list: {movies_already_in_list}")
        print(f"Movies not found: {movies_not_found}")

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(f"An error occurred: {e}")
        print(exc_type, fname, exc_tb.tb_lineno)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage TMDb lists from a CSV file.")
    parser.add_argument("csv_file", help="Path to the CSV file.")
    parser.add_argument("api_key", help="Your TMDb API key.")
    parser.add_argument("-u", "--username", help="Your TMDB username.")
    parser.add_argument("-p", "--password", help="Your TMDB password.")
    parser.add_argument("-d", "--dry-run", action="store_true", help="Perform a dry run.")
    parser.add_argument("-l", "--movielistid", help="Int identifier for your movie list")

    args = parser.parse_args()

    create_or_update_tmdb_list(args.csv_file, args.movielistid, args.username, args.password, args.api_key, dry_run=args.dry_run)