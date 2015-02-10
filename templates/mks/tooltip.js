{% autoescape off %}
function generateMkFrameSet(elementId) {
  var okURL = "http://{{ site_url }}",
      frameNum = 0;

  function createMkFrame( mkId, width ){
    var mkFrame = document.createElement("iframe");
    mkFrame.src = okURL + "/member/" + mkId + "/embed/";
    mkFrame.style.border =  "0px";
    mkFrame.style.margin =  "3px 0";
    mkFrame.style.width = "414px";
    mkFrame.style.height = "200px";
    // mkFrame.style.height = "100%";
    mkFrame.className = "autoHeight oknesset_frame";
    mkFrame.scrolling = "no";
    mkFrame.id = "mkFrame_"+frameNum;
    frameNum++;
    return mkFrame;
  }
  jQuery(document).ready( function () {
    var re = RegExp("{{ re }}", "g"),
        mks_by_name = {{ mks_by_name }};

    /* a two pass modifier - first create the span than add the mk_id
    $(selector).each(function (i, el) {
      $(el).html($(el).html().replace(re, '<span class="oknesset_mk">$&</span>'));
    })
     */
    findAndReplaceDOMText(document.getElementById(elementId), {
        find: re,
        replace: function (portion, match) {
          var node = document.createElement('span');
          node.innerHTML = portion.text;
          node.classList.add("oknesset_mk");
          return node;
        }

    });
    $('span.oknesset_mk').each(function (i, el) {
      var id = mks_by_name[$(el).html()]
      $(el).attr('mk_id', id)
      var frame = createMkFrame(id);
      frame.style.display = "none";
      jQuery(this).after(frame)
      jQuery(this).tooltip({position: "bottom center", delay: 500} );
    })
  });
}

