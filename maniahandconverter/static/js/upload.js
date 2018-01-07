$(function() {
  var heroInputElem = $('.hero-input');

  $(".js-upload-hhs").click(function () {
    $("#fileupload").click();
  });

  $('#fileupload').fileupload({
    dataType: 'json',
    add: add,
    done: done
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
                                    convertElem.replaceWith('<p>Uploading...</p>');
                                    data.submit();
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

    data.context = $(outerElem);
  }

  function done(e, data) {
    console.log('done', data.result);
    var convertWrapperElem = data.context.find('.convert-button-wrapper');
    var convertElem = convertWrapperElem.children();

    if(data.result.is_valid) {
      convertElem.html('<p>Syncing...</p>');
      $.ajax({
        type: 'POST',
        url: window.location.href,
        data: {
          csrfmiddlewaretoken: data.result.csrf,
          hh_id: data.result.hh_id,
        },
        success: success,
        error: error,
        dataType: 'json'
      });
    } else {
      convertElem.html('<p>Error</p>');
    }

    function success(data) {
      console.log('success1', data);

      if(data.is_valid) {
        convertElem.html('<p>Saving...</p>');
        $.ajax({
          type: 'POST',
          url: window.location.href,
          data: {
            csrfmiddlewaretoken: data.csrf,
            hh_json_id: data.hh_json_id,
          },
          success: function(data) {
            console.log('success2', data);
            var outerElem = convertWrapperElem.parent();

            if(data.is_valid) {
              convertElem.html('Done!');
              var newSelectElem = $('<select/>').addClass('new-select-button');
              $.each(data.players, function(key, value) {
                newSelectElem
                  .append($("<option></option>")
                  .attr("value",key)
                  .text(key + ': ' + value['count']));
              });

              var newButtonElem = $('<input type="submit"/>')
                                    .addClass('new-convert-button')
                                    .val('Convert')

              newButtonElem.click(function() {
                newButtonElem.replaceWith('<span> Converting...</span>')

                $.ajax({
                  type: 'POST',
                  url: window.location.href,
                  data: {
                    csrfmiddlewaretoken: data.csrf,
                    hero: newSelectElem.val(),
                  },
                  success: function(data) {
                    console.log('final', data)
                    if(data.is_valid === true) {
                      var parentElem = convertWrapperElem.parent()
                      parentElem
                        .find('.new-form-wrapper')
                        .replaceWith('<p>'+data.hero+'</p>')
                    }
                  },
                  error: function(err) {
                    console.log(err);
                  },
                  dataType: 'json'
                });
              });

              var formWrapperElem = $('<div/>')
                                      .addClass('col-sm-4')
                                      .addClass('new-form-wrapper')
                                      .append(newSelectElem)
                                      .append(newButtonElem);

              outerElem.append(formWrapperElem);
            }
          },
          dataType: 'json'
        });
      } else {
        convertElem.html('<p>Error</p>');
      }
    }

    function error(err) {
      console.log(err);
    }
  }
});
