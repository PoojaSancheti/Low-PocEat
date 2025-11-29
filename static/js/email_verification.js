document.addEventListener('DOMContentLoaded', function () {
    console.log("JavaScript loaded");

    const verifyEmailBtn = document.getElementById('verify-email-btn');
    const emailField = document.getElementById('email');
    const feedbackDiv = document.getElementById('email-feedback');
    const passwordFields = document.getElementById('password-fields');

    if (!verifyEmailBtn) {
        console.error("Verify Email button not found!");
        return;
    }

    verifyEmailBtn.addEventListener('click', function () {
        console.log("Verify Email button clicked");

        const email = emailField.value.trim();
        console.log("Email entered:", email);

        if (!email) {
            feedbackDiv.innerText = "Please enter a valid email address.";
            return;
        }

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

        fetch('/check-email/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ email: email })
        })
            .then(response => response.json())
            .then(data => {
                console.log("Server response:", data);
                if (data.status === 'success') {
                    feedbackDiv.innerText = data.message;
                    passwordFields.style.display = 'block';
                } else {
                    feedbackDiv.innerText = data.message;
                }
            })
            .catch(error => {
                feedbackDiv.innerText = "An error occurred. Please try again.";
                console.error("Error:", error);
            });
    });
});