(function(f){function p(a,b,c){var h=c.relative?a.position().top:a.offset().top,d=c.relative?a.position().left:a.offset().left,i=c.position[0];h-=b.outerHeight()-c.offset[0];d+=a.outerWidth()+c.offset[1];if(/iPad/i.test(navigator.userAgent))h-=f(window).scrollTop();var j=b.outerHeight()+a.outerHeight();if(i=="center")h+=j/2;if(i=="bottom")h+=j;i=c.position[1];a=b.outerWidth()+a.outerWidth();if(i=="center")d-=a/2;if(i=="left")d-=a;return{top:h,left:d}}function u(a,b){var c=this,h=a.add(c),d,i=0,j=
0,m=a.attr("title"),q=a.attr("data-tooltip"),r=o[b.effect],l,s=a.is(":input"),v=s&&a.is(":checkbox, :radio, select, :button, :submit"),t=a.attr("type"),k=b.events[t]||b.events[s?v?"widget":"input":"def"];if(!r)throw'Nonexistent effect "'+b.effect+'"';k=k.split(/,\s*/);if(k.length!=2)throw"Tooltip: bad events configuration for "+t;a.bind(k[0],function(e){clearTimeout(i);if(b.predelay)j=setTimeout(function(){c.show(e)},b.predelay);else c.show(e)}).bind(k[1],function(e){clearTimeout(j);if(b.delay)i=
setTimeout(function(){c.hide(e)},b.delay);else c.hide(e)});if(m&&b.cancelDefault){a.removeAttr("title");a.data("title",m)}f.extend(c,{show:function(e){if(!d){if(q)d=f(q);else if(b.tip)d=f(b.tip).eq(0);else if(m)d=f(b.layout).addClass(b.tipClass).appendTo(document.body).hide().append(m);else{d=a.next();d.length||(d=a.parent().next())}if(!d.length)throw"Cannot find tooltip for "+a;}if(c.isShown())return c;d.stop(true,true);var g=p(a,d,b);b.tip&&d.html(a.data("title"));e=e||f.Event();e.type="onBeforeShow";
h.trigger(e,[g]);if(e.isDefaultPrevented())return c;g=p(a,d,b);d.css({position:"absolute",top:g.top,left:g.left});l=true;r[0].call(c,function(){e.type="onShow";l="full";h.trigger(e)});g=b.events.tooltip.split(/,\s*/);if(!d.data("__set")){d.bind(g[0],function(){clearTimeout(i);clearTimeout(j)});g[1]&&!a.is("input:not(:checkbox, :radio), textarea")&&d.bind(g[1],function(n){n.relatedTarget!=a[0]&&a.trigger(k[1].split(" ")[0])});d.data("__set",true)}return c},hide:function(e){if(!d||!c.isShown())return c;
e=e||f.Event();e.type="onBeforeHide";h.trigger(e);if(!e.isDefaultPrevented()){l=false;o[b.effect][1].call(c,function(){e.type="onHide";h.trigger(e)});return c}},isShown:function(e){return e?l=="full":l},getConf:function(){return b},getTip:function(){return d},getTrigger:function(){return a}});f.each("onHide,onBeforeShow,onShow,onBeforeHide".split(","),function(e,g){f.isFunction(b[g])&&f(c).bind(g,b[g]);c[g]=function(n){n&&f(c).bind(g,n);return c}})}f.tools=f.tools||{version:"1.2.5"};f.tools.tooltip=
{conf:{effect:"toggle",fadeOutSpeed:"fast",predelay:0,delay:30,opacity:1,tip:0,position:["top","center"],offset:[0,0],relative:false,cancelDefault:true,events:{def:"mouseenter,mouseleave",input:"focus,blur",widget:"focus mouseenter,blur mouseleave",tooltip:"mouseenter,mouseleave"},layout:"<div/>",tipClass:"tooltip"},addEffect:function(a,b,c){o[a]=[b,c]}};var o={toggle:[function(a){var b=this.getConf(),c=this.getTip();b=b.opacity;b<1&&c.css({opacity:b});c.show();a.call()},function(a){this.getTip().hide();
a.call()}],fade:[function(a){var b=this.getConf();this.getTip().fadeTo(b.fadeInSpeed,b.opacity,a)},function(a){this.getTip().fadeOut(this.getConf().fadeOutSpeed,a)}]};f.fn.tooltip=function(a){var b=this.data("tooltip");if(b)return b;a=f.extend(true,{},f.tools.tooltip.conf,a);if(typeof a.position=="string")a.position=a.position.split(/,?\s/);this.each(function(){b=new u(f(this),a);f(this).data("tooltip",b)});return a.api?b:this}})(jQuery);
{% endautoescape %}


/**
 * findAndReplaceDOMText v 0.4.2
 * @author James Padolsey http://james.padolsey.com
 * @license http://unlicense.org/UNLICENSE
 *
 * Matches the text of a DOM node against a regular expression
 * and replaces each match (or node-separated portions of the match)
 * in the specified element.
 */
