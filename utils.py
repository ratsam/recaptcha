from django.http import HttpRequest
import inspect

def obtain_request():
	ancestors = inspect.getouterframes(inspect.currentframe())
	for frame_record in ancestors:
		frame = frame_record[0]
		if 'request' in frame.f_locals:
			req = frame.f_locals['request']
			if isinstance(req, HttpRequest):
				return req