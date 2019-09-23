from __future__ import unicode_literals

import re
try:
    from urllib.error import HTTPError
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen, HTTPError
from time import strptime, strftime


class CourseStringMapper:
    @staticmethod
    def widget():
        from django import forms
        w = forms.CharField(
            required=False,
            widget=forms.TextInput,
            help_text=(
                'Alternate to choosing a group. '
                'Enter the section key from the directory of courses. '
                'e.g. 20101SCNC1000F001 (which is yyyytddddnnnnLsss where '
                'y=year, t=term (with "1" for Spring and '
                '"3" for Fall), '
                'd=dept, n=course number, '
                'L=course letter, s=section). You can also enter the course-'
                'string in the format the group names appear for another '
                'course (e.g. "t1.y2010.s001.cf1000.scnc.st.course:'
                'columbia.edu" ). '
                '<br /><br /> '
                'This will create a group that automatically ties '
                'registered students '
                'to the class upon login. '
                '<br /><br /> '
                'If the course is not found in the '
                '<a href="http://www.columbia.edu/cu/bulletin/uwb/">'
                'Directory of Classes</a>, then it will still create '
                'a course. '
                'This is a GOOD WAY to create a course that is not '
                'associated '
                'with a directory. Alternatively, click the (+) '
                'signs next '
                'to "Group" and "Faculty group" fields and create groups '
                'manually, before clicking save. '
                '<br /> '
                'If you accidentally entered the wrong course '
                'string, blank out '
                'the groups (course and faculty) and type in '
                'the string again.')
        )

        def clean(sectionkey):
            if sectionkey:
                class_info = SectionkeyTemplate.to_dict(sectionkey)
                if not class_info:
                    raise forms.ValidationError('Invalid course string.')
                else:
                    return sectionkey
        w.clean = clean
        return w

    @staticmethod
    def get_groups(sectionkey):
        from django.contrib.auth.models import Group
        section_dict = SectionkeyTemplate.to_dict(sectionkey)
        if not section_dict:
            section_dict = WindTemplate.to_dict(sectionkey)

        if section_dict:
            stud_grp_name = WindTemplate.to_string(section_dict)
            fac_grp_name = WindTemplate.to_string(
                dict(section_dict, member='fc'))

            stud_grp, created = Group.objects.get_or_create(name=stud_grp_name)
            fac_grp, created = Group.objects.get_or_create(name=fac_grp_name)
            return stud_grp, fac_grp
        else:
            return None, None

    @staticmethod
    def get_course_info(course_dict):
        directory_link = DirectoryLinkTemplate.to_string(course_dict)
        response = urlopen(directory_link).read()

        return DirectoryPageTemplate.to_dict(response)

    @staticmethod
    def on_create(course):
        course_dict = WindTemplate.to_dict(course.group.name)
        from courseaffils.models import CourseInfo

        info, created = CourseInfo.objects.get_or_create(course=course)
        if course_dict:
            info.year = int(course_dict['year'])
            info.term = int(course_dict['term'])
        try:
            info_from_web = CourseStringMapper.get_course_info(
                WindTemplate.to_dict(course.group.name))

            for val in info_from_web:
                if val == 'days':
                    info.days = info_from_web[val]
                elif val in ('starttime', 'endtime'):
                    tm = strptime(info_from_web[val], '%I:%M%p')
                    setattr(info, val, strftime('%H:%M', tm))
                else:
                    course.coursedetails_set.get_or_create(
                        name=val,
                        value=info_from_web[val],
                        course=course)
        except (TypeError, KeyError, ValueError, HTTPError):
            # oh well, couldn't get extra data.
            # maybe because it's a fake course string or not a proper course
            pass
        info.save()

    @staticmethod
    def course_slug(course, attempt=0):
        "returns a slug for the course, with higher resolution for attempt > 0"
        class_info = WindTemplate.to_dict(course.group.name)
        slug = None
        if class_info and 'number' in class_info:
            attempts = {
                0: "CU%s%s" % (class_info['dept'],
                               class_info['number'], ),
                1: "CU%s%s_%s" % (class_info['dept'],
                                  class_info['number'],
                                  class_info['section'],),
            }
            slug = attempts[attempt]
        else:
            slug = re.sub(r' ', '_', course.title)
        return re.sub(r'\W', '', slug)

    @staticmethod
    def to_string(cdict):
        return WindTemplate.to_string(cdict)

    @staticmethod
    def to_dict(wind_string):
        return WindTemplate.to_dict(wind_string)


