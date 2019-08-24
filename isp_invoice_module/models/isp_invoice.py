# -*- coding: utf-8 -*-

from odoo import api, fields, models
# from isp_invoice_module.report.numtocurrencyword import *

digitstens1 = ["Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen", "Seventeen", "Eighteen",
               "Nineteen"]
digitstens2 = ["", "Ten", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]
digits = ["Zero", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine"]
i = 0
j = 0
k = 0
numword = ""
numlength2 = ""


def converttopaisa(i, numlength, j, k, numword, digitstens1, digitstens2, digits, myVar2, myVar, digit):
    j = j + 1
    k = i - j
    digit = str(myVar)[k]
    numword1 = digits[int(digit)]
    if numword != "Zero":
        numword = numword1

    j = j + 1
    k = i - j
    if k >= 0:
        digit = int(str(myVar)[k])
        if digit == 1:

            digit = str(myVar)[k + 1]
            numword2 = digitstens1[int(digit)]
            numword = numword2

        else:
            digitnext = int(str(myVar)[k + 1])
            if digit == 0 and digitnext == 0:

                numword = ""
            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
            if numword2 != "":

                if numword1 == "Zero":

                    numword = numword2
                else:
                    numword = numword2 + " " + numword1

        j = j + 1
        k = i - j
        if k >= 0:

            digit = str(myVar)[k]
            numword3 = digits[int(digit)]
            if numword3 == "Zero":

                numword = numword
            else:
                numword = numword3 + " Hundred " + numword

    numword = ", Paisa " + numword
    i = 0
    j = 0
    k = 0
    return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar2, digit)


def converttoword(i, j, k, numword, digitstens1, digitstens2, digits, myVar, digit):
    j = j + 1
    k = i - j
    detectpoint = numword.split(",")
    digit = str(myVar)[k]
    numword1 = digits[int(digit)]
    numwordafterpoint = numword
    if numword1 != "Zero":
        numword = numword1 + numword

    j = j + 1
    k = i - j
    if k >= 0:

        digit = int(str(myVar)[k])

        if digit == 1:

            digit = str(myVar)[k + 1]
            numword2 = digitstens1[int(digit)]
            if len(detectpoint) > 1:
                numword = numwordafterpoint
                numword = numword2 + numword
            else:
                numword = numword2
        else:
            digitnext = int(str(myVar)[k + 1])
            if digit == 0 and digitnext == 0:
                if len(detectpoint) > 1:
                    numword = "" + numword
                else:
                    numword = ""
            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "Zero":
                        if len(detectpoint) > 1:
                            numword = numwordafterpoint
                            numword = numword2 + numword
                        else:
                            numword = numword2
                    else:
                        if len(detectpoint) > 1:
                            numword = numword2 + " " + numword
                        else:
                            numword = numword2 + " " + numword1

        j = j + 1
        k = i - j
        if k >= 0:

            digit = str(myVar)[k]
            numword3 = digits[int(digit)]
            if numword3 == "Zero":

                numword = numword
            else:
                if len(numword) > 2:
                    if len(detectpoint) > 1:
                        if len(numword.split(",")[0]) > 2:
                            numword = numword3 + " Hundred and " + numword
                        else:
                            numword = numword3 + " Hundred " + numword
                    else:
                        numword = numword3 + " Hundred and " + numword
                else:
                    numword = numword3 + " Hundred " + numword

        return converttothousand(i, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)

    elif numword != "":
        return numword
        numword = ""


def converttothousand(i, j, k, numword, digitstens1, digitstens2, digits, myVar, digit):
    j = j + 1
    k = i - j
    numwordth = numword

    if k >= 0:

        digit = str(myVar)[k]
        numword1 = digits[int(digit)]
        if numword1 == "Zero":

            numwordth = numword
        else:
            numwordth = numword1 + " Thousand " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " Thousand " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "Zero":

                        numwordth = numword2 + " Thousand " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " Thousand " + numword

        return converttolakh(i, j, k, numwordth, digitstens1, digitstens2, digits, myVar, digit)

    elif numwordth != "":
        return numwordth
        numwordth = ""


def converttolakh(i, j, k, numword, digitstens1, digitstens2, digits, myVar, digit):
    j = j + 1
    k = i - j
    numwordth = numword
    if k >= 0:

        digit = str(myVar)[k]
        numword1 = digits[int(digit)]
        if numword1 == "Zero":

            numwordth = numword
        else:
            numwordth = numword1 + " Lakh " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " Lakh " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "Zero":

                        numwordth = numword2 + " Lakh " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " Lakh " + numword

        return converttocrore(i, j, k, numwordth, digitstens1, digitstens2, digits, myVar, digit)
    elif numwordth != "":
        return numwordth
        numwordth = ""


def converttocrore(i, j, k, numword, digitstens1, digitstens2, digits, myVar, digit):
    j = j + 1
    k = i - j
    numwordth = numword
    if k >= 0:

        digit = str(myVar)[k]
        numword1 = digits[int(digit)]
        numwordth = numword1 + " Crore " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " Crore " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "Zero":

                        numwordth = numword2 + " Crore " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " Crore " + numword

    if numwordth != "":
        return numwordth
        numwordth = ""


class ISPInvoice(models.Model):
    """
    Model for different type of Problems.
    """
    _inherit = "account.invoice"
    _description = "ISP Invoices"

    def convert(slef,numbertoconvert):
        number = numbertoconvert
        number = str(number).split(".")
        myVar = number[0]
        numlength = len(str(myVar))
        digit = str(myVar)[1]
        if len(number) > 1:
            numlength2 = len(str(number[1]))
            # return converttopaisa(numlength2, numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, number[1],
            #                digit)
            return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)

        else:
            return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)

class ISPCRMQuotation(models.Model):
    """
    Model for different type of Problems.
    """
    _inherit = "sale.order"
    _description = "ISP CRM Quotation"

    def convert(slef,numbertoconvert):
        number = numbertoconvert
        number = str(number).split(".")
        myVar = number[0]
        numlength = len(str(myVar))
        digit = str(myVar)[1]
        if len(number) > 1:
            numlength2 = len(str(number[1]))
            # return converttopaisa(numlength2, numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, number[1],
            #                digit)
            return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)

        else:
            return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)


