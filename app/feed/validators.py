"""
Cutom Validations
"""
from rest_framework import serializers


not_allowed_words = ('murder',)


def check_allowed_words(value):
    """Check if the field contain any forbiden word"""
    for item in not_allowed_words:
        if item in value.lower():
            raise serializers.ValidationError(
                detail=f'<{item}> word is not an allowed word')
