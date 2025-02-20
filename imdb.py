import pandas as pd
import imdb
import time

def create_or_update_imdb_list(csv_filepath, list_name="My Movie List", dry_run=True):
    """
    Creates or updates an IMDb list with movie titles from a CSV file.
    Dry run mode displays actions without modifying the IMDb list.

    Args:
        csv_filepath: Path to the CSV file containing movie titles.
        list_name: Name of the IMDb list to create or update.
        dry_run: If True, performs a dry run, only displaying actions.
    """

    try:
        # 1. Read movie titles from CSV
        df = pd.read_csv(csv_filepath)
        movie_titles = df['title'].tolist()

        # 2. Initialize IMDb API
        ia = imdb.Cinemetiq()

        if not dry_run:  # Only get user and lists if not a dry run
            user = ia.get_current_user()
            lists = ia.get_lists(user)

            my_list = None
            for lst in lists:
                if lst['name'] == list_name:
                    my_list = lst
                    break

            if my_list is None:
                if not dry_run:
                    my_list = ia.create_list(user, list_name)
                    print(f"Created new list: {list_name}")
            else:
                print(f"Found existing list: {list_name}")

            if not dry_run:
                current_movies_in_list = [movie['title'] for movie in my_list.get('list items', []) if isinstance(movie, dict) and 'title' in movie]
        else:
            current_movies_in_list = []  # In dry run, we don't know the actual list contents

        movies_added = 0
        movies_not_found = 0
        movies_already_in_list = 0

        for title in movie_titles:
            if title in current_movies_in_list:
                movies_already_in_list += 1
                print(f"(Dry Run) Movie already in list: {title}")
                continue

            results = ia.search_movie(title)
            if results:
                movie = results[0]
                if dry_run:
                    print(f"(Dry Run) Would add: {title} ({movie.movieID})")
                    movies_added += 1
                else:
                    try:
                        ia.add_item_to_list(my_list, movie)
                        movies_added += 1
                        print(f"Added: {title} ({movie.movieID})")
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


# Example usage (dry run):
csv_file = "movie_list.csv"
create_or_update_imdb_list(csv_file, "My Awesome Movie Collection", dry_run=True)  # Set dry_run to True

# Example usage (actual update):
# create_or_update_imdb_list(csv_file, "My Awesome Movie Collection", dry_run=False)  # Set dry_run to False for real update
