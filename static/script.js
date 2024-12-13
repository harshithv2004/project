// Preview the uploaded image for encoding
document.getElementById("image")?.addEventListener("change", function (event) {
    const preview = document.createElement("img");
    preview.id = "previewImage";
    preview.style.maxWidth = "100%";
    preview.style.marginTop = "10px";

    const container = event.target.closest("form").querySelector(".preview-container");
    if (container) {
        container.innerHTML = ""; // Clear previous preview
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        }
    }
});

// Preview the uploaded encoded image for decoding
document.getElementById("encodedImage")?.addEventListener("change", function (event) {
    const preview = document.createElement("img");
    preview.id = "previewEncodedImage";
    preview.style.maxWidth = "100%";
    preview.style.marginTop = "10px";

    const container = event.target.closest("form").querySelector(".preview-container");
    if (container) {
        container.innerHTML = ""; // Clear previous preview
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function (e) {
                preview.src = e.target.result;
                container.appendChild(preview);
            };
            reader.readAsDataURL(file);
        }
    }
});

// Handle decoding message and dynamically display it in a modal
document.querySelector("form[action='/decode']")?.addEventListener("submit", async function (event) {
    event.preventDefault();
    const formData = new FormData(this);

    const response = await fetch("/decode", {
        method: "POST",
        body: formData,
    });

    const modal = document.getElementById("decodedModal");
    const messageContainer = document.getElementById("decodedMessage");

    if (response.ok) {
        const message = await response.text();
        messageContainer.textContent = `Decoded Message: ${message}`;
        modal.style.display = "block"; // Show the modal
    } else {
        messageContainer.textContent = "Failed to decode the message.";
        modal.style.display = "block"; // Show the modal even on failure
    }
});

// Close the modal when the user clicks the close button
document.getElementById("closeModal")?.addEventListener("click", function () {
    const modal = document.getElementById("decodedModal");
    modal.style.display = "none"; // Hide the modal
});

// Close the modal if the user clicks outside the modal content
window.addEventListener("click", function (event) {
    const modal = document.getElementById("decodedModal");
    if (event.target === modal) {
        modal.style.display = "none"; // Hide the modal when clicked outside
    }
});
