const csrf = document.getElementsByName('csrfmiddlewaretoken')[0].value;
const submitButton = document.getElementById('upload-btn');
const alertBox2 = document.getElementById('alert-box2');

submitButton.disabled = true;
const handleAlerts = (type, msg) =>{
    alertBox2.innerHTML = `
        <div class="alert alert-${type}" role="alert">
         ${msg}
        </div>
    `
};

Dropzone.autoDiscover = false
const myDropzone = new Dropzone('#my-dropzone2',{
    url: '/municipios/upload/',
    autoProcessQueue: false,
    init: function(){
        submitButton.addEventListener("click", function(){            
            myDropzone.processQueue();            
        });
        this.on("addedfile",file =>{
            submitButton.disabled = false;
        });
        this.on('sending', function(file, xhr, formData){            
            console.log('sending')
            formData.append('csrfmiddlewaretoken', csrf);        
        });
        this.on('success',function(file, response){
            console.log(response.ex)
            const created = response.created
            if(created){
                handleAlerts('success','¡El archivo fue cargado exitosamente!');                
            }else{
                handleAlerts('danger','Ooops.. No se pudo cargar el archivo. <br>  El archivo: '+response.fileName+', ya existe');
            }
        });
    },
    maxFiles: 1, 
    maxFileSize: 3,
    acceptedFiles: '.csv'
})