class WindTemplate:
    example = 't3.y2007.s001.cw3956.engl.fc.course:columbia.edu'

    @staticmethod
    def to_string(cdict):
        cdict['member'] = cdict.get('member', 'st')
        return 't%s.y%s.s%s.c%s%s.%s.%s.course:columbia.edu' % (
            cdict['term'],
            cdict['year'],
            cdict['section'].lower(),
            cdict['letter'].lower(),
            cdict['number'],
            cdict['dept'].lower(),
            cdict['member'].lower(),
        )

    @staticmethod
    def to_dict(wind_string):
        wind_match = re.match(
            (r't(?P<term>\d).y(?P<year>\d{4}).s(?P<section>\w{3})'
             r'.c(?P<letter>\w)(?P<number>\w{4})'
             r'.(?P<dept>[\w&]{4}).(?P<member>\w\w).course:columbia.edu'),
            wind_string)
        if wind_match:
            return wind_match.groupdict()


class SectionkeyTemplate:
    example = '20101SCNC1000F001'  # and 20103MIMD036PN004

    @staticmethod
    def to_dict(sectionkey):
        key_match = re.match(
            (r'(?P<year>\d{4})(?P<term>\d)(?P<dept>[\w&]{4})'
             r'(?P<number>\w{4})(?P<letter>\w)(?P<section>\w{3})'),
            sectionkey)
        if key_match:
            return key_match.groupdict()


class DirectoryLinkTemplate:
    example = ('http://www.columbia.edu/cu/bulletin/'
               'uwb/subj/SCNC/C1100-20101-003/')

    @staticmethod
    def to_string(cdict):
        return (
            'http://www.columbia.edu/cu/bulletin/'
            'uwb/subj/%s/%s%s-%s%s-%s/') % (
                cdict['dept'].upper(),
                cdict['letter'].upper(),
                cdict['number'],
                cdict['year'],
                cdict['term'],
                cdict['section'], )


class CanvasTemplate:
    example = 'SDEVW2300_001_2011_1'

    @staticmethod
    def to_dict(affil_string):
        affil_match = re.match(
            (r'(?P<dept>[\w&]{4})(?P<letter>\w)'
             r'(?P<number>\w{4})_(?P<section>\w{3})_'
             r'(?P<year>\d{4})_(?P<term>\d)'),
            affil_string)
        if affil_match:
            return affil_match.groupdict()


class AffilTemplate:
    example = 'CUcourse_SDEVW2300_001_2011_1'

    @staticmethod
    def to_dict(affil_string):
        affil_match = re.match(
            (r'CUcourse_(?P<dept>[\w&]{4})(?P<letter>\w)'
             r'(?P<number>\w{4})_(?P<section>\d{3})_'
             r'(?P<year>\d{4})_(?P<term>\d)'),
            affil_string)
        if affil_match:
            return affil_match.groupdict()


class DirectoryPageTemplate:
    @staticmethod
    def to_dict(html_page):
        ret_val = {}
        look_for = (
            r'Call Number</td>[^>]*>(?P<call_number>\d*)</td>',
            r'Location</td>[^>]*>(?P<times>[^<]*)<br>(?P<location>[^<]*)</td>',
            r'Points</td>[^>]*>(?P<points>[\d\-.]*)</td>',
            r'Campus</td>[^>]*>(?P<campus>[\w\s]*)</td>',
            r'Instructor</td>[^>]*>(?P<instructor>[^<]*)</td>',
            # 'approvals_required', 'type', 'enrollment',
            # 'max_enrollment', 'status',
            # 'title', 'open_to', 'note', 'sectionkey',
        )
        for reg in look_for:
            m = re.search(reg, html_page)
            if m:
                ret_val.update(m.groupdict())

        if 'times' in ret_val:
            m = re.match(
                (r'(?P<days>\w*)\s*(?P<starttime>[\d:apm]*)\-'
                 r'(?P<endtime>[\d:apm]*)'),
                ret_val['times'])
            if m:
                ret_val.update(m.groupdict())

        return ret_val


class HashTagTemplate:
    example = '#CUviet1201'

    @staticmethod
    def to_string(cdict):
        return '#CU%s%s' % (
            cdict['dept'].lower(),
            cdict['number'],
        )
