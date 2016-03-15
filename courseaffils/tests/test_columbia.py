from __future__ import unicode_literals

from django.test import TestCase
from courseaffils.columbia import HashTagTemplate
from courseaffils.columbia import DirectoryPageTemplate
from courseaffils.columbia import CourseStringMapper
from courseaffils.columbia import WindTemplate
from courseaffils.columbia import SectionkeyTemplate
from courseaffils.columbia import AffilTemplate


class DummyRequest(object):
    COOKIES = dict()


class ColumbiaSimpleTest(TestCase):

    def test_hashtagtemplate(self):
        self.assertEqual(
            HashTagTemplate.to_string(dict(dept="FOO", number="five")),
            "#CUfoofive")

    def test_directorytagtemplate(self):
        # searching an empty page should return an empty dict
        self.assertEqual(DirectoryPageTemplate.to_dict(""), dict())

        self.assertEqual(DirectoryPageTemplate.to_dict(
            """Points</td><td>5</td>"""), dict(points="5"))

        self.assertEqual(
            DirectoryPageTemplate.to_dict(
                'Location</td><td>MW 9am-10<br>Lewisohn 123</td>'
            ),
            dict(
                location="Lewisohn 123",
                times="MW 9am-10",
                days="MW",
                starttime="9am",
                endtime="10",))

    def test_affiltemplate(self):
        self.assertEqual(
            AffilTemplate.to_dict(AffilTemplate.example),
            dict(
                dept="SDEV",
                letter="W",
                number="2300",
                section="001",
                year="2011",
                term="1",
            )
        )

    def test_directorylinktemplate(self):
        pass

    def test_sectionkeytemplate(self):
        example1 = '20101SCNC1000F001'  # and 20103MIMD036PN004
        self.assertEqual(
            SectionkeyTemplate.to_dict(example1),
            dict(
                year="2010",
                term="1",
                dept="SCNC",
                number="1000",
                letter="F",
                section="001",))

        # a newstyle sw section key, w/ a leading letter for the section

        example2 = '20153SOCW0006TD21'
        self.assertEqual(
            SectionkeyTemplate.to_dict(example2),
            dict(
                year="2015",
                term="3",
                dept="SOCW",
                number="0006",
                letter="T",
                section="D21",))

    def test_windtemplate(self):
        example = 't3.y2007.s001.cw3956.engl.fc.course:columbia.edu'
        # round-trip it
        self.assertEqual(
            WindTemplate.to_string(WindTemplate.to_dict(example)),
            example)

        example = 't3.y2007.sd21.cw3956.engl.fc.course:columbia.edu'
        # round-trip it
        self.assertEqual(
            WindTemplate.to_string(WindTemplate.to_dict(example)),
            example)

    def test_csmapper_course_slug(self):
        class StubGroup(object):
            name = 't3.y2007.s001.cw3956.engl.fc.course:columbia.edu'

        class StubCourse(object):
            def __init__(self):
                self.group = StubGroup()
        self.assertEqual(
            CourseStringMapper.course_slug(StubCourse()),
            'CUengl3956')

    def test_csmapper_widget(self):
        self.assertEqual(
            CourseStringMapper.widget().clean('20101SCNC1000F001'),
            '20101SCNC1000F001')

    def test_csmapper_get_groups(self):
        s, f = CourseStringMapper.get_groups('20101SCNC1000F001')
        self.assertIsNotNone(s)
        self.assertIsNotNone(f)
        s, f = CourseStringMapper.get_groups(WindTemplate.example)
        self.assertIsNotNone(s)
        self.assertIsNotNone(f)

        s, f = CourseStringMapper.get_groups("something completely invalid")
        self.assertIsNone(s)
        self.assertIsNone(f)

    def test_csmapper_get_course_info(self):
        # this one makes an HTTP request to the CU DOC site
        # so it's not really appropriate for unit testing
        pass
