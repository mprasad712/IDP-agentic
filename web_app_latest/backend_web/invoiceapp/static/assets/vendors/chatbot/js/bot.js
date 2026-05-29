// document.addEventListener('scroll', () => {
//     console.log("iside scroll listener")

//     if (document.body.scrollTop > 70 || document.documentElement.scrollTop > 70) {

//         $('#chatb').stop().animate({ height: "783px" }, 0);
//     }
//     else {
//         $('#chatb').stop().animate({ height: "400px" }, 0);
//     }
// });

function b_post(query,csrf,inputpath) {    
    $("#sendb").attr("disabled", true)
    $("#sendb").css('opacity', 0.5);
    var chatlist = document.getElementById('chatb');
    $('#buser_text').val('');
        $("#msg-listb li a").css("pointer-events", "none");
        $('#msg-listb').append('<li class="my-chatb list-group-item">' + query + '</li>');
        $('#msg-listb').append('<li class="client-chatb list-group-item"><div class="dot-pulse"></div></li>');
        
        if (chatlist) {
            chatlist.scrollTop = chatlist.scrollHeight;
        }
        
        $.ajax({
            url: 'http://10.89.148.86:443/pdf_bot/',
            headers: { "X-CSRFToken": csrf, 'Content-Type': undefined },
            type: "POST",
            crossDomain: true,
            data: { msgbox: query, inputpath: inputpath},
            success: function (json) {
            $("#bot_info").hide();     
            $("#sendb").attr("disabled", false);
            $("#sendb").css('opacity', 1.0);
            $('#msg-listb li:last-child').remove();
            $('#msg-listb').append('<li class="client-chatb list-group-item">' + json.response + '</li>');
            if (chatlist) {
                chatlist.scrollTop = chatlist.scrollHeight;
            }
            }
        });
    }

$('#chatb-formb').on('submit', function (event) {
    
    event.preventDefault();
    var user_text = $('#buser_text').val();
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    var inputpath = $("input[name=inputpath]").val();
    $('#bot_info').addClass("no-print")
    b_post(user_text,csrf,inputpath)

});
function info_exitb(query) {
    $("#msg-listb li a").css("pointer-events", "none");
    var csrf = $("input[name=csrfmiddlewaretoken]").val();
    b_post(query,csrf)
}
// var file_n = ""
