{
    "name": "CRM_Inheritance",
    "version": "1.0",
    "summary": "CRM Module Inheritance and add menu",
    "category": "Operations",
    "author": "Eyuel",
    "depends": ["base",'mail','crm','ahadubit_property_base','temer_structure'],
    "data": [

        "views/crm_lead_callcenter_views.xml",
        "views/crm_lead_reception_views.xml",
        "views/crm_lead_actions.xml",
        
        "views/crm_config.xml",
        "security/call_center_security.xml",
        "security/reception_security.xml",
        "security/ir.model.access.csv",
        "views/crm_lead_menu.xml",
    ],
    "installable": True,
    "application": True,
}
