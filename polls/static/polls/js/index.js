var selected_polls = 'underway_polls'
var underway_polls = {}
var finished_polls = {}
var current_underway_page = 1
var current_finished_page = 1

var display_polls = function(polls){
  // <li class="list-group-item"><a href="{{url('polls:detail', args=(poll.id,))}}">{{poll.title}}</a></li>
  content = $('<div></div>')
  if (polls){
    for (k in polls){
      content.append(`<li class="list-group-item"><a href="${polls[k].url}">${polls[k].title}</a></li>`)
    }
    $('#display_polls ul').html(content.html())
  }else{
    $('#display_polls ul').html('没有数据')
  }
}


$(function(){
  underway_polls_first_page = JSON.parse($('[data-first-underway-page]').attr('data-first-underway-page'))
  finished_polls_first_page = JSON.parse($('[data-first-finished-page]').attr('data-first-finished-page'))

  if (Object.keys(underway_polls_first_page).length){
    Object.assign(underway_polls, {'1': underway_polls_first_page})
  }
  if (Object.keys(finished_polls_first_page).length){
    Object.assign(finished_polls, {'1':finished_polls_first_page})
  }
  console.log(underway_polls)
  console.log(finished_polls)

  $('.nav li').click(function(event){
    if (!($(this).hasClass('active'))){
      $(this).addClass('active')
      $(this).siblings().filter('.active').removeClass('active')
      if ($(this).attr('id')=='underway_nav'){
        $('#underway_page').removeAttr('hidden')
        $('#finished_page').attr('hidden', 'hidden')
        selected_polls = 'underway_polls'
        display_polls(underway_polls[current_underway_page])
      }else if ($(this).attr('id')=='finished_nav'){
        $('#finished_page').removeAttr('hidden')
        $('#underway_page').attr('hidden', 'hidden')
        selected_polls = 'finished_polls'
        display_polls(finished_polls[current_finished_page])
      }
    }
    console.log(underway_polls)
    console.log(finished_polls)
  })

  $('.pagination li').filter('.page').click(function(event){
    if (!($(this).hasClass('active'))){
      $(this).addClass('active')
      $(this).siblings().filter('.active').first().removeClass('active')
      var page = $(this).text()
      if (selected_polls=='underway_polls'){
        current_underway_page = page
        if (underway_polls[page]){
          display_polls(underway_polls[page])
        }else{
          url = window.location.pathname + `?underway_page=${page}`
          $.get(url, function(data){
            display_polls(data)
            underway_polls[page] = data
          })
        }
      }else if (selected_polls=='finished_polls'){
        cunrent_finished_page = page
        if (finished_polls[page]){
          display_polls(finished_polls[page])
        }else{
          url = window.location.pathname + `?finished_page=${page}`
          $.get(url, function(data){
            display_polls(data)
            finished_polls[page] = data
          })
        }
      }
    }
    console.log(underway_polls)
    console.log(finished_polls)
  }) 
  
  $('.pagination .previous').click(function(){
      var prev = $('.pagination li').filter('.page').filter('.active').prev()
      if (parseInt(prev.text()) > 0){
        prev.trigger('click')
      }
    })

  $('.pagination .next').click(function(){
      var next = $('.pagination li').filter('.page').filter('.active').next()
      if (parseInt(next.text()) > 0){
        next.trigger('click')
      }
    })
})
