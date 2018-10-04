$(function() {
  var format_size = function(file_size) {
    var size = parseInt(file_size/1000)
    var color = file_size > 1999000 ? 'red' : 'green';

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

  var csrf_token = $('meta[name="csrf-token"]').attr('content');

  $(".js-upload-hhs").click(function (evt) {
    evt.preventDefault();
    $("#fileupload").click();
  });

  $('#fileupload').fileupload({
    // url: window.location.href,
    paramName: 'file',
    add: add,
    // done: function(e, data) {
    //   data.context.convertWrapperElem.html('Done');
    // }
  });

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
                                  .html('Convert')
                                  .click(function(evt) {
                                    evt.preventDefault();
                                    file = data.files[0];
                                    processFileLocally(file, nameElem.val())
                                    // data.formData = {'csrfmiddlewaretoken': csrf_token}
                                    // data.submit();
                                  });

    var nameElem = $('<input/>')
                      .attr('placeholder', 123456789);

    var nameWrapperElem = $('<div/>')
                            .addClass('col-sm-2')
                            .append(nameElem);

    var convertWrapperElem  =   $('<div/>')
                                  .addClass('col-sm-3')
                                  .addClass('convert-button-wrapper')
                                  .append(convertElem);

    var outerElem           =   $('<div/>')
                                  .addClass('row')
                                  .addClass('hh-wrapper')
                                  .appendTo('.selected-hh')
                                  .append(fileWrapperElem)
                                  .append(nameWrapperElem)
                                  .append(convertWrapperElem)

    data.context = {
      outerElem: outerElem,
      convertWrapperElem: convertWrapperElem
    };
  }
  function processFileLocally(file, id) {
    var reader = new FileReader();
    reader.onload = function(fileLoadedEvent){
      convertFile(fileLoadedEvent.target.result, id);
    };

    var text = reader.readAsText(file, "UTF-8");
  }

  function convertFile(text, id) {
    var tournament_id = id;

    if (!tournament_id) {
      return;
    }

    var results = [];
    var re_hand_number = /\#Game No : (\d+)/;
    var re_small_blind = /(.+) posts small blind \[\$(.+)\]/;
    var re_big_blind = /(.+) posts big blind \[\$(.+)\]/;
    var re_table = /Table (.+) \(Real Money\)/;
    var re_button_num = /Seat (\d+) is the button/;
    var re_seat_line = /Seat (\d+): (.+) \( \$(.+) \)/;
    var re_ante_line = /(.+) posts ante \[\$(.+)\]/;
    var re_dealt_line = /Dealt to (\S+)( \[ (.+), (.+) \])?/;
    var re_action = /(.+) (folds|checks|calls|bets|raises)( \[\$(.+)\])?/;
    var re_flop = /\*\* Dealing flop \*\* \[ (.+), (.+), (.+) \]/;
    var re_big_street = /\*\* Dealing (turn|river) \*\* \[ (.+) \]/;
    var re_collected_line = /(\S+) collected \[ \$(.+) \]/;
    var re_showdown = /(\S+) (did not show his hand|shows|mucks)( \[ (.+), (.+) \])?/;

    var hands = text.split(/\n\n/).filter(function(str) {
      return str !== ''
    });

    hands.forEach(function(hand, index) {
      var result = [];
      var lines = hand.split('\n').filter(function(line) {
        return line !== '';
      });
      var current_index = 6;

      var game_num_details = re_hand_number.exec(lines[0]);
      // var game_type = line[2];
      var small_blind_details = re_small_blind.exec(hand);
      var big_blind_details = re_big_blind.exec(hand);
      var table_details = re_table.exec(lines[3]);
      var button_num_details = re_button_num.exec(lines[4]);

      // Heading
      var small_blind;
      if (!small_blind_details) {
        small_blind = parseInt(big_blind_details[2].replace(/,/g, '')) /2;
      } else {
        small_blind = small_blind_details[2]
      }

// indent here for testing
      var heading1 = `PokerStars Hand #${game_num_details[1]}: Tournament #${tournament_id}, $50+5 USD `;
      heading1 += `Hold'em No Limit - Level I (${small_blind}/${big_blind_details[2]})`;
      heading1 += ' - 2018/10/02 12:00:00 ET';
      var heading2 = `Table '${tournament_id} 1' Seat #${button_num_details[1]} is the button`;
      // var heading1 = `PokerStars Hand #${game_num_details[1]}: Hold'em No Limit ($${small_blind}/$${big_blind_details[2]} USD)`;
      // heading1 += ' - 2018/10/02 12:00:00 ET';
      // var heading2 = `Table '${table_details[1]}' Seat #${button_num_details[1]} is the button`;
      result.push(heading1);
      result.push(heading2);

      // Seat Numbers
      var players_order = []
      for (var i = current_index; i < lines.length; i++) {
        var seat_details = re_seat_line.exec(lines[i]);
        if (!seat_details) {
          break;
        }
        var player_line = `Seat ${seat_details[1]}: ${seat_details[2]} (${parseInt(seat_details[3].replace(/,/g, ''))} in chips)`;
        // ordering isn't right on HH
        players_order.push(seat_details[2]);
        result.push(player_line);
      }

      // Antes
      current_index = i;
      for (var i = current_index; i < lines.length; i++) {
        var ante_details = re_ante_line.exec(lines[i]);
        if (!ante_details) {
          break;
        }
        var ante_line = `${players_order[i - current_index]}: posts the ante ${parseInt(ante_details[2].replace(/,/g, ''))}`;
        result.push(ante_line);
      }

      // Blinds and Hole Card Heading
      current_index = i;
      var small_blind_line;
      if (small_blind_details) {
        small_blind_line = `${small_blind_details[1]}: posts small blind ${parseInt(small_blind_details[2].replace(/,/g, ''))}`;
        result.push(small_blind_line);
      }
      var big_blind_line = `${big_blind_details[1]}: posts big blind ${parseInt(big_blind_details[2].replace(/,/g, ''))}`;
      result.push(big_blind_line);
      result.push('*** HOLE CARDS ***');
      current_index += 3;

      // Dealt Lines
      for (var i = current_index; i < lines.length; i++) {
        var dealt_details = re_dealt_line.exec(lines[i]);
        if (!dealt_details) {
          break;
        }
        if (dealt_details[2]) {
          var dealt_line = `Dealt to ${dealt_details[1]} [${dealt_details[3]} ${dealt_details[4]}]`;
          result.push(dealt_line)
        }
      }

      var current_sizing = parseInt(big_blind_details[2].replace(/,/g, ''));

      // Preflop Action
      current_index = i;
      var preflop_result = action(re_action, lines, current_sizing, current_index, small_blind_details, big_blind_details);
      result = result.concat(preflop_result['lines']);
      is_walk = preflop_result['is_walk'];

      // // Flop Heading
      current_index = preflop_result['index'];
      var board_details = [];
      var flop_details = re_flop.exec(lines[current_index]);

      if (flop_details) {
        var flop_heading = `*** FLOP *** [${flop_details[1]} ${flop_details[2]} ${flop_details[3]}]`;
        result.push(flop_heading);
        board_details.push(flop_details[1]);
        board_details.push(flop_details[2]);
        board_details.push(flop_details[3]);
        current_index += 1;
        var flop_result = action(re_action, lines, current_sizing, current_index);
        result = result.concat(flop_result['lines']);

        // Turn Heading
        current_index = flop_result['index'];
        var turn_details = re_big_street.exec(lines[current_index]);
        if (turn_details) {
          var turn_heading = `*** TURN *** [${turn_details[2]}]`;
          board_details.push(turn_details[2]);
          result.push(turn_heading);
          current_index += 1;
          var turn_result = action(re_action, lines, current_sizing, current_index);
          result = result.concat(turn_result['lines']);

          // River Heading
          current_index = turn_result['index'];
          var river_details = re_big_street.exec(lines[current_index]);
          if (river_details) {
            var river_heading = `*** RIVER *** [${river_details[2]}]`;
            board_details.push(river_details[2]);
            result.push(river_heading);
            current_index += 1;
            var river_result = action(re_action, lines, current_sizing, current_index);
            result = result.concat(river_result['lines']);

            current_index = river_result['index'];
          }
        }
      }

      // Summary

      // pot size and showdown
      var pot_size = 0;
      var winners = [];
      var showdowns = [];
      for (var i = current_index+1; i < lines.length; i++) {
        var collected_details = re_collected_line.exec(lines[i]);
        var showdown_details = re_showdown.exec(lines[i]);

        if (showdown_details) {
          if (showdown_details[2] === 'shows') {
            showdowns.push(`${showdown_details[1]}: shows [${showdown_details[4]} ${showdown_details[5]}]`);
          }
        } else if (collected_details) {
          pot_size += parseInt(collected_details[2].replace(/,/g, ''));
          winners.push([collected_details[1], collected_details[2]]);
        }
      }

      // handle no flop situations because site doesn't...
      if (is_walk) {
        if (!small_blind_details) {
          pot_size -= parseInt(big_blind_details[2].replace(/,/g, ''));
        } else {
          pot_size -= parseInt(small_blind_details[2].replace(/,/g, ''))
        }
        winners[0][1] = pot_size + '';
      }

      // board
      board = 'Board ['
      board_details.forEach(function(card, index) {
        if (index+1 !== board_details.length) {
          board += `${card} `;
        } else {
          board += `${card}`;
        }
      });
      board += ']'

      // pushing to result
      if (showdowns.length > 0) {
        result.push('*** SHOW DOWN ***');
        showdowns.forEach(function(showdown) {
          result.push(showdown);
        });
      }
      winners.forEach(function(winner) {
        result.push(`${winner[0]} collected ${winner[1].replace(/,/g, '')} from pot`);
      });
      result.push('*** SUMMARY ***');
      result.push(`Total pot ${pot_size} | Rake 0`);
      result.push(board);

      results.push(result);

// indent here for esting
    });

    var OpenWindow = window.open('unsaved.html');
    OpenWindow.document.write(`<pre>`);
    results.forEach(function(lines) {
      lines.forEach(function(line) {
        OpenWindow.document.write(`${line}\n`);
      });
      OpenWindow.document.write(`\n`);
    });
    OpenWindow.document.write(`</pre>`);
  }

  function action(re_action, lines, current_sizing, current_index, small_blind_details, big_blind_details) {
    var result = {
      lines: [],
      index: 0,
      is_walk: true
    };
    var previous_raiser = {};
    for (var i = current_index; i < lines.length; i++) {
      var action = re_action.exec(lines[i]);
      if (!action) {
        result['index'] = i;
        return result;
      }
      var action_line = `${action[1]}: `;

      if (!big_blind_details) {
        result['is_walk'] = false;
      }

      if (action[2] === 'folds') {
        action_line += 'folds';
      } else if (action[2] === 'checks') {
        action_line += 'checks';
        result['is_walk'] = false;
      } else if (action[2] === 'calls') {
        action_line += `calls ${parseInt(action[4].replace(/,/g, ''))}`;
        previous_raiser[action[1]] = parseInt(action[4].replace(/,/g, ''));
        result['is_walk'] = false;
      } else if (action[2] === 'bets') {
        previous_raiser[action[1]] = parseInt(action[4].replace(/,/g, ''));
        action_line += `bets ${parseInt(action[4].replace(/,/g, ''))}`;
        current_sizing = parseInt(action[4].replace(/,/g, ''));
        result['is_walk'] = false;
      } else {
        var raise_amount = parseInt(action[4].replace(/,/g, ''));
        if (small_blind_details && action[1] === small_blind_details[1]) {
          raise_amount += parseInt(small_blind_details[2].replace(/,/g, ''));
        }
        if (big_blind_details && action[1] === big_blind_details[1]) {
          raise_amount += parseInt(big_blind_details[2].replace(/,/g, ''));
        }
        if (previous_raiser[action[1]] && action[1] in previous_raiser) {
          previous_raiser[action[1]] += raise_amount;
        } else {
          previous_raiser[action[1]] = raise_amount;
        }
        action_line += `raises ${previous_raiser[action[1]] - current_sizing} to ${previous_raiser[action[1]]}`;
        current_sizing = parseInt(action[4].replace(/,/g, ''));
        result['is_walk'] = false;
      }
      result['lines'].push(action_line);
    }
  }
});
