import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from knesset.annotations.models import JsonField, Annotation

class AnnotationModelTest(TestCase):
    def test_json_field_object_to_python(self):
        field = JsonField()
        result = field.to_python('{ "key": "value", "listkey": ["item1", "item2"] }')
        self.assertEqual("value", result["key"])

    def test_json_field_object_to_db(self):
        field = JsonField()
        obj = {"key": "value", "listkey": ["item1", "item2"]}
        result = field.get_db_prep_save(obj)
        self.assertEqual(obj, json.loads(result))

    def test_json_field_list_to_python(self):
        field = JsonField()
        result = field.to_python('["word1","word2","word3"]')
        self.assertEqual("word1", result[0])

    def test_json_field_list_to_db(self):
        field = JsonField()
        result = field.get_db_prep_save(['word1', 'word2', 'word3'])
        self.assertEqual(u'["word1", "word2", "word3"]', result)

    def test_create_annotation(self):
        data = {"permissions":
          {"read":["testuser"],
           "update":["testuser"],
           "delete":["testuser"],
           "admin":["testuser"]},
           "user":
             {"id":"testuser","name":"Test User"},
           "text":"This is a test",
           "tags":[],
           "ranges":[{
             "start":"/div[3]/div[2]/blockquote/p",
             "startOffset":4,
             "end":"/div[3]/div[2]/blockquote/p",
             "endOffset":19}],
           "quote":"Quote",
           "uri":"http://oknesset.org/committee/meeting/4163/"}

        res = self.client.post(reverse('annotation-handler'), json.dumps(data), content_type="application/json")
        self.assertEqual(201, res.status_code)
        self.assertEqual(1, Annotation.objects.count())
