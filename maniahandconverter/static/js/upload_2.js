$(function() {
  $(".js-upload-hhs").click(function () {
    $("#fileupload").click();
  });

  $('#fileupload').fileupload({
    dataType: 'json',
    add: add,
  });

  function add(e, data) {
    var filename            =   data.files[0].name;

    var fileElem            =   $('<p/>')
                                  .addClass('hh-name')
                                  .text(filename);

    var fileWrapperElem     =   $('<div/>')
                                  .addClass('col-sm-4')
                                  .addClass('hh-wrapper')
                                  .append(fileElem);
    var convertElem         =   $('<input type="submit"/>')
                                  .addClass('convert-button')
                                  .val('Upload')
                                  .click(function() {
                                    file = data.files[0];
                                    convertElem.replaceWith('<p>Uploading...</p>');
                                    getSignedRequest(file);
                                  });

    var convertWrapperElem  =   $('<div/>')
                                  .addClass('col-sm-2')
                                  .addClass('convert-button-wrapper')
                                  .append(convertElem);

    var outerElem           =   $('<div/>')
                                  .addClass('row')
                                  .addClass('hh-wrapper')
                                  .appendTo('.selected-hh')
                                  .append(fileWrapperElem)
                                  .append(convertWrapperElem)

  }

  function getSignedRequest(file){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type);
    xhr.onreadystatechange = function(){
      if(xhr.readyState === 4){
        if(xhr.status === 200){
          var response = JSON.parse(xhr.responseText);
          console.log(response)
          uploadFile(file, response.data, response.url);
        }
        else{
          alert("Could not get signed URL.");
        }
      }
    };
    xhr.send();
  }

  function uploadFile(file, s3Data, url){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", s3Data.url);

    var postData = new FormData();
    for(key in s3Data.fields){
      postData.append(key, s3Data.fields[key]);
    }
    postData.append('file', file);

    xhr.onreadystatechange = function() {
      if(xhr.readyState === 4){
        if(xhr.status === 200 || xhr.status === 204){
          console.log('success', url);
        }
        else{
          alert("Could not upload file.");
        }
     }
    };
    xhr.send(postData);
  }
});
