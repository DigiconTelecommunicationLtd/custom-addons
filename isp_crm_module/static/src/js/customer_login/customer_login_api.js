var ajax;
var utils;

odoo.define('isp_crm_module.customer_login', ['web.ajax'], function (require) {
    "use strict";

    //Define Ajax variable

    ajax = require('web.ajax');


});

odoo.define('isp_crm_module.customer_login', ['web.utils'], function (require) {
    "use strict";

    //Define Ajax variable

    utils = require('web.utils');


});


var rand = function() {
        return Math.random().toString(36).substr(2); // remove `0.`
    };

var token = function() {
        return rand() + rand(); // to make it longer
    };


document.getElementById("customer_login").onclick = function() {customerLoginRequest()};

function customerLoginRequest() {

    var login = document.getElementById("login").value;
    var password = document.getElementById("password").value;

    //Json rpc call

    ajax.jsonRpc("/customer/login/", 'call', {

        'Login' : login,
        'Password': password,

    }).then(function (data) {

         var output_data = data['success_msg'];
         var loginToken = data['logincode'];

         if (loginToken.length > 2){
            utils.set_cookie('login_token', loginToken);
         }

         var alertSuccessMessage = "<div class=\"alert alert-success\"><strong>"+output_data+"</strong></div>";
         var alertDangerMessage = "<div class=\"alert alert-danger\"><strong>"+output_data+"</strong></div>";

         if(output_data == "Successfully logged in"){
            $(".alertmsg").html(alertSuccessMessage);
         }else{
            $(".alertmsg").html(alertDangerMessage);
         }
    });
}