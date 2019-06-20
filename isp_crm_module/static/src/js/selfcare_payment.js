$(document).ready(function() {
    var monthly_payment_bill_amount = $("p#monthly_payment_bill_amount").text();
    $("select#payment_service_type").change(function(){
        var selected_service_type = $(this).val();
        if (selected_service_type == "1") {
//            document.getElementById("payment_bill_amount").value = monthly_payment_bill_amount;
            $("input#payment_bill_amount").val(monthly_payment_bill_amount.trim());
        }else {
          $("input#payment_bill_amount").val("");
        }
    });

});