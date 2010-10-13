from django.db import models

class Tag(models.Model):
    """ Generic class to implement tagging. """
    name = models.CharField(max_length=80, db_index=True, unique = True)

    def __unicode__(self):
        return self.name
