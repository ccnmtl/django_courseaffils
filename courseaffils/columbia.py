import re
import urllib

class CourseStringMapper:
    @classmethod
    def widget(cls):
        from django import forms
        w = forms.CharField(required=False,
                            widget=forms.TextInput,
                            help_text="""Alternate to choosing a group. Enter the section key from the directory of courses.  e.g. 20101SCNC1000F001 (which is yyyytddddnnnnLsss where y=year, t=term, d=dept, n=course number, L=course letter, s=section) """
                            )
        def clean(data):
            if data:
                if not SectionkeyTemplate.to_dict(data):
                    raise forms.ValidationError('Invalid course string.')
                else:
                    return data
        w.clean = clean
        return w

    @classmethod
    def get_groups(cls,section_key):
        from django.contrib.auth.models import Group
        section_dict = SectionkeyTemplate.to_dict(section_key)
        if section_dict:
            stud_grp_name = WindTemplate.to_string(section_dict)
            fac_grp_name = WindTemplate.to_string(dict(section_dict, member='fc'))

            stud_grp,created = Group.objects.get_or_create(name=stud_grp_name)
            fac_grp,created = Group.objects.get_or_create(name=fac_grp_name)
            return stud_grp,fac_grp
        else:
            return None,None

    @classmethod
    def get_course_info(cls,groupname):
        course_dict = WindTemplate.to_dict(groupname)
        directory_link = DirectoryLinkTemplate.to_string(course_dict)
        
        response = urllib.urlopen(directory_link).read()
        return DirectoryPageTemplate.to_dict(response)

class WindTemplate:
    example = 't3.y2007.s001.cw3956.engl.fc.course:columbia.edu'

    @staticmethod
    def to_string(cdict):
        cdict['member'] = cdict.get('member','st')
        return 't%s.y%s.s%s.c%s%s.%s.%s.course:columbia.edu' % (
            cdict['term'],
            cdict['year'],
            cdict['section'],
            cdict['letter'].lower(),
            cdict['number'],
            cdict['dept'].lower(),
            cdict['member'].lower(),
            )

    @staticmethod
    def to_dict(wind_string):
         wind_match = re.match('t(?P<term>\d).y(?P<year>\d{4}).s(?P<section>\d{3}).c(?P<letter>\w)(?P<number>\d{4}).(?P<dept>[\w&]{4}).(?P<member>\w\w).course:columbia.edu',wind_string)
         if wind_match:
             return wind_match.groupdict()

class SectionkeyTemplate:
    example = '20101SCNC1000F001'

    @staticmethod
    def to_dict(sectionkey):
        key_match = re.match('(?P<year>\d{4})(?P<term>\d)(?P<dept>[\w&]{4})(?P<number>\d{4})(?P<letter>\w)(?P<section>\d{3})',sectionkey)
        if key_match:
            return key_match.groupdict()


class DirectoryLinkTemplate:
    example = 'http://www.columbia.edu/cu/bulletin/uwb/subj/SCNC/C1100-20101-003/'
    @staticmethod
    def to_string(cdict):
        return 'http://www.columbia.edu/cu/bulletin/uwb/subj/%s/%s%s-%s%s-%s/' % (
            cdict['dept'].upper(),
            cdict['letter'].upper(),
            cdict['number'],
            cdict['year'],
            cdict['term'],
            cdict['section'],
            )
        
class DirectoryPageTemplate:
    @staticmethod
    def to_dict(html_page):
        ret_val = { }
        look_for = (
            'Call Number</td>[^>]*>(?P<call_number>\d*)</td>',
            'Location</td>[^>]*>(?P<times>[^<]*)<br>(?P<location>[^<]*)</td>',
            'Points</td>[^>]*>(?P<points>[\d-.]*)</td>',
            'Campus</td>[^>]*>(?P<campus>\w*)</td>',
            #'approvals_required','type','enrollment','max_enrollment','status',
            #'title','open_to','note','sectionkey',
            )
        for reg in look_for:
            m = re.search(reg,html_page)
            if m: ret_val.update( m.groupdict() )

        if ret_val.has_key('times'):
            m = re.match('(?P<days>\w*)\s*(?P<starttime>[\d:apm]*)-(?P<endttime>[\d:apm]*)', 
                         ret_val['times'])
            if m: ret_val.update( m.groupdict() )

        return ret_val

class HashTagTemplate:
    example = '#CUviet1201'

    @staticmethod
    def to_string(cdict):
        return '#CU%s%s' % (
            cdict['dept'].lower(),
            cdict['number'],
            )

