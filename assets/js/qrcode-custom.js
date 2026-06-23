function downloadQRCode() {
    const qrImg = document.querySelector("#qrcode img");

    if (!qrImg) {
        alert("Please generate a QR code first.");
        return;
    }

    const link = document.createElement("a");
    link.href = qrImg.src;
    link.download = "qrcode.png";

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadQRCode_from_Canvas() {
    const qrContainer = document.getElementById("qrcode");

    const img = qrContainer.querySelector("img");
    const canvas = qrContainer.querySelector("canvas");

    let dataUrl = null;

    if (img) {
        dataUrl = img.src;
    } else if (canvas) {
        dataUrl = canvas.toDataURL("image/png");
    }

    if (!dataUrl) {
        alert("Please generate a QR code first.");
        return;
    }

    const link = document.createElement("a");
    link.href = dataUrl;
    link.download = "qrcode.png";
    link.click();
}



function downloadQRCode_Polished() {
    const qrCanvas = document.querySelector("#qrcode canvas");

    if (!qrCanvas) {
        alert("Please generate a QR code first.");
        return;
    }

    const padding = 40;
    const borderRadius = 20;

    // Create a larger canvas for the final image
    const outputCanvas = document.createElement("canvas");
    outputCanvas.width = qrCanvas.width + (padding * 2);
    outputCanvas.height = qrCanvas.height + (padding * 2);

    const ctx = outputCanvas.getContext("2d");

    // Draw rounded white background
    ctx.fillStyle = "#FFFFFF";
    ctx.beginPath();
    ctx.roundRect(
        0,
        0,
        outputCanvas.width,
        outputCanvas.height,
        borderRadius
    );
    ctx.fill();

    // Draw QR code centered within the padding
    ctx.drawImage(
        qrCanvas,
        padding,
        padding,
        qrCanvas.width,
        qrCanvas.height
    );

    // Download
    const link = document.createElement("a");
    link.href = outputCanvas.toDataURL("image/png");
    link.download = "armada-qrcode.png";
    link.click();
}