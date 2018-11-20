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

});
