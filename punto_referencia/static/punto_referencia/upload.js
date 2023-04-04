const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
const alertBox = document.getElementById('alert-box');
const submitButton = document.getElementById('upload-btn');
const municipio = document.getElementById('id_municipio');

if (municipio.value == "") {
    submitButton.disabled = true;
}

const handleAlerts = (type, msg) =>{
    alertBox.innerHTML = `
        <div class="alert alert-${type}" role="alert">
         ${msg}
        </div>
    `
};

Dropzone.autoDiscover = false
const myDropzone = new Dropzone('#my-dropzone',{
    url: '/punto_referencia/upload/',
    autoProcessQueue: false,
    init: function(){
        submitButton.addEventListener("click", function(){            
            myDropzone.processQueue();            
        });
        this.on("addedfile", file => {
            if (municipio.value == "") {
                submitButton.disabled = true;
            }else{
                if (municipio.value != "") {
                    submitButton.disabled = false;
                }
            }
            $(function(){
                $('#id_municipio').change(function(){
                    if (municipio.value != "") {
                        submitButton.disabled = false;
                    }else{
                        submitButton.disabled = true;
                    }
                });
            });            
          });
        this.on('sending', function(file, xhr, formData){            
            formData.append('csrfmiddlewaretoken', csrf);        
            formData.append('municipio', municipio.value);        
        });
        this.on('success',function(file, response){
            const created = response.created
            if(created){
                handleAlerts('success','¡El archivo fue cargado exitosamente!');                
            }else{
                handleAlerts('danger','Ooops.. No se pudo cargar el archivo.  <br>  El archivo ya existe');
            }
        });
    },
    maxFiles: 1, 
    maxFileSize: 3,
    acceptedFiles: '.csv'
})

