var NAV_SUFFIX = '#nav-';
var DEFAULT_STATE = 'vote';
var DEFAULT_HEADER_AT = "#content-main h1"
var DEFAULT_CONTENT_AT = "#content-main div";

var Pages = {
    'main': new PageObject({
        name : 'main',
        header : gettext('main'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'main',
        has_more : false,
        page_at : DEFAULT_CONTENT_AT }),
    'member' : new PageObject({ 
        name : 'member',
        header : gettext('members'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'members',
        has_more : false,
        page_at : DEFAULT_CONTENT_AT }),
    'vote': new PageObject({
        name : 'vote',
        header : gettext('votes'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'past-votes',
        cls : '<ul id="item-list"></ul>' + 
			  '<a id="more" href="#">'+
				gettext("more") + '</a>',
        more_at : '#more',
        page_at : DEFAULT_CONTENT_AT,
        content_at : '#item-list' }),
    'law-approve': new PageObject({
        name : 'law-approve',
        header : gettext('law-approve'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'law-approve',
        cls : '<ul id="item-list"></ul>' + 
			  '<a id="more" href="#">'+
				gettext("more") + '</a>',
        more_at : '#more',
        page_at : DEFAULT_CONTENT_AT,
        content_at : '#item-list' }),

    'party': new PageObject({
        name : 'party',
        header : gettext('parties'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'parties',
        has_more : false,
        page_at : DEFAULT_CONTENT_AT }),
    'about': new PageObject({
        name : 'about',
        header : gettext('about'),
        header_at: DEFAULT_HEADER_AT,
        nav_id : NAV_SUFFIX + 'about',
        has_more : false,
        page_at : DEFAULT_CONTENT_AT })
};

