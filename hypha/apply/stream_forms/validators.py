from django import forms


def word_count(text):
    # TODO: match js implementation as close as possible
    # see https://github.com/tinymce/tinymce/blob/fd6e231164abc0141c7de653fcc6d85a4ce738d1/modules/polaris/src/main/ts/ephox/polaris/words/Words.ts#L115
    return len(text.split())


def word_limit_validator(word_limit):
    def validator(text):
        if word_count(text) > word_limit:
            # TODO: better error message
            # TODO: translated error message
            raise forms.ValidationError("too many words")
        return text

    return validator
