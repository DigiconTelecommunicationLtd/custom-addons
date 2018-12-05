$(document).ready(function() {
    /**
    Custom functions and views of portal keeps here
    **/
    BASE_URL = window.location.origin
    ERROR_MSG = "Sorry, You don't have any unpaid bill!!!"

    var showInvoiceError = function () {
        var invoice_error = "<th></th>";
        invoice_error += "<td>";
            invoice_error += '<span class="text text-danger">';
                invoice_error += '<strong>';
                    invoice_error += ERROR_MSG;
                invoice_error += '</strong>';
            invoice_error += '</span>';
        invoice_error += "</td>";
        $("tr#show_invoice_info").html(invoice_error);
        $("input#payment_bill_amount").val('').removeAttr('readonly');
    }
    var showInvoiceInfo = function (invoiceId, invoiceNumber, invoiceAmount) {
        /*
        Shows invoice info on view
        */
        var invoice_info = "<th>Invoice No:</th>";
        invoice_info += "<td>";
            invoice_info += '<div class="input-group">';
                invoice_info += '<div class="input-group-addon">';
                    invoice_info += '<i class="fa fa-file"></i>';
                invoice_info += '</div>';
                invoice_info += '<input type="hidden" name="invoice_id" value="' + invoiceId + '" />';
                invoice_info += '<input type="text" name="invoice_number" class="form-control pull-right" readonly="1" ';
                invoice_info += 'value="' + invoiceNumber + '" />';
            invoice_info += '</div>';
        invoice_info += "</td>";

        $("tr#show_invoice_info").html(invoice_info);
        $("input#payment_bill_amount").val(invoiceAmount).attr('readonly', 1);
    }


    var getPackageChangeSuccessMsg = function () {
        /*
        Returns Package Change success msg
        */
        var msg = "";
        msg += '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">×</button>';
        msg += '<h4><i class="icon fa fa-check"></i> Success</h4>';
        msg += 'Your Package change request enlisted Successfully';

        return msg;
    }

    var getCustomerInvoiceInfo = function (type_id) {
        /*
        Make a get call to the server to retrieve the customer and invoice info
        */
        url = BASE_URL + "/selfcare/get-invoice/" + type_id
        $.ajax({
            url: url,
            method: "GET",
            success: function(result){
                var res = JSON.parse(result);
                console.log(res);
                if ((res.invoice.id)) {
                    showInvoiceInfo(res.invoice.id, res.invoice.number, res.invoice.amount_total)
                } else {
                    if (res.invoice.in_service_type){
                        showInvoiceError();
                    } else {
                        $("tr#show_invoice_info").attr('style', "display : none;");
                        $("input#payment_bill_amount").val('').removeAttr('readonly');
                    }
                }
            }
        });
    };




    var postPackageChangeInfo = function (csrf_token, next_package_id, change_from, date) {
        /*
        Make a post call to the server to change the plan
        */
        url = BASE_URL + "/selfcare/change-package/" + next_package_id
        $.ajax({
            url: url,
            method: "POST",
            data : {
                'csrf_token' : csrf_token,
                'change_package_from' : change_from,
                'date' : date,
            },
            success: function(result){
                var res = JSON.parse(result);
                if (res['response']) {
                    var show_success_msg = getPackageChangeSuccessMsg()
                    $('div#idShowPackageChangeSuccessMsg').show();
                    $('div#idShowPackageChangeSuccessMsg').html(show_success_msg);
                    $('button#idSubmitChangePackage').removeAttr('disabled');
                }
            }
        });
    };


    var getCustomerPackageModalMsg = function (current_package_name, next_package_name) {
        /*
        Returns Message that will show on the modal of package change
        */
        var msg = "";
        msg += "You want to change the Current Plan (<strong>" + current_package_name +"</strong>)";
        msg += " to <strong>" + next_package_name +"</strong>.";

        return msg;
    }

    $("select#payment_service_type").on('change', function(){
        var type_id = $(this).val()
        var show_inv_dom = $("tr#show_invoice_info")
        show_inv_dom.attr('style', "display : all;");
        getCustomerInvoiceInfo(type_id);
//        $("tr#show_invoice_info").attr('style', "display : none;");
    });


    // remove attr in change the plan modal
    $('input#idImmediately').on('click', function(){
        var activation_date_obj = $('input#idPackageActivationDate');
        activation_date_obj.removeAttr('disabled').select();
    });
    // disable the datepicker
    $('input#idNextBillCycle').on('click', function(){
        var activation_date_obj = $('input#idPackageActivationDate');
        activation_date_obj.attr('disabled', 1)
    });

    // showing modal messages
    $('button.change_to_package_info').on('click', function(){
        var this_obj_id = $(this).attr('data-id');
        var this_obj_name = $(this).attr('data-name');
        var user_current_package_name = $('input#idUserCurrentPackageName').val();
        var modal_msg_id_obj = $('p#idShowPackageChangeModalMsg');
        var show_package_success_msg = $('div#idShowPackageChangeSuccessMsg').hide();
        var package_modal_msg = '';

        // change to package id
        var change_to_package_id = $('input#idChangeToPackageId').val(this_obj_id);

        // showing packages names in modal
        package_modal_msg = getCustomerPackageModalMsg(user_current_package_name, this_obj_name);
        modal_msg_id_obj.html(package_modal_msg);
    });

    // submit the data to change the plan or package
   $('button#idSubmitChangePackage').on('click', function(event){
       event.preventDefault();
       $('button#idSubmitChangePackage').attr('disabled', 1);

       var csrf_token = $('input#idCSRFToken').val();
       var data_json = $("form#idChangePackageForm").serializeArray();

       // post the data to url
       csrf_token = data_json[0]['value'];
       next_package_id = data_json[1]['value'];
       change_from = data_json[2]['value'];
       date = (data_json[2]['value'] == 'immediately') ? data_json[3]['value'] : '';

       postPackageChangeInfo(csrf_token, next_package_id, change_from, date);
       // $('button#idSubmitChangePackage').removeAttr('disabled');
   });

    // Click event of 'Create Ticket' button of 'Customer Profile'
    $('button#createTicket').on('click', function(event){
        // Disable the button for multiple click event.
        $('button#createTicket').attr('disabled', 1);
    });



    //Date picker
    $('input#idPackageActivationDate').datepicker({
        autoclose: true,
        format: 'yyyy-mm-dd',
        changeMonth: true,
        changeYear: true
    });

    var url = window.location.pathname;
    url = url.substring(url.indexOf('/'));

    $('.sidebar-menu-item').each(function() {
        var href = $(this).attr('href');
        if (url == href) {
            $(this).parent().attr("class","active");
            if ($(this).parent().parent().parent().attr('class') == "treeview"){
                $(this).parent().parent().show();
                $(this).parent().parent().parent().attr("class","treeview menu-open");
            }
        }
    });

});
