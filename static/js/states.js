var Members = function ()  {
    var i = new BreadCrumb();
    i.name = 'member';
	i.one_liner = function (item) {
		return [item.name].join("\t");
	};
    i.div_view = function (item) { 
        return [item.start_date, item.end_date].join('\t');
    };
    return i;
};

var PastVotes = function ()  {
    var i = new BreadCrumb();
    i.name = 'vote';
	i.one_liner = function (item) {
		return item.title;
	};
    i.div_view = function (item) { 
        return [item.time, item.summary, '<a href="' + item.full_text_url + '">full text</a>'].join('\t');
    };

    return i;
};

$(document).ready (function () {
    jsr(Members);
});
