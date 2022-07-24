let camera_button = document.querySelector("#start-camera");
        let video = document.querySelector("#video");
        let click_button = document.querySelector("#click-photo");
        let canvas = document.querySelector("#canvas");

        camera_button.addEventListener('click', async function() {
   	        let stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
	        video.srcObject = stream;
        });

    click_button.addEventListener('click', function() {
   	        canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
   	        var image_data_url = canvas.toDataURL('image/jpeg');

   	// data url of the image
            console.log("URL of Image is :");
   	        console.log(image_data_url);
            const dict_values={image_data_url}
            const s = JSON.stringify(dict_values);
            $.ajax({
                url:"/mood",
                type:"POST",
                contentType: "application/json",
                data: JSON.stringify(s)});
    });