from django import forms
from .models import Comment, Board  
from tag.models import Tag

class BoardForm(forms.ModelForm):
    title = forms.CharField(
        error_messages={
            'required': '제목을 입력해주세요.'
        }, max_length=64, label="제목")
    contents = forms.CharField(
        error_messages={
            'required': '내용을 입력해주세요.'
        }, widget=forms.Textarea, label="내용")
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False)  

    class Meta:
        model = Board
        fields = ['title', 'contents', 'tags']

    def clean_tags(self):
        tags = self.cleaned_data.get('tags')
        if isinstance(tags, list):
            tags = ', '.join(tags)
        return tags

class CommentForm(forms.ModelForm):
    parent = forms.ModelChoiceField(
        queryset=Comment.objects.all(),
        widget=forms.HiddenInput,
        required=False
    )

    class Meta:
        model = Comment
        fields = ['comment', 'parent']

    def __init__(self, *args, **kwargs):
        self.board = kwargs.pop('board', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        comment = super().save(commit=False)
        comment.board = self.board
        if commit:
            comment.save()
        return comment