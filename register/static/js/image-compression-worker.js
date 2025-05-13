importScripts('https://cdn.jsdelivr.net/npm/browser-image-compression@2.0.2/dist/browser-image-compression.js');

self.onmessage = function(e) {
    const blob = e.data;

    compressImage(blob)
        .then(compressedBlob => self.postMessage(compressedBlob))
        .catch(error => self.postMessage({ error: error.message }));
};

function compressImage(blob) {
    const options = {
        maxSizeMB: 0.3,
        maxWidthOrHeight: 1080,
        useWebWorker: true
    };

    return imageCompression(blob, options);
}