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
			notFoundMessage: '<strong>Die Adresse konnte nicht gefunden werden.</strong> Bitte gehe zurück und überprüfe die Eingaben. Sollte die Adresse trotzdem nicht gefunden werden, kontaktiere uns bitte unter <a href="mailto:meet&eat@exma.de">meet&amp;eat@exma.de</a>'
		});
		searcher.addTo(map);

	}

	$(function () {
		var myWizard = $('#myWizard');
		var myPrevBtn = $('#wizard-prev');
		var myNextBtn = $('#wizard-next');


		myWizard.wizard();
		myWizard.on('change', function (e, data) {
			var havePrev = true;
			var haveNext = true;
			var form;
			switch (data.step) {
				case 1:
					if (data.direction == "next") {
						form = $("#step1").find(">form");
						if (form.find("input").jqBootstrapValidation("hasErrors")) {
							form.submit();
							e.preventDefault();
							return;
						}
					}
					break;
				case 2:
					if (data.direction != "next")
						break;
					if (map !== undefined || searcher !== undefined || searcher.getSelectedLocation() !== undefined) {
						console.log("Your location is: " + searcher.getSelectedLocation());
					} else {
						e.preventDefault();
						return;
					}
					break;
				case 3:
					if (data.direction === 'next') {
						form = $("#step3").find(">form");
						if (form.find("input").jqBootstrapValidation("hasErrors")) {
							form.submit();
							e.preventDefault();
							return;
						}
						var resultData = {
							teamname: $("#inputName").val(),
							email: $("#inputEmail").val(),
							phone: $("#inputPhone").val(),
							street: $("#inputStreet").val(),
							zip: $("#inputZip").val(),
							geolocation: searcher.getSelectedLocation(),
							member1: $("#inputMemberName1").val(),
							member2: $("#inputMemberName2").val(),
							member3: $("#inputMemberName3").val(),
							allergies: $("#allergies").val(),
							vegetarians: $("#vegetarians").val(),
							accepted: $("#terms").is(":checked")
						};
						alert("(Would) send data via ajax:\n" + JSON.stringify(resultData, null, '\t'));
						haveNext = false;
					}

					havePrev = false;
					break;
				case 4:
					e.preventDefault();
					return;

			}
			myNextBtn.attr("disabled", false === haveNext);
			myPrevBtn.attr("disabled", false === havePrev);
		});
		myWizard.on('changed', function (e, data) {
			var item = myWizard.data("wizard").selectedItem().step;
			if (item === 2) {
				if (map == undefined) {
					displayMap();
				}
				var qry = $("#inputStreet").val() + ", " + $("#inputZip").val() + ", Dresden";
				searcher.geosearch(qry);
				$modal.find(".btn-primary").on("click", function (e) {
					e.preventDefault();
					console.log(searcher.getSelectedLocation());
					alert(searcher.getSelectedLocation());
				});
			}
			console.log('changed');

		});
		myWizard.on('finished', function (e, data) {
			console.log('finished');
			myWizard.data("wizard").$prevBtn.attr("disabled", true);
		});

		myPrevBtn.on('click', function () {
			$('#myWizard').wizard('previous');
		});
		myPrevBtn.attr("disabled", true);
		myNextBtn.on('click', function () {
			$('#myWizard').wizard('next', 'foo');
		});
		$('#wizard-logItem').on('click', function () {
			var item = $('#myWizard').wizard('selectedItem');
			console.log(item.step);
		});
		$("input").jqBootstrapValidation();
	});
