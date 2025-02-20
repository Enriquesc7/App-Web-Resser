$(document).ready(function() {

    // APARICIÓN GATO EN INDEX ===========================================================

    /* .animate( {   }, 1000, function(){...});
-El primer argumento permite entre {} modificar las propiedades css
-El segundo argumento permite establecer un tiempo de animacion en milisegundos
-El tercer argumento permite incluir una funcion anidada (funcion anonima) 
---> El codigo que se ingrese dentro de la "funcion anonima" se va a ejecutar siempre y cuando
se termine la animacion anterior.   */

    //$("#img_welcome").hide().delay(2000)
    //$("#img_welcome").show(2000)
    
    
//==== Slider Empresas que Valorizan ======

    var img_position_enterprise = 1;
    var direccion_enterprise = "adelante";
    

    // Detectamos cuantos li hay en el slide
    var count_li_enterprise = 0
    $(".slider_enterprise li").each(function(){
        count_li_enterprise++;
    });

    // Modificamos el ancho del slide dependiendo de la cantidad de li
    $(".slider_enterprise"). css("width", count_li_enterprise*100+"%");


//==== Slider Partners ==============

    var img_position_partners = 1;
    var direccion_partners = "adelante";
    

    // Detectamos cuantos li hay en el slide
    var count_li_partners = 0
    $(".slider_partners li").each(function(){
        count_li_partners++;
    });

    // Modificamos el ancho del slide dependiendo de la cantidad de li
    $(".slider_partners"). css("width", count_li_partners*100+"%");    




//======= Ejecutamos todas las funciones ============
    $(".direcciones_enterprise .adelante").click(siguiente_enterprise);
    $(".direcciones_enterprise .atras").click(anterior_enterprise);
    //Generamos que sea automatico...
    var ciclo_enterprise=setInterval(function(){
        automatico_enterprise();
    },4000);

//======= Ejecutamos todas las funciones ============
    $(".direcciones_partners .adelante").click(siguiente_partners);
    $(".direcciones_partners .atras").click(anterior_partners);
    //Generamos que sea automatico...
    var ciclo_partners=setInterval(function(){
        automatico_partners();
    },4000);






//====== Funciones Enterprise ================

    function siguiente_enterprise(){
        adelante_enterprise();
        clearInterval(ciclo_enterprise);}

    function anterior_enterprise(){
        atras_enterprise();
        clearInterval(ciclo_enterprise);}

    function automatico_enterprise(){
        if (direccion_enterprise=="adelante"){
            adelante_enterprise();}

        else if(direccion_enterprise=="atras"){
            atras_enterprise();}}
    
//====== Funciones Partners ================

function siguiente_partners(){
    adelante_partners();
    clearInterval(ciclo_partners);}

function anterior_partners(){
    atras_partners();
    clearInterval(ciclo_partners);}

function automatico_partners(){
    if (direccion_partners=="adelante"){
        adelante_partners();}

    else if(direccion_partners=="atras"){
        atras_partners();}}





//======== Slider Partners ==============
    // Definimos la función de avance 
    function adelante_partners(){
        if (img_position_partners < count_li_partners-1){
            $(".slider_partners").stop().animate({marginLeft:"-"+(img_position_partners)*100+"%"},1500,"easeOutQuint")
            img_position_partners++;}
        
        else if (img_position_partners == count_li_partners-1){
            $(".slider_partners").stop().animate({marginLeft:"-"+(img_position_partners)*100+"%"},1500,"easeOutQuint")
            img_position_partners++;
            direccion_partners="atras";}
        }

    // Definimos la función de retroceso
    function atras_partners(){

        if (img_position_partners==count_li_partners){
            $(".slider_partners").stop().animate({marginLeft:"-"+(img_position_partners-2)*100+"%"},1500,"easeOutQuint")
            img_position_partners--;}
        
        else if(img_position_partners>1){
            $(".slider_partners").stop().animate({marginLeft:"-"+(img_position_partners-2)*100+"%"},1500,"easeOutQuint")
            img_position_partners--;
            direccion_partners="adelante";}
        }
        


//======== Slider Enterprise ==============
    // Definimos la función de avance 
    function adelante_enterprise(){
        if (img_position_enterprise < count_li_enterprise-1){
            $(".slider_enterprise").stop().animate({marginLeft:"-"+(img_position_enterprise)*100+"%"},1500,"easeOutQuint")
            img_position_enterprise++;}
        
        else if (img_position_enterprise == count_li_enterprise-1){
            $(".slider_enterprise").stop().animate({marginLeft:"-"+(img_position_enterprise)*100+"%"},1500,"easeOutQuint")
            img_position_enterprise++;
            direccion_enterprise="atras";}
        }

    // Definimos la función de retroceso
    function atras_enterprise(){

        if (img_position_enterprise==count_li_enterprise){
            $(".slider_enterprise").stop().animate({marginLeft:"-"+(img_position_enterprise-2)*100+"%"},1500,"easeOutQuint")
            img_position_enterprise--;}
        
        else if(img_position_enterprise>1){
            $(".slider_enterprise").stop().animate({marginLeft:"-"+(img_position_enterprise-2)*100+"%"},1500,"easeOutQuint")
            img_position_enterprise--;
            direccion_enterprise="adelante";}
        }




    //FIN SLIDESHOW IMAGENES INDEX ===========================================================================
});