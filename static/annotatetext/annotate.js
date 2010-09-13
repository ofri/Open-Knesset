var annotation_objects = {};

function Annotations(id){
    this.id = id;
    this.text_div = $("#annotationtext_"+id);
    this.text = this.text_div.text().replace("&gt;", ">").replace("&lt;", "<");
    this.original_html = this.text_div.html();
    this.annotation_div = $("#annotations-"+id);
    this.insert_count = 0;
    this.annotations = {};
    this.selectable = false;
}

Annotations.prototype = {
    buildTextTree : function(){
      insertAt = function(str, pos, insert){
        return str.substring(0,pos)+insert+str.substring(pos,str.length);
      };
      var all_html = this.text_div.html();
      // This is a hack
      all_html = all_html.replace("&lt;", "\x02").replace("&gt;", "\x03").replace("&amp;", "\x04").replace("&quot;", "\x05").replace("&#39;", "\x06");
      var new_html = all_html;
      var rest_html = all_html;
      var textCursor = 0;
      var htmlCursor = 0;
      var htmlOffset = 0;
      var opened = [];
      var reopen = [];
      var footnoteCount = 0;
      next = this.getNextStartOrEnd(textCursor);
      if (next == -1){return new_html;}
      while (new_html.charAt(htmlCursor) == "<"){
        rest_html = new_html.substring(htmlCursor, new_html.length);
        var endOfTag = rest_html.indexOf(">")+1;
        rest_html = new_html.substring(endOfTag, new_html.length);
        htmlCursor += endOfTag;
        htmlOffset += endOfTag;
      }
      while (true){
        var ends = this.getOrderedEndsAt(textCursor);
        var reopen = [];
        for(var i=0;i<ends.length;i++){
          while(opened.length > 0 && opened[opened.length-1] != ends[i]){
            reopen.push(opened[opened.length-1]);
            new_html = insertAt(new_html, htmlCursor, this.annotations[opened[opened.length-1]].end_html);
            htmlCursor += this.annotations[opened[opened.length-1]].end_html.length;
            htmlOffset += this.annotations[opened[opened.length-1]].end_html.length;
            opened = this.removeLast(opened);
          }
          new_html = insertAt(new_html, htmlCursor, this.annotations[ends[i]].end_html);
          htmlCursor += this.annotations[ends[i]].end_html.length;
          htmlOffset += this.annotations[ends[i]].end_html.length;
          opened = this.removeLast(opened);
        }
        if(new_html.charAt(htmlCursor) == "<"){
          for(var i=opened.length-1;i>=0;i--){
            new_html = insertAt(new_html, htmlCursor, this.annotations[opened[i]].end_html);
            htmlCursor += this.annotations[opened[i]].end_html.length;
            htmlOffset += this.annotations[opened[i]].end_html.length;
            reopen.push(opened[i]);            
          }
          opened = [];
        }
        while (new_html.charAt(htmlCursor) == "<"){
          rest_html = new_html.substring(htmlCursor, new_html.length);
          var endOfTag = rest_html.indexOf(">")+1;
          rest_html = rest_html.substring(endOfTag, new_html.length);
          htmlCursor += endOfTag;
          htmlOffset += endOfTag;
        }
        if(reopen.length > 0) {
          for(var j = reopen.length-1; j >= 0; j--){
            new_html = insertAt(new_html, htmlCursor, this.annotations[reopen[j]].start_html);
            htmlCursor += this.annotations[reopen[j]].start_html.length;
            htmlOffset += this.annotations[reopen[j]].start_html.length;
            opened.push(reopen[j]);
          }
        }
        var starts = this.getOrderedStartsAt(textCursor);
        for (var i = 0; i < starts.length; i++){
          new_html = insertAt(new_html, htmlCursor, this.annotations[starts[i]].start_html);
          htmlCursor += this.annotations[starts[i]].start_html.length;
          htmlOffset += this.annotations[starts[i]].start_html.length;
          if (this.annotations[starts[i]].start != this.annotations[starts[i]].end){
            opened.push(starts[i]);
          } else {
            footnoteCount += 1;
            new_html = insertAt(new_html, htmlCursor, String(footnoteCount));
            htmlCursor += String(footnoteCount).length;
            htmlOffset += String(footnoteCount).length;
            new_html = insertAt(new_html, htmlCursor, this.annotations[starts[i]].end_html);
            htmlCursor += this.annotations[starts[i]].end_html.length;
            htmlOffset += this.annotations[starts[i]].end_html.length;
            $("#a_"+starts[i]).hide();
            $("#footnotelist-"+this.id).append("<li>"+$("#a_"+starts[i]+" .content").html()+"</li>");
          }
        }
        var next = this.getNextStartOrEnd(textCursor);
        if (next == -1) {
            break;
        }
        rest_html = new_html.substring(htmlCursor, new_html.length);
        var nextHtml = rest_html.indexOf("<");
        if(nextHtml != -1 && next + htmlOffset < htmlCursor + nextHtml){
          textCursor = next;
          htmlCursor = next + htmlOffset;
        } else {
          htmlCursor = htmlCursor + nextHtml;
          textCursor = htmlCursor - htmlOffset;
        }
      }
      // Revert hack
      new_html = new_html.replace("\x02","&lt;").replace("\x03","&gt;").replace("\x04", "&amp;").replace("\x05", "&quot;").replace("\x06", "&#39;");
      return new_html;
    },
    
    insertQuotes: function(){
      if (this.annotation_count>0){
        this.text_div.html(this.original_html);
        this.text_div.html(this.buildTextTree());
        $("#annotationtoolbox-"+this.id).show();
        var total_height = this.text_div.height() + this.text_div.nextAll(".eventlist").height();
        // $("#annotations-"+this.id).css({"height": total_height+"px"});
        this.setupQuotes();
        this.repositionAnnotation();
      }
    },
    
    importQuotes: function(){
        var annotation_divs = $("#annotations-"+this.id+" .semannotation");
        this.annotation_count = annotation_divs.length;
        for (var j=0; j < annotation_divs.length; j++){
            var element = annotation_divs[j];
            var annotation = {};
            annotation.counter = j;
            annotation.id = parseInt($(element).attr("id").split("_")[1]);
            var classes = $(element).find("q").hide().attr("class");
            annotation.color = $(element).css("border-left-color");
            annotation.defaultColor = "inherit";
            classes = classes.split(" ");
            for(var i = 0; i < classes.length; i++){
                var cls = classes[i].split("_");
                if (cls.length == 2 && cls[0]=="start"){
                    annotation.start = parseInt(cls[1]);
                }
                if (cls.length == 2 && cls[0]=="end"){
                    annotation.end = parseInt(cls[1]);
                }
            }
            if (annotation.end == undefined){
                annotation.end = annotation.start;
            }
            if(annotation.end == annotation.start){
              annotation.start_html = '<sup class="annotation annotation_'+annotation.id+'">';
              annotation.end_html = "</sup>";
            }else {
              annotation.start_html = '<span class="annotation annotation_'+annotation.id+'">';
              annotation.end_html = "</span>";              
            }
            annotation.content = $(element).find(".content").html();
            this.annotations[annotation.id] = annotation;
        }
    },

    sortByEnd: function(a,b){
        if (a != -1 && b != -1){
            var diff = this.annotations[a].end - this.annotations[b].end;
            if (diff == 0){
              diff = this.annotations[b].start - this.annotations[a].start;
              if(diff == 0){
                return a - b;
              }
              return diff;
            }
            return diff;                
        }
        return a - b;
    },
    
    getOrderedEndsAt: function(index){
        var result = [];
        for(var aid in this.annotations){
            if(this.annotations[aid].end == index){
                result.push(parseInt(aid));
            }
        }
        var that = this;
        result.sort(function(a,b){return that.sortByEnd.apply(that,[a,b]);});
        return result;
    },
    getOrderedStartsAt: function(index){
        var result = [];
        for(var aid in this.annotations){
            if(this.annotations[aid].start == index){
                result.push(parseInt(aid));
            }
        }
        var that = this;
        result.sort(function(a,b){return that.sortByEnd.apply(that,[a,b]);});
        result.reverse();
        return result;
    },
        
    getNextStartOrEnd: function(textIndex){
        result = [];
        for(var aid in this.annotations){
            if(this.annotations[aid].start > textIndex){
                result.push(this.annotations[aid].start);
            }
            if(this.annotations[aid].end > textIndex){
                result.push(this.annotations[aid].end);                    
            }
        }
        if (result.length == 0){
            return -1;
        }
        sort = function(a,b){
            return a - b;
        };
        result.sort(sort);
        return result[0];
    },
        
    removeLast: function(a){
        return a.slice(0,a.length-1);
    },
    
    repositionAnnotation : function(){
      var relOffset = 0;
      var leftOffset = 0;
      var offsetMap = {};
      for (var aid in this.annotations){
        var annotop = $(".annotation_"+aid).offset().top;
        var selftop = $("#a_"+aid).offset().top;
        if(Math.abs(annotop - selftop) > 200){
          relOffset = Math.abs(annotop - selftop);
          if (typeof offsetMap[annotop] === "undefined"){
            offsetMap[annotop] = 0;
          } else {offsetMap[annotop] = offsetMap[annotop]+1;}
        }
        if(annotop - selftop < -300){
          leftOffset = 100;
        }
        $("#a_"+aid).css({"top": relOffset+offsetMap[annotop]*20, "left": leftOffset+offsetMap[annotop]*20});
        leftOffset = 0;
      }
    },

    mark_quotes: function(cls){
        var color = this.getColorById(cls.split("_")[1]);
        color = this.getColorString(color);
        $("."+cls).css({"background": color});
//        $("."+cls).children().css({"background": color});
    },
    
    clear_quotes: function(cls){
        $("."+cls).css({"background": "#fff "});
//        $("."+cls).children().css({"background": "#fff "});
    },
    
    mark_quote: function(aid){
        $(".annotation_"+aid).css({"background": this.annotations[aid].color});
//        $(".annotation_"+aid).children().css({"background": this.annotations[aid].color});
    },
    
    clear_quote: function(aid){
        $(".annotation_"+aid).css({"background": this.annotations[aid].defaultColor });
//        $(".annotation_"+aid).children().css({"background": this.annotations[aid].defaultColor });
    },
    
    setupQuotes: function(){
        var obj = this;
        $(".annotationfor-"+this.id).mouseover(function(){
          var o = obj;
          var aid = $(this).attr("id").split("_")[1];
          o.mark_quote(aid);
        });
        $(".annotationfor-"+this.id).mouseout(function(){
          var o = obj;
          var aid = $(this).attr("id").split("_")[1];
          o.clear_quote(aid);
        });
/*        $(".annotation").mouseover(function(){
            obj.callFunctionForAnnotation.apply(obj,[this, obj.mark_quotes]);
        });
        $(".annotation").mouseout(function(){
            obj.callFunctionForAnnotation.apply(obj,[this, obj.clear_quotes]);
        });*/
    },
    
    getColorRGBA: function(hex, alpha){
      if(hex.indexOf("rgb")!=-1){
        hex = hex.substring(hex.indexOf("(")+1,hex.indexOf(")")).split(",");
        var r = parseInt(hex[0]);
        var g = parseInt(hex[1]);
        var b = parseInt(hex[2]);
      }
      else{
        hex = (hex.charAt(0)=="#") ? hex.substring(1,hex.length):hex;
        if (hex.length == 6){
          var r = parseInt(hex.substring(0,2), 16);
          var g = parseInt(hex.substring(2,4), 16);
          var b = parseInt(hex.substring(4,6), 16);
        }else{
          var r = parseInt(hex.substring(0,1) + hex.substring(0,1), 16);
          var g = parseInt(hex.substring(1,2) + hex.substring(1,2), 16);
          var b = parseInt(hex.substring(2,3) + hex.substring(2,3), 16);
        }
      }
      return "rgba("+r+","+g+","+b+","+alpha+")";
    },
    
    getColorById : function(aid){
        var q = parseInt(this.annotations[aid].counter);
        q = q / this.annotation_count;
        return [255 * q, 255 * (1-q), 128];
    },
    
    getColorString : function(array){
        return "rgba("+Math.round(array[0])+","+Math.round(array[1])+","+Math.round(array[2])+",0.5)";
    },
    
    callFunctionForAnnotation : function(obj, func){
        var classes = $(obj).attr("class").split(" ");
        for(var i=0;i<classes.length;i++){
            if (classes[i].match(/annotation_[0-9]+/)){
                func.apply(this, [classes[i]]);
                return;
            }
        }
    },
    
    toggleSelectView : function(){
        if(this.selectable){
            this.text_div.show();
            this.selectView.hide();
            $("#selectionhint-"+this.id).css("color", "#000");
        }
        else{
            if(this.selectView == undefined){
                var ta = document.createElement("textarea");
                ta.setAttribute("class", "selectableText");
                ta.setAttribute("id", "selectableText_"+this.id);
                ta.setAttribute("style", "display:none");
                ta.appendChild(document.createTextNode(this.text));
                this.text_div.after(ta);
                this.selectView = $("#selectableText_"+this.id);
                this.selectView.height(this.text_div.height());
                var that = this;
                if(!(/webkit/i).test(navigator.userAgent)){
                  this.selectView.attr("readonly", "true");
                }
                this.selectView.select(function(e){
                  that.updateSelectionInputs(e);
                });
                this.selectView.mouseup(function(e){
                 that.updateSelectionInputs(e);
                });
                if((/webkit/i).test(navigator.userAgent)){
                  this.selectView.keydown(function(e){
                    if(!(e.keyCode==37 || e.keyCode==38 || e.keyCode==39 || e.keyCode==40 || e.KeyCode == 16 || e.keyCode==9)){
                      e.preventDefault();
                    }
                  });
                }
                this.selectView.keyup(function(e){
                  that.updateSelectionInputs(e);
                });
              }
          this.text_div.hide();
          this.selectView.show();
          this.selectView.focus();
          }
      this.selectable = !this.selectable;
    },
    updateSelectionInputs : function(e){
      var selStart = null;
      var selEnd = null;
      if(e.target){
        if(typeof(e.target.selectionStart) == "number"){
          selStart = e.target.selectionStart;
        }
        if(typeof(e.target.selectionEnd) == "number"){
          selEnd = e.target.selectionEnd;
        }
      }
//      
      if(selStart !== null){
        $("#selection_start-"+this.id).val(selStart);
      }
      if(selEnd !== null){
       $("#selection_end-"+this.id).val(selEnd); 
      }
      if(selEnd !== null && selStart !==null){
/*        if(selEnd === selStart){
          var selected_text = this.text.substring(selStart-12, selStart)+"<sup>[1]</sup>"+this.text.substring(selEnd, selEnd+12);
          $("#selectionhint-"+this.id).html('Fußnote bei "[&hellip;]'+selected_text+'[&hellip;]"');
        }*/
        if(selEnd !== selStart){
          var selected_text = this.text.substring(selStart, selEnd);
          if(selected_text.length > 40){
            selected_text = this.text.substring(selStart, selStart+20)+"[&hellip;]"+this.text.substring(selEnd-20, selEnd);
          }
          $("#selectionhint-"+this.id).html('"'+selected_text+'"');
          $("#selectionempty-"+this.id).hide();
          $("#selectionhint-"+this.id).show();
        }
        else{
          $("#selectionempty-"+this.id).show();
          $("#selectionhint-"+this.id).hide();
        }
      }
      else{
          $("#selectionempty-"+this.id).show();
          $("#selectionhint-"+this.id).hide();
      }
    },
    updateDefaultAnnotationColor : function(color){
      for(var aid in this.annotations){
        if(color == "self"){this.annotations[aid].defaultColor = this.annotations[aid].color;}
        else{this.annotations[aid].defaultColor = color;}
        if(color != "inherit"){
          $(".annotation_"+aid).css({"background": this.getColorRGBA(this.annotations[aid].defaultColor,0.5)});  
        } else{
          $(".annotation_"+aid).css({"background": this.annotations[aid].defaultColor});   
        }
      }
    }
};
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
