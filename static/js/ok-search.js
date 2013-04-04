/* =============================================================
 * OpenKnesst search completions. Base on bootstrap's
 * Type ahead widget
 * ============================================================ */


!function($){

  "use strict"; // jshint ;_;


 /* TYPEAHEAD PUBLIC CLASS DEFINITION
  * ================================= */

  var _okItems = {}, // defined here and can be resused by all search field, prevent multiple requests
      _requesting = false;

  var OKSearch = function (element, options) {
    this.$element = $(element)
    this.options = $.extend({}, $.fn.oksearch.defaults, options)
    this.matcher = this.options.matcher || this.matcher
    this.highlighter = this.options.highlighter || this.highlighter
    this.updater = this.options.updater || this.updater
    this.source = this.options.source || this.sourceItems;

    this.$menu = $(this.options.menu)

    this.shown = false
    this.listen()

    // #TODO hardcoded for now
    this.searchFor = {
        member: {
            url: '/api/v2/member/',
			title: gettext('Members'),
            render: function(item) {
                var el = $('<li class="search-member"><a></a></li>');
                el.find('a')
                    .attr('href', item.absolute_url)
                    .text(item.name)
                    .append($('<img>').attr('src', item.img_url));
                return el;
            }
        },
		party: {
            url: '/api/v2/party/',
			title: gettext('Parties'),
            render: function(item) {
                var el = $('<li class="search-party"><a></a></li>');
                el.find('a').attr('href', item.absolute_url).text(item.name);
                return el;
            }
		},
        tag: {
            url: '/api/v2/tag/',
			title: gettext('Tags'),
            render: function(item) {
                var el = $('<li class="search-tag"><a></a></li>');
                el.find('a').attr('href', item.absolute_url).text(item.name);
                return el;
            }
        }, 
        committee: {
            url: '/api/v2/committee/',
			title: gettext('Committees'),
            render: function(item) {
                var el = $('<li class="search-committee"><a></a></li>');
                el.find('a').attr('href', item.absolute_url).text(item.name)
                return el;
            }
        }
    }
  }

  OKSearch.prototype = {

    constructor: OKSearch

  , sourceItems: function() {
        var that = this;

        if (_requesting || !$.isEmptyObject(_okItems)) return;
        _requesting = true;
    
        var params = $.map(this.searchFor, function(value) { return $.get(value.url) })

        $.when.apply(this, params)
         .done(function() {
             var count = 0,
                 res = arguments;
             $.each(that.searchFor, function(key, value) {
                 _okItems[key] = res[count][0].objects;
                 count++;
             })
             that.lookup();
         })
         .always(function() {_requesting = false;})

        return this;
    }

  , select: function () {
      var $el = this.$menu.find('.active');

	  // no selection ? submit the form
	  if ($el.length === 0) {
		  this.$element.closest('form').submit();
		  return;
	  }

      var val = $el.attr('data-value'),
          url = $el.find('a').attr('href');

          window.location.href = url;
    }

  , updater: function (item) {
      return item
    }

  , show: function () {
      var pos = $.extend({}, this.$element.position(), {
        height: this.$element[0].offsetHeight
      })

      this.$menu
        .insertAfter(this.$element)
        .css({
          top: pos.top + pos.height
        , left: pos.left
        })
        .show()

      this.shown = true
      return this
    }

  , hide: function () {
      this.$menu.hide()
      this.shown = false
      return this
    }

  , lookup: function (event) {
      this.query = this.$element.val()

      if (!this.query || this.query.length < this.options.minLength) {
        return this.shown ? this.hide() : this
      }

      if ($.isEmptyObject(_okItems)) {
        if (!_requesting) {this.source()};
      }

      return (!$.isEmptyObject(_okItems)) ? this.process() : this
    }

  , process: function () {
      var that = this,
          items = {},
          matched = 0;
      

      $.each(that.searchFor, function(key, value) {
          items[key] = $.grep(_okItems[key], function (item) {
              return that.matcher(item)
          });
          matched += items[key].length;
          items[key] = items[key].slice(0, that.options.items);
      })

      if (!matched) {
        return this.shown ? this.hide() : this
      }

      return this.render(items).show()
    }

  , matcher: function (item) {
      return ~item.name.toLowerCase().indexOf(this.query.toLowerCase())
    }

  , highlighter: function (item) {
      var query = this.query.replace(/[\-\[\]{}()*+?.,\\\^$|#\s]/g, '\\$&')
      return item.replace(new RegExp('(' + query + ')', 'ig'), function ($1, match) {
        return '<strong>' + match + '</strong>'
      })
    }

  , render: function (items) {
      var that = this,
          elements = new Array();

      $.each(items, function(key, values) {
          if (values.length) {
            elements.push($('<li class="nav-header"></li>').text(that.searchFor[key].title));
            $.each(values, function(idx, item) {
                var i = that.searchFor[key].render(item),
                	highlighted = that.highlighter(item.name),
                    $a = i.find('a'),
                    $img = $a.find('img');

                $a.html(highlighted).prepend($img);
                elements.push(i[0]);
            });
          }
      })
      
      this.$menu.html(elements)
      return this
    }

  , next: function (event) {
      var active = this.$menu.find('.active').removeClass('active')
        , next = active.nextAll('li:not(.nav-header)')

      if (!next.length) {
        next = $(this.$menu.find('li:not(.nav-header)')[0])
      }
      else {
          next = $(next.get(0));
      }

      next.addClass('active')
    }

  , prev: function (event) {
      var active = this.$menu.find('.active').removeClass('active')
        , prev = active.prevAll('li:not(.nav-header)')

      if (!prev.length) {
        prev = this.$menu.find('li:not(.nav-header)').last()
      }
      else {
          prev = $(prev.get(0));
      }

      prev.addClass('active')
    }

  , listen: function () {
      this.$element
        .on('blur',     $.proxy(this.blur, this))
        .on('keypress', $.proxy(this.keypress, this))
        .on('keyup',    $.proxy(this.keyup, this))

      if (this.eventSupported('keydown')) {
        this.$element.on('keydown', $.proxy(this.keydown, this))
      }

      this.$menu
        .on('click', $.proxy(this.click, this))
        .on('mouseenter', 'li', $.proxy(this.mouseenter, this))
    }

  , eventSupported: function(eventName) {
      var isSupported = eventName in this.$element
      if (!isSupported) {
        this.$element.setAttribute(eventName, 'return;')
        isSupported = typeof this.$element[eventName] === 'function'
      }
      return isSupported
    }

  , move: function (e) {
      if (!this.shown) return

      switch(e.keyCode) {
        case 9: // tab
        case 13: // enter
        case 27: // escape
          e.preventDefault()
          break

        case 38: // up arrow
          e.preventDefault()
          this.prev()
          break

        case 40: // down arrow
          e.preventDefault()
          this.next()
          break
      }

      e.stopPropagation()
    }

  , keydown: function (e) {
      this.suppressKeyPressRepeat = ~$.inArray(e.keyCode, [40,38,9,13,27])
      this.move(e)
    }

  , keypress: function (e) {
      if (this.suppressKeyPressRepeat) return
      this.move(e)
    }

  , keyup: function (e) {
      switch(e.keyCode) {
        case 40: // down arrow
        case 38: // up arrow
        case 16: // shift
        case 17: // ctrl
        case 18: // alt
          break

        case 9: // tab
        case 13: // enter
          if (!this.shown) return
          this.select()
          break

        case 27: // escape
          if (!this.shown) return
          this.hide()
          break

        default:
          this.lookup()
      }

      e.stopPropagation()
      e.preventDefault()
  }

  , blur: function (e) {
      var that = this
      setTimeout(function () { that.hide() }, 150)
    }

  , click: function (e) {
      e.stopPropagation()
      e.preventDefault()
      this.select()
    }

  , mouseenter: function (e) {
      this.$menu.find('.active').removeClass('active')
      $(e.currentTarget).addClass('active')
    }

  }


  /* TYPEAHEAD PLUGIN DEFINITION
   * =========================== */

  var old = $.fn.oksearch

  $.fn.oksearch = function (option) {
    return this.each(function () {
      var $this = $(this)
        , data = $this.data('oksearch')
        , options = typeof option == 'object' && option
      if (!data) $this.data('oksearch', (data = new OKSearch(this, options)))
      if (typeof option == 'string') data[option]()
    })
  }

  $.fn.oksearch.defaults = {
    source: null
  , items: 5
  , menu: '<ul class="oksearch dropdown-menu nav nav-list"></ul>'
  , minLength: 1
  }

  $.fn.oksearch.Constructor = OKSearch


 /* TYPEAHEAD NO CONFLICT
  * =================== */

  $.fn.oksearch.noConflict = function () {
    $.fn.oksearch = old
    return this
  }


 /* TYPEAHEAD DATA-API
  * ================== */

  $(document).on('focus.oksearch.data-api', '[data-provide="oksearch"]', function (e) {
    var $this = $(this)
    if ($this.data('oksearch')) return
    e.preventDefault()
    $this.oksearch($this.data())
  })

}(window.jQuery);
