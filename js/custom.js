	var map = undefined;
	var searcher = undefined;

	function displayMap() {
		map = L.map('map').setView([51.050399, 13, 737246], 11);

		var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
				osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
				osm = L.tileLayer(osmUrl, {maxZoom: 18, attribution: osmAttrib}).addTo(map);


		searcher = new L.Control.GeoSearch({
			provider: new L.GeoSearch.Provider.OpenStreetMap(),
			zoomLevel: 17,
			messageHideDelay: 9999,
			notFoundMessage: '<strong>Die Adresse konnte nicht gefunden werden.</strong> Bitte gehe zurück und überprüfe die Eingaben. Sollte die Adresse trotzdem nicht gefunden werden, kontaktiere uns bitte unter <a href="mailto:meet-and-eat@exma.de">meet-and-eat@exma.de</a>'
		});
		searcher.addTo(map);

	}

	$(function () {
		var myWizard = $('#myWizard');
		var myPrevBtn = $('#wizard-prev');
		var myNextBtn = $('#wizard-next');

		var resultData;

		myWizard.wizard();
		myWizard.on('change', function (e, data) {
			var havePrev = true;
			var haveNext = true;
			var form;
			switch (data.step) {
				case 1:
					if (data.direction == 'next') {
						form = $('#step1').find('>form');
						if (form.find('input').jqBootstrapValidation('hasErrors')) {
							form.submit();
							e.preventDefault();
							return;
						}
					}
					break;
				case 2:
					if (data.direction != 'next') {
						havePrev = false;
						break;
					}
					if (map !== undefined || searcher !== undefined || searcher.getSelectedLocation() !== undefined) {
						console.log('Your location is: ' + searcher.getSelectedLocation());
					} else {
						e.preventDefault();
						return;
					}
					break;
				case 3:
					if (data.direction == 'next') {
						form = $('#step3').find('>form');
						if (form.find('input').jqBootstrapValidation('hasErrors')) {
							form.submit();
							e.preventDefault();
							return;
						}
						resultData = {
							teamname: $('#inputName').val(),
							email: $('#inputEmail').val(),
							phone: $('#inputPhone').val(),
							street: $('#inputStreet').val(),
							zip: $('#inputZip').val(),
							geolocation: searcher.getSelectedLocation(),
							member1: $('#inputMemberName1').val(),
							member2: $('#inputMemberName2').val(),
							member3: $('#inputMemberName3').val(),
							allergies: $('#allergies').val(),
							vegetarians: $('#vegetarians').val(),
							accepted: $('#terms').is(':checked')
						};

						var tBody = '';
						tBody += '<tr><td>Teamname</td><td>'+resultData.teamname+'</td></tr>';
						tBody += '<tr><td>E-Mail-Adresse</td><td>'+resultData.email+'</td></tr>';
						tBody += '<tr><td>Handynummer</td><td>'+resultData.phone+'</td></tr>';
						tBody += '<tr><td>Adresse</td><td>'+resultData.street+', '+resultData.zip+' Dresden</td></tr>';
						tBody += '<tr><td>Eure Namen</td><td>'+resultData.member1+', '+resultData.member2+', '+resultData.member3+'</td></tr>';
						tBody += '<tr><td>Allergien</td><td>'+ ((resultData.allergies == '') ? 'keine' : resultData.allergies )+'</td></tr>';
						tBody += '<tr><td>Anzahl Vegetarier</td><td>'+resultData.vegetarians+'</td></tr>';

						$('#step4 tbody').html(tBody);

						myNextBtn.html('Anmeldung abschicken').addClass('btn-primary'); // Weiter-Button -> Abschicken-Button
					}
					break;
				case 4:
					if (data.direction == 'next') {
						form = $('#step3').find('>form');
						if (form.find('input').jqBootstrapValidation('hasErrors')) {
							form.submit();
							e.preventDefault();
							return;
						}
						alert('(Would) send data via ajax:\n' + JSON.stringify(resultData, null, '\t'));

						// success callback -> step5
						// error callback -> step6
						haveNext = false;
					} else {
						myNextBtn.html('weiter <i class="icon-arrow-right"></i>').removeClass('btn-primary'); // Abschicken-Button -> Weiter-Button
					}
					break;
				case 5:
					e.preventDefault();
					return;

			}
			myNextBtn.attr('disabled', false === haveNext);
			myPrevBtn.attr('disabled', false === havePrev);
		});
		myWizard.on('changed', function (e, data) {
			var item = myWizard.data('wizard').selectedItem().step;
			if (item === 2) {
				if (map == undefined) {
					displayMap();
				}
				var qry = $('#inputStreet').val() + ', ' + $('#inputZip').val() + ', Dresden';
				searcher.geosearch(qry);
			}

		});
		myWizard.on('finished', function (e, data) {
			$('.wizard-footer').hide(); // Navigationsleiste ausblenden
		});

		myPrevBtn.on('click', function () {
			$('#myWizard').wizard('previous');
		});

		myNextBtn.on('click', function () {
			$('#myWizard').wizard('next', 'foo');
		});

		// myPrevBtn.attr('disabled', true);

		$('input').jqBootstrapValidation();
	});
