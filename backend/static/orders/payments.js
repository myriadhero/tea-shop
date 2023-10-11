// This is a public sample test API key.
// Don’t submit any personally identifiable information in requests made with this key.
// Sign in to see your own test API key embedded in code samples.
const stripe = Stripe(stripePublicKey);

const appearance = {
  theme: "stripe",
};
const options = {
  mode: "shipping",
  allowedCountries: ["AU"],
  ...(stripeDefaultAddressValues && {
    defaultValues: stripeDefaultAddressValues,
  }),
};
const elements = stripe.elements({
  appearance,
  clientSecret: stripeClientSecret,
});
const addressElement = elements.create("address", options);
const paymentElement = elements.create("payment");
addressElement.mount("#address-element");
paymentElement.mount("#payment-element");

// initialize();
checkStatus();

document
  .querySelector("#payment-form")
  .addEventListener("submit", handleSubmit);

async function handleSubmit(e) {
  e.preventDefault();
  setLoading(true);

  const form = e.target;
  const data = new FormData(form);

  let { complete, value } = await addressElement.getValue();

  if (!complete) {
    setLoading(false);
    showMessage("Address is incomplete.");
    return;
  }
  const address = value;
  data.append("name", address.name);
  data.append("city", address.address.city);
  data.append("country", address.address.country);
  data.append("postal_code", address.address.postal_code);
  data.append("state", address.address.state);
  data.append("line1", address.address.line1);
  data.append("line2", address.address.line2);

  // send user data to server (but not financial data!)
  const serverResponse = await fetch(orderDetailsUpdateUrl, {
    method: "post",
    body: data,
  });

  // if not success, show error message and return
  if (!serverResponse.ok) {
    setLoading(false);
    // get error messages to show
    try {
      const serverResponseData = await serverResponse.json();
      // TODO: design proper error messages
      showMessage(serverResponseData.errors);
    } catch (err) {
      // if error messages not available, show generic error message
      showMessage(
        "An unexpected error occurred. Please try refreshing the page."
      );
    }
    return;
  }

  const { error } = await stripe.confirmPayment({
    elements,
    confirmParams: {
      // Payment completion page
      return_url: stripeRedirectSuccessUrl,
    },
  });

  // This point will only be reached if there is an immediate error when
  // confirming the payment. Otherwise, your customer will be redirected to
  // your `return_url`. For some payment methods like iDEAL, your customer will
  // be redirected to an intermediate site first to authorize the payment, then
  // redirected to the `return_url`.
  if (error.type === "card_error" || error.type === "validation_error") {
    showMessage(error.message);
  } else {
    showMessage("An unexpected error occurred.");
  }

  setLoading(false);
}

// Fetches the payment intent status after payment submission
async function checkStatus() {
  const clientSecret = new URLSearchParams(window.location.search).get(
    "payment_intent_client_secret"
  );

  if (!clientSecret) {
    return;
  }

  const { paymentIntent } = await stripe.retrievePaymentIntent(clientSecret);

  switch (paymentIntent.status) {
    case "succeeded":
      showMessage("Payment succeeded!");
      break;
    case "processing":
      showMessage("Your payment is processing.");
      break;
    case "requires_payment_method":
      showMessage("Your payment was not successful, please try again.");
      break;
    default:
      showMessage("Something went wrong.");
      break;
  }
}

// ------- UI helpers -------

function showMessage(messageText) {
  const messageContainer = document.querySelector("#payment-message");

  messageContainer.classList.remove("hidden");
  messageContainer.textContent = messageText;

  setTimeout(function () {
    messageContainer.classList.add("hidden");
    messageContainer.textContent = "";
  }, 4000);
}

// Show a spinner on payment submission
function setLoading(isLoading) {
  if (isLoading) {
    // Disable the button and show a spinner
    document.querySelector("#submit").disabled = true;
    document.querySelector("#spinner").classList.remove("hidden");
    document.querySelector("#button-text").classList.add("hidden");
  } else {
    document.querySelector("#submit").disabled = false;
    document.querySelector("#spinner").classList.add("hidden");
    document.querySelector("#button-text").classList.remove("hidden");
  }
}
