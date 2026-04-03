# Copyright <YEAR(S)> <AUTHOR(S)>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Sports Association Sale",
    "summary": "Manage sports association sales",
    "version": "17.0.1.0.0",
    "category": "Sports",
    "author": "<Vicente Galiana>, Punt Sitemes",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sports_association","sale_management"
    ],
    "data": [
        "views/sport_ticket_views.xml",
        "views/sale_order_views.xml",
        "views/product_template_views.xml",
    ],
}