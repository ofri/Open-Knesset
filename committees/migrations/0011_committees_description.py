# encoding: utf-8
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

DESCS = {u'ועדת הכנסת': '''תקנון הכנסת ועניינים הנובעים ממנו; חסינות חברי הכנסת ובקשות לנטילתה; סדרי הבית; המלצות על הרכב הוועדות הקבועות והוועדות לעניינים מסויימים, ויושבי-ראש שלהן; תיחום ותיאום הוועדות; העברת בקשות המוגשות לכנסת מן הציבור ליושב-ראש הכנסת או לוועדות המתאימות; דיון בתלונות על חברי הכנסת; תשלומים לחברי הכנסת; דיון בבקשות ובעניינים שאינם נוגעים לשום ועדה או שלא נכללו בתפקידי ועדה אחרת.
''', u'ועדת העלייה, הקליטה והתפוצות': '''עלייה; קליטה; הטיפול ביורדים; חינוך יהודי וציוני בגולה; מכלול הנושאים הקשורים בעניינים אלה והנמצאים בתחום טיפולו של המוסד לתיאום בין ממשלת ישראל לבין ההסתדרות הציונית העולמית ובין ממשלת ישראל לבין הסוכנות היהודית.
''', u'ועדת הפנים והגנת הסביבה': '''שלטון מקומי; בניין ערים; כניסה לישראל ומרשם האוכלוסין; אזרחות; עיתונות ומודיעין; עדות; ארגון הדתות של יהודים ושל לא-יהודים; משטרה ובתי-הסוהר; איכות הסביבה.
''', u'ועדת החוקה, חוק ומשפט': '''דיוני ועדת החוקה חוק ומשפט בהצעות חקיקה והכנתן של הצעות החוק לשלבי קריאה ראשונה, שניה ושלישית במליאת הכנסת
''', u'ועדת החינוך, התרבות והספורט': '''חינוך; תרבות; מדע; אמנות; שידור; קולנוע; תרבות הגוף.
''', u'ועדה לענייני ביקורת המדינה': '''דיון בדוחות מבקר המדינה ונציב תלונות הציבור; סמכויות על-פי חוק מבקר המדינה וחוקים אחרים; מעמדם וסמכויותיהם של מבקרים פנימיים; הוועדה לענייני ביקורת המדינה רשאית להורות על מינוי ועדת חקירה ממלכתית בעקבות דיון בדוח מבקר המדינה.
''', u'ועדת  המדע  והטכנולוגיה': '''מדיניות מחקר ופיתוח אזרחי בישראל, טכנולוגיות מתקדמות, מחקר ופיתוח סביבתי, מחקר מדעי באקדמיה ישראלית למדעים, מחקר מדעי שלא במוסדות להשכלה גבוהה, מכוני מחקר, מדענים ראשיים של כלל משרדי הממשלה, מועצה לאומית למחקר ופיתוח, קרנות מחקר, מידע ומיחשוב.
''', u'ועדת הכספים': '''תקציב המדינה; מסים לכל סוגיהם; מכס ובלו; מלוות; ענייני מטבע חוץ; בנקאות ושטרי כסף; הכנסות והוצאות המדינה.
''', u'ועדת העבודה, הרווחה והבריאות': '''עבודה; ביטחון סוציאלי; לרבות מערכת הבטחת הכנסה; המוסד לביטוח לאומי; בריאות; סעד; שיקום; נכים ושיקומם; לרבות נכי צה”ל ומשפחות נפגעי מלחמה וכן נפגעים אחרים; עבריינים צעירים; גמלאות ותגמולים; חוקת התשלומים לחיילים ולמשפחותיהם.
''', u'ועדה לקידום מעמד האישה': '''קידום מעמד האשה לקראת שוויון בייצוג; בחינוך ובמעמד האישי, וכן למניעת אפליה בשל מין או נטייה מינית בכל התחומים; להקטנת פערים בכלכלה ובשוק העבודה ולמאבק באלימות כלפי נשים.
''', u'ועדה מיוחדת לבעיית העובדים הזרים': '''היתרי הכניסה לישראל והשהייה בה עובדים זרים חוקיים ובלתי חוקיים מעצר וגירוש עובדים זרים בלתי חוקיים היתרי עבודה ושילובם בענפי הבנין, הסיעוד, החקלאות, התעשיה ומסעדנות תנאים סוציאלים ובכלל זה: בריאות, רווחה, חינוך, טיפול הרשויות, טיפול העמותות ועוד.
הערה: עבודת הוועדה מתמקדת בכל תחומי עיסוקם, הן התנאים הסוציאלים והחברתיים בהם הם חיים, הן לגבי העובדים החוקיים והן לגבי העובדים הלא חוקיים.
''', u'ועדת משנה למאבק בסחר בנשים': '''בדיקת תופעת הסחר בנשים בארץ בנושאים הבאים:
1. היקף התופעה וממדיה בישראל;
2. התנאים בהם מוחזקות הנשים על-ידי ”מעבידיהן”;
3. התנאים בהם מוחזקות הנשים לצורכי חקירה (תנאי מעצר);
4. המצב החוקי בישראל לגבי סחר בבני אדם והתיקונים הנדרשים;
הוועדה תקבע את סדרי עבודתה ודיוניה, תיעזר בחומרים שיונחו על שולחנה ובארגונים וולונטריים ובינלאומיים. בגמר עבודתה תגיש הוועדה דין וחשבון על תוצאות חקירתה והמלצותיה.
''', u'ועדה מיוחדת לפניות הציבור': ''' סמכויות הוועדה:
1. טיפול ומתן מענה שוטף לפניות הציבור שמגיעות לוועדה מאזרחים וארגונים שונים.
2. קיום קשר שוטף עם משרדי הממשלה ועם נציגי פניות ציבור בגופים שונים, תוך כדי הבטחת זכויותיהם וסמכויותיהם לטיפול בפניות הציבור במוסדותיהם.
3. הסדרת נושא הטיפול בפניות הציבור במוסדות הממשלתיים והציבוריים לשם קביעת נורמות טיפול אחידות ככל האפשר בין כל הגופים שעוסקים בנושא.
4. שמירה והגנה על מקבלי שירותים ציבוריים.
5. יצירת שיתוף פעולה עם משרדי הממשלה וגורמים שונים בניסיון להיטיב את השירות הניתן לאזרח.
6. קיום דיונים בנושאים מגוונים הנוגעים למצוקות הפרט, להגנת הצרכן ומקבלי השירותים הציבוריים.
''', u'ועדה לזכויות הילד': '''הגנה על הילדים וקידום מעמד הילדים ובני הנוער, במטרה לממש את זכויותיהם ברוח האמנה הבינלאומית לזכויות הילד, לרבות מימוש העקרונות של טובת הילד, אי-אפליה, הזכות להתפתחות בתנאים נאותים, וזכות של ילדים בני נוער להשמיע את דעתם ולהשתתף בעניינים הנוגעים בהם.
''', u'ועדה מיוחדת למאבק בנגע הסמים': '''טיפול מקיף בבעית הסמים במדינת ישראל; פיקוח על הרשויות העוסקות ומטפלות בכל נושא הקשור לנושא הסמים או הנובע ממנו; לרבות הרשויות המטפלות במניעה, אכיפה, תביעה, שפיטה, טיפול ושיקום; טיפול בכל הבעיות בחברה הישראלית הנובעות מהתמכרותם של אנשים לסם מסוכן, העבירות המבוצעות בשל הדחף לסם מסוכן, או מכל היבט אחר הקשור לסמים; שימוש בסמים מסוכנים לצרכים רפואיים.
''', u'ועדת הכלכלה': '''בהתאם לסעיף 13 לתקנון הכנסת, תחומי ענייניה של ועדת הכלכלה הם:
מסחר ותעשיה; אספקה וקיצוב; חקלאות ודיג; תחבור ה - ספנות, תעופה , מערכת הכבישים, תחבורה ציבורית, הרכבת והבטיחות בדרכים; איגוד שיתופי; תכנון ותיאום כלכלי; פיתוח; זיכיונות המדינה ואפוטרופסות על הרכוש; רכוש הערבים הנעדרים; רכוש היהודים מארצות האויב; רכוש היהודים שאינם בחיים; עבודות ציבוריות ובינוי ושיכון.

בהתאם לתחומים האמורים מטפלת ועדת הכלכלה ומקיימת פעילות ענפה, בין היתר, בנושאים אלה:
הצרכנות והגנת הצרכן; האנרגיה והתשתיות - גז (גפ"מ), גז טבעי, דלק וחשמל; התקשורת - דואר, טלפוניה נייחת וניידת, שידורי טלוויזיה ורדיו; הבנקאות למשקי הבית; התיירות; מינהל מקרקעי ישראל; מים וביוב; זכות יוצרים ובית דין לתמלוגים; הגבלים עסקיים; הפיקדון על מכלי המשקה ותאגיד המחזור; הגבלות העישון ופרסום מוצרי הטבק.
'''}

