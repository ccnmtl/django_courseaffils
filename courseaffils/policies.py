#### Structured Collaboration Support ####
try:
    from structuredcollaboration.policies import CollaborationPolicy
    from structuredcollaboration.policies import CollaborationPolicies
    from structuredcollaboration.policies import PrivateEditorsAreOwners

    class PrivateStudentAndFaculty(CollaborationPolicy):
        def manage(self, coll, request):
            return (coll.context == request.collaboration_context
                    and request.course
                    and request.course.is_faculty(request.user))

        delete = manage

        def read(self, coll, request):
            return (coll.context == request.collaboration_context
                    and ((request.course
                          and request.course.is_faculty(request.user))
                         or coll.user_id == request.user.id  # student
                         or (coll.group_id
                             and request.user in coll.group.user_set.all())
                         ))

        edit = read

    class InstructorShared(PrivateEditorsAreOwners):
        def read(self, coll, request):
            return (self.manage(coll, request)
                    or request.course.is_faculty(request.user))

    class InstructorManaged(CollaborationPolicy):
        def manage(self, coll, request):
            return (coll.context == request.collaboration_context
                    and ((request.course
                          and request.course.is_faculty(request.user))
                         or coll.user == request.user)
                    )
        delete = manage

        def read(self, coll, request):
            return (coll.context == request.collaboration_context)

        edit = read

    class CourseProtected(CollaborationPolicy):
        def manage(self, coll, request):
            return (coll.context == request.collaboration_context
                    and (coll.user == request.user
                         or (coll.group
                             and request.user in coll.group.user_set.all())))

        edit = manage
        delete = manage

        def read(self, coll, request):
            return (getattr(request, 'course', None)
                    and coll.context == getattr(
                    request, 'collaboration_context', None)
                    and request.course.is_member(request.user))

    class CourseCollaboration(CourseProtected):
        edit = CourseProtected.read

    class CoursePublicCollaboration(CourseCollaboration):
        read = lambda c, r: True

    class Assignment(CollaborationPolicy):
        def manage(self, coll, request):
            return (coll.context == request.collaboration_context
                    and ((request.course
                          and request.course.is_faculty(request.user))
                         or coll.user == request.user)
                    )
        delete = manage
        edit = manage

        def read(self, coll, request):
            return (request.course
                    and coll.context == request.collaboration_context)

        add_child = read

    class PublicAssignment(Assignment):
        def read(self, coll, request):
            return (coll.context == request.collaboration_context)

    CollaborationPolicies.register_policy(
        InstructorManaged,
        'InstructorManaged',
        'Instructors/Staff and user manage, Course members read')

    CollaborationPolicies.register_policy(
        InstructorShared,
        'InstructorShared',
        'group/user manage/edit and instructors can view')

    CollaborationPolicies.register_policy(
        PrivateStudentAndFaculty,
        'PrivateStudentAndFaculty',
        'Private between faculty and student')

    CollaborationPolicies.register_policy(
        CourseProtected,
        'CourseProtected',
        'Protected to Course Members')

    CollaborationPolicies.register_policy(CourseCollaboration,
                                          'CourseCollaboration',
                                          'Course Collaboration')

    CollaborationPolicies.register_policy(CoursePublicCollaboration,
                                          'CoursePublicCollaboration',
                                          'Public Course Collaboration')

    CollaborationPolicies.register_policy(
        Assignment,
        'Assignment',
        'Course assignment (instructors can manage/edit, '
        'course members can read/respond)')

    CollaborationPolicies.register_policy(
        PublicAssignment,
        'PublicAssignment',
        'Public Assignment (instructors can manage/edit, '
        'course members can respond, world can see)')

except ImportError:
    pass
