#!/usr/bin/env python

try:
    from mimetools import choose_boundary
except:
    from email.generator import _make_boundary as choose_boundary
from mimetypes import guess_type
import six
import os


DEFAULT_MIME_TYPE = 'application/octet-stream'
USER_AGENT = 'Python Telegram Bot'\
             ' (https://github.com/leandrotoledo/python-telegram-bot)'

if six.PY3:
    import io

    def is_file(item):
        return isinstance(item, io.TextIOWrapper)
else:
    def is_file(item):
        return isinstance(item, file)


class InputFile(object):
    def __init__(self,
                 data):
        self.data = data
        self.boundary = choose_boundary()

        if 'audio' in data and is_file(data['audio']):
            self.input_name = 'audio'
            self.input_file = data.pop('audio')
        if 'document' in data and is_file(data['document']):
            self.input_name = 'document'
            self.input_file = data.pop('document')
        if 'photo' in data and is_file(data['photo']):
            self.input_name = 'photo'
            self.input_file = data.pop('photo')
        if 'video' in data and is_file(data['video']):
            self.input_name = 'video'
            self.input_file = data.pop('video')

        self.input_file_content = self.input_file.read()
        self.filename = os.path.basename(self.input_file.name)
        self.mimetype = guess_type(self.filename)[0] or DEFAULT_MIME_TYPE

    @property
    def headers(self):
        return {'User-agent': USER_AGENT, 'Content-type': self.content_type}

    @property
    def content_type(self):
        return 'multipart/form-data; boundary=%s' % self.boundary

    def to_form(self):
        form = []
        form_boundary = '--' + self.boundary

        # Add data fields
        for name, value in self.data.iteritems():
            form.extend([
                form_boundary,
                str('Content-Disposition: form-data; name="%s"' % name),
                '',
                str(value)
            ])

        # Add input_file to upload
        form.extend([
            form_boundary,
            str('Content-Disposition: form-data; name="%s"; filename="%s"' % (
                self.input_name, self.filename
                )),
            'Content-Type: %s' % self.mimetype,
            '',
            self.input_file_content
        ])

        form.append('--' + self.boundary + '--')
        form.append('')

        return '\r\n'.join(form)
