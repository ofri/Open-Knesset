var partyMap;
var memberMap;
var memberIdArray;
var partyNameArray;
var slimData;
var slimDataMap;
var stringImageListForDownload;

var OKnessetParser = new function(){
	var callbackFunction = null;

	function parseMembers(members){
	    memberMap = {};
	    memberIdArray = new Array();
	    stringImageListForDownload = "";

	    Ext.each(members, function(value, index){
	        // TODO - do not add memebers that are not "current"
	        if (typeof value == "undefined") {
	            console.log("member index " + index + " is undefined.");
	            return;
	        }

			// Filter non active members
			if (value.roles.indexOf('לשעבר') != -1){
				console.log("excluding " + value.name);
				return;
			}

			console.log(value.roles);
			if (value.roles === "יו\"ר ועדת הפירושים") {
				value.roles = "יושב ראש הכנסת";
			}

			// filter out bills with stage 2 or less
			for (var i = 0; i < value.bills.length; i++) {
				if (parseInt(value.bills[i].stage) < 2) {
					value.bills.splice(i,1);
					i--;
				}

			}

	        memberIdArray.push(value);
	        memberMap[value.id] = value;

//			Ext.each(value.bills, function(index, value){
//				if (parseInt(value.stage) < 2){
//
//				}
//			});
	        partyMap[value.party].members.push(value);

	        var slimMember = {
	            name: value.name
	        };
	        slimDataMap[value.party].members.push(slimMember);

	       // stringImageListForDownload += "-O\nurl = \"" + value.img_url + "\"\n";
	    });

		// sort members
		Ext.iterate(partyMap, function(key, value) {
			console.log("party id " + value.id + " for member sort exists? " + (typeof sortedMembers[value.id]));
			if (typeof sortedMembers[value.id] != "undefined") {
				value.members.sort(function(member1, member2){
					return compareMembers(member1, member2, value.id);
				});
			}
		});

		Ext.each(slimData, function(value, index) {
			console.log("slim party id " + value.id + " for member sort exists? " + (typeof sortedMembers[value.id]));
			if (typeof sortedMembers[value.id] != "undefined") {
				value.members.sort(function(member1, member2){
					return compareMembers(member1, member2, value.id);
				});
			}
		});

	}

	function compareMembers(member1, member2, partyId){
		var idx1 = indexInArray(member1.name, sortedMembers[partyId]);
		var idx2 = indexInArray(member2.name, sortedMembers[partyId]);
		var compareValue = 0;
		if (idx1 < idx2) {
			compareValue = -1;
		} else if (idx1 > idx2){
			compareValue = 1;
		}

		return compareValue;
	}

	function indexInArray(str, arr){
		for (var i = 0 ; i < arr.length ; i++)	{
			if (str == arr[i]) {
				return i;
			}
		}

		console.log("!! member " + str + " cannot be found in sortedMembers array");
		return -1;
	}

	function onMemberComplete(options, success, response){
	    console.log("onMemeberComplete " + success);
	}

	function onMemberFailure(result, request){
	    console.warn("onMemberFailure " + result.responseText);
	}

	function storeMembers(result, request){
	    console.log("storeMembers");
	    parseMembers(JSON.parse(result.responseText));


		callbackFunction(partyNameArray, slimData);
	}

	// ***
	// Parties
	// ***
	function parseParties(parties){
	    partyNameArray = parties;
	    partyMap = {};
	    slimData = new Array();
	    slimDataMap = {};
		Ext.each(parties, function(value, index){
	        var slimParty = {
	            name: value.name,
				id : value.id,
	            members: []
	        };
	        slimDataMap["" + value.name] = slimParty;
	        slimData.push(slimParty);
	        partyMap["" + value.name] = value;
	        partyMap["" + value.name].members = new Array();
	    });
	}

	function onPartyComplete(options, success, response){
	    console.log("onPartyComplete " + success);
	}

	function onPartyFailure(result, request){
	    console.warn("onPartyFailure");
	}

	function storeParties( result, request){
	    console.log("storeParties");
	    parseParties(JSON.parse(result.responseText));

		Ext.Ajax.request({
		    url: 'http://www.oknesset.org/api/member/',
			success : storeMembers,
			timeout : 60000,
			failure : onMemberFailure,
		    callback: onMemberComplete
		});
	}

/********
 * sorted members by party
 */

var sortedMembers =  {
  	"9" : ["ג`מאל זחאלקה","סעיד נפאע","חנין זועבי","עבאס זכור"],
	"7" : ["אליהו ישי","אריאל אטיאס","יצחק כהן","אמנון כהן","משולם נהרי","יעקב מרגי","דוד אזולאי","יצחק וקנין","נסים זאב","חיים אמסלם","אברהם מיכאלי","מזור בהיינה","רפאל כהן","עמי ביטון","אורן מלכה","רפאל מלאכי","חיים אלי רואש","גרשון לוי","דוד גבאי","פינחס צברי","צבי זאב חי חקוק","יצחק אבידני","בנימין אלחרר","חגי חדד","עופר כרדי","יצחק סולטן","צבי אסולין","גבריאל רחמים"],
	"11" : ["חיים אורון","אילן גילאון","ניצן הורוביץ","זהבה גלאון","משה רז","אבשלום וילן","טליה ששון","צביה גרינפלד","צלי רשף","עיסווי פריג`","מיכל רוזין","אברהם מיכאלי","מזור בהיינה","רפאל כהן","עמי ביטון","אורן מלכה","רפאל מלאכי","חיים אלי רואש"],
	"10" : ["אברהים צרצור","אחמד טיבי","טלב אלסאנע","מסעוד גנאים","טלב אבו עראר","גסאן עבדאללה","באסל דראושה","יוסף פדילה","איעתמאד קעדאן","מחמוד מואסי"],
	"8" : ["מוחמד ברכה","חנא סוייד","דב חנין","עפו אגבאריה","עאידה תומא -סלימאן","נורית חג`אג`","דח`יל אבו זייד (חאמד)","עבדאללה אבו מערוף","פדרו גולדפרב","מהא אלנקיב"],
	"1" : ["יעקב (כצל`ה) כ”ץ","אורי יהודה אריאל","אריה אלדד","מיכאל בן-ארי","אורי בנק","אלון דוידי","אברהם רט","רון ברימן","בצלאל סמורטיף","אילן כהן","שבתאי ויינטראוב","אהד ברט","אמיתי כהן","משה כהן","נצר מנצור","חוה טבנקין"],
	"4" :["יעקב ליצמן","משה גפני","מאיר פרוש","אורי מקלב","מנחם אליעזר מוזס","ישראל אייכלר","מנחם כרמל","יעקב אשר גוטרמן","אברהם יוסף לייזרזון","שמעון חדד","יהושע מנחם פולק","יעקב אשר","חיים מאיר כץ","אריה צבי בוימל","אפרים וובר","אליהו מרדכי קרליץ","יוסף יהושע קופרברג","אברהם רובינשטיין","יוסף דייטש","יצחק זאב פינדרוס"],
	"12" : ["דניאל הרשקוביץ","זבולון אורלב","אורי אורבך","ניסן סולומינסקי","שר שלום ג`רבי","לאורה מינקה","שלה רוזנק-שורשן","אברהם נגוסה","אופיר יחזקאל כהן","אלישיב רייכנר","אהרון אטיאס","יפה פרץ","יעקב סולר","יהודה דה-פריידיגר","אברהם מועלם","יורם כמיסה","אליעזר אויירבך","משה אהרון פת","אבי סילימן"],
	"5" : ["אביגדור ליברמן","עוזי לנדאו","סטס מיסז`ניקוב","יצחק אהרונוביץ","סופה לנדבר","אורלי לוי-אבקסיס","דניאל אילון","דוד רותם","אנסטסיה מיכאלי","פאינה (פניה) קירשנבאום","רוברט אילטוב","חמד עמאר","משה מוץ מטלון","ליה שמטוב","אלכס מילר","יצחק סלבין","סמדר בת אדם לויטן"],
	"2" : ["בנימין נתניהו","גדעון סער","גלעד ארדן","ראובן ריבלין","זאב בנימין  בגין","משה כחלון","סילבן שלום","משה יעלון","יובל שטייניץ","לאה נס","ישראל כץ","יולי - יואל אדלשטיין","לימור לבנת","חיים כץ","יוסי פלד","מיכאל איתן","דן מרידור","ציפי חוטובלי","גילה גמליאל","זאב אלקין","יריב לוין","ציון פיניאן","איוב קרא","דני דנון","כרמל שאמה","אופיר אקוניס","מירי רגב","אללי אדמסו","יצחק (איציק) דנינו","דוד אבן צור","קטי (קטרין) שיטרית","קרן ברק","שגיב אסולין","בועז ישראל העצני","גיא חנן יפרח","משה זלמן פייגלין","מיכאל רצון","אהוד יצחק יתום","שלום לרנר","הילה -אסנת מארק","אסף חפץ","יחיאל (מיכאל) לייטר","דניאל בנלולו","עוזי דיין","אדמונד חסין","פנינה רוזנבלום סימונוב","זאב -יאיר ז`בוטינסקי","מיכאל קליינר","נורית (יונה) קורן","סמיר קאידבה","יוסף- ספי ריבלין","דוד מנע","יחיאל- מיכאל חזן","משה שלמה מוסקל","אליהו גבאי","גיל חדד","אלי אבידר","חמי - נחמיה דורון","מיכל - דאה כפרי - ירדני","אתי תלמי","בלהה ניסנסון","ריכאד חיאדין","אפריים אבן","איילה שטגמן","מרים ארז","עטאף קרינאוי","יוסף בדש","רפעאת אסדי","חאתם חסון","צפורה בר","יאנה זהר","שלמה ציביון","שוש- שושנה הלוי","גיל-עד זגר","גבריאל אביטל","שאול אדם","פרוספר אזוט"],
	"3" : ["אהוד ברק","יצחק הרצוג","אופיר פינס-פז","אבישי ברוורמן","שלי יחימוביץ","מתן וילנאי","איתן כבל","בנימין (פואד) בן-אליעזר","יולי תמיר","עמיר פרץ","דניאל בן-סימון","שלום שמחון","אורית נוקד","עינת וילף","ראלב מג`אדלה","שכיב שנאן","יורם מרציאנו","לאון ליטינצקי","קולט אביטל","משה סמיה","יוסף סולימני","אריק חדד","אבי חזקיהו","מנחם ליבוביץ","עפר קורנפלד","יואב חי","עזי נגר","בנימין לוין","אבי שקד","נאדיה חילו","שמעון שיטרית","יריב אופנהיימר","רות דיין מדר","אסתר ביתן","דנה אורן","אמנון זילברמן","ואפד קבלאן","יעקב רומי","מיקי מיכאל גולד","מאיר וייס","ולדימיר סברדלוב","מעין אמודאי","פייצל אלהזייל","ניקולא מסעד","זאב-ולוולה שור","אהרון קראוס","אמנון זך","מוטי ששון","חנה מרשק","הדסה חנה רוסו","אלי אורן","דב צור","סימון אלפסי","יוסף ונונו","שייע יצחק ישועה","שלומי וייזר","מישל שלום חלימי","יוסי ארבל","לאה יונה גבע","ארז שלמה אבו","יובל אדמון","דקל דוד עוזר","יהונתן מאייר עוזר","אהרון רוני כהן","משה פרנקל","אדית אבוד","יהודית הרן","אליהו סדן","רבקה בית הלחמי","אבינועם טובים","אברהם הצמרי","רמי אזרן","שמעון קמרי","שרה גנסטיל","מוטי דותן","יהודית אוליאל","נורית לוי","יהודה שביט","דניאל עטר"],
	"6" : ["ציפי לבני","שאול מופז","דליה איציק","צחי הנגבי","רוני בר-און","זאב בוים","מאיר שטרית","רוחמה אברהם בלילא","אבי (משה) דיכטר","מרינה סולודקין","יואל חסון","גדעון עזרא","יעקב אדרי","אלי אפללו","זאב בילסקי","רונית תירוש","חיים רמון","נחמן שי","שלמה (נגוסה) מולה","רוברט טיבייב","מגלי והבה","רחל אדטו","יוחנן פלסנר","שי חרמש","ישראל חסון","אריה ביבי","עתניאל שנלר","אורית זוארץ","יוליה שמאלוב ברקוביץ`","נינו אבסדזה","אבנר ברזאני","דורון אביטל","אברהם דואן","יובל צלנר","אכרם חסון","אחמד דבאח","דוד טל","דימטרי רוסינסקי","אהרון רוני בן חמו","איתן שלום","נחמיה רייבי","גליה אלבין","שלמה יצחק","מושון גבאי","וליד שנאן","מוטי מרדכי אלפריח","יורי בוצ'רוב","אלי בן מנחם","עדי שטרנברג","חליל קאסם","אתי אסתר לבני","גילה אוגניה וקסמן","סימה נבון","משה קונפורטי","לזר קפלון","מרינה קונצביה","סוריה נוג'ידאת","אבי אברהם וידרמן","עודד אליגון","אופיר מילר","יצחק רגב","יוסי מנור","שבתאי בירן","איזיק פיטרמן","אורי נאמן","שלמה אברמוביץ","חוסיין סלימאן","ציפי גורדין","רומי זונדר כסלו","שרון מנחם בר און","יהודה סקר","יניב קזז","צבי אדנייב -עדי","רמי פרדרו","נסים הדס","מאיר דורון","שלמה טל","ענת זיו","דוד אזולאי"]
};

// סיעת העצמאות היא בעצם סיעת העבודה
sortedMembers["13"] = sortedMembers["3"];
/*********
 * API function
 */
	this.loadData = function(callback){

		callbackFunction = callback;

		Ext.Ajax.request({
		    url: 'http://www.oknesset.org/api/party/',
			success : storeParties,
			failure : onPartyFailure,
		    callback: onPartyComplete
		});

	}

}
