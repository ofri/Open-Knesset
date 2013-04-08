# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models


class Migration(DataMigration):

    POSITIONS = (
        ("יולי - יואל אדלשטיין", 12),
        #("אללי אדמסו", 28),
        ("מיכאל איתן", 16),
        ("זאב אלקין", 20),
        ("אופיר אקוניס", 26),
        ("גלעד ארדן", 3),
        ("זאב בנימין  בגין", 5),
        ("גילה גמליאל", 19),
        ("דני דנון", 24),
        ("ציפי חוטובלי", 18),
        ("משה יעלון", 8),
        ("משה כחלון", 6),
        ("חיים כץ", 14),
        ("ישראל כץ", 11),
        ("לימור לבנת", 13),
        ("יריב לוין", 21),
        ("דן מרידור", 17),
        ("לאה נס", 10),
        ("בנימין נתניהו", 1),
        ("גדעון סער", 2),
        ("ציון פיניאן", 22),
        ("איוב קרא", 23),
        ("מירי רגב", 27),
        ("ראובן ריבלין", 4),
        ("כרמל שאמה", 25),
        ("יובל שטייניץ", 9),
        ("סילבן שלום", 7),
        ("דורון אביטל", 32),
        ("נינו אבסדזה", 30),
        ("רוחמה אברהם בלילא", 8),
        ("יעקב אדרי", 13),
        ("דליה איציק", 3),
        ("אריה ביבי", 26),
        ("זאב בילסקי", 15),
        ("רוני בר-און", 5),
        #("אחמד דבאח", 36),
        ("אברהם (אבי) דואן", 33),
        ("אכרם חסון", 35),
        ("ישראל חסון", 25),
        ("שי חרמש", 24),
        ("שאול מופז", 2),
        ("מרינה סולודקין", 10),
        ("יוחנן פלסנר", 23),
        ("יובל צלנר", 34),
        ("נחמן שי", 18),
        ("יוליה שמאלוב ברקוביץ`", 29),
        ("עתניאל שנלר", 27),
        ("רונית תירוש", 16),
        ("יצחק אהרונוביץ", 4),
        ("דניאל אילון", 7),
        ("רוברט אילטוב", 11),
        ("אורלי לוי-אבקסיס", 6),
        ("אביגדור ליברמן", 1),
        ("עוזי לנדאו", 2),
        ("סופה לנדבר", 5),
        ("משה מוץ מטלון", 13),
        ("אנסטסיה מיכאלי", 9),
        ("אלכס מילר", 15),
        ("סטס מיסז`ניקוב", 3),
        ("חמד עמאר", 12),
        ("פאינה (פניה) קירשנבאום", 10),
        ("דוד רותם", 8),
        ("ליה שמטוב", 14),
        ("דוד אזולאי", 7),
        ("אריאל אטיאס", 2),
        ("יצחק וקנין", 8),
        ("נסים זאב", 9),
        ("אליהו ישי", 1),
        ("אמנון כהן", 4),
        ("יצחק כהן", 3),
        ("אברהם מיכאלי", 11),
        ("יעקב מרגי", 6),
        ("משולם נהרי", 5),
        ("בנימין (פואד) בן-אליעזר", 8),
        ("דניאל בן-סימון", 11),
        ("אבישי ברוורמן", 4),
        ("יצחק הרצוג", 2),
        ("שלי יחימוביץ", 5),
        ("איתן כבל", 7),
        ("ראלב מג`אדלה", 15),
        #("יורם מרציאנו", 17),
        ("רחל אדטו", 22),
        ("מגלי והבה", 21),
        ("אורית זוארץ", 28),
        ("יואל חסון", 11),
        ("רוברט טיבייב", 20),
        ("שלמה (נגוסה) מולה", 19),
        ("מאיר שטרית", 7),
        ("אהוד ברק", 1),
        ("עינת וילף", 14),
        ("אורית נוקד", 13),
        ("שלום שמחון", 12),
        ("שכיב שנאן", 16),
        ("ישראל אייכלר", 6),
        ("משה גפני", 2),
        ("יעקב ליצמן", 1),
        ("מנחם אליעזר מוזס", 5),
        ("אורי מקלב", 4),
        ("עפו אגבאריה", 4),
        ("מוחמד ברכה", 1),
        ("דב חנין", 3),
        ("חנא סוייד", 2),
        ("חנין זועבי", 3),
        ("ג`מאל זחאלקה", 1),
        ("סעיד נפאע", 2),
        ("אורי אורבך", 3),
        ("זבולון אורלב", 2),
        ("דניאל הרשקוביץ", 1),
        ("אילן גילאון", 2),
        ("זהבה גלאון", 4),
        ("ניצן הורוביץ", 3),
        ("מסעוד גנאים", 4),
        ("אחמד טיבי", 2),
        ("אברהים צרצור", 1),
        ("אורי יהודה אריאל", 2),
        ("יעקב (כצל`ה) כ”ץ", 1),
        ("אריה אלדד", 3),
        ("מיכאל בן-ארי", 4),
        ("חיים אמסלם", 10),
    )

    def forwards(self, orm):
        "Write your forwards methods here."
        for name, pos in self.POSITIONS:
            member = orm.Member.objects.get(name=name)
            membership = orm.Membership.objects.filter(member=member).order_by('-start_date')[0]

            member.current_position = pos
            member.save()

            membership.position = pos
            membership.save()

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
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
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
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'mks.coalitionmembership': {
            'Meta': {'ordering': "('party', 'start_date')", 'object_name': 'CoalitionMembership'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'coalition_memberships'", 'to': "orm['mks.Party']"}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
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
            'Meta': {'ordering': "['name']", 'object_name': 'Member'},
            'area_of_residence': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'average_monthly_committee_presence': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'average_weekly_presence_hours': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'backlinks_enabled': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'bills_stats_approved': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bills_stats_first': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bills_stats_pre': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'bills_stats_proposed': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'blog': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['planet.Blog']", 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'current_party': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'members'", 'null': 'True', 'to': "orm['mks.Party']"}),
            'current_position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '999', 'blank': 'True'}),
            'current_role_descriptions': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_of_death': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'null': 'True', 'blank': 'True'}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'family_status': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'fax': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_url': ('django.db.models.fields.URLField', [], {'max_length': '200', 'blank': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'db_index': 'True'}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'website': ('django.db.models.fields.URLField', [], {'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'year_of_aliyah': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.memberaltname': {
            'Meta': {'object_name': 'MemberAltname'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'mks.membership': {
            'Meta': {'object_name': 'Membership'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Party']"}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'default': '999', 'blank': 'True'}),
            'start_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'})
        },
        'mks.party': {
            'Meta': {'ordering': "('-number_of_seats',)", 'object_name': 'Party'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
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
            'Meta': {'ordering': "('title', 'url')", 'object_name': 'Blog'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024', 'db_index': 'True'})
        }
    }

    complete_apps = ['mks']
    symmetrical = True