class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."

        for c in orm.Committee.objects.all():
            if c.name in DESCS:
                c.description = DESCS[c.name]
                c.save()

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
        'committees.committee': {
            'Meta': {'object_name': 'Committee'},
            'chairpersons': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'chaired_committees'", 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'committees'", 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'replacements': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'replacing_in_committees'", 'symmetrical': 'False', 'to': "orm['mks.Member']"})
        },
        'committees.committeemeeting': {
            'Meta': {'ordering': "('-date',)", 'object_name': 'CommitteeMeeting'},
            'committee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'meetings'", 'to': "orm['committees.Committee']"}),
            'date': ('django.db.models.fields.DateField', [], {}),
            'date_string': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mks_attended': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'committee_meetings'", 'symmetrical': 'False', 'to': "orm['mks.Member']"}),
            'protocol_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'src_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'topics': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'votes_mentioned': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'committee_meetings'", 'blank': 'True', 'to': "orm['laws.Vote']"})
        },
        'committees.protocolpart': {
            'Meta': {'object_name': 'ProtocolPart'},
            'body': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'header': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'meeting': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'parts'", 'to': "orm['committees.CommitteeMeeting']"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'speaker': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'protocol_parts'", 'null': 'True', 'to': "orm['persons.Person']"})
        },
        'committees.topic': {
            'Meta': {'object_name': 'Topic'},
            'committees': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['committees.Committee']", 'symmetrical': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'editors': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'editing_topics'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'meetings': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': "orm['committees.CommitteeMeeting']", 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'rating_score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'rating_votes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'what': ('django.db.models.fields.TextField', [], {}),
            'when': ('django.db.models.fields.DateTimeField', [], {}),
            'where': ('django.db.models.fields.TextField', [], {}),
            'which_pk': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'which_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'event_for_event'", 'null': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'who': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['persons.Person']", 'symmetrical': 'False'})
        },
        'laws.vote': {
            'Meta': {'ordering': "('-time', '-id')", 'object_name': 'Vote'},
            'against_party': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'controversy': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'full_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'full_text_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'importance': ('django.db.models.fields.FloatField', [], {'default': '0.0'}),
            'meeting_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'src_url': ('django.db.models.fields.URLField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'summary': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {}),
            'time_string': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'vote_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'votes': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'votes'", 'blank': 'True', 'through': "orm['laws.VoteAction']", 'to': "orm['mks.Member']"}),
            'votes_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'laws.voteaction': {
            'Meta': {'object_name': 'VoteAction'},
            'against_coalition': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'against_opposition': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'against_own_bill': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'against_party': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'vote': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['laws.Vote']"})
        },
        'links.link': {
            'Meta': {'object_name': 'Link'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'content_type_set_for_link'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'link_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['links.LinkType']", 'null': 'True', 'blank': 'True'}),
            'object_pk': ('django.db.models.fields.TextField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '1000'})
        },
        'links.linktype': {
            'Meta': {'object_name': 'LinkType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '200'})
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
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
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
        'mks.membership': {
            'Meta': {'object_name': 'Membership'},
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'member': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Member']"}),
            'party': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['mks.Party']"}),
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
        'persons.person': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Person'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mk': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'person'", 'null': 'True', 'to': "orm['mks.Member']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'titles': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'persons'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['persons.Title']"})
        },
        'persons.title': {
            'Meta': {'object_name': 'Title'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'})
        },
        'planet.blog': {
            'Meta': {'ordering': "('title', 'url')", 'object_name': 'Blog'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '255', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'unique': 'True', 'max_length': '1024', 'db_index': 'True'})
        },
        'tagging.tag': {
            'Meta': {'ordering': "('name',)", 'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
        },
        'tagging.taggeditem': {
            'Meta': {'unique_together': "(('tag', 'content_type', 'object_id'),)", 'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'items'", 'to': "orm['tagging.Tag']"})
        }
    }

    complete_apps = ['committees']
