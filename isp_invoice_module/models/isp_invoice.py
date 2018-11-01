# -*- coding: utf-8 -*-

from odoo import api, fields, models
# from isp_invoice_module.report.numtocurrencyword import *

digitstens1 = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
               "nineteen"]
digitstens2 = ["", "ten", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]
digits = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
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
    if numword != "zero":
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

                if numword1 == "zero":

                    numword = numword2
                else:
                    numword = numword2 + " " + numword1

        j = j + 1
        k = i - j
        if k >= 0:

            digit = str(myVar)[k]
            numword3 = digits[int(digit)]
            if numword3 == "zero":

                numword = numword
            else:
                numword = numword3 + " hundred " + numword

    numword = ", paisa " + numword
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
    if numword1 != "zero":
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

                    if numword1 == "zero":
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
            if numword3 == "zero":

                numword = numword
            else:
                if len(numword) > 2:
                    if len(detectpoint) > 1:
                        if len(numword.split(",")[0]) > 2:
                            numword = numword3 + " hundred and " + numword
                        else:
                            numword = numword3 + " hundred " + numword
                    else:
                        numword = numword3 + " hundred and " + numword
                else:
                    numword = numword3 + " hundred " + numword

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
        if numword1 == "zero":

            numwordth = numword
        else:
            numwordth = numword1 + " thousand " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " thousand " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "zero":

                        numwordth = numword2 + " thousand " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " thousand " + numword

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
        if numword1 == "zero":

            numwordth = numword
        else:
            numwordth = numword1 + " lakh " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " lakh " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "zero":

                        numwordth = numword2 + " lakh " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " lakh " + numword

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
        numwordth = numword1 + " crore " + numword

        j = j + 1
        k = i - j
        if k >= 0:

            digit = int(str(myVar)[k])
            if digit == 1:

                digit = str(myVar)[k + 1]
                numword2 = digitstens1[int(digit)]
                numwordth = numword2 + " crore " + numword

            else:
                digit = str(myVar)[k]
                numword2 = digitstens2[int(digit)]
                if numword2 != "":

                    if numword1 == "zero":

                        numwordth = numword2 + " crore " + numword
                    else:
                        numwordth = numword2 + " " + numword1 + " crore " + numword

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
        print(numbertoconvert)
        number = numbertoconvert
        number = str(number).split(".")
        myVar = number[0]
        numlength = len(str(myVar))
        digit = str(myVar)[1]
        if len(number) > 1:
            numlength2 = len(str(number[1]))
            return converttopaisa(numlength2, numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, number[1],
                           digit)

        else:
            return converttoword(numlength, j, k, numword, digitstens1, digitstens2, digits, myVar, digit)


