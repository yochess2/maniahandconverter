// After user selects HHs, a bunch of files populates the screen
// Then when the user clicks upload on a file,
//   1. a signature is requested from the backend
//   2. the file is then uploaded to s3 from the frontend
//   3. another request is made to the backend to create a HH Object
$(function() {
  $(".js-upload-hhs").click(function (evt) {
    evt.preventDefault();
    $("#fileupload").click();
  });

  $('#fileupload').fileupload({
    dataType: 'json',
    add: add,
  });

  var format_size = function(file_size) {
    var size = parseInt(file_size/1000)
    var color = file_size > 999000 ? 'red' : 'green';

    return "<b>size:</b> <span style='color:"+color+"'>"+size +" kb</span>";
  }

  var get_ext = function(filename) {
    var fs = filename.split('.');
    if(filename.length === fs[0].length) {
      return "";
    } else {
      return fs[fs.length-1];
    }
  }

  var format_ext = function(ext) {
    if(ext === "txt") {
      return "<b>extension</b>: txt";
    } else if(ext === "") {
      return "<b>extension</b>: <span style='color:red;'>NONE</span>"
    } else {
      return "<b>extension</b>: <span style='color:red;'>"+ext+"</span"
    }
  }

  function add(e, data) {
    var filename            =   data.files[0].name;
    var file_size           =   data.files[0].size;

    var fileElem            =   $('<p/>')
                                  .addClass('hh-name')
                                  .text(filename)
                                  .append('<p>'+format_size(file_size)+' | '+format_ext(get_ext(filename))+'</p>')

    var fileWrapperElem     =   $('<div/>')
                                  .addClass('col-sm-5')
                                  .addClass('hh-wrapper')
                                  .append(fileElem);
    var convertElem         =   $('<button/>')
                                  .addClass('convert-button')
                                  .addClass('btn')
                                  .addClass('btn-primary')
                                  .html('Upload')
                                  .click(function(evt) {
                                    evt.preventDefault();
                                    file = data.files[0];
                                    convertElem.replaceWith('<p>Getting Signature... 1/4</p>');
                                    getSignedRequest(file, convertWrapperElem, outerElem);
                                  });

    var convertWrapperElem  =   $('<div/>')
                                  .addClass('col-sm-3')
                                  .addClass('convert-button-wrapper')
                                  .append(convertElem);

    var outerElem           =   $('<div/>')
                                  .addClass('row')
                                  .addClass('hh-wrapper')
                                  .appendTo('.selected-hh')
                                  .append(fileWrapperElem)
                                  .append(convertWrapperElem)

  }

  function getSignedRequest(file, convertWrapperElem, outerElem){
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/sign_s3?file_name="+file.name+"&file_type="+file.type+"&file_size="+file.size);

    xhr.onreadystatechange = function(){
      if(xhr.readyState === 4){
        if(xhr.status === 200){
          var response = JSON.parse(xhr.responseText);
          if (response.is_valid) {
            convertWrapperElem.children().html('Uploading File... 2/4');
            uploadFile(file, response.data, response.url, response.hh_id, convertWrapperElem, outerElem);
          } else {
            convertWrapperElem.children().html(response.message);
          }
        }
        else{
          convertWrapperElem.children().html('Could not get signed URL.');
        }
      }
    };
    xhr.send();
  }

  function uploadFile(file, s3Data, url, hh_id, convertWrapperElem, outerElem){
    var xhr = new XMLHttpRequest();
    xhr.open("POST", s3Data.url);
    var postData = new FormData();
    for(key in s3Data.fields){
      postData.append(key, s3Data.fields[key]);
    }
    postData.append('file', file);
    xhr.send(postData);
    xhr.onreadystatechange = function() {
      if(xhr.readyState === 4){
        if(xhr.status === 200 || xhr.status === 204){
          convertWrapperElem.children().html('Creating Object... 3/4');
          var csrf_token = $('meta[name="csrf-token"]').attr('content');
          $.ajax({
            type: 'POST',
            url: window.location.href,
            data: {
              csrfmiddlewaretoken: csrf_token,
              hh_id: hh_id,
              key: s3Data.fields.key,
              type: 'sync1'
            },
            success: function(data) {
              if (data.is_valid) {
                convertWrapperElem.children().html('Creating Models... 4/4')
                $.ajax({
                  type: 'POST',
                  url: window.location.href,
                  data: {
                    csrfmiddlewaretoken: csrf_token,
                    hh_json_id: data.hh_json_id,
                    type: 'sync2'
                  },
                  success: function(data_2) {
                    if (data_2.is_valid) {
                      convertWrapperElem.children().html('Done!')

                      var formWrapperElem = $('<div/>');
                      var newSelectElem = $('<select/>').addClass('new-select-button');
                      var newButtonElem = $('<input type="submit"/>');

                      formWrapperElem
                        .addClass('col-sm-4')
                        .addClass('new-form-wrapper')
                        .append(newSelectElem)
                        .append(newButtonElem);

                      $.each(data_2.players, function(key, value) {
                        newSelectElem
                          .append($("<option></option>")
                          .attr("value",key)
                          .text(key + ': ' + value['count']));
                      });

                      outerElem.append(formWrapperElem);

                      newButtonElem
                        .addClass('new-convert-button')
                        .val('Convert')

                      newButtonElem.click(function(evt) {
                        evt.preventDefault();
                        var parentElem = convertWrapperElem.parent()
                        formWrapperElem.html('<p>Converting...</p>');
                        $.ajax({
                          type: 'POST',
                          url: window.location.href,
                          data: {
                            csrfmiddlewaretoken: csrf_token,
                            hero: newSelectElem.val(),
                            hh_json_id: data.hh_json_id,
                            type: 'convert'
                          },
                          success: function(data_3) {
                            if (data_3.is_valid) {
                              parentElem
                                .find('.new-form-wrapper')
                                .html('<p><a target="_blank" href="/new/'+data_3.new_hh_id+'">'+data_3.hero+'</a></p>')
                            }
                          },
                          error: function(err) {
                            parentElem
                              .find('.new-form-wrapper')
                              .html('<p>Error Converting File</p>')
                          },
                          dataType: 'json'
                        })
                      });
                    }
                  },
                  error: function(err) {
                    convertWrapperElem.children().html('Error Creating Models...')
                  },
                  dataType: 'json'
                });
              }
            },
            error: function(err) {
              convertWrapperElem.children().html('Error Creating Objects...')
            },
            dataType: 'json'
          });
        }
        else{
          convertWrapperElem.children().html('Could not upload file.');
        }
     }
    };
  }
});
