# Contains callable-scripts for db operations

import datetime
from .models import Activity
from .balance import convert_to_utc


def delete_obsolete_activities():
    """
    Clears Activity objects in database that are no longer relevant ( >2 days old )
    :return: status code
    """

    # convert current time to aware datetime object (UTC)
    now = datetime.datetime.now()
    now_utc = convert_to_utc(now)

    # To be safe, I can delete activities that are greater than 2 days old when called
    two_days = datetime.timedelta(days=2)

    activity_removal_cutoff_date = str(now_utc - two_days)
    print('cutoff date: ', activity_removal_cutoff_date)

    # get all acts from at least 2 days ago
    acts_to_delete = Activity.objects.filter(date_added__lt=activity_removal_cutoff_date)

    try:
        # delete Activity objects created before the aware cutoff-date
        acts_to_delete.delete()
        print('Activities from 2 days ago or longer have been deleted.')
        return 0
    except Exception as e:
        print('No activities were deleted: ', e)
        return 1


# called on initial load
delete_obsolete_activities()
