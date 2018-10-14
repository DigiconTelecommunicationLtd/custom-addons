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
         var subscriberId = data['subscriber_id'];
         var father = data['father'];
         var mother = data['mother'];
         var birthday = data['birthday'];
         var gender = data['gender'];
         var identifierName = data['identifier_name'];
         var identifierPhone = data['identifier_phone'];
         var identifierMobile = data['identifier_mobile'];
         var identifierNid = data['identifier_nid'];
         var serviceType = data['service_type'];
         var connectionType = data['connection_type'];
         var connectionMedia = data['connection_media'];
         var connectionStatus = data['connection_status'];
         var billCycleDate = data['bill_cycle_date'];
         var totalInstallationCharge = data['total_installation_charge'];
         var packageId = data['package_id'];

         if(father == ""){

            father = "N/A";
         }
         if(mother == ""){

            mother = "N/A";
         }
         if(identifierName == ""){

            identifierName = "N/A";
         }
         if(identifierPhone == ""){

            identifierPhone = "N/A";
         }
         if(identifierMobile == ""){

            identifierMobile = "N/A";
         }
         if(identifierNid == false){

            identifierNid = "N/A";
         }
         if(serviceType == false){

            serviceType = "N/A";
         }
         if(connectionType == false){

            connectionType = "N/A";
         }
         if(connectionMedia == false){

            connectionMedia = "N/A";
         }
         if(connectionStatus == false){

            connectionStatus = "N/A";
         }
         if(packageId == false){

            packageId = "N/A";
         }
         if(birthday == false){

            birthday = "N/A";
         }
         if(gender == false){

            gender = "N/A";
         }
         if(identifierNid == false){

            identifierNid = "N/A";
         }


         document.getElementById("company_name").innerHTML = name;
         document.getElementById("subscriber_id").innerHTML = subscriberId;
         document.getElementById("father").innerHTML = father;
         document.getElementById("mother").innerHTML = mother;
         document.getElementById("birthday").innerHTML = birthday;
         document.getElementById("gender").innerHTML = gender;
         document.getElementById("identifier_name").innerHTML = identifierName;
         document.getElementById("identifier_phone").innerHTML = identifierPhone;
         document.getElementById("identifier_mobile").innerHTML = identifierMobile;
         document.getElementById("identifier_nid").innerHTML = identifierNid;
         document.getElementById("service_type").innerHTML = serviceType;
         document.getElementById("connection_type").innerHTML = connectionType;
         document.getElementById("connection_media").innerHTML = connectionMedia;
         document.getElementById("connection_status").innerHTML = connectionStatus;
         document.getElementById("bill_cycle_date").innerHTML = billCycleDate;
         document.getElementById("total_installation_charge").innerHTML = totalInstallationCharge;
         document.getElementById("package_id").innerHTML = packageId;


    });


});