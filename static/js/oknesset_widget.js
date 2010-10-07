
function generateMkFrameSet( Mks,style,targetId,okURI ){
  var style = typeof(style) != 'undefined' ? style : {width:414};
  var targetId = typeof(targetId) != 'undefined' ? targetId : '';
  var okURI = typeof(okURI) != 'undefined' ? okURI : guessScriptURI();
	
	if ( okURI.charAt( okURI.length-1 ) != '/' )
	  okURI += '/';
	
  var frameNum = 0;
  var MkIds = {};
  if (Mks.MkIds) 
      getMkIdsFromIdList( Mks.MkIds );
  if (Mks.classHook)
      getMkIdsFromClassHook( Mks.classHook );
  
  for ( var key in MkIds ) {

    MkIds[key] = createMkFrame(key, style.width );
    // jQuery(targetId).append(MkIds[key])
    // TODO: add support for footnotes 
    document.getElementById(targetId).appendChild(MkIds[key])        
  }

  resizeFrames();

  /* end of main */

  function getMkIdsFromIdList( list ) {
    for (var i=0; i<list.length; i++) {
      MkIds[list[i]] = true;
    }
  }

  function getMkIdsFromClassHook( hook ) {
      MkElements = document.getElementsByClassName( hook );
      for (var i=0; i<MkElements.length; i++){
          MkIds[MkElements[i].innerHTML] = true;
      }
  }

  function guessScriptURI() {
    var myDomain = (function(scripts) {
        var scripts = document.getElementsByTagName('script'),
            script = scripts[scripts.length - 2];

        if (script.getAttribute.length !== undefined) {
            return script.src.match('http://[^/]*/')
        }

        return script.getAttribute('src', -1)
      }());
      
    return myDomain + "static/html/";
  }

  function createMkFrame( mkId, width ){
    var mkFrame = document.createElement("iframe");
    mkFrame.src = okURI + "static/html/oknesset-iframe.html?id="+mkId;
    mkFrame.style.display = "block";
    mkFrame.style.border =  "0px";
    mkFrame.style.margin =  "3px 0";
    mkFrame.style.width = width+"px";
    mkFrame.style.height = "240px";
	mkFrame.className = "oknesset_frame";
    mkFrame.scrolling = "no";
    mkFrame.id = "mkFrame_"+frameNum;
    frameNum++;
    return mkFrame;
  }
	
  function resizeFrames() {
  // iframe height adjustment
    document.onload = (function()
    {
        // Set specific variable to represent all iframe tags.
        var iFrames = document.getElementsByClassName('oknesset_frame');

        // Resize heights.
        function iResize()
        {
          // Iterate through all iframes in the page.
          for (var i = 0, j = iFrames.length; i < j; i++)
          {
            // Set inline style to equal the body height of the iframed content.
            iFrames[i].style.height = iFrames[i].contentWindow.document.body.offsetHeight + 'px';
          }
        }

        // Check if browser is Safari or Opera.
        if (navigator.appCodeName == "safari" || navigator.appCodeName == "opera")
        {
          // Start timer when loaded.
          getElementsByTagName('iframe').onload = function()
            {
              setTimeout(iResize, 0);
            };

          // Safari and Opera need a kick-start.
          for (var i = 0, j = iFrames.length; i < j; i++)
          {
            var iSource = iFrames[i].src;
            iFrames[i].src = '';
            iFrames[i].src = iSource;
          }
        }
        else
        {
          // For other good browsers.
          getElementsByClassName('oknesset_frame').onload = function()
            {
              // Set inline style to equal the body height of the iframed content.
              this.style.height = this.contentWindow.document.body.offsetHeight + 'px';
            };
        }
      }
    );

  }
}
// Simple JavaScript Templating
// John Resig - http://ejohn.org/ - MIT Licensed
(function() {
    var cache = {};

    this.tmpl = function tmpl(str, data) {
        // Figure out if we're getting a template, or if we need to
        // load the template - and be sure to cache the result.
        var fn = !/\W/.test(str) ?
      cache[str] = cache[str] ||
        tmpl(document.getElementById(str).innerHTML) :

        // Generate a reusable function that will serve as a template
        // generator (and which will be cached).
      new Function("obj",
        "var p=[],print=function(){p.push.apply(p,arguments);};" +

        // Introduce the data as local variables using with(){}
        "with(obj){p.push('" +

        // Convert the template into pure JavaScript
str.replace(/[\r\t\n]/g, " ")
   .replace(/'(?=[^%]*%>)/g,"\t")
   .split("'").join("\\'")
   .split("\t").join("'")
   .replace(/<%=(.+?)%>/g, "',$1,'")
   .split("<%").join("');")
   .split("%>").join("p.push('")
   + "');}return p.join('');");
        // Provide some basic currying to the user
        return data ? fn(data) : fn;
    };
})();
