
//============================= SECTION JQUERY =====================================================
$(document).ready(function() {


//============= Ajax para el formulario de Registro de Usuario ============================

    // Obtenemos una referencia al formulario de registro
    const form_register_user = $('#register_user');
    // Maneja el evento onSubmit del formulario
    form_register_user.on('submit', (event) => {
    // Evitamos que el formulario se envie en forma predeterminada
    event.preventDefault();
    // Obtenemos los datos del formulario
    const DataRegister = form_register_user.serialize();

    // Envía una petición Ajax para registrar al usuario
    $.ajax({
        url: '/register/',
        type: 'POST',
        data: DataRegister,
        dataType: 'json',
        success: function(response){

            if (response.redirect) {
                // Redirigimos a login
                window.location.href = response.redirect;
            }
        },
        error: function(xhr, textStatus, error){
            if (xhr.status === 400) {
                const error_register = $('#error_register');
                error_register.empty();
                const response = JSON.parse(xhr.responseText);
                error_register.append($('<p style="color: red; text-align: center;">').text(response.message));
            }
        }
    });
});


//============= Ajax para crear usuario y actualizar tablas - Users ============================

    // Obtiene una referencia al formulario
    const form_create_user = $('#admin_create_user');

    // Maneja el evento onSubmit del formulario
    form_create_user.on('submit', (event) => {
        
        // Evita que el formulario se envíe de forma predeterminada
        event.preventDefault();
        
        // Obtiene los datos del formulario
        const formData = form_create_user.serialize();

        // Envía una petición Ajax para crear el usuario
        $.ajax({
            url: '/admin/users/create/ajax',
            type: 'POST',
            data: formData,
            dataType: 'json',
            success: function(response) {
                
                const container_message = $('#error_create');
                container_message.empty();
                if (response.message == 'El usuario fue creado con exito'){
                    container_message.append($('<p style="color: green; padding-left:100px; font-weight:bold;">').val(response.message).text(response.message));
                    // limpiamos el formulario
                    form_create_user.trigger('reset');

                    // Obtiene las URL de las imágenes desde los atributos data del formulario
                    const editImgUrl = form_create_user.data('edit-img');
                    const loginImgUrl = form_create_user.data('login-img');
                    const deleteImgUrl = form_create_user.data('delete-img');

                    // Obtenemos el objeto de usuario recién creado
                    const newUser = response.new_user;
                    
                    const updateDate = newUser.update ? new Date(newUser.update).toLocaleDateString() : "";
                    const userStatus = newUser.disabled === false ? "True" : "False";
                    
                    // Construye la fila de la tabla con el objeto de usuario recién creado
                    const newRow = `<tr>
                        <th>${newUser.id}</th>
                        <th>${newUser.email}</th>
                        <th>${newUser.first_name}</th>
                        <th>${newUser.last_name}</th>
                        <th>${new Date(newUser.create).toLocaleDateString()}</th>
                        <th>${updateDate}</th>
                        <th>${userStatus}</th>
                        <th>
                            <a href="/admin/users/${newUser.id}">
                                <img src="${editImgUrl}" alt="Editar" title="Editar" width="20px">
                            </a>
                        </th>
                        <th>
                            <a href="#">
                                <img src="${loginImgUrl}" alt="Loguear" title="Loguear" width="20px">
                            </a>
                        </th>
                        {% if permission == 'Super Admin' %}
                        <th>
                            <a href="/admin/users/${newUser.id}/delete" onclick="return DeleteUser()">
                                <img src="${deleteImgUrl}" alt="Editar" title="Eliminar" width="20px">
                            </a>
                        </th>
                        {% endif %}
                    </tr>`;

                    const newRow_superAdmin = `<tr>
                        <th>${newUser.id}</th>
                        <th>${newUser.email}</th>
                        <th>${newUser.first_name}</th>
                        <th>${newUser.last_name}</th>
                        <th>${new Date(newUser.create).toLocaleDateString()}</th>
                        <th>${updateDate}</th>
                        <th>${userStatus}</th>
                    </tr>`;

                    // Añade la nueva fila a la tabla dependiento del rol 
                    if (newUser.rol == 'Super Admin') {
                        $('#table_super_admin tbody').append(newRow_superAdmin);
                    } else if (newUser.rol == 'Admin') {
                        $('#table_admin tbody').append(newRow);
                    } else if (newUser.rol == 'User') {
                        $('#table_user tbody').append(newRow);
                    }

                }else{
                    container_message.append($('<p style="color: red; padding-left:100px; font-weight:bold;">').val(response.message).text(response.message));
                }
            },
            error: function(error) {
                // Si la petición Ajax falla, muestra un mensaje de error
                alert('Error al crear el usuario');
            }
        });
    });




//============= Ajax para cambio de optiones en etiquetas select - Team ============================

    function updateSelects(parameter, value, commune) {
        $.ajax({
            url: '/admin/team/ajax',
            type: 'GET',
            data: {[parameter]: value},
            dataType: 'json',
            success: function(data) {
                if (data.communes) {
                    const communes = $(commune);
                    communes.empty();
                    for (let i = 0; i < data.communes.length; i++) {
                        const reg = data.communes[i];
                        communes.append($('<option>').val(reg).text(reg));
                    }
                }
                if (data.employments) {
                    const employments = $('#employments');
                    employments.empty();
                    for (let i = 0; i < data.employments.length; i++) {
                        const employ = data.employments[i];
                        employments.append($('<option>').val(employ).text(employ));
                    }
                }
            }
        });
    }

    const region = $('#region');
    const region_customer = $('#region_customer');
    const region_business_customer = $('#region_business_customer')

    region.on('change', () => {
        var regionSelected = region.val();
        updateSelects('region', regionSelected, '#commune');
    });

    region_customer.on('change', () => {
        var regionSelected = region_customer.val();
        updateSelects('region', regionSelected, '#commune_customer');
    });

    region_business_customer.on('change', () => {
        var regionSelected = region_business_customer.val();
        updateSelects('region', regionSelected, '#commune_business_customer');
    });

    const area = $('#work_areas');
    area.on('change', () => {
        const areaSelected = area.val();
        updateSelects('area', areaSelected);
    });

    // Llama a la función updateSelects al cargar la página con los valores iniciales
    const initialRegion = region.val();
    updateSelects('region', initialRegion, '#commune')
    const initialRegionC = region_customer.val();
    updateSelects('region', initialRegionC, '#commune_customer');
    const initialRegionB = region_business_customer.val();
    updateSelects('region', initialRegionB, '#commune_business_customer')
    const initialArea = area.val();
    updateSelects('area', initialArea);


    // ========================= FIN JQUERY ==================================================
});