document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("contactForm");
    const responseMessage = document.getElementById("responseMessage");

    form.addEventListener("submit", async function (event) {
        event.preventDefault(); // Evitar recargar la página

        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch("/contact", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(jsonData),
            });

            const result = await response.json();
            responseMessage.textContent = result.message;
            responseMessage.classList.remove("hidden");

            form.reset(); // Limpiar el formulario después de enviarlo
        } catch (error) {
            responseMessage.textContent = "Error al enviar el mensaje.";
            responseMessage.classList.remove("hidden");
        }
    });
});
