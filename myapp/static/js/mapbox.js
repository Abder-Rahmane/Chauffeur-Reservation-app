  mapboxgl.accessToken = '';
  var map = new mapboxgl.Map({
      container: 'map',
      style: 'mapbox://styles/mapbox/streets-v11',
      center: [2.3522, 48.8566],
      scrollZoom: false,
      dragPan: false,
      doubleClickZoom : false,
      zoom: 7
  });
  
  function distanceBetweenPoints(point1, point2) {
      var dx = point1[0] - point2[0];
      var dy = point1[1] - point2[1];
      return Math.sqrt(dx*dx + dy*dy);
  }
  
  
  map.on('load', function () {
      map.loadImage('https://cdn-icons-png.flaticon.com/512/57/57123.png', function(error, image) {
          if (error) throw error;
  
          map.addImage('car-image', image);
  
          map.addSource('vtcCars', {
              type: 'geojson',
              data: {
                  type: 'FeatureCollection',
                  features: []
              }
          });
  
          map.addLayer({
              id: 'carsLayer',
              type: 'symbol',
              source: 'vtcCars',
              layout: {
                  'icon-image': 'car-image', 
                  'icon-size': 0.02, 
                  'icon-rotation-alignment': 'map',
                  'icon-allow-overlap': true,
                  'icon-ignore-placement': true,
              }
          });
  
          var vehicles = [];
  
          for (var i = 0; i < 41; i++) {
              var isTooClose;
              var newVehicle;
  
              do {
                  newVehicle = {
                      position: [
                          2.3522 + (Math.random() - 0.5) * 2.5,
                          48.8566 + (Math.random() - 0.5) * 2.5
                      ],
                      bearing: Math.random() * 360
                  };
  
                  isTooClose = vehicles.some(function(vehicle) {
                      return distanceBetweenPoints(vehicle.position, newVehicle.position) < 0.02;
                  });
              } while (isTooClose);
  
              vehicles.push(newVehicle);
          }
  
          function updateVehicles() {
              var speed = 0.001;
  
              var features = vehicles.map(function (vehicle) {
                  vehicle.position[0] += Math.cos(vehicle.bearing * Math.PI / 180) * speed;
                  vehicle.position[1] += Math.sin(vehicle.bearing * Math.PI / 180) * speed;
                  vehicle.bearing += (Math.random() - 0.5) * 20; 
  
                  return {
                      type: 'Feature',
                      geometry: {
                          type: 'Point',
                          coordinates: vehicle.position
                      },
                      properties: {
                          bearing: vehicle.bearing
                      }
                  };
              });
  
              map.getSource('vtcCars').setData({
                  type: 'FeatureCollection',
                  features: features
              });
          }
  
          updateVehicles(); 
  
          setInterval(function () {
              updateVehicles();
          }, 1600);
      });
  });
  
  function isValidCoords(coords) {
      return coords && typeof coords[0] === 'number' && !isNaN(coords[0]) && typeof coords[1] === 'number' && !isNaN(coords[1]);
  }
  
  function updateMapBounds() {
      if (fromCoords && toCoords) {
          var bounds = new mapboxgl.LngLatBounds();
  
          if (isValidCoords(fromCoords)) bounds.extend(fromCoords);
          if (isValidCoords(toCoords)) bounds.extend(toCoords);
          if (isValidCoords(window.stepCoords)) bounds.extend(window.stepCoords);
  
           console.log("fromCoords:", fromCoords);
          console.log("toCoords:", toCoords);
          console.log(" currentRoute = ", currentRoute);
          if (currentRoute && currentRoute.length) {
              currentRoute.forEach(function(coord, index) {
                  console.log("route coord #" + index + ":", coord);
                  if (isValidCoords(coord) === false) {
                      console.error("Invalid coord at currentRoute index", index, coord);
                  } else {
                      bounds.extend(coord);
                  }
              });
          if (!bounds.getNorthEast() || !bounds.getSouthWest()) {
              console.error('Bounds are not properly defined:', bounds);
              return;
          }
  
          console.log('start fitBounds');
          console.log(bounds.toArray());
          try {
            map.fitBounds(bounds, {padding: 100, maxZoom: 10});
              console.log('end fitBounds');
          } catch (error) {
              console.error('Error during fitBounds:', error);
          }
          }
          
      }
  }
 
 var markers = {
     from: null,
     to: null,
     step: null
 };
 
 function manageMarkers(coords, type) {
     if (markers[type]) {
         markers[type].remove();
     }
 
     let colors = {
         from: 'black',
         to: 'black',
         step: 'black'
     };
 
     if (coords) {
         markers[type] = new mapboxgl.Marker({ color: colors[type] })
             .setLngLat(coords)
             .addTo(map);
     } else {
         markers[type] = null;
     }
 
     if (markers.step) {

     } else {
         if (markers.from && markers.to && markers.step) {
             markers.step.remove();
             markers.step = null;
         }
     }
     updateMapBounds();
 }
 
 var currentRoute = null;
 
 function addRoute(from, to, stepCoords) {
     console.log("addRoute function called"); 
 
     console.log("From:", from, "To:", to, "StepCoords:", stepCoords);
 
     try {
         var apiUrl = `https://api.mapbox.com/directions/v5/mapbox/driving/${from[0]},${from[1]};${to[0]},${to[1]}?geometries=geojson&access_token=${mapboxgl.accessToken}`;
 
         var stepInputElem = document.getElementById('step_place');
         if (window.stepCoords) {
             apiUrl = `https://api.mapbox.com/directions/v5/mapbox/driving/${from[0]},${from[1]};${window.stepCoords[0]},${window.stepCoords[1]};${to[0]},${to[1]}?geometries=geojson&access_token=${mapboxgl.accessToken}`;
         }
 
         console.log("Fetching API with URL:", apiUrl); 
 
         fetch(apiUrl)
             .then(response => {
                 if (!response.ok) {
                     throw new Error("Response from Mapbox API was not ok");
                 }
                 return response.json();
             })
             .then(data => {
                 if (!data.routes || !data.routes[0]) {
                     throw new Error("No routes data found in the response.");
                 }
 
                 var distance = data.routes[0].distance / 1000; 
                 var duration = data.routes[0].duration / 60;  
                 currentRoute = data.routes[0].geometry.coordinates;
 
                 console.log("Received route coordinates:", currentRoute); 
                 updateMapBounds();  
 
                 updateBanner(duration, distance); 
                 
 
                 var route = {
                     'type': 'FeatureCollection',
                     'features': [
                         {
                             'type': 'Feature',
                             'geometry': data.routes[0].geometry,
                             'properties': {}
                         }
                     ]
                 };
 
                 if (map.getSource('route')) {
                     map.getSource('route').setData(route);
                 } else {
                     map.addLayer({
                         'id': 'route',
                         'type': 'line',
                         'source': {
                             'type': 'geojson',
                             'data': route
                         },
                         'layout': {
                             'line-join': 'round',
                             'line-cap': 'round'
                         },
                         'paint': {
                             'line-color': '#000',
                             'line-width': 3
                         }
                     });
                 }
             })
             .catch(error => {
                 console.error('Erreur API Mapbox:', error);
             });
     } catch (error) {
         console.error("Error in addRoute:", error); 
     }
 }
 
 function calculateAndDisplayRoute() {
     console.log("Inside calculateAndDisplayRoute: ", fromCoords, toCoords);
     if (fromCoords && toCoords) {
         addRoute(fromCoords, toCoords); 
     }else{
         console.log("erreur calculateAndDisplayRoute"); 
     }
     
 }
 
 
 
 
 
 
 
 
 
 