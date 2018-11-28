$(document).ready(function() {
    /**
    Custom functions and views of portal keeps here
    **/
    BASE_URL = window.location.origin
    ERROR_MSG = "Sorry, You don't have any unpaid monthly bill!!!"

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

    var getCustomerInvoiceInfo = function () {
        /*
        Make a get call to the server to retrieve the customer and invoice info
        */
        url = BASE_URL + "/selfcare/get-invoice"
        $.ajax({
            url: url,
            method: "GET",
            success: function(result){
                var res = JSON.parse(result);
                console.log(res)
                if (res.invoice.id) {
                    showInvoiceInfo(res.invoice.id, res.invoice.number, res.invoice.amount_total)
                } else {
                    showInvoiceError()
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
        if (type_id == 1) {
            show_inv_dom.attr('style', "display : all;");
            getCustomerInvoiceInfo()
        } else {
            show_inv_dom.attr('style', "display : none;");
        }
    });


    // remove attr in change the plan modal
    $('input#idImmediately').on('click', function(){
        var activation_date_obj = $('input#idPackageActivationDate');
        activation_date_obj.removeAttr('disabled').select();
    });

    $('input#idNextBillCycle').on('click', function(){
        var activation_date_obj = $('input#idPackageActivationDate');
        activation_date_obj.attr('disabled', 1)
    });




    $('button.change_to_package_info').on('click', function(){
        var this_obj_id = $(this).attr('data-id');
        var this_obj_name = $(this).attr('data-name');
        var user_current_package_name = $('input#idUserCurrentPackageName').val();
        var modal_msg_id_obj = $('p#idShowPackageChangeModalMsg');
        var package_modal_msg = '';

        // showing packages names in modal
        package_modal_msg = getCustomerPackageModalMsg(user_current_package_name, this_obj_name);
        modal_msg_id_obj.html(package_modal_msg);
    });





    //Date picker
    $('input#idPackageActivationDate').datepicker({
      autoclose: true
    })

});
