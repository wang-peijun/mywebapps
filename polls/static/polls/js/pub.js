var question_list = {}
var added_questions = {}
var choice_list_set = {}
var added_choices_set = {}
var new_item_id = 1
var csq_id = null       // current_selected_question_id
var question_types = {'0':'单选', '1':'多选', '2':'回答'}
var choice_has_extra_data = {'0':'没有', '1':'有'}

var gen_select_option = function(option, options){
    var ret = ''
    for (var k in options){
        if (option == k){
            ret += `<option value=${k} selected>${options[k]}</option>`
        }
        else{
            ret += `<option value=${k}>${options[k]}</option>`
        }
    }
    return ret
}

var sort_added_questions = function(){
    cnt = 1
    $('#added_question_list').children().each(function(){
        $(this).children().first().text(cnt)
        added_questions[$(this).attr('id')]['index'] = cnt
        cnt++
    })
}

var sort_added_choices = function(){
    cnt = 1
    $('#added_choice_list').children().each(function(){
        $(this).children().first().text(cnt)
        added_choices_set[csq_id][$(this).attr('id')]['index'] = cnt
        cnt++
    })
}

var display_question_list = function (questions, append=true){
    var content = $('<div></div>')
    for (var k in questions){
        if (!(k in added_questions)) {
            content.append(`<option value="${k}">${questions[k]['content']}</option>`)
        }
    }
    if (append){
        $('#question_list').append(content.html())
    }else{
        $('#question_list').html(content.html())
    }
};


var display_choice_list = function (choices, append=true){
    var content = $('<div></div>')
    for (var k in choices){
        if (!(k in added_choices_set[csq_id])) {
            content.append(`<option value="${k}">${choices[k]['content']}</option>`)
        }
    }
    if (append){
        $('#choice_list').append(content.html())
    }else{
        $('#choice_list').html(content.html())
    }
};

var remove_question = function(event){
    // console.log(event.target.value)
    event.stopPropagation()   // 阻止向外传播事件
    var q_id = event.target.value
    delete added_questions[q_id]
    delete choice_list_set[q_id]
    delete added_choices_set[q_id]
    $(event.target).parent().parent().remove()

    display_question_list(question_list['questions'], false)

    if ($('#added_question_list').children().length==0){
        csq_id = null
    }
    else if (q_id==csq_id){
        $('#added_question_list').children().first().trigger('click')
        sort_added_questions()
    }else{
        sort_added_questions()
    }
    console.log(added_questions)
    console.log(added_choices_set) 
}

var remove_choice = function(event){
    // console.log(event.target.value)
    event.stopPropagation()
    var c_id = event.target.value
    delete added_choices_set[csq_id][c_id]
    if (!(c_id.startsWith('new'))){
        display_choice_list(choice_list_set[csq_id]['choices'], false)
    }
    $(event.target).parent().parent().remove()
    sort_added_choices() 
    console.log(added_questions)
    console.log(added_choices_set)
}

// 修改后，生成新的对象, 即对id重命名
var rename_question_id = function(old_id, new_id, event){
    added_questions[new_id] = JSON.parse(JSON.stringify(added_questions[old_id]))
    delete added_questions[old_id]
    choice_list_set[new_id] = choice_list_set[old_id]
    delete choice_list_set[old_id]
    added_choices_set[new_id] = added_choices_set[old_id]
    delete added_choices_set[old_id]
    added_questions[new_id].type = parseInt(event.target.value)

    // 修改tr对应的数据
    $(event.target).parent().parent().attr('id', new_id)
    $(event.target).parent().siblings().last().children().last().attr('value', new_id)
}

var rename_choice_id = function(old_id, new_id, event){
    added_choices_set[csq_id][new_id] = JSON.parse(JSON.stringify(added_choices_set[csq_id][old_id]))
    delete added_choices_set[csq_id][old_id]
    // 修改tr对应的数据
    $(event.target).parent().parent().attr('id', new_id)
    $(event.target).parent().siblings().last().children().last().attr('value', new_id)
}


var change_question_type = function(event){
    event.stopPropagation()
    var q_id = $(event.target).parent().parent().attr('id')
    var new_id = `new${new_item_id++}`

    if (!(q_id.startsWith('new'))){
        rename_question_id(q_id, new_id, event)
    }else
    {
        added_questions[q_id].type = parseInt(event.target.value)
        new_id = q_id
    }

    if (added_questions[new_id].type == 2){
        added_choices_set[new_id] = {}
        choice_list_set[new_id].choices = {}
        display_choice_list({}, false)
        display_added_choice({}, false)
    }
    console.log(added_questions)
}

var change_choice_has_extra_data = function(event){
    var c_id = $(event.target).parent().parent().attr('id')
    added_choices_set[csq_id][c_id].has_extra_data = event.target.value

    if (!(c_id.startsWith('new'))){
        rename_choice_id(c_id, `new${new_item_id++}`, event)
    }
    console.log(added_choices_set[csq_id])
}

