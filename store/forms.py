from django import forms
from .models import ReviewAndRating


class ReviewAndRatingForm(forms.ModelForm):
    model = ReviewAndRating
    fields = ['subject', 'review', 'rating']