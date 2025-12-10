$(document).ready(function() {
	$('.text').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "bounceIn",
        },
        out: {
            effect: "bounceOut",
        },

    });


    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

      $('.siri-message').textillate({
        loop: true,
        sync: true,
        in: {
            effect: "fadeInUp",
            sync: true,
        },
        out: {
            effect: "fadeOutUp",
            sync: true,
        },

    });


    $("#MicBtn").click(function() {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.playClickSound();
        eel.allCommands(); 
    });
// Function to handle typed input
function sendTypedCommand() {
    let typedText = $("#chatbox").val().trim();

    if (typedText !== "") {
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.playClickSound(); // optional
        eel.allCommands(typedText); // pass text to Python
        $("#chatbox").val(""); // clear input field
    }
}

// When ChatBtn is clicked
$("#ChatBtn").click(function () {
    sendTypedCommand();
});

// When Enter is pressed in the input field
$("#chatbox").keypress(function (event) {
    if (event.which === 13) {
        event.preventDefault(); // prevent form submission if in a form
        sendTypedCommand();
    }
});


});