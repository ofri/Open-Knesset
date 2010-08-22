generateMkFrameSet('code',{MkIds:[780],classHook:''},{width:480},'oknesset_container');
function generateMkFrameSet(action,Mks,style,targetId){
    style = typeof(style) != 'undefined' ? style : {width:414};
    targetId = typeof(targetId) != 'undefined' ? targetId : '';
    
    var MkIds = {};
    if (Mks.MkIds) 
        getMkIdsFromIdList( Mks.MkIds );
    if (Mks.classHook)
        getMkIdsFromClassHook( Mks.classHook );
        
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
    
    for ( var key in MkIds ) {
        MkIds[key] = createMkFrame(key, style.width );
    }
    
    if ( action == "embed" )
      embedFrames( targetId );
    
    return MkIds;

  function createMkFrame( mkId, width ){
    var mkFrame = document.createElement("iframe");
    mkFrame.src = "http://oknesset.org/static/html/oknesset-iframe.html?id="+mkId;
    mkFrame.style.display = "block";
    mkFrame.style.border =  "0px";
    mkFrame.style.margin =  "3px 0";
    mkFrame.style.width = width+"px";
    mkFrame.scrolling = "no";
    mkFrame.id = "mkFrame_"+frameNum;
    frameNum++;
    return mkFrame;
  }
  
  function embedFrames( targetId ) {
    for (var key in MkIds) {
      $('#' + targetId).append( MkIds[key] );
    }
    resizeFrames();
  }
  
  function resizeFrames() {
  // iframe height adjustment
    jQuery(document).ready(function()
    {
        // Set specific variable to represent all iframe tags.
        var iFrames = document.getElementsByTagName('iframe');

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
        if (jQuery.browser.safari || jQuery.browser.opera)
        {
          // Start timer when loaded.
          jQuery('iframe').load(function()
            {
              setTimeout(iResize, 0);
            }
          );

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
          jQuery('iframe').load(function()
            {
              // Set inline style to equal the body height of the iframed content.
              this.style.height = this.contentWindow.document.body.offsetHeight + 'px';
            }
          );
        }
      }
    );

  }
}
