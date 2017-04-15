
$(document).ready(function() {

	var $container = $('#sponsors');
	// initialize Isotope
	$container.isotope({
		masonry: {
			columnWidth: 220
		},
		itemSelector : '.sponsor'
	});

	// update columnWidth on window resize
	$(window).smartresize(function(){
		$container.isotope({
			masonry: {
				columnWidth: 220
			}
		});
	});

});
