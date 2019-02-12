import standalone

standalone.run('settings')

from productions.models import Production, Scene, Shot, Person

p = Person.objects.get(name='Joachim Trier', tmdb_id='71609')


obj, created = Person.objects.get_or_create(name='Joachim Trier', tmdb_id='71609')


print obj, created