var ajax;

odoo.define('isp_crm_module.template_ticket_create', ['web.ajax'], function (require) {
    "use strict";

    //Define Ajax variable

    ajax = require('web.ajax');


});

document.getElementById("create_customer_profile_update_ticket").onclick = function() {createCustomerProfileUpdateTicket()};

function createCustomerProfileUpdateTicket() {

    var selectProblem = document.getElementById("select_problem");
    var selectedProblem = selectProblem.options[selectProblem.selectedIndex].text;

    var description = document.getElementById("description").value;


    //Json rpc call

    ajax.jsonRpc("/customer/profile/ticket/create/", 'call', {

        'problem' : selectedProblem,
        'description': description,

    }).then(function (data) {

         var output_data = data['success_msg'];

         $(".alert-success").html(output_data);

    });
}