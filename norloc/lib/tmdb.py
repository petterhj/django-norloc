# -*- coding: utf-8 -*-

# Imports
import logging
import tmdbsimple as tmdb
from json import dumps
from django.conf import settings


# Logger
logger = logging.getLogger('norloc')


# Class: TMDb
class TMDb(object):
    # Init
    def __init__(self):
        # Setup
        tmdb.API_KEY = settings.TMDB_API_KEY
        self.language = settings.TMDB_LANGUAGE

    
    # Search
    def search(self, title, limit=10):
        # Search films/shows by title
        logging.info('Searching for "%s" (limit=%d)' % (title, limit))
        tmdb_search = tmdb.Search()
        results = []

        for production_type, method in {'film': tmdb_search.movie, 'tv': tmdb_search.tv}.items():
            logging.info('> Searching type %s' % (production_type))

            for production in method(query=title, language=self.language).get('results')[0:limit]:
                title = production.get('original_title') or production.get('title') or production.get('name')
                poster_path = production.get('poster_path')
                poster = 'https://image.tmdb.org/t/p/w200' + poster_path if poster_path else None

                results.append({
                    'tmdb_id': production.get('id'),
                    'type': production_type,
                    'title': title,
                    'original_language': production.get('original_language'),
                    'popularity': production.get('popularity', 0),
                    'overview': production.get('overview'),
                    'poster': poster,
                    'release': production.get('release_date') or production.get('first_air_date')
                })

        # Sort results by popularity
        # results = sorted(results['films'], key=lambda f: f['popularity'], reverse=True) 

        return results


    # Details
    def details(self, production_type, tmdb_id):
        search_types = {'film': tmdb.Movies, 'tv': tmdb.TV}
        
        if production_type not in search_types:
            return {}

        # Fetch production details
        production = search_types.get(production_type)(tmdb_id)
        details = production.info(language=self.language, append_to_response='credits')

        # Parse data
        title = details.get('original_title') or details.get('title')
        title = title or details.get('original_name') or details.get('name')
        poster_base = 'https://image.tmdb.org/t/p/w500'
        crew = details.get('credits', {}).get('crew', [])
        production_countries = [c['iso_3166_1'] for c in details.get('production_countries', [])]

        production_countries = production_countries or details.get('origin_country', [])

        parsed = {
            'tmdb_id': details.get('id'),
            'imdb_id': details.get('imdb_id', ''),
            'title': title,
            'overview': details.get('overview'),
            'poster': poster_base + details.get('poster_path') if details.get('poster_path') else None,
            'release': details.get('release_date') or details.get('first_air_date'),
            'languages': {l['iso_639_1']: l['name'] for l in details.get('spoken_languages', {})},
            'production_countries': production_countries,
            'production_companies': [{
                'name': company.get('name'),
                'country': company.get('origin_country')
            } for company in details.get('production_companies')],
            'runtime': details.get('runtime') or details.get('episode_run_time', [])[0:1],
            'directors': [{
                'tmdb_id': p.get('id'),
                'name': p.get('name'),
                'image': poster_base + p.get('profile_path') if p.get('profile_path') else None,
            } for p in crew if p.get('job') == 'Director'],
            'writers': [{
                'tmdb_id': p.get('id'),
                'name': p.get('name'),
                'image': poster_base + p.get('profile_path') if p.get('profile_path') else None,
            } for p in crew if p.get('job') in ['Writer', 'Screenplay']],
            'photographers': [{
                'tmdb_id': p.get('id'),
                'name': p.get('name'),
                'image': poster_base + p.get('profile_path') if p.get('profile_path') else None,
            } for p in crew if p.get('job') == 'Director of Photography'],
        }

        return parsed


    # Search people
    def people_search(self, name, limit=10):
        # Search people by name
        tmdb_search = tmdb.Search()
        results = []
        
        from json import dumps
        for person in tmdb_search.person(query=name, language=self.language).get('results')[0:limit]:
            headshot_path = person.get('profile_path')
            headshot = 'https://image.tmdb.org/t/p/w200' + headshot_path if headshot_path else None

            results.append({
                'tmdb_id': person.get('id'),
                'name': person.get('name'),
                'popularity': person.get('popularity', 0),
                'productions': [{
                    'title': p.get('title') or p.get('name'),
                    'release': p.get('release_date') or p.get('first_air_date')
                } for p in person.get('known_for', [])],
                'headshot': headshot
            })

        return results


    # Person details
    def person_details(self, tmdb_id):
        # Fetch person details
        person = tmdb.People(tmdb_id)
        details = person.info(language=self.language)

        # Parse data
        poster_base = 'https://image.tmdb.org/t/p/w500'

        parsed = {
            'tmdb_id': details.get('id'),
            'imdb_id': details.get('imdb_id'),
            'name': details.get('name'),
            'biography': details.get('biography'),
            'headshot': poster_base + details.get('profile_path') if details.get('profile_path') else None,
            'known_for_department': details.get('known_for_department'),
            'birthplace': details.get('place_of_birth'),
            'birthdate': details.get('birthday'),
        }

        return parsed#{'d': details, 'p': parsed}