function placeHelptext(obj,left,top) {
  $('#helptextcontainer').empty();
  obj.clone().appendTo($('#helptextcontainer'))

  if (left<500) {
      $('#helptextcontainer .helptext').removeClass('right')
      $('#helptextcontainer .helptext').addClass('left')
  } else {
      $('#helptextcontainer .helptext').removeClass('left')
      $('#helptextcontainer .helptext').addClass('right')
  }

  $('#helptextcontainer .helptext').css('z-index',1000);
  $('#helptextcontainer .helptext .x').bind('click',function(){
        $('#helptextcontainer').empty();});
  $('#helptextcontainer .helptext').css('display','inline-block');
  $('#helptextcontainer .helptext').css('top',top-50).css('left',left);
}
$('body').append('<div id="helptextcontainer"></div>');
$(document).ready(function() {
  $('.quest-mark').click(function(e) {placeHelptext($(e.currentTarget).find(".helptext"),e.pageX,e.pageY)});
});
