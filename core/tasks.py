import random
from celery import shared_task
from matching import match_main





@shared_task
def match_task():
    # Celery recognizes this as the `movies.tasks.add` task
    # the name is purposefully omitted here.
    match_main()
    

