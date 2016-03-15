from __future__ import unicode_literals

from django.contrib.auth.models import Group
from django.conf import settings

auto_groups = getattr(settings, "COURSEAFFIL_AUTO_MAP_GROUPS", [])


def auto_group_mapper(sender, **kwargs):
    for group in auto_groups:
        group = Group.objects.get_or_create(name=group)[0]
        sender.groups.add(group)
        sender.save()


class AutoGroupWindMapper:
    """
    maps all wind-based users to a fixed set of groups on login
    (autovivifying if necessary)
    """

    def map(self, user, affils):
        for group in auto_groups:
            group = Group.objects.get_or_create(name=group)[0]
            user.groups.add(group)
            user.save()
