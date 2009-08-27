var NAV_SUFFIX = '#nav-';

var Members = function ()  {
    var i = new BreadCrumb();
    i.name = 'member';
    i.nav_id = NAV_SUFFIX + 'members';
    i.one_liner = function (item) {
        return [item.name, item.start_date, item.end_date].join("\t");
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
    return i;
};

$(document).ready (function () {
    jsr(Members);
});
