odoo.define('isp_crm_module.customer_profile_show', ['web.ajax'], function (require) {
    "use strict";

    //Define Ajax variable

    var ajax = require('web.ajax');

    //Json rpc call

    ajax.jsonRpc("/customer/profile/", 'call', {

    }).then(function (data) {

         var user = data['user'];
         var name = data['name'];
         var isPotentialCustomer = data['is_potential_customer'];

         console.log(name);
         console.log(isPotentialCustomer);

         document.getElementById("company_name").innerHTML = name;
         document.getElementById("is_potential_customer").innerHTML = isPotentialCustomer;


    });


});