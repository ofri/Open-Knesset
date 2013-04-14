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

	var getCountFor = $('.suggest-modal form').map(function() {
		var $el = $(this),
			res = $el.data('forModel'),
			pk = $el.data('forPk');

		
		if (pk) {
			res = res + '-' + pk;
		}
		return {name: 'for', value:res};
	}).get();

	if (getCountFor.length > 0) {
		var countUrl = $('.suggest-modal form').data('countUrl'),
			detailUrl =  $('.suggest-modal form').data('detailUrl');
		// Get the pending suggestions for each suggestion form
		$.get(countUrl, getCountFor)
			.done(function(data) {
				if ($.isEmptyObject(data)) { return; }

				var container = $('<div class="alert alert-info"><a href="#" class="close" data-dismiss="alert">&times;</a>' + gettext('Pending suggestions') + ':<ul/></div>'),
					suggestion_ul = $('ul', container),
					detail = $('<a href="#" class="btn btn-info"></a>').text(gettext('View pending suggestions'));

				detail.insertAfter(suggestion_ul);

				$.each(data, function(key, val){
					var suggestion_li = $('<li/>');
					suggestion_li.text(key+ ': ' + val);
					suggestion_li.appendTo(suggestion_ul);
				})

				$($('.container').get(1)).prepend(container);
				container.alert();

				detail.click(function(ev) {
					ev.preventDefault();

					$.get(detailUrl, getCountFor).done(function(data) {
						// TODO implement me
					});
					return false;
				});
			})
		// end getting pending suggestions
	}
  }) // end ready
}(window.jQuery);
