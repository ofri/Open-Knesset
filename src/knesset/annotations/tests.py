import json
from django.test import TestCase
from django.core.urlresolvers import reverse
from knesset.annotations.models import DictField, CommaDelimitedStringListField, Annotation

class AnnotationModelTest(TestCase):
    def test_dict_field_to_python(self):
        field = DictField()
        result = field.to_python('{ "key": "value", "listkey": ["item1", "item2"] }')
        self.assertEqual("value", result["key"])

    def test_dict_field_to_db(self):
        field = DictField()
        obj = {"key": "value", "listkey": ["item1", "item2"]}
        result = field.get_db_prep_save(obj)
        self.assertEqual(obj, json.loads(result))

    def test_comma_delimited_string_list_field_to_python(self):
        field = CommaDelimitedStringListField()
        result = field.to_python('word1,word2,word3')
        self.assertEqual("word1", result[0])

    def test_comma_delimited_string_list_field_to_db(self):
        field = CommaDelimitedStringListField()
        result = field.get_db_prep_save(['word1', 'word2', 'word3'])
        self.assertEqual('word1,word2,word3', result)

    def test_create_annotation(self):
        data = json.loads("""
        {"permissions":
          {"read":["habeanf"],
           "update":["habeanf"],
           "delete":["habeanf"],
           "admin":["habeanf"]},
           "user":
             {"id":"habeanf","name":"habeanf"},
           "text":"oiuio",
           "tags":[],
           "ranges":[{
             "start":"/div[3]/div[2]/blockquote/p",
             "startOffset":4,
             "end":"/div[3]/div[2]/blockquote/p",
             "endOffset":19}],
           "quote":"Quote",
           "uri":"http://localhost:8000/committee/meeting/4163/"}
        """)
        data2 = {"permissions":
          {"read":["habeanf"],
           "update":["habeanf"],
           "delete":["habeanf"],
           "admin":["habeanf"]},
           "user":
             {"id":"habeanf","name":"habeanf"},
           "text":"oiuio",
           "tags":[],
           "ranges":[{
             "start":"/div[3]/div[2]/blockquote/p",
             "startOffset":4,
             "end":"/div[3]/div[2]/blockquote/p",
             "endOffset":19}],
           "quote":"Quote",
           "uri":"http://localhost:8000/committee/meeting/4163/"}
         
        res = self.client.post(reverse('annotation-handler'), data2)
        print res
        self.assertEqual(201, res.status_code)
        self.assertEqual(1, Annotation.objects.count())
