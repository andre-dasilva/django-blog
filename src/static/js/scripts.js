// All the javascript logic for this project

$(document).ready(function () {
    $(".delete-button").click(function() {
        event.preventDefault();
        var answer = confirm("Are you sure you want to delete?");
        if (answer) {
           window.location = $(this).attr('href');
        }
    });
    
    $(".comment-reply-btn").click(function (event) {
        event.preventDefault();
        $(this).parent().next(".comment-reply").fadeToggle();
    });

    $('.image-popup').magnificPopup({
		type: 'image',
        gallery: {
            enabled: true
        }
	});
});


