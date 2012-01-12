
function placeHelptext(obj,left,top) {
  $('#helptextcontainer').empty();
  obj.clone().appendTo($('#helptextcontainer'))

  if (left <500) {
    $('#helptextcontainer .helptext').removeClass('right')
    $('#helptextcontainer .helptext').addClass('left')
    }   

  $('#helptextcontainer .helptext').css('z-index',1000);           
   $('#helptextcontainer .helptext .x').bind('click',function() 
    {
    $('#helptextcontainer').empty();

    });
   $('#helptextcontainer .helptext').css('display','inline-block');
   helptextheight=$('#helptextcontainer .helptext').height();

   
   $('#helptextcontainer .helptext').css('top',top+helptextheight) ;
}
$('body').append('<div id="helptextcontainer"></div>');
$(document).ready(function() {
  $('.quest-mark').click(function(e) {placeHelptext($(e.currentTarget).find(".helptext"),e.pageX,e.pageY)});
});
