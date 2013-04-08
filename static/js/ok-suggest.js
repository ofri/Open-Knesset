!function ($) {

  "use strict"; // jshint ;_;

  // reset function for forms
  jQuery.fn.reset = function () {
    $(this).each (function() { this.reset(); });
  }

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

			// Remove pre-existing errors
			$('.text-error', $this).remove();
			$btn.button('loading');

			$.post($this.attr('action'), $this.serialize())
			.done(function(data){
			   if (data.success) {
				var container = $('<div class="alert"><a href="#" class="close" data-dismiss="alert">&times;</a></div>'),
				msg = $('<span/>').text(gettext("Your suggestion is submitted. Thank you !"));

				msg.appendTo(container);

				$($('.container').get(1)).prepend(container);
				container.alert();

				$this.reset();
				$modal.modal('hide');
			   }
			   else {
					// we assume we got the validation errors in data.errors object
					// TODO handle form validation errors for __all__

					$.each(data.errors, function(key, item_errors) {
						var el = $('<div class="text-error"/>'),
							target = $('[name=' + key  +']', $this);

						el.insertAfter(target).text(item_errors.join());

				   })
			   }
			})
			.always(function() {
			   $btn.button('reset');
			})
		  return false;
	  })
  }) // end ready
}(window.jQuery);
