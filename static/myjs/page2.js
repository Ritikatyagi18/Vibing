let s="";
let count=0;
function artist_click(clicked) {
    s+=clicked;
    s+=',';
    document.getElementById(`${clicked}`).disabled = true;
    document.getElementById(`${clicked}`).innerText = 'Selected';
    count++;
}
let button_submit=document.querySelector('#submit');
button_submit.addEventListener("click",function(){
    if(count<5){
        alert('Select more artist');
    }
    else{
        s+='submit';
        button_submit.innerText='Submitted';
                var dict = {s} 
                const artist = JSON.stringify(dict);
               $.ajax({
                url:"/songs",
                type:"POST",
                contentType:"application/json",
                data: JSON.stringify(artist),
                success: function(data){window.location = '/playlistDisplay'}
                });
                alert("This may take a while");
    }
});