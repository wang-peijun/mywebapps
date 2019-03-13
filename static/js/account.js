$(function () {
   $('#div_id_captcha img').bind('click', function () {
       $.get('?update_captcha=1', function (data) {
           $('#div_id_captcha img').attr('src', data)
       })
   })
});