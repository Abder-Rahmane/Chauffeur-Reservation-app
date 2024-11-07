function updateAddresses() {
    var departureAddress = document.getElementById('fromPlace').value;
    var arrivalAddress = document.getElementById('toPlace').value;
    var stepAddress  = document.getElementById('step_place');

    if (stepAddress) {
        var stepInputElem = document.getElementById('step_place').value;
        document.getElementById('step-address-container').style.display = 'block';
        document.getElementById('step-address-container1').style.display = 'block';
        document.getElementById('step-address-container2').style.display = 'block';
        document.getElementById('step-address-container3').style.display = 'block';

        document.getElementById('departure-address-step2').textContent = departureAddress;
        document.getElementById('arrival-address-step2').textContent = arrivalAddress;
        document.getElementById('step-address-step2').textContent = stepInputElem;

        document.getElementById('departure-address-step3').textContent = departureAddress;
        document.getElementById('arrival-address-step3').textContent = arrivalAddress;
        document.getElementById('step-address-step3').textContent = stepInputElem;

        document.getElementById('departure-address-step4').textContent = departureAddress;
        document.getElementById('arrival-address-step4').textContent = arrivalAddress;
        document.getElementById('step-address-step4').textContent = stepInputElem;
        
        document.getElementById('departure-address-step5').textContent = departureAddress;
        document.getElementById('arrival-address-step5').textContent = arrivalAddress;
        document.getElementById('step-address-step5').textContent = stepInputElem;

        document.getElementById('roadmap-image_base').style.display ='none';   
        document.getElementById('roadmap-image1').style.display ='initial';

        document.getElementById('roadmap-image_base1').style.display ='none';   
        document.getElementById('roadmap-image2').style.display ='initial';

        document.getElementById('roadmap-image_base2').style.display ='none';   
        document.getElementById('roadmap-image3').style.display ='initial';

        document.getElementById('roadmap-image_base3').style.display ='none';   
        document.getElementById('roadmap-image4').style.display ='initial';


    } else {

        document.getElementById('step-address-container').style.display = 'none';
        document.getElementById('step-address-container1').style.display = 'none';
        document.getElementById('step-address-container2').style.display = 'none';
        document.getElementById('step-address-container3').style.display = 'none';
        document.getElementById('departure-address-step2').textContent = departureAddress;
        document.getElementById('arrival-address-step2').textContent = arrivalAddress;

        document.getElementById('departure-address-step3').textContent = departureAddress;
        document.getElementById('arrival-address-step3').textContent = arrivalAddress;

        document.getElementById('departure-address-step4').textContent = departureAddress;
        document.getElementById('arrival-address-step4').textContent = arrivalAddress;
        
        document.getElementById('departure-address-step5').textContent = departureAddress;
        document.getElementById('arrival-address-step5').textContent = arrivalAddress;

        document.getElementById('roadmap-image_base').style.display ='initial';   
        document.getElementById('roadmap-image1').style.display ='none';

        document.getElementById('roadmap-image_base1').style.display ='initial';   
        document.getElementById('roadmap-image2').style.display ='none';

        document.getElementById('roadmap-image_base2').style.display ='initial';   
        document.getElementById('roadmap-image3').style.display ='none';

        document.getElementById('roadmap-image_base3').style.display ='initial';   
        document.getElementById('roadmap-image4').style.display ='none';
    }
}


function updateBanner(time, distance) {
    let timeStr, distanceStr = Math.round(distance).toString();
    
    if (time >= 60) {
        let hours = Math.floor(time / 60);
        let minutes = Math.round(time % 60);
        timeStr = `${hours}h${String(minutes).padStart(2, '0')}`;
    } else {
        timeStr = Math.round(time) + ' minutes';
    }
    
    var banner = document.querySelector('.banner-time-km span');
    var banner1 = document.querySelector('.banner-time-km1 span');
    var banner2 = document.querySelector('.banner-time-km2 span');
    var banner3 = document.querySelector('.banner-time-km3 span');
    banner.textContent = `⌛ Environ ${timeStr} et ${distanceStr} km de routes`;
    banner1.textContent = `⌛ Environ ${timeStr} et ${distanceStr} km de routes`;
    banner2.textContent = `⌛ Environ ${timeStr} et ${distanceStr} km de routes`;
    banner3.textContent = `⌛ Environ ${timeStr} et ${distanceStr} km de routes`;

    for (const vehicleType in vehicleCosts) {
        calculateAndDisplayCost(vehicleType, time, distance);
    }
}

function selectVehicle(element, vehicleType) {
    const optionPrice = element.querySelector('.s-price').textContent;
    const optionDetailsStrong = element.querySelector('.details strong').textContent;
    const optionDetailsSTP = element.querySelector('.details .s-t-p').textContent;
    
    document.querySelectorAll('.banner-price-auto strong').forEach((bannerStrong) => {
        bannerStrong.textContent = optionDetailsStrong;
    });

    document.querySelectorAll('.banner-price-auto .s-t-p').forEach((bannerSTP) => {
        bannerSTP.textContent = optionDetailsSTP;
    });

    document.querySelectorAll('.banner-price-auto .s-price').forEach((bannerPrice) => {
        bannerPrice.textContent = optionPrice;
        bannerPrice.style.color = '#000000';
    });

    const vehicleInput = document.querySelector('#selectedVehicle');
    vehicleInput.value = vehicleType;

    const price = document.querySelector(`.price[data-vehicle-type="${vehicleType}"] .s-price`).innerText.replace('€', '');
    document.getElementById('selectedPrice').value = price;

    document.querySelectorAll('.option').forEach((veh) => {
        veh.classList.remove('selected');
    });
    
    element.classList.add('selected');
}


