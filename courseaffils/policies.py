#### Structured Collaboration Support ####
try:
    from structuredcollaboration.policies import CollaborationPolicy, CollaborationPolicies

    class PrivateStudentAndFaculty(CollaborationPolicy):
        def manage(self,coll,request):
            return (coll.context == request.collaboration_context
                    and request.course.is_faculty(request.user))

        edit = manage
        delete = manage

        def read(self,coll,request):
            return (coll.context == request.collaboration_context
                    and (request.course.is_faculty(request.user)
                         or coll.user == request.user #student
                         ))

        add_child = read

    class InstructorManaged(CollaborationPolicy):
        def manage(self,coll,request):
            return (coll.context == request.collaboration_context
                    and (request.course.is_faculty(request.user)
                         or coll.user == request.user)
                    )
        edit = manage
        delete = manage

        def read(self,coll,request):
            return (coll.context == request.collaboration_context)

    class CourseProtected(CollaborationPolicy):
        def manage(self,coll,request):
            return (coll.context == request.collaboration_context
                    and (coll.user == request.user
                         or (coll.group and request.user in coll.group.user_set.all())))

        edit = manage
        delete = manage
        add_child = manage

        def read(self,coll,request):
            return (coll.context == request.collaboration_context
                    and course.is_member(request.user))

    class CourseCollaboration(CourseProtected):
        edit = CourseProtected.read
        add_child = CourseProtected.read

    class CoursePublicCollaboration(CourseCollaboration):
        read = lambda c,r:True

        
    CollaborationPolicies.register_policy(InstructorManaged,
                                          'InstructorManaged',
                                          'Instructors/Staff and user manage, Course members read')

    CollaborationPolicies.register_policy(PrivateStudentAndFaculty,
                                          'PrivateStudentAndFaculty',
                                          'Private between faculty and student')

    
    CollaborationPolicies.register_policy(CourseProtected,
                                          'CourseProtected',
                                          'Protected to Course Members')

    CollaborationPolicies.register_policy(CourseCollaboration,
                                          'CourseCollaboration',
                                          'Course Collaboration')

    CollaborationPolicies.register_policy(CoursePublicCollaboration,
                                          'CoursePublicCollaboration',
                                          'Public Course Collaboration')



except ImportError:
    pass
