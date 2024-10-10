var fromCoords, toCoords, fromAutocomplete, toAutocomplete;

const parisPostcodes = [
"75001", "75002", "75003", "75004", "75005",
"75006", "75007", "75008", "75009", "75010",
"75011", "75012", "75013", "75014", "75015",
"75016", "75017", "75018", "75019", "75020"
 ];

const airportNames = {
    'ChIJW89MjgM-5kcRLKZbL5jgKwQ': 'CDG',
    'ChIJHTtq-rF15kcRIoTbQ9feeJ0': 'Orly'
};

var fromPostalCode = "";
var fromPlaceId = "";
var toPlaceId = "";

function initMap() {
    var options = {
        types: ['geocode', 'establishment'],
        componentRestrictions: {country: 'fr'}
    };
    
    fromAutocomplete = new google.maps.places.Autocomplete(
        document.getElementById('fromPlace'),
        options
    );

    toAutocomplete = new google.maps.places.Autocomplete(
        document.getElementById('toPlace'),
        options
    );

    

    fromAutocomplete.addListener('place_changed', function() {
        var place = fromAutocomplete.getPlace();
        if (!place.geometry) {
            console.log("Autocomplete's returned place contains no geometry");
            return;
        }
        fromCoords = [place.geometry.location.lng(), place.geometry.location.lat()];
        console.log("fromCoords:", fromCoords);
        manageMarkers(fromCoords, 'from');
    
        var isAirportOrStation = place.types.includes('airport') || place.types.includes('train_station');
    
        var address = place.formatted_address;
        fromPostalCode = ""; 
    
        if (!isAirportOrStation) {
            var postalCode = "";
            for (var i = 0; i < place.address_components.length; i++) {
                var addressType = place.address_components[i].types[0];
                if (addressType === 'postal_code') {
                    postalCode = place.address_components[i]['long_name'];
                    break;
                }
            }
            
            fromPostalCode = postalCode; 
        
            
            if (parisPostcodes.includes(postalCode)) {
                console.log("L'adresse est dans Paris, code postal: " + postalCode);
                fromPlaceId = place.place_id;
            }
        
            if (postalCode && !address.includes(postalCode)) {
                address += ', ' + postalCode;
            }
        } else {
            
            address = place.name;
        }
        
        document.getElementById('fromPlace').value = address;
        calculateAndDisplayRoute();
    });

    toAutocomplete.addListener('place_changed', function() {
        var place = toAutocomplete.getPlace();
        if (!place.geometry) {
            console.log("Autocomplete's returned place contains no geometry");
            return;
        }
        toCoords = [place.geometry.location.lng(), place.geometry.location.lat()];
        console.log("toCoords:", toCoords);
        manageMarkers(toCoords, 'to');

        var isAirportOrStation = place.types.includes('airport') || place.types.includes('train_station');

        var address = place.formatted_address;

        if (isAirportOrStation) {
            
            address = place.name;

            if (airportNames.hasOwnProperty(place.place_id)) {
                console.log("Le lieu est l'aéroport: " + airportNames[place.place_id]);
                toPlaceId = place.place_id;
            }

        } else {
            
            address = place.name;
        }
        document.getElementById('toPlace').value = address; 
        calculateAndDisplayRoute();
        
    
        
    });

}

// function calculateAndDisplayRouteIfBothPointsDefined() {
//     console.log('calculateAndDisplayRouteIfBothPointsDefined called')
//     if (fromCoords && toCoords) {
//         calculateAndDisplayRoute();
//     } else {
//         console.log("Both start and end points are not defined yet.");
//     }
// }

// function calculateAndDisplayRoute() {
//     console.log("Inside calculateAndDisplayRoute: ", fromCoords, toCoords);

//  }

var isStepInputAdded = false; 

function initializeStepAutocomplete() {
    var options = {
        types: ['geocode', 'establishment'],
        componentRestrictions: {country: 'fr'}
    };
    var stepInputElem = document.getElementById('step_place');
    if (stepInputElem) {
        var autocomplete = new google.maps.places.Autocomplete(stepInputElem, options);
        
        autocomplete.addListener('place_changed', function() {
            var place = autocomplete.getPlace();
            if (place.geometry) {
                window.stepCoords = [place.geometry.location.lng(), place.geometry.location.lat()];
                manageMarkers(window.stepCoords, 'step');
            } else {
                console.log('Pas de détails disponibles pour la saisie:', place.name);
                window.stepCoords = null;
                manageMarkers(null, 'step');
            }
            calculateAndDisplayRoute();
        });
    } else {
        console.error("Élément 'step_place' non trouvé !");
    }
}

google.maps.event.addDomListener(window, 'load', initMap);