window.findAndReplaceDOMText = (function() {

	var PORTION_MODE_RETAIN = 'retain';
	var PORTION_MODE_FIRST = 'first';

	var doc = document;
	var toString = {}.toString;

	function isArray(a) {
		return toString.call(a) == '[object Array]';
	}

	function escapeRegExp(s) {
		return String(s).replace(/([.*+?^=!:${}()|[\]\/\\])/g, '\\$1');
	}

	function exposed() {
		// Try deprecated arg signature first:
		return deprecated.apply(null, arguments) || findAndReplaceDOMText.apply(null, arguments);
	}

	function deprecated(regex, node, replacement, captureGroup, elFilter) {
		if ((node && !node.nodeType) && arguments.length <= 2) {
			return false;
		}
		var isReplacementFunction = typeof replacement == 'function';

		if (isReplacementFunction) {
			replacement = (function(original) {
				return function(portion, match) {
					return original(portion.text, match.startIndex);
				};
			}(replacement));
		}

		// Awkward support for deprecated argument signature (<0.4.0)
		var instance = findAndReplaceDOMText(node, {

			find: regex,

			wrap: isReplacementFunction ? null : replacement,
			replace: isReplacementFunction ? replacement : '$' + (captureGroup || '&'),

			prepMatch: function(m, mi) {

				// Support captureGroup (a deprecated feature)

				if (!m[0]) throw 'findAndReplaceDOMText cannot handle zero-length matches';

				if (captureGroup > 0) {
					var cg = m[captureGroup];
					m.index += m[0].indexOf(cg);
					m[0] = cg;
				}
		 
				m.endIndex = m.index + m[0].length;
				m.startIndex = m.index;
				m.index = mi;

				return m;
			},
			filterElements: elFilter
		});

		exposed.revert = function() {
			return instance.revert();
		};

		return true;
	}

	/** 
	 * findAndReplaceDOMText
	 * 
	 * Locates matches and replaces with replacementNode
	 *
	 * @param {Node} node Element or Text node to search within
	 * @param {RegExp} options.find The regular expression to match
	 * @param {String|Element} [options.wrap] A NodeName, or a Node to clone
	 * @param {String|Function} [options.replace='$&'] What to replace each match with
	 * @param {Function} [options.filterElements] A Function to be called to check whether to
	 *	process an element. (returning true = process element,
	 *	returning false = avoid element)
	 */
	function findAndReplaceDOMText(node, options) {
		return new Finder(node, options);
	}

	exposed.Finder = Finder;

	/**
	 * Finder -- encapsulates logic to find and replace.
	 */
	function Finder(node, options) {

		options.portionMode = options.portionMode || PORTION_MODE_RETAIN;

		this.node = node;
		this.options = options;

		// ENable match-preparation method to be passed as option:
		this.prepMatch = options.prepMatch || this.prepMatch;

		this.reverts = [];

		this.matches = this.search();

		if (this.matches.length) {
			this.processMatches();
		}

	}

	Finder.prototype = {

		/**
		 * Searches for all matches that comply with the instance's 'match' option
		 */
		search: function() {

			var match;
			var matchIndex = 0;
			var regex = this.options.find;
			var text = this.getAggregateText();
			var matches = [];

			regex = typeof regex === 'string' ? RegExp(escapeRegExp(regex), 'g') : regex;

			if (regex.global) {
				while (match = regex.exec(text)) {
					matches.push(this.prepMatch(match, matchIndex++));
				}
			} else {
				if (match = text.match(regex)) {
					matches.push(this.prepMatch(match, 0));
				}
			}

			return matches;

		},

		/**
		 * Prepares a single match with useful meta info:
		 */
		prepMatch: function(match, matchIndex) {

			if (!match[0]) {
				throw new Error('findAndReplaceDOMText cannot handle zero-length matches');
			}
	 
			match.endIndex = match.index + match[0].length;
			match.startIndex = match.index;
			match.index = matchIndex;

			return match;
		},

		/**
		 * Gets aggregate text within subject node
		 */
		getAggregateText: function() {

			var elementFilter = this.options.filterElements;

			return getText(this.node);

			/**
			 * Gets aggregate text of a node without resorting
			 * to broken innerText/textContent
			 */
			function getText(node) {

				if (node.nodeType === 3) {
					return node.data;
				}

				if (elementFilter && !elementFilter(node)) {
					return '';
				}

				var txt = '';

				if (node = node.firstChild) do {
					txt += getText(node);
				} while (node = node.nextSibling);

				return txt;

			}

		},

		/** 
		 * Steps through the target node, looking for matches, and
		 * calling replaceFn when a match is found.
		 */
		processMatches: function() {

			var matches = this.matches;
			var node = this.node;
			var elementFilter = this.options.filterElements;

			var startPortion,
				endPortion,
				innerPortions = [],
				curNode = node,
				match = matches.shift(),
				atIndex = 0, // i.e. nodeAtIndex
				matchIndex = 0,
				portionIndex = 0,
				doAvoidNode,
				nodeStack = [node];

			out: while (true) {

				if (curNode.nodeType === 3) {

					if (!endPortion && curNode.length + atIndex >= match.endIndex) {

						// We've found the ending
						endPortion = {
							node: curNode,
							index: portionIndex++,
							text: curNode.data.substring(match.startIndex - atIndex, match.endIndex - atIndex),
							indexInMatch: atIndex - match.startIndex,
							indexInNode: match.startIndex - atIndex, // always zero for end-portions
							endIndexInNode: match.endIndex - atIndex,
							isEnd: true
						};

					} else if (startPortion) {
						// Intersecting node
						innerPortions.push({
							node: curNode,
							index: portionIndex++,
							text: curNode.data,
							indexInMatch: atIndex - match.startIndex,
							indexInNode: 0 // always zero for inner-portions
						});
					}

					if (!startPortion && curNode.length + atIndex > match.startIndex) {
						// We've found the match start
						startPortion = {
							node: curNode,
							index: portionIndex++,
							indexInMatch: 0,
							indexInNode: match.startIndex - atIndex,
							endIndexInNode: match.endIndex - atIndex,
							text: curNode.data.substring(match.startIndex - atIndex, match.endIndex - atIndex)
						};
					}

					atIndex += curNode.data.length;

				}

				doAvoidNode = curNode.nodeType === 1 && elementFilter && !elementFilter(curNode);

				if (startPortion && endPortion) {

					curNode = this.replaceMatch(match, startPortion, innerPortions, endPortion);

					// processMatches has to return the node that replaced the endNode
					// and then we step back so we can continue from the end of the 
					// match:

					atIndex -= (endPortion.node.data.length - endPortion.endIndexInNode);

					startPortion = null;
					endPortion = null;
					innerPortions = [];
					match = matches.shift();
					portionIndex = 0;
					matchIndex++;

					if (!match) {
						break; // no more matches
					}

				} else if (
					!doAvoidNode &&
					(curNode.firstChild || curNode.nextSibling)
				) {
					// Move down or forward:
					if (curNode.firstChild) {
						nodeStack.push(curNode);
						curNode = curNode.firstChild;
					} else {
						curNode = curNode.nextSibling;
					}
					continue;
				}

				// Move forward or up:
				while (true) {
					if (curNode.nextSibling) {
						curNode = curNode.nextSibling;
						break;
					}
					curNode = nodeStack.pop();
					if (curNode === node) {
						break out;
					}
				}

			}

		},

		/**
		 * Reverts ... TODO
		 */
		revert: function() {
			// Reversion occurs backwards so as to avoid nodes subsequently
			// replaced during the matching phase (a forward process):
			for (var l = this.reverts.length; l--;) {
				this.reverts[l]();
			}
			this.reverts = [];
		},

		prepareReplacementString: function(string, portion, match, matchIndex) {
			var portionMode = this.options.portionMode;
			if (
				portionMode === PORTION_MODE_FIRST &&
				portion.indexInMatch > 0
			) {
				return '';
			}
			string = string.replace(/\$(\d+|&|`|')/g, function($0, t) {
				var replacement;
				switch(t) {
					case '&':
						replacement = match[0];
						break;
					case '`':
						replacement = match.input.substring(0, match.startIndex);
						break;
					case '\'':
						replacement = match.input.substring(match.endIndex);
						break;
					default:
						replacement = match[+t];
				}
				return replacement;
			});

			if (portionMode === PORTION_MODE_FIRST) {
				return string;
			}

			if (portion.isEnd) {
				return string.substring(portion.indexInMatch);
			}

			return string.substring(portion.indexInMatch, portion.indexInMatch + portion.text.length);
		},

		getPortionReplacementNode: function(portion, match, matchIndex) {

			var replacement = this.options.replace || '$&';
			var wrapper = this.options.wrap;

			if (wrapper && wrapper.nodeType) {
				// Wrapper has been provided as a stencil-node for us to clone:
				var clone = doc.createElement('div');
				clone.innerHTML = wrapper.outerHTML || new XMLSerializer().serializeToString(wrapper);
				wrapper = clone.firstChild;
			}

			if (typeof replacement == 'function') {
				replacement = replacement(portion, match, matchIndex);
				if (replacement && replacement.nodeType) {
					return replacement;
				}
				return doc.createTextNode(String(replacement));
			}

			var el = typeof wrapper == 'string' ? doc.createElement(wrapper) : wrapper;

			replacement = doc.createTextNode(
				this.prepareReplacementString(
					replacement, portion, match, matchIndex
				)
			);

			if (!replacement.data) {
				return replacement;
			}

			if (!el) {
				return replacement;
			}

			el.appendChild(replacement);

			return el;
		},

		replaceMatch: function(match, startPortion, innerPortions, endPortion) {

			var matchStartNode = startPortion.node;
			var matchEndNode = endPortion.node;

			var preceedingTextNode;
			var followingTextNode;

			if (matchStartNode === matchEndNode) {

				var node = matchStartNode;

				if (startPortion.indexInNode > 0) {
					// Add `before` text node (before the match)
					preceedingTextNode = doc.createTextNode(node.data.substring(0, startPortion.indexInNode));
					node.parentNode.insertBefore(preceedingTextNode, node);
				}

				// Create the replacement node:
				var newNode = this.getPortionReplacementNode(
					endPortion,
					match
				);

				node.parentNode.insertBefore(newNode, node);

				if (endPortion.endIndexInNode < node.length) { // ?????
					// Add `after` text node (after the match)
					followingTextNode = doc.createTextNode(node.data.substring(endPortion.endIndexInNode));
					node.parentNode.insertBefore(followingTextNode, node);
				}

				node.parentNode.removeChild(node);

				this.reverts.push(function() {
					if (preceedingTextNode === newNode.previousSibling) {
						preceedingTextNode.parentNode.removeChild(preceedingTextNode);
					}
					if (followingTextNode === newNode.nextSibling) {
						followingTextNode.parentNode.removeChild(followingTextNode);
					}
					newNode.parentNode.replaceChild(node, newNode);
				});

				return newNode;

			} else {
				// Replace matchStartNode -> [innerMatchNodes...] -> matchEndNode (in that order)


				preceedingTextNode = doc.createTextNode(
					matchStartNode.data.substring(0, startPortion.indexInNode)
				);

				followingTextNode = doc.createTextNode(
					matchEndNode.data.substring(endPortion.endIndexInNode)
				);

				var firstNode = this.getPortionReplacementNode(
					startPortion,
					match
				);

				var innerNodes = [];

				for (var i = 0, l = innerPortions.length; i < l; ++i) {
					var portion = innerPortions[i];
					var innerNode = this.getPortionReplacementNode(
						portion,
						match
					);
					portion.node.parentNode.replaceChild(innerNode, portion.node);
					this.reverts.push((function(portion, innerNode) {
						return function() {
							innerNode.parentNode.replaceChild(portion.node, innerNode);
						};
					}(portion, innerNode)));
					innerNodes.push(innerNode);
				}

				var lastNode = this.getPortionReplacementNode(
					endPortion,
					match
				);

				matchStartNode.parentNode.insertBefore(preceedingTextNode, matchStartNode);
				matchStartNode.parentNode.insertBefore(firstNode, matchStartNode);
				matchStartNode.parentNode.removeChild(matchStartNode);

				matchEndNode.parentNode.insertBefore(lastNode, matchEndNode);
				matchEndNode.parentNode.insertBefore(followingTextNode, matchEndNode);
				matchEndNode.parentNode.removeChild(matchEndNode);

				this.reverts.push(function() {
					preceedingTextNode.parentNode.removeChild(preceedingTextNode);
					firstNode.parentNode.replaceChild(matchStartNode, firstNode);
					followingTextNode.parentNode.removeChild(followingTextNode);
					lastNode.parentNode.replaceChild(matchEndNode, lastNode);
				});

				return lastNode;
			}
		}

	};

	return exposed;

}());
