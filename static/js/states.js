var NAV_SUFFIX = '#nav-';

var Members = function ()  {
    var i = new BreadCrumb();
    i.name = 'member';
    i.nav_id = NAV_SUFFIX + 'members';
	i.one_liner = function (item) {
		return item.name
	};
    i.div_view = function (item) { 
        return [item.start_date, item.end_date].join('\t');
    };
    return i;
};

var PastVotes = function ()  {
    var i = new BreadCrumb();
    i.name = 'vote';
    i.nav_id = NAV_SUFFIX + 'past-votes';
    i.one_liner = function (item) {
        return [item.time, item.title].join("\t");
    };
    i.div_view = function (item) { 
        return [item.time, item.summary, '<a href="' + item.full_text_url + '">full text</a>'].join('\t');
    };
    return i;
};

var Parties = function ()  {
    var i = new BreadCrumb();
    i.name = 'party';
    i.nav_id = NAV_SUFFIX + 'parties';
	i.one_liner = function (item) {
		return item.name;
	};
    return i;
};

$(document).ready (function () {
    jsr(PastVotes);
});