var change_question_content = function(event){
    event.stopPropagation()
    var q_id = $(event.target).parent().parent().attr('id')
    added_questions[q_id].content = event.target.value

    if (!(q_id.startsWith('new'))){
        rename_question_id(q_id, `new${new_item_id++}`, event)
    }
    console.log(added_questions)
} 

var change_choice_content = function(event){
    var c_id = $(event.target).parent().parent().attr('id')
    added_choices_set[csq_id][c_id].content = event.target.value

    if (!(c_id.startsWith('new'))){
        rename_choice_id(c_id, `new${new_item_id++}`, event)
    }
    console.log(added_choices_set[csq_id])
}

var display_added_question = function(questions, append=true){
    var context = $('<div></div>')
    var before = $('#added_question_list').children().last().children().first().text()

    if (append){
        var index = parseInt((before)?before:0) + 1
    }else{
        var index = 1
    }
    var oindex = index
    
    for (var k in questions){
        questions[k].index = index
        context.append(`<tr id="${k}" ${index==1?'class="success"':''}>
            <td class="index">${index++}</td>
            <td>
                <select onchange="change_question_type(event);">
                ${gen_select_option(questions[k].type, question_types)}
                </select>
            </td>
            <td>
            <textarea class="col-xs-11" onchange="change_question_content(event);">${questions[k].content}</textarea>
            <button onclick="remove_question(event);" class="col-xs-1 btn btn-default glyphicon glyphicon-remove" value="${k}"></button>
            </td>
            </tr>`)
    }

    if (append){
        $('#added_question_list').append(context.html())
    }else{
        $('#added_question_list').html(context.html())
    }

    if (oindex == 1){
        $('#added_question_list').children().first().trigger('click')
        $('#search_choice').removeAttr('disabled')
    }
}

var display_added_choice = function(choices, append=true){
    var context = $('<div></div>')
    var before = $('#added_choice_list').children().last().children().first().text()

    if (append){
        var index = parseInt((before)?before:0) + 1
    }else{
        var index = 1
    }
    
    for (var k in choices){
        choices[k].index = index
        context.append(`<tr id="${k}"}>
            <td class="index">${index++}</td>
            <td>
                <select onchange="change_choice_has_extra_data(event);">
                ${gen_select_option(choices[k].has_extra_data, choice_has_extra_data)}
                </select>
            </td>
            <td>
            <textarea class="col-xs-11" onkeyup="change_choice_content(event);">${choices[k].content}</textarea>
            <button onclick="remove_choice(event);" class="col-xs-1 btn btn-default glyphicon glyphicon-remove" value="${k}"></button>
            </td>
            </tr>`)
    }

    if (append){
        $('#added_choice_list').append(context.html())
    }else{
        $('#added_choice_list').html(context.html())
    }
}

var new_question = function(event){
    var key = `new${new_item_id++}`
    var new_q = {}
    new_q[key] = {'content':'','type':0,'index':0}
    Object.assign(added_questions, new_q)
    choice_list_set[key] = {'offset':0, 'choices':{}, 'search':'', 'have_searched':false}
    added_choices_set[key] = {}
    display_added_question(new_q)
    console.log(added_questions)
    console.log(added_choices_set)
}

var new_choice = function(event){
    if (csq_id){
        var key = `new${new_item_id++}`
        var new_c = {}
        new_c[key] = {'content':'','has_extra_data':0,'index':0}
        display_added_choice(new_c)
        Object.assign(added_choices_set[csq_id], new_c)
    }else{
        $('#please_choice_question').show().hide(4000)

    }
    console.log(added_questions)
    console.log(added_choices_set)
}

var search_question = function(event){
    var search = $(this).val().trim()
    var url = window.location.pathname + `question?search=${search}`
    question_list['search'] = search
    $.get( url, function( data ) {
        question_list['questions'] = data['questions']
        if (data['offset']){
            question_list['offset'] = data['offset']
        }
        display_question_list(question_list['questions'], false)
        console.log(data['message'])
    });
}

var more_question = function(event){
    var search = question_list['search']
    var offset = question_list['offset']
    var url = window.location.pathname + `question?search=${search}&offset=${offset}`
    $.get(url, function(data){
        Object.assign(question_list['questions'], data['questions'])
        if (data['offset']){
            question_list['offset'] = data['offset']
        }
        display_question_list(data['questions'])
        console.log(data['message'])
    })
}

var search_choice = function(event){
    
    if (csq_id){
        var key = $('#search_choice').val().trim()
        choice_list_set[csq_id]['search'] = key
        var q_id = csq_id.startsWith('new')?'':csq_id
        var url = window.location.pathname + `question_choices?search=${key}&q_id=${q_id}`
        $.get( url, function( data ) {
            choice_list_set[csq_id]['choices'] = data['choices']
            choice_list_set[csq_id]['have_searched'] = true
            if (data['offset']){
                choice_list_set[csq_id]['offset'] = data['offset']
            }
            display_choice_list(data['choices'], false)
            console.log(data['message'])
        });
    }
    else{
        $('#please_choice_question').show().hide(4000)

    }
}

