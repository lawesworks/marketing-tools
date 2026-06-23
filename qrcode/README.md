# Armada QR Code Generator

A lightweight web-based QR Code Generator for creating and downloading QR codes for URLs, WiFi networks, contact information, and other supported QR payload formats.

## Features

* Generate QR codes directly in the browser
* Supports URLs, text, and other QR-compatible data formats
* Download generated QR codes as PNG images
* Clean modern user interface
* No backend required
* Fully client-side operation

## Current Capabilities

### URL QR Codes

Generate QR codes that open websites when scanned.

Example:

```text
https://armada.ai
```

### Text QR Codes

Generate QR codes containing plain text.

Example:

```text
Armada Vision AI Demo
```

### WiFi QR Codes

Generate QR codes that allow smartphones to join WiFi networks without manually entering credentials.

Example:

```text
WIFI:T:WPA;S:ArmadaGuest;P:Password123;;
```

## Downloading QR Codes

Generated QR codes can be downloaded as PNG images with:

* White padded background
* Rounded corners
* Presentation-ready formatting

## Technology Stack

* HTML5
* CSS3
* JavaScript
* jQuery
* QRCode.js

## Project Structure

```text
qrcode/
├── assets/
│   ├── css/
│   ├── js/
│   └── images/
├── index.html
├── qrcode.js
├── qrcode.min.js
└── README.md
```

## Future Enhancements

Planned QR code templates include:

* Contact Cards (vCard)
* Email
* SMS
* Phone Numbers
* Google Maps Locations
* PDF Downloads
* Calendar Events
* App Store Links

## License

This project utilizes the open-source QRCode.js library and is intended for internal marketing, sales, and demonstration workflows.
