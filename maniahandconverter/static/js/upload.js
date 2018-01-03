$(function() {
  var heroInputElem = $('.hero-input');

  $(".js-upload-hhs").click(function () {
    $("#fileupload").click();
  });

  $('#fileupload').fileupload({
    dataType: 'json',
    add: function (e, data) {
      var filename = data.files[0].name;

      var fileElem            =   $('<p/>')
                                    .addClass('hh-name')
                                    .text(filename);

      var fileWrapperElem     =   $('<div/>')
                                    .addClass('col-sm-4')
                                    .addClass('hh-wrapper')
                                    .append(fileElem);
      var heroElem            =   heroInputElem
                                    .clone()
                                    .attr('type', 'text')
      var heroWrapperElem     =   $('<div/>')
                                    .addClass('col-sm-2')
                                    .addClass('hero-input-wrapper')
                                    .append(heroElem)

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
                                    // .append(heroWrapperElem)
                                    .append(convertWrapperElem)

      data.context = $(outerElem);
    },
    // progress: function (e, data) {
    //   var barElem = $('<div class="bar"></>')
    //   var progressBarElem = $('<div/>')
    //                           .addClass('.progress')
    //                           .append(barElem)


    //   var convertWrapperElem = data.context.find('.convert-button-wrapper');
    //   $(convertWrapperElem).children().replaceWith(progressBarElem)
    //    var progress = parseInt(data.loaded / data.total * 100, 10);
    //    $(barElem).css(
    //        'width',
    //        progress + '%'
    //    ).html(progress + '%');
    // },
    done: function (e, data) {
      console.log(data);
      var convertWrapperElem = data.context.find('.convert-button-wrapper');
      if(data.result.is_valid) {
        $(convertWrapperElem).children().replaceWith('<p>Done</p>');

        var newSelectElem    =   $('<select/>').addClass('new-select-button');
        $.each(data.result.players, function(key, value) {
          newSelectElem
            .append($("<option></option>")
            .attr("value",key)
            .text(key + ': ' + value['count']));
        });

        var newButtonElem   =   $('<input type="submit"/>')
                                  .addClass('new-convert-button')
                                  .val('Convert')
                                  .click(function() {
                                    newButtonElem
                                      .replaceWith('<span> Converting...</span>')

                                    $.ajax({
                                      type: 'POST',
                                      url: window.location.href,
                                      data: {
                                        csrfmiddlewaretoken: data.result.csrf,
                                        hero: newSelectElem.val(),
                                        // obj: data.result.hh_obj
                                      },
                                      success: function(data) {
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

                                  // convert files

        var formWrapperElem =   $('<div/>')
                                  .addClass('col-sm-4')
                                  .addClass('new-form-wrapper')
                                  .append(newSelectElem)
                                  .append(newButtonElem);

        // outerElem
        data.context.append(formWrapperElem);
      } else {
        $(convertWrapperElem).children().replaceWith('<p>Please use .txt</p>');
      }
    }
  });
});