function fillForImmediateBooking() {
    if(document.getElementById('fromPlace').value && document.getElementById('toPlace').value) {
        document.getElementById('dateInputId').value = getCurrentDate(); 
        document.getElementById('timeInputId').value = getCurrentTime(); 
        
        showStep(2);
    } else {
        alert("Veuillez remplir les lieux de départ et d'arrivée pour réserver pour maintenant.");
    }
}

function getCurrentDate() {
    const today = new Date();
    const dd = String(today.getDate()).padStart(2, '0');
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const yyyy = today.getFullYear();
    return yyyy + '-' + mm + '-' + dd;
}

function getCurrentTime() {
    const now = new Date();
    const hh = String(now.getHours()).padStart(2, '0');
    const mm = String(now.getMinutes()).padStart(2, '0');
    return hh + ':' + mm;
}

function fillForImmediateBooking() {
    document.getElementById('startDate').value = getCurrentDate();
    document.getElementById('startTime').value = getCurrentTime();
}

function validateStep(stepNumber) {
    let isValid = true;
    let errorMsg = '';
    
    document.getElementById('errorStep1').innerText = '';
    document.getElementById('errorStep2').innerText = '';
    document.getElementById('errorStep3').innerText = '';
    document.getElementById('errorStep4').innerText = '';

    switch(stepNumber) {
        case 1:
             const fromPlace = document.getElementById('fromPlace').value;
             const toPlace = document.getElementById('toPlace').value;
             const startDate = document.getElementById('startDate').value;
             const startTime = document.getElementById('startTime').value;
             
             if(fromPlace === '' || toPlace === '' || startDate === '' || startTime === '') {
                 isValid = false;
                 errorMsg = 'Tous les champs doivent être remplis.';
             }
             break;
              
        case 2:
              const selectedVehicle = document.getElementById('selectedVehicle').value;
              
              if(selectedVehicle === '') {
                  isValid = false;
                  errorMsg = 'Veuillez sélectionner un type véhicule.';
              }
              break;
              
        case 3:
              const inputName = document.getElementById('inputName').value;
              const inputFirstname = document.getElementById('inputFirstname').value;
              const inputTel = document.getElementById('inputTel').value;
              const inputEmail = document.getElementById('inputEmail').value;
                       
              const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
              const phoneRegex = /^[0-9\-\+]{9,15}$/;
      
              if(inputName === '' ||  inputFirstname === '' || inputTel === '' || inputEmail === '') {
                  isValid = false;
                  errorMsg = 'Tous les champs doivent être remplis.';
              }
              else if (!emailRegex.test(inputEmail)) {
                  isValid = false;
                  errorMsg = "L'adresse e-mail n'est pas valide.";
              } 
              else if (!phoneRegex.test(inputTel)) {
                  isValid = false;
                  errorMsg = "Le numéro de téléphone n'est pas valide.";
              }
              else if (/[^a-zA-Z0-9@._-]/.test(inputEmail)) {
                  isValid = false;
                  errorMsg = "L'adresse e-mail ne doit pas contenir de caractères spéciaux.";
              }
              break;
               
        case 4:

            const input1Step4 = document.getElementById('passengersid').value;
            if (input1Step4 === '') {
                isValid = false;
                errorMsg = 'Renseignez le nombre de passagers';
            }
            break;
            
        default:
            isValid = true;
    }
    
    if (!isValid) {
        document.getElementById('errorStep' + stepNumber).innerText = errorMsg;
    }
    
    return isValid;
}

function showStep(stepNumber) {
    if(validateStep(stepNumber - 1)) { 
        document.querySelectorAll('.step').forEach(function (step) {
            step.classList.remove('active');
        });
        updateAddresses();
        updateBannerInfo();

    document.getElementById('step' + stepNumber).classList.add('active');
    document.getElementById('name').textContent = document.getElementById('inputName').value;
    document.getElementById('firstname').textContent = document.getElementById('inputFirstname').value;
    document.getElementById('tel').textContent = document.getElementById('inputTel').value;
    document.getElementById('email').textContent = document.getElementById('inputEmail').value;
    document.getElementById('name1').textContent = document.getElementById('inputName').value;
    document.getElementById('firstname1').textContent = document.getElementById('inputFirstname').value;
    document.getElementById('tel1').textContent = document.getElementById('inputTel').value;
    document.getElementById('email1').textContent = document.getElementById('inputEmail').value;
    
  }
}
document.getElementById('backToStep1').addEventListener('click', function() {
    showStep(1);
});
document.getElementById('backToStep2').addEventListener('click', function() {
    showStep(2);
});
document.getElementById('backToStep3').addEventListener('click', function() {
    showStep(3);
});
document.getElementById('backToStep4').addEventListener('click', function() {
    showStep(4);

});



function updateBannerInfo() {
    var startDate = document.getElementById('startDate').value;
    var startTime = document.getElementById('startTime').value;
    var isRoundTrip = document.querySelector('select[name="is_round_trip"]').value;
    var stepOnReturn = document.querySelector('select[name="step_on_return"]').value;

    var dateTimeText = `${startDate} à ${startTime}`;

    var transferTypeText = isRoundTrip === 'Yes' ? 'Aller / Retour sans étape au retour' : 'Aller simple';
    if (isRoundTrip === 'Yes' && stepOnReturn === 'Yes') {
        transferTypeText += ' avec étape au retour';
    }

    var dateAndTimeElems = document.querySelectorAll('#date_and_time');
    var typeTransfertElems = document.querySelectorAll('#type_transfert');

    dateAndTimeElems.forEach(elem => {
        elem.textContent = dateTimeText;
    });

    typeTransfertElems.forEach(elem => {
        elem.textContent = transferTypeText;
    });
}

function clearField(fieldId) {
    document.getElementById(fieldId).value = '';
}





