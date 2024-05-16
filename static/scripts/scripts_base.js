// Funciones para confirmar la eliminación de recursos.
function DeleteAdmin(){
    var respuesta = confirm("¿Estas seguro que deseas eliminar este Administrador?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}
function DeleteUser(){
    var respuesta = confirm("¿Estas seguro que deseas eliminar este usuario?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}
function DeleteService(){
    var respuesta = confirm("¿Estas seguro que deseas eliminar el servicio?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}
function DeleteImage(){
    var respuesta = confirm("¿Estas seguro que deseas eliminar la imagen?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}
function DeletePlan(){
    var respuesta = confirm("¿Estas seguro que deseas eliminar este Plan?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}
function ConvertToAdmin(){
    var respuesta = confirm("¿Estas seguro que deseas convertir en Administrador a este Usuario?");

    if (respuesta == true){
        return true;
    }
    else{
        return false;
    }
}

// Sección en STOP... se averigua como modificar el alert
// Función para abrir la section_question
function OpenQuestion(e){
	$("#section_question").fadeIn();
    console.log("Algo ???")
    console.log($(".id_user").text());
}
// Función para cerrar la section_question
function CloseQuestion(e){
	$("#section_question").fadeOut();
}

//============================= SECTION JQUERY =====================================================
$(document).ready(function() {


    //================= MENU VERTICAL ==========================

    $(".nav_admin").hover(function(){   // Se agrega un tercer parametro a la funcion animate(), que 
		$(this).stop().animate({  // correspondera a un efecto de movimiento obtenido de los
			left:"30px"             // plugins descargados de JQuery (easing)... 
		},300,"easeInSine");//Luego para no tener una sucesion de eventos al jugar con el evento
	},                      //se agrega la funcion "stop()" que impide la acumulacion de eventos.
	function(){
		$(this).stop().animate({
			left:"0px"
		},300, "easeInSine"); //easeOutBounce
	});
    
    
    
    




    //================= QUESTION SI/NO ==========================

    $("#section_question").hide();
    //$(".delete_user").on("click", open_question)
    //$("#option_no").on("click", out_question)


   


    //================================== ADMIN FRONT ====================================

    //============== Section Add content======================
    $(".container_form").hide()    

    // Esta interacción quedará desabilitada hasta identificar de donde es, ya que afecta
    // afecta los h3 de todos las paginas. 

    //$("h3").click(function(){
      // next() apunto a lo siguiente (en este caso .respuesta) de donde nos encontramos (h3)...
      // fadeToggle tiene un comportamiento on/off de los elementos fadeIn y fadeOut
    //  $(this).next().slideToggle();
      // toggleClass tiene un comportamiento on/off con una clase que se quiera aplicar y quitar...
    //  $(this).toggleClass("cerrar");
    //})

    //============== Section Update content ======================
    $(".section_update_front").hide();
    
    $(".update_content img").click(function(){
        // fadeToggle tiene un comportamiento on/off de los elementos fadeIn y fadeOut
        $(".section_update_front").slideToggle();
        // toggleClass tiene un comportamiento on/off con una clase que se quiera aplicar y quitar...
      })

    //================================== ADMIN TEAM ====================================
    
    //======= Usando JQuery UI para calendarios =================
   
    $("#start_date").datepicker({
        changeMonth: true,
        changeYear: true,
        showAnim: "blind"
       });
  
    $("#end_date").datepicker({
        changeMonth: true,
        changeYear: true,
        showAnim: "blind"
    });
    

// ========================= FIN JQUERY ==================================================
})

