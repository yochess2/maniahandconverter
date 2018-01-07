$(function() {
  var csrf_token = $('meta[name="csrf-token"]').attr('content');
  var $select = $('select');
  var $hhId = $('#hh-id');
  var $list = $('.converted-file-list');
  var $message = $('#message')
  $('button').on('click', function(evt) {
    evt.preventDefault();
    $.ajax({
      type: 'POST',
      url: window.location.origin + '/history/' + $hhId.html() + '/',
      data: {
        csrfmiddlewaretoken: csrf_token,
        hero_id: $select.val()
      },
      success: function(data) {
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
