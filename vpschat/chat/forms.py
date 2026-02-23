from django import forms

class EnterRoomForm(forms.Form):
    display_name = forms.CharField(
        label="نام نمایشی",
        max_length=80,
        required=False,
        widget=forms.TextInput(attrs={"class": "input", "placeholder": "مثلاً علی"}),
    )
    password = forms.CharField(
        label="رمز اتاق",
        required=False,
        widget=forms.PasswordInput(attrs={"class": "input", "placeholder": "رمز (در صورت نیاز)"}),
    )

class RoomAdminForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={"class": "input"}))
    slug = forms.SlugField(max_length=140, widget=forms.TextInput(attrs={"class": "input"}))
    is_protected = forms.BooleanField(required=False)
    password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={"class": "input"}))

    def clean(self):
        cleaned = super().clean()
        is_protected = cleaned.get("is_protected")
        password = cleaned.get("password")
        if is_protected and not password:
            # allow blank password only when editing and user doesn't want to change it (handled in view)
            pass
        if not is_protected:
            cleaned["password"] = ""
        return cleaned
