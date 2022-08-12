django-courseaffils
===================

[![Actions Status](https://github.com/ccnmtl/django_courseaffils/workflows/build-and-test/badge.svg)](https://github.com/ccnmtl/django_courseaffils/actions)

`django_courseaffils` is a django app which manages course information, parsing
course info out of CAS affiliations.

The selected course is available in `request.course`.

Several settings are available to be added to a django project's
`settings.py`:

`COURSEAFFILS_EXEMPT_PATHS`

Directories which are available without selecting a course.
request.course will not be available from these directories.

Example:

    ('/accounts/','/site_media/','/admin/','/api/',)

`COURSEAFFILS_PATHS`

Directories where selecting a course is forced
Example:

    ('/users/','/essays/',
     re.compile(r'^/$'), #the homepage
    )

`COURSEAFFILS_COURSESTRING_MAPPER`

This will be a Class that has several connections to the Course admin
form, which make it possible to enter a course string and
automatically generate the proper group names.


`COURSEAFFILS_COURSESTRING_MAPPER.on_create` also gives a hook when a
course is created to do post-creation changes on it (to fill in course
info)

Example: see `courseaffils.columbia.CourseStringMapper`

`SERVER_ADMIN_SECRETKEYS`

This is a dict of hosts which can get override access and possibly
info about a course through an api, without logging in, etc.

Example:

    {'http://www.example.com/':'secret_when_example.com_interfaces with us'}



Template Tags
-------------

When developers include `{% load coursetags %}` into their template,
their are several tags available:

`{% public_name for user %}`

prints the full name of `user` variable and falls back to the
username.  When an `ANONYMIZE` cookie is present, then it will be
replaced with "User Name_<uid>" so things can be anonymized quickly.

This calls `courseaffils.lib.get_public_name(user, request)`

`{% get_courses for user as courses %}`

sets the variable `courses` to the list of courses the `user` variable
is in

`{% course_role for user in course as course_role %}`

sets the variable `course_role` to one of:

* `no-course`
* `non-member`
* `instructor`
* `student`
