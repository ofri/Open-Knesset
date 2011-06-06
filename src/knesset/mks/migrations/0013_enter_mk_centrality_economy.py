# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

from knesset.mks.models import Member

class Migration(DataMigration):

    def forwards(self, orm):
        mks = """אבי (משה) דיכטר
אביגדור ליברמן
אבישי ברוורמן
אברהים צרצור
אברהם מיכאלי
אהוד ברק
אופיר אקוניס
אופיר פינס-פז
אורי אורבך
אורי יהודה אריאל
אורי מקלב
אורית זוארץ
אורית נוקד
אורלי לוי-אבקסיס
אחמד טיבי
איוב קרא
אילן גילאון
איתן כבל
אלי אפללו
אליהו ישי
אלכס מילר
אמנון כהן
אנסטסיה מיכאלי
אריאל אטיאס
אריה אלדד
אריה ביבי
בנימין (פואד) בן-אליעזר
בנימין נתניהו
ג`מאל זחאלקה
גדעון סער
גדעון עזרא
גילה גמליאל
גלעד ארדן
דב חנין
דוד אזולאי
דוד רותם
דליה איציק
דן מרידור
דני דנון
דניאל אילון
דניאל בן-סימון
דניאל הרשקוביץ
זאב אלקין
זאב בוים
זאב בילסקי
זאב בנימין  בגין
זבולון אורלב
חיים אורון
חיים אמסלם
חיים כץ
חיים רמון
חמד עמאר
חנא סוייד
חנין זועבי
טלב אלסאנע
יואל חסון
יובל שטייניץ
יוחנן פלסנר
יולי - יואל אדלשטיין
יולי תמיר
יוליה שמאלוב ברקוביץ`
יוסי פלד
יעקב (כצל`ה) כ”ץ
יעקב אדרי
יעקב ליצמן
יעקב מרגי
יצחק אהרונוביץ
יצחק הרצוג
יצחק וקנין
יצחק כהן
יריב לוין
ישראל חסון
ישראל כץ
כרמל שאמה
לאה נס
ליה שמטוב
לימור לבנת
מאיר פרוש
מאיר שטרית
מגלי והבה
מוחמד ברכה
מיכאל בן-ארי
מירי רגב
מנחם אליעזר מוזס
מסעוד גנאים
מרינה סולודקין
משה גפני
משה יעלון
משה כחלון
משה מוץ מטלון
משולם נהרי
מתן וילנאי
נחמן שי
ניצן הורוביץ
נסים זאב
סופה לנדבר
סטס מיסז`ניקוב
סילבן שלום
סעיד נפאע
עוזי לנדאו
עינת וילף
עמיר פרץ
עפו אגבאריה
עתניאל שנלר
פאינה (פניה) קירשנבאום
צחי הנגבי
ציון פיניאן
ציפי חוטובלי
ציפי לבני
ראובן ריבלין
ראלב מג`אדלה
רוברט אילטוב
רוברט טיבייב
רוחמה אברהם בלילא
רוני בר-און
רונית תירוש
רחל אדטו
שאול מופז
שי חרמש
שלום שמחון
שלי יחימוביץ
שלמה (נגוסה) מולה
מיכאל איתן"""

        mks = mks.split('\n')
        economy = [5,4,8,3,5,8,8,8,8,4,4,7,9,5,3,4,5,6,5,4,6,4,7,4,4,6,7,4,4,8,8,8,5,8,4,6,4,4,8,8,8,7,4,8,8,4,4,7,4,8,None,3,4,4,1,8,8,8,4,8,8,8,4,5,4,4,8,8,5,5,8,9,6,8,8,8,8,4,6,3,3,6,6,4,2,5,2,8,7,6,4,6,8,8,4,5,7,8,3,8,8,5,2,3,3,8,5,6,8,4,4,6,4,7,6,8,8,8,7,5,8,7,5]
        centrality = [6,5,10,7,8,10,10,8,7,6,9,7,7,4,7,5,7,8,5,9,6,8,9,9,6,9,9,9,6,10,7,10,6,10,4,5,9,9,7,8,10,6,9,8,8,9,9,5,9,7,None,5,4,6,4,10,7,8,5,10,8,10,5,6,9,4,7,10,3,6,7,5,6,10,9,8,10,9,7,4,5,5,8,9,4,6,10,7,6,5,9,6,7,10,9,7,9,10,4,8,10,5,6,6,6,7,4,8,10,9,6,7,4,9,6,10,7,7,5,3,10,9,5]
        for (i,m) in enumerate(mks):
            try:
                member = orm.Member.objects.get(name = m)
                member.residence_economy = economy[i]
                member.residence_centrality = centrality[i]
                member.save()
            except orm.Member.DoesNotExist:
                #print 'memer %s not found in db' % m
                pass

    def backwards(self, orm):
        "Write your backwards methods here."


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mks.correlation': {
            'Meta': {'object_name': 'Correlation'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'm1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'m1'", 'to': "orm['mks.Member']"}),
            'm2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'m2'", 'to': "orm['mks.Member']"}),
            'normalized_score': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'not_same_party': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'mks.member': {
            'Meta': {'object_name': 'Member'},
            'area_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'blog': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['planet.Blog']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'current_party': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'members'", 'null': 'True', 'to': "orm['mks.Party']"}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'family_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_children': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'parties': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'all_members'", 'symmetrical': 'False', 'through': "orm['mks.Membership']", 'to': "orm['mks.Party']"}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'place_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'place_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'place_of_residence_lat': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'place_of_residence_lon': ('django.db.models.fields.CharField', [], {'max_length': '16', 'null': 'True', 'blank': 'True'}),
            'residence_centrality': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'residence_economy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year_of_aliyah': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.membership': {
            'Meta': {'object_name': 'Membership'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Party']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.party': {
            'Meta': {'object_name': 'Party'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'number_of_members': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'number_of_seats': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.weeklypresence': {
            'Meta': {'object_name': 'WeeklyPresence'},
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'hours': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"})
        },
        'planet.blog': {
            'Meta': {'object_name': 'Blog'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '200', 'db_index': 'True'})
        }
    }

    complete_apps = ['mks']
