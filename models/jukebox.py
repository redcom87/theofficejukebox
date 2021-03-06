'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import datetime
import random
from google.appengine.ext import ndb
from google.appengine.api import users
from models.tracks import *
from models.ndb_models import *


class Jukebox(ndb.Expando, DictModel, NDBCommonModel):

    title = ndb.StringProperty()
    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date = ndb.DateTimeProperty(auto_now=True)
    owner_key = ndb.KeyProperty()

    # deprecated due to lots of results
    @property
    def queued_tracks(self):
        queued_tracks = QueuedTrack.query(ancestor=self.key).filter(QueuedTrack.archived==False).order(QueuedTrack.edit_date).fetch(100)
        return queued_tracks

    @property
    def player(self):
        player = JukeboxPlayer.query(ancestor=self.key).get()
        return player

    @classmethod
    def random_archived_queued_track(cls, jukebox_key):
        queued_track_keys = QueuedTrack.query(ancestor=jukebox_key)\
            .filter(QueuedTrack.archived==True)\
            .order(QueuedTrack.edit_date).fetch(2, keys_only=True)
        if not queued_track_keys:
            return False
        random_key = random.choice(queued_track_keys)
        return random_key.get()

    @classmethod
    def	membership_types(cls):

        membership_types = {
            'admins': ['admin','owner'],
            'members': ['admin','owner', 'member']
        }
        return membership_types



    @classmethod
    def _to_dict(cls, jukebox):
        jukebox_id = jukebox.key.id()
        jukebox_dict = jukebox.to_dict(
            exclude=[
                'creation_date',
                'edit_date',
                'on_datetime',
                'owner_key'
            ]
        )
        jukebox_dict.update({
            'id': jukebox_id,
        })
        return jukebox_dict


# Has as id the person id. 1 person to many. Als as prop to query without parent?
class JukeboxMembership(ndb.Expando, DictModel, NDBCommonModel):

    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date = ndb.DateTimeProperty(auto_now=True)
    person_key = ndb.KeyProperty()
    type = ndb.StringProperty()

    @classmethod
    def _to_dict(cls, jukebox_membership):
        jukebox_membership_id = jukebox_membership.key.id()
        jukebox_membership_dict = jukebox_membership.to_dict(
            exclude=[
                'creation_date',
                'edit_date',
                'person_key',
            ]
        )
        jukebox_membership_dict.update({
            'id': jukebox_membership_id,
            'jukebox_id': jukebox_membership.key.parent().id()
        })
        return jukebox_membership_dict


class JukeboxPlayer(ndb.Expando, DictModel, NDBCommonModel):

    creation_date = ndb.DateTimeProperty(auto_now_add=True)
    edit_date = ndb.DateTimeProperty(auto_now=True)
    on = ndb.BooleanProperty(default=False)
    time_since_on = ndb.DateTimeProperty()
    status = ndb.StringProperty()
    track_queued_on = ndb.DateTimeProperty()
    track_duration = ndb.IntegerProperty()
    # can also be used as key
    track_key = ndb.KeyProperty()

    @property
    def duration_on(self):
        if not self.on:
            return False
        duration_on = datetime.datetime.now() - self.track_queued_on
        return duration_on.total_seconds()

    '''
    All Hooks etc go here
    '''

    #@classmethod
    #def _pre_delete_hook(cls, key):
        #should delete all the queue tracks