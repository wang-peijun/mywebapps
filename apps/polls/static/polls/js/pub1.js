var question_list = {}
var added_question_list = {}
var choice_lists = {}
var added_choice_lists = {}
var current_question_id = null
var new_item_id = 1
var question_types = ['type', {'0':'单选', '1':'多选', '2':'回答'}]
var choice_has_extra_data = ['has_extra_data', {'0':'没有', '1':'有'}]
var map_list = {'question_list':[question_list, added_question_list, 'added_question_list'], 'choice_list':[choice_lists, added_choice_lists, 'added_choice_list']}
var map_added_list = {'added_question_list': [question_types, 'question_list'], 'added_choice_list': [choice_has_extra_data, 'choice_list']}


var display_list = function (list_id){
    var content = $('<div></div>')
    for (var k in map_list[list_id][0]){
        if (!(k in map_list[list_id][1])) {
            content.append(`<option value="${k}">${map_list[list_id][0][k]['content']}</option>`)
        }
    }
    $(`#${list_id}`).html(content.html())
};


var gen_select_option = function(type, options){
    var ret = ''
    for (var k in options){
        if (type == k){
            ret += `<option value=${k} selected>${options[k]}</option>`
        }
        else{
            ret += `<option value=${k}>${options[k]}</option>`
        }
    }
    return ret
};

var sort_added_index = function(added_list_id){
    var div = $(`#${added_list_id}`).children()
    cnt = 1
    div.each(function(){
        $(this).first().children().first().text(cnt++)
    })
}

var remove_item = function(event, list_id){
    var id = event.target.value
    delete map_list[list_id][1][id]
    if (!(id.startsWith('new'))){
        display_list(list_id)
    }
    $(event.target).parent().parent().remove()
    sort_added_index(map_list[list_id][2])
}

var change_select_option = function(event){
    var tr = $(event.target).parent().parent()
    var item_id = tr.attr('id')
    var added_list_id = tr.parent().attr('id')
    var list_id = map_added_list[added_list_id][1]
    map_list[list_id][1][item_id][map_added_list[added_list_id][0][0]] = event.target.value
    console.log(map_list[list_id][1])
}

var change_item_content = function(event){
    var tr = $(event.target).parent().parent()
    var item_id = tr.attr('id')
    var added_list_id = tr.parent().attr('id')
    var list_id = map_added_list[added_list_id][1]
    map_list[list_id][1][item_id].content = event.target.value
    console.log(map_list[list_id][1])
} 

var display_added_items = function(items, added_list_id, append=true){
    var context = $('<div></div>')
    var before = $(`#${added_list_id}`).children().last().children().first().text()
    if (append){
        var index = parseInt((before)?before:0) + 1
    }else{
        var index = 1
    }
    var oindex = index
    
    for (var k in items){
        var [attr, options] = map_added_list[added_list_id][0]
        context.append(`<tr id="${k}" ${index==1?'class="active"':''}>
            <td class="index">${index++}</td>
            <td>
                <select onchange="change_select_option(event)">
                ${gen_select_option(items[k][attr], options)}
                </select>
            </td>
            <td>
            <textarea class="col-xs-11" onchange="change_item_content(event);">${items[k].content}</textarea>
            <button onclick="remove_item(event, '${map_added_list[added_list_id][1]}');" class="col-xs-1 btn btn-default glyphicon glyphicon-remove" value="${k}"></button>
            </td>
            </tr>`)
    }

    if (append){
        $(`#${added_list_id}`).append(context.html())
    }else{
        $(`#${added_list_id}`).html(context.html())
    }

    if (oindex == 1){
        console.log($('#added_question_list :first-child :first-child').trigger('click'))
        current_question_id = $('#added_question_list :first-child').attr('id')
    }
}

var new_question = function(event){
    var key = `new${new_item_id++}`
    var new_q = {}
    new_q[key] = {'content':'','type':0,'index':0}
    display_added_items(new_q, 'added_question_list')
    Object.assign(added_question_list, new_q)
}


var new_choice = function(event){
    var key = `new${new_item_id++}`
    var new_c = {}
    new_c[key] = {'content':'','has_extra_data':0,'index':0}
    display_added_items(new_c, 'added_choice_list')
    Object.assign(added_choice_list, new_c)
}


var search_question = function(event){
    var key = $(this).val().trim()
    url = window.location.pathname + `question?search=${key}`
    $.get( url, function( data ) {
        for (k in question_list){
            delete question_list[k]
        }
        Object.assign(question_list, data['questions'])
        console.log(data['message'])
        display_list('question_list')
    });
}

var search_choice = function(event, q_id){
    var key = $('#search_choice').val().trim()
    q_id = q_id?q_id:''
    url = window.location.pathname + `question_choices?search=${key}&q_id=${q_id}`
    $.get( url, function( data ) {
        for (k in choice_list){
            delete choice_list[k]
        }
        Object.assign(choice_list, data['choices'])
        console.log(data['message'])
        display_list('choice_list')
    });
}

var add_item = function(event, list_id){
    $(`#${list_id} option:selected`).each(function(){
        var id = $(this).val()
        if (list_id=='question_list'){
            choice_lists[id] = {}
            added_choice_lists[id] = {}
        }
        map_list[list_id][1][id] = map_list[list_id][0][id]
        var item = {}
        item[id] = map_list[list_id][0][id]
        display_added_items(item, map_list[list_id][2])
    })
    display_list(list_id)
}


$(function(){
    Object.assign(question_list, $.parseJSON($('[data-questions-json]').attr('data-questions-json')))
    Object.assign(choice_lists, $.parseJSON($('[data-choices-json]').attr('data-choices-json')))

    $('#search_question').keyup(search_question);
    $('#search_choice').keyup(search_choice);

    $('#add_question').click(function(event){
        add_item(event, 'question_list')
    });
    $('#add_choice').click(function(event){
        add_item(event, 'choice_list')
    });
    
    $('#new_question').click(new_question);
    $('#new_choice').click(new_choice);

    $('#added_question_list').on('click', 'tr', function(){
        tr = $(this)
        if (!(tr.attr('class'))){
            tr.attr('class','active')
        }
        tr.siblings().filter('.active').removeAttr('class')

        if (!(tr.attr('id').startsWith('new'))){
            search_choice('', tr.attr('id'))
        }
        
        current_question_id = tr.attr('id')


    })

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
        });
    };

    // $("#sort tbody").sortable({
    // helper: fixHelperModified,
    // stop: updateIndex
    // }).disableSelection();

    $(".sort tbody").sortable({
        helper: fixHelperModified,
        stop: updateIndex
        }).disableSelection();
    // 排序完成
    

});


