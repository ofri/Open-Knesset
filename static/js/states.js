var Members = function ()  {
        var i = new BreadCrumb();
        i.name = 'member';
	i.one_liner = function (item) {
		return [item.name, item.start_date, item.end_date].join("\t");
	};
        return i;
    };
var PastVotes = function ()  {
        var i = new BreadCrumb();
        i.name = 'vote';
	i.one_liner = function (item) {
		return [item.time, item.title].join("\t");
	};
        return i;
    };
$(document).ready (function () {
    jsr(Members);
});
