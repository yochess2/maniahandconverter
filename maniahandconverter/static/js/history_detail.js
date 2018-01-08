$(function() {
  var csrf_token = $('meta[name="csrf-token"]').attr('content');
  var $select = $('select');
  var $hhjsonId = $('#hhjson-id');
  var $list = $('.converted-file-list');
  var $message = $('#message')
  $('button').on('click', function(evt) {
    var $button = $(this);
    $button.attr('disabled','disabled');
    evt.preventDefault();
    $.ajax({
      type: 'POST',
      url: window.location.origin + '/history/' + $hhjsonId.html() + '/',
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
