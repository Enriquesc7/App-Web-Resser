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
    
    // FIN APARICIÓN GATO EN INDEX


    //ANIMACION SLIDESHOW IMAGENES INDEX========================================================================
    
    var img_position=1;
    var direccion="adelante";
    // Detectamos cuantos li hay en el slide
    var count_li = 0
    $(".slider li").each(function(){
        count_li++;
    });

    // Modificamos el ancho del slide dependiendo de la cantidad de li
    $(".slider"). css("width", count_li*100+"%");

    //Ejecutamos todas las funciones ============
    $(".direcciones .adelante").click(siguiente);
    $(".direcciones .atras").click(anterior);
    //Generamos que sea automatico...
    var ciclo=setInterval(function(){
        automatico();
    },4000);

    // FUNCIONES =================================

    function siguiente(){
        adelante();
        clearInterval(ciclo);}

    function anterior(){
        atras();
        clearInterval(ciclo);}

    function automatico(){
        if (direccion=="adelante"){
            adelante();}

        else if(direccion=="atras"){
            atras();}}


    // Definimos la función de avance
    function adelante(){
        if (img_position < count_li-1){
            $(".slider").stop().animate({marginLeft:"-"+(img_position)*100+"%"},1500,"easeOutQuint")
            img_position++;}
        
        else if (img_position == count_li-1){
            $(".slider").stop().animate({marginLeft:"-"+(img_position)*100+"%"},1500,"easeOutQuint")
            img_position++;
            direccion="atras";}
        }

    // Definimos la función de retroceso
    function atras(){

        if (img_position==count_li){
            $(".slider").stop().animate({marginLeft:"-"+(img_position-2)*100+"%"},1500,"easeOutQuint")
            img_position--;}
        
        else if(img_position>1){
            $(".slider").stop().animate({marginLeft:"-"+(img_position-2)*100+"%"},1500,"easeOutQuint")
            img_position--;
            direccion="adelante";}
        }

    //FIN SLIDESHOW IMAGENES INDEX ===========================================================================
});