var more_choice = function(event){
    if (csq_id){
        var key = choice_list_set[csq_id]['search']
        q_id = csq_id.startsWith('new')?'':csq_id
        offset = choice_list_set[csq_id]['offset']
        url = window.location.pathname + `question_choices?search=${key}&q_id=${q_id}&offset=${offset}`
        $.get( url, function( data ) {
            Object.assign(choice_list_set[csq_id]['choices'], data['choices'])
            if (data['offset']){
                choice_list_set[csq_id]['offset'] = data['offset']
            }
            display_choice_list(data['choices'])
            console.log(data['message'])
        });
    }else{
        $('#please_choice_question').show().hide(4000)

    }
}

var add_question = function(event){
    var questions = {}
    $('#question_list option:selected').each(function(){
        var q_id = $(this).val()
        questions[q_id] = question_list['questions'][q_id]  
        added_questions[q_id] = question_list['questions'][q_id]
        choice_list_set[q_id] = {'offset':0, 'choices':{}, 'search':'', 'have_searched':false}
        added_choices_set[q_id] = {}
    })
    display_added_question(questions)
    display_question_list(question_list['questions'], false)

    console.log(added_questions)
    console.log(added_choices_set)
}

var add_choice = function(event){
    if (csq_id){
        var choices = {}
        $('#choice_list option:selected').each(function(){
            var c_id = $(this).val()
            added_choices_set[csq_id][c_id] = choice_list_set[csq_id]['choices'][c_id]
            choices[c_id] = choice_list_set[csq_id]['choices'][c_id]
        })
        display_added_choice(choices)
        display_choice_list(choice_list_set[csq_id]['choices'], false)
    }else{
        $('#please_choice_question').show().hide(4000)

    }
    console.log(added_questions)
    console.log(added_choices_set)
}

var submit = function(event){
        data = {'title': $('#title').val(), 'desc': $('#desc').val(), 'questions': added_questions, 'choices':added_choices_set}
        url = window.location.pathname + 'submit/'
        $.ajax({url:url,
            type:'post',
            success:function(data){
            if (data['type'] == 'error'){
                console.log(data)
            }else if(data['type'] == 'success'){
                window.location.replace(data['redirect'])
            }},
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            'data':JSON.stringify(data),
            'headers': {'X-CSRFToken': $.cookie('csrftoken')}})
    }

var preview = function(event){
        data = {'title': $('#title').val(), 'desc': $('#desc').val(), 'questions': added_questions, 'choices':added_choices_set}
        url = window.location.pathname + 'preview/'
        $.ajax({url:url,
            type:'post',
            success:function(data){
            if (data['type'] == 'error'){
                console.log(data)
            }else if(data['type'] == 'success'){
                var obj = window.open("about:blank");
	            obj.document.write(data['html'])
            }},
            contentType: "application/json; charset=utf-8",
            dataType: "json",
            'data':JSON.stringify(data),
            'headers': {'X-CSRFToken': $.cookie('csrftoken')}})
    }

var click_question = function(event){
        tr = $(this)
        if (!(tr.attr('class'))){
            tr.attr('class','success')
            tr.siblings().filter('.success').removeAttr('class')
        }
        csq_id = tr.attr('id')
        if (added_questions[csq_id].type == 2){
            display_choice_list(choice_list_set[csq_id]['choices'], false)
            display_added_choice(added_choices_set[csq_id], false)
            $('#search_choice').val(choice_list_set[csq_id]['search'])
            csq_id = null
        }
        if (csq_id){
            if (choice_list_set[csq_id]['have_searched']){
                $('#search_choice').val(choice_list_set[csq_id]['search'])
            }else{
                search_choice()
            }
            display_choice_list(choice_list_set[csq_id]['choices'], false)
            display_added_choice(added_choices_set[csq_id], false)
        }
    }

$(function(){
    question_list['questions'] = $.parseJSON($('[data-questions-json]').attr('data-questions-json'))
    question_list['offset'] = $('#more_question').attr('data-offset')
    question_list['search'] = ''

    $('#search_question').keyup(search_question);
    $('#search_choice').bind('keyup', search_choice);

    $('#more_question').click(more_question);
    $('#more_choice').click(more_choice)

    $('#add_question').click(add_question);
    $('#add_choice').click(add_choice)

    $('#new_question').click(new_question);
    $('#new_choice').click(new_choice);

    // 点击question，改变choice, 并查询
    $('#added_question_list').on('click', 'tr', click_question)

    $("#submit").click(submit)

    $('#preview').click(preview)

    // 排序
    var fixHelperModified = function(e, tr) {
        var $originals = tr.children();
        var $helper = tr.clone();
        $helper.children().each(function(index) {
            $(this).width($originals.eq(index).width())
        });
        return $helper;
    },
    updateIndex = function(e, ui) {
        $('td.index', ui.item.parent()).each(function (i) {
            $(this).html(i + 1);
            sort_added_choices()
            sort_added_questions()
            console.log(added_questions)
            console.log(added_choices_set)
        });
    };

    $(".sort tbody").sortable({
    helper: fixHelperModified,
    stop: updateIndex
    }).disableSelection();

});


