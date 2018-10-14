odoo.define('isp_crm_module.template_ticket_list', ['web.ajax'], function (require) {
    "use strict";

    //Define Ajax variable

    var ajax = require('web.ajax');

    //Json rpc call

    ajax.jsonRpc("/customer/profile/ticket/", 'call', {

    }).then(function (data) {

         var user = data['user'];
         var problemName = data['problemName'];
         var problemDescription = data['problemDescription'];
         var problemStage = data['problemStage'];

         document.getElementById("ticket_list_table").getElementsByTagName("tbody")[0].innerHTML = "<tr><td scope=\"row\">"+problemName[0]+"</td><td>"+problemDescription[0]+"</td><td>"+problemStage[0]+"</td></tr>";

         for(var i = 1; i < problemName.length; i++){

            document.getElementById("ticket_list_table").getElementsByTagName("tbody")[0].innerHTML += "<tr><td scope=\"row\">"+problemName[i]+"</td><td>"+problemDescription[i]+"</td><td>"+problemStage[i]+"</td></tr>";

         }

    });


});