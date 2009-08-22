var Members = function ()  {
        var i = new BreadCrumb();
        i.name = 'member';
	i.one_liner = function (item) {
		return item.name + " " + item.start_date + " - " + item.end_date;
	};
        return i;
    };
$(document).ready (function () {
    jsr(Members);
});
