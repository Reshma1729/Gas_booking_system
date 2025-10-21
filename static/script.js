// toggle login/register
document.addEventListener("DOMContentLoaded", () => {
  const showLogin = document.getElementById("show-login");
  const registerForm = document.getElementById("register-form");
  const loginForm = document.getElementById("login-form");

  if (showLogin) {
    showLogin.addEventListener("click", (e) => {
      e.preventDefault();
      registerForm.classList.add("hidden");
      loginForm.classList.remove("hidden");
    });
  }

  // // payment method show/hide
  // const paymentSelect = document.getElementById("payment_type");
  // if (paymentSelect) {
  //   paymentSelect.addEventListener("change", () => {
  //     const card = document.getElementById("card-details");
  //     const online = document.getElementById("online-details");
  //     if (card) card.classList.add("hidden");
  //     if (online) online.classList.add("hidden");

  //     console.log("paymentSelect.value", paymentSelect.value);
  //     if (paymentSelect.value === "card") {
  //       if (card) card.classList.remove("hidden");
  //     } else if (paymentSelect.value === "online") {
  //       if (online) online.classList.remove("hidden");
  //     }
  //   });
  // }

  // const paymentType = document.getElementById('payment_type');
  // const cardDetails = document.getElementById('card-details');
  // const onlineDetails = document.getElementById('online-details');

  // paymentType.addEventListener('change', function() {
  //   const value = this.value;

  //   // Hide all
  //   cardDetails.classList.add('hidden');
  //   onlineDetails.classList.add('hidden');

  //   // Show based on selection
  //   if (value === 'card') {
  //     cardDetails.classList.remove('hidden');
  //   } else if (value === 'online') {
  //     onlineDetails.classList.remove('hidden');
  //   }
  //   // COD does not show any additional fields
  // });


  // pincode numeric only enforcement
  const pin = document.getElementById("pincode");
  if (pin) {
    pin.addEventListener("input", function() {
      this.value = this.value.replace(/\D/g, '').slice(0,6);
    });
  }
});


