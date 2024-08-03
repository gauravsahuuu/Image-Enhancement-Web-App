document.getElementById('uploadButton').addEventListener('click', function() {
    var fileInput = document.getElementById('fileInput');
    var file = fileInput.files[0];

    if (!file) {
        alert('Please select a file!');
        return;
    }

    var formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.original_url && data.enhanced_url) {
            var originalImage = document.getElementById('originalImage');
            var enhancedImage = document.getElementById('enhancedImage');
            var resultSection = document.getElementById('result');
            var imageComparison = document.querySelector('.image-comparison');
            var downloadButton = document.getElementById('downloadButton');

            originalImage.src = data.original_url;
            enhancedImage.src = data.enhanced_url;
            imageComparison.style.display = 'flex';
            downloadButton.style.display = 'block';

            downloadButton.onclick = function() {
                var a = document.createElement('a');
                a.href = data.enhanced_url;
                a.download = 'enhanced_image.jpg';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };
        } else {
            alert('An error occurred: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred. Please try again.');
    });
});
