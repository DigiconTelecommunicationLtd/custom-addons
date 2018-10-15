odoo.define('isp_crm_module.customer_package_list', ['web.ajax'], function (require) {
    "use strict";

    //Define Ajax variable

    var ajax = require('web.ajax');

    //Json rpc call

    ajax.jsonRpc("/customer/package/list/", 'call', {

    }).then(function (data) {

         var user = data['user'];
         var packageName = data['packageName'];
         var packageCode = data['packageCode'];
         var packagePrice = data['packagePrice'];

         if(packageName.length > 0){
             document.getElementById("package_list_table").getElementsByTagName("tbody")[0].innerHTML = "<tr><td scope=\"row\">"+packageName[0]+"</td><td>"+packageCode[0]+"</td><td>"+packagePrice[0]+"</td></tr>";

             for(var i = 1; i < packageName.length; i++){

                document.getElementById("package_list_table").getElementsByTagName("tbody")[0].innerHTML += "<tr><td scope=\"row\">"+packageName[i]+"</td><td>"+packageCode[i]+"</td><td>"+packagePrice[i]+"</td></tr>";

             }
         }

    });


});