window.onload = function() {
const socket = io('https://chris9125-code50-81937083-4jgx95x5rc7g6j-5000.app.github.dev');
var teste = ""
const connected_users = [];

socket.on('connect', ()=> {
    socket.send("Usuário conectado ao socket")

});

socket.on('userConnected', (user)=> {
    connected_users.push(user);
    const div = document.createElement("div");
    const user_list = document.getElementById("users");
    div.innerHTML = "<div class='click_user' id='click_user' value='user'>"
    user_list.append(div);
});

    document.getElementById("form_chat").addEventListener("submit", function(event){
        event.preventDefault();
        socket.emit('sendMessage', {nome: teste, message: event.target[0].value})
    })
    socket.on('getm', (msg)=>{
        const span = document.createElement("span");
        const chat = document.getElementById("chat");
        span.innerHTML = "<div class='chat-container'><strong>" + msg.nome+ ": </strong>" + msg.message + "</div>";
        chat.append(span);

    })

document.querySelectorAll('#click_user').forEach(click_user);

function click_user(user){
    user.addEventListener('click', function () {
        console.log(user)
        teste = $(this).attr("value")
        console.log(teste)
        if($("#chat-button").html() == "-")
        {
            $("#chat-button").html("+");
            $("#chat-header").css("top", '95%');
            $("#chat-messages").css("visibility", 'hidden')
            $("#chat-header").css("visibility", 'hidden')

        }
        else
        {
            //esse else deixa visivel o chat

            socket.emit('getConversation', teste)
            socket.on('getConversation', (messages)=> {
                const chat = document.getElementById("chat");
                function adc(message){
                    const span = document.createElement("span");
                    console.log(message['message_content'])
                    span.innerHTML = "<div class='chat-container'><strong>" + message['username']+ ": </strong>" + message['message_content'] + "</div>";
                    chat.append(span);
                }
                   chat.innerHTML = "";
                   messages.forEach((element) => adc(element));
                   var objDiv = document.getElementById("chat");
                   objDiv.scrollTop = objDiv.scrollHeight;

            })
            $("#chat-header").css("visibility", 'Visible')
            $("#chat-button").html("-");
            $("#chat-header").css("top", '69%');
            $("#chat-messages").css("visibility", 'Visible')
            $("#chat-header").html(teste+"<div class='chat-button' id='chat-button'>-</div>")

        }
        $("#chat").slideToggle(200);
        console.log(teste)
    })};

$("#chat-button").click(function(){
    console.log("a")
    teste = document.getElementById("click_user").getAttribute('value');
    $("#chat-button").html("+");
    $("#chat-header").css("top", '95%');
    $("#chat-messages").css("visibility", 'hidden')
    $("#chat-header").css("visibility", 'hidden')
    console.log("if")

    $("#chat").slideToggle(200);



});

$("#header_button").click(function(){
    if($(this).html() == "-"){
        $(this).html("+");


    }
    else{
        $(this).html("-");


    }
    $("#users").slideToggle(200);
});



}

