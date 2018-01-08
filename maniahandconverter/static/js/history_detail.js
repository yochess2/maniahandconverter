$(function() {
  var csrf_token = $('meta[name="csrf-token"]').attr('content');
  var hhjsonId = $('meta[name="hhjson-id"]').attr('content');
  var $select = $('select');
  var $list = $('.converted-file-list');
  var $message = $('#message');

  $('.delete-all').on('click', function(evt) {
    var $button = $(this);
    will_delete = confirm('Are you sure?');
    if(will_delete) {
      $.ajax({
        type: 'PUT',
        url: window.location.origin + '/history/' + hhjsonId + '/',
        beforeSend:function(xhr){
          xhr.setRequestHeader("X-CSRFToken", csrf_token);
        },
        success: function(data) {
          console.log('cool');
        },
        error: function(err) {
          console.log(err);
        },
        dataType: 'json'
      });
    }
  });


  $('.add-button').on('click', function(evt) {
    var $button = $(this);
    $button.attr('disabled','disabled');
    $.ajax({
      type: 'POST',
      url: window.location.origin + '/history/' + hhjsonId + '/',
      data: {
        csrfmiddlewaretoken: csrf_token,
        hero_id: $select.val()
      },
      success: function(data) {
        $button.removeAttr('disabled');
        if(data.is_valid === true) {
          $list.append('<li><a target="_blank" href="/new/'+ data.new_hh_id +'">'+ data.hero +'</li>')
          $message.html('');
        } else {
          $message.html('already exists');
        }
      },
      error: function(err) {
        console.log(err);
      },
      dataType: 'json'
    });
  });

})
