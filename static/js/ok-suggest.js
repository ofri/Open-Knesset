!function ($) {

  "use strict"; // jshint ;_;

  $(function() {
	  // setup submit button
	  $('.suggest-modal .btn-primary').click(function() {
		  var $form = $('form', $(this).closest('.suggest-modal'));
		  $form.submit();
	  });

	  // setup form submmission
	  $('.suggest-modal form').submit(function() {
		var $modal = $(this).closest('.suggest-modal'),
			$btn = $('.btn-primary', $modal),
			$this = $(this);

			// don't send if already sending
			if ($btn.attr('disabled') === 'disabled') {
				return false;
			}

			$btn.button('loading');

			$.post($this.attr('action'), $this.serialize())
			.done(function(data){
			   if (data.success) {
				var container = $('<div class="alert"><a href="#" class="close" data-dismiss="alert">&times;</a></div>'),
				msg = $('<span/>').text('{% trans "Your suggestion is submitted. Thank you" %}');

				msg.appendTo(container);

				$($('.container').get(1)).prepend(container);
				container.alert();
				$modal.modal('hide');
			   }
			   else {
				// TODO handle form validation errors
			   }
			})
			.always(function() {
			   $btn.button('reset');
			})
		  return false;
	  })
  }) // end ready
}(window.jQuery);
