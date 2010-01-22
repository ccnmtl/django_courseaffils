from django import forms
from django.contrib.auth.models import User,Group
from django.conf import settings
from courseaffils.models import Course

class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course

    if hasattr(settings,'COURSEAFFILS_COURSESTRING_MAPPER'):
         course_string = settings.COURSEAFFILS_COURSESTRING_MAPPER.widget()

    add_user = forms.CharField(
        required=False,
        widget=forms.Textarea,
        label="Add users to group (one per line)",
        help_text="Put a [ * ] in front of the username to make them faculty.",
        )

    users_to_remove = forms.ModelMultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        queryset=User.objects.none(),
        label="Remove users from group",
        )

    def __init__(self, *args, **kw):
        forms.ModelForm.__init__(self, *args, **kw)
        if self.instance.user_set:
            ruf = self.fields['users_to_remove']
            ruf.queryset = ruf._choices = self.instance.user_set.all()

    def clean(self):
        if hasattr(settings,'COURSEAFFILS_COURSESTRING_MAPPER')  \
                and self.cleaned_data.get('course_string',False):
            m = settings.COURSEAFFILS_COURSESTRING_MAPPER
            stud_grp,fac_grp = m.get_groups(self.cleaned_data['course_string'])
            if fac_grp:
                self.cleaned_data['faculty_group'] = fac_grp
            self.cleaned_data['group'] = stud_grp
            return self.cleaned_data
        
        return self.cleaned_data

    def clean_users_to_remove(self):
        users = self.cleaned_data['users_to_remove']
        if self.instance.group_id:
            group = self.instance.group

            for user in users:
                user.groups.remove(group)
        return users

    def clean_add_user(self):
        usernames = self.cleaned_data['add_user']
        if not usernames:
            return

        #take it from here, in case instance is not yet created
        group = self.cleaned_data['group']
        for line in usernames.split('\n'):
            username = line.strip().rstrip()
            also_faculty = False
            if username.startswith('*'):
                username = username[1:]
                also_faculty = True
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = User(username=username)
                    user.save()
                user.groups.add(group)
                if also_faculty:
                    user.groups.add(self.cleaned_data['faculty_group'])
        return usernames

