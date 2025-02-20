import pandas as pd
import tmdb3
import argparse
import time
import webbrowser
import os

def create_or_update_tmdb_list(csv_filepath, list_name, api_key, dry_run=True):
    tmdb3.api_key = api_key

    try:
        # --- TMDb Authentication (Corrected and Simplified) ---
        session_id = os.environ.get("TMDB_SESSION_ID")

        if session_id is None:
            auth = tmdb3.Authentication()
            request_token = auth.request_token.request_token
            authorization_url = f"https://www.themoviedb.org/authenticate/{request_token}"
            webbrowser.open_new_tab(authorization_url)
            print(f"Please authorize at: {authorization_url}")
            print("After authorizing, press Enter to continue...")
            input()
            session = auth.create_session(request_token=request_token)
            session_id = session.session_id

            os.environ["TMDB_SESSION_ID"] = session_id
            print(f"Session ID stored in environment variable.")

        tmdb3.session_id = session_id  # Set the session ID globally

        # ... (Rest of the code for list management)
        df = pd.read_csv(csv_filepath)
        movie_titles = df['title'].tolist()

        account = tmdb3.Account()
        account_id = account.id

        lists = account.lists()  # Get all lists
        my_list = None
        for lst in lists:
            if lst.name == list_name:
                my_list = lst
                break

        if my_list is None:
            if not dry_run:
                my_list = account.create_list(name=list_name, description="List created by script")
                print(f"Created new list: {list_name} (ID: {my_list.id})")
        else:
            print(f"Found existing list: {list_name} (ID: {my_list.id})")

        if not dry_run:
            current_movies_in_list = [movie.title for movie in my_list.items]
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

            results = tmdb3.searchMovie(title)  # Corrected: Use tmdb3.searchMovie() directly
            if results:
                movie = results[0]
                if dry_run:
                    print(f"(Dry Run) Would add: {title} (TMDb ID: {movie.id})")
                    movies_added += 1
                else:
                    try:
                        my_list.add_movie(movie)
                        movies_added += 1
                        print(f"Added: {title} (TMDb ID: {movie.id})")
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
