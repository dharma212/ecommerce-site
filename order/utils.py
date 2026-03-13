from io import BytesIO
from datetime import date
from decimal import Decimal
from django.core.files.base import ContentFile
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from .models import Invoice


def generate_invoice(order):

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(8.5 * inch, 11 * inch),
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    styles["Normal"].fontSize = 9
    styles["Normal"].leading = 12

    elements = []

    # ================= HEADER =================
    header_data = [[
        # Paragraph("<b>E COMMERCE PVT LTD</b>", styles["Title"]),
        Paragraph("<b>TAX INVOICE</b>", styles["Heading2"]),
    ]]

    header_tab = Table(header_data, colWidths=[4 * inch, 3.5 * inch])
    header_tab.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
    ]))

    elements.append(header_tab)
    elements.append(Spacer(1, 20))

    # ================= INVOICE DETAILS =================
    meta_data = [[
        Paragraph(
            "<b>FROM:</b><br/>"
            "E Commerce Pvt Ltd<br/>"
            "GSTIN: 24ABCDE1234F1Z5<br/>"
            "Ahmedabad, Gujarat - 380001",
            styles["Normal"],
        ),
        Paragraph(
            f"<b>Invoice No:</b> INV-{order.id}<br/>"
            f"<b>Date:</b> {date.today()}<br/>"
            f"<b>Order ID:</b> {order.id}",
            styles["Normal"],
        ),
    ]]

    meta_table = Table(meta_data, colWidths=[3.75 * inch, 3.75 * inch])
    elements.append(meta_table)
    elements.append(Spacer(1, 20))

    # ================= BILL TO =================
    bill_data = [[
        Paragraph(
            f"<b>BILL TO:</b><br/>"
            f"{order.user.get_full_name()}<br/>"
            f"{order.address}<br/>"
            f"Phone: {order.phone}",
            styles["Normal"],
        )
    ]]

    bill_tab = Table(bill_data, colWidths=[7.5 * inch])
    bill_tab.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(bill_tab)
    elements.append(Spacer(1, 25))

    # ================= PRODUCT TABLE =================
    product_data = [[
        Paragraph("<b>Description</b>", styles["Normal"]),
        Paragraph("<b>Qty</b>", styles["Normal"]),
        Paragraph("<b>Price</b>", styles["Normal"]),
        Paragraph("<b>CGST</b>", styles["Normal"]),
        Paragraph("<b>SGST</b>", styles["Normal"]),
        Paragraph("<b>Total</b>", styles["Normal"]),
    ]]

    taxable_value = Decimal("0.00")
    cgst_total = Decimal("0.00")
    sgst_total = Decimal("0.00")
    total_amount = Decimal("0.00")

    for item in order.items.all():
        amount = item.price * item.quantity
        base_price = amount / Decimal("1.18")
        cgst = base_price * Decimal("0.09")
        sgst = base_price * Decimal("0.09")

        taxable_value += base_price
        cgst_total += cgst
        sgst_total += sgst
        total_amount += amount

        product_data.append([
            Paragraph(item.product.name, styles["Normal"]),  # ✅ wrapped properly
            Paragraph(str(item.quantity), styles["Normal"]),
            Paragraph(f"{base_price:.2f}", styles["Normal"]),
            Paragraph(f"{cgst:.2f}", styles["Normal"]),
            Paragraph(f"{sgst:.2f}", styles["Normal"]),
            Paragraph(f"{amount:.2f}", styles["Normal"]),
        ])

    product_table = Table(
        product_data,
        colWidths=[3 * inch, 0.7 * inch, 1 * inch, 0.9 * inch, 0.9 * inch, 1 * inch],
        repeatRows=1,
    )

    product_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#333333")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))

    elements.append(product_table)
    elements.append(Spacer(1, 20))

    # ================= TOTALS =================
    payment_charge = Decimal("47.00") if order.payment_method == "cod" else Decimal("7.00")
    grand_total = total_amount + payment_charge

    totals_data = [
        ["", "Taxable Value:", f"Rs. {taxable_value:.2f}"],
        ["", "CGST (9%):", f"Rs. {cgst_total:.2f}"],
        ["", "SGST (9%):", f"Rs. {sgst_total:.2f}"],
        ["", "Shipping:", f"Rs. {payment_charge:.2f}"],
        ["", "Grand Total:", f"Rs. {grand_total:.2f}"],
    ]

    totals_tab = Table(totals_data, colWidths=[4 * inch, 2 * inch, 1.5 * inch])
    totals_tab.setStyle(TableStyle([
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("FONTNAME", (1, -1), (2, -1), "Helvetica-Bold"),
        ("LINEABOVE", (1, -1), (2, -1), 1, colors.black),
    ]))

    elements.append(totals_tab)
    elements.append(Spacer(1, 30))

    elements.append(
        Paragraph("This is a computer generated invoice.", styles["Normal"])
    )

    doc.build(elements)

    buffer.seek(0)

    invoice = Invoice.objects.create(
        order=order,
        invoice_number=f"INV-{order.id}",
    )

    invoice.invoice_file.save(
        f"INV-{order.id}.pdf",
        ContentFile(buffer.getvalue()),
        save=True,
    )

    buffer.close()

    return invoice