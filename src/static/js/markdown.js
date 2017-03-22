// Logic for form with markdown

$(document).ready(function () {
    var contentInput = $("#id_content");
    function setContent(value) {
        var markedContent = marked(value);
        $("#preview-content").html(markedContent);
        $("#preview-content img").each(function () {
            $(this).addClass("img-responsive");
        })
    }
    setContent(contentInput.val());
    contentInput.keyup(function () {
        setContent($(this).val());
    });

    var titleInput = $("#id_title");
    function setTitle(value) {
         $("#preview-title").text(value);
    }
    setTitle(titleInput.val());
    titleInput.keyup(function () {
        setTitle($(this).val());
    